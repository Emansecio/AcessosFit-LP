"""Offline tests: provider mocked; no credential mounts or outgoing purchases."""
import json
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch
import server


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        server.DB = self.temp.name + '/orders.sqlite3'
        server.initialize()
        self.body = {'plan': 'individual', 'name': 'Teste local', 'document': '52998224725', 'acknowledged': True}
        self.response = {'id': 'offline-sale-123', 'amount': 150, 'status': 'pending', 'pixCode': 'OFFLINE-TEST-CODE-NOT-FOR-PAYMENT'}

    def tearDown(self):
        self.temp.cleanup()

    def create(self):
        with patch.object(server, 'provider', return_value=self.response) as provider:
            result = server.create_order('session1', self.body)
            return result, provider

    def test_fixed_price_and_minimal_data(self):
        self.body['amount'] = 1
        result, provider = self.create()
        self.assertEqual(provider.call_args.args[1]['amount'], 150)
        self.assertEqual(result['order']['amount'], 150)
        saved = server.get_order('session1')
        self.assertNotIn(self.body['document'], json.dumps(saved))
        self.assertNotIn(self.body['name'], json.dumps(saved))

    def test_family_price(self):
        self.body['plan'] = 'familia'
        self.response['amount'] = 200
        _, provider = self.create()
        self.assertEqual(provider.call_args.args[1]['amount'], 200)

    def test_duplicate_reuses_order(self):
        first, _ = self.create()
        with patch.object(server, 'provider') as provider:
            second = server.create_order('session1', self.body)
            self.assertEqual(first, second)
            provider.assert_not_called()

    def test_timeout_reuses_idempotency_key(self):
        with patch.object(server, 'provider', side_effect=server.CheckoutError('timeout', 502)) as provider:
            with self.assertRaises(server.CheckoutError):
                server.create_order('session1', self.body)
            ref = provider.call_args.args[2]
        with server.db() as con:
            con.execute('UPDATE orders SET checked=0')
        _, provider = self.create()
        self.assertEqual(ref, provider.call_args.args[2])

    def test_reject_bad_inputs_without_provider(self):
        for body in ({**self.body, 'plan': 'free'}, {**self.body, 'document': '11111111111'}, {**self.body, 'acknowledged': False}):
            with patch.object(server, 'provider') as provider:
                with self.assertRaises(server.CheckoutError):
                    server.create_order('session1', body)
                provider.assert_not_called()

    def test_paid_requires_provider_verification(self):
        self.create()
        with patch.object(server, 'provider', return_value={**self.response, 'status': 'paid'}):
            self.assertEqual(server.refresh('session1')['order']['status'], 'paid')

    def test_wrong_amount_and_sale_not_accepted(self):
        self.create()
        for response in ({**self.response, 'status': 'paid', 'amount': 1}, {**self.response, 'status': 'paid', 'id': 'other-sale-123'}):
            with patch.object(server, 'provider', return_value=response):
                with self.assertRaises(server.CheckoutError):
                    server.refresh('session1')
            self.assertEqual(server.get_order('session1')['status'], 'pending')

    def test_expired_failed_refunded(self):
        self.create()
        for status in ('expired', 'failed', 'refunded'):
            with server.db() as con:
                con.execute('UPDATE orders SET checked=0')
            with patch.object(server, 'provider', return_value={**self.response, 'status': status}):
                result = server.refresh('session1')['order']
                self.assertEqual(result['status'], status)
                self.assertIsNone(result['pixCode'])

    def test_session_isolation_and_persistence(self):
        self.create()
        self.assertIsNone(server.get_order('session2'))
        server.initialize()
        self.assertEqual(server.get_order('session1')['sale'], self.response['id'])

    def test_no_local_expiry_can_confirm_payment(self):
        self.create()
        with server.db() as con:
            con.execute('UPDATE orders SET created=?', (time.time()-1900,))
        result = server.public_order(server.get_order('session1'))['order']
        self.assertEqual(result['status'], 'pending')
        self.assertIsNone(result['pixCode'])

    def test_qr_encodes_exact_provider_value(self):
        import qrcode
        import qrcode.image.svg
        qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage)
        qr.add_data(self.response['pixCode'])
        self.assertIn(b'<svg', qr.make_image().to_string())

    def test_http_rejects_cross_origin_and_unauthenticated(self):
        httpd = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(httpd.server_port)
        try:
            request = urllib.request.Request(base + '/comprar/api/create', data=b'{}', headers={'Origin': 'https://example.invalid', 'Content-Type': 'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code, 403)
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(base + '/comprar/api/status')
            self.assertEqual(error.exception.code, 401)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
