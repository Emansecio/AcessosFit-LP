"""Run against the checkout image with a temporary database and no network."""
import importlib.util
import tempfile
import time
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('checkout', '/app/server.py')
checkout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checkout)


class SessionRetentionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        checkout.DB = self.directory.name + '/orders.sqlite3'
        checkout.LAST_SESSION_CLEANUP = 0
        checkout.initialize()
        self.now = time.time()

    def tearDown(self):
        self.directory.cleanup()

    def test_expired_anonymous_sessions_are_removed_and_orders_preserved(self):
        with checkout.db() as con:
            con.executemany('INSERT INTO sessions VALUES (?,?)', [
                ('expired-anonymous', self.now - 8 * 86400),
                ('expiry-boundary', self.now - 7 * 86400),
                ('active-anonymous', self.now - 86400),
                ('expired-paid', self.now - 30 * 86400),
                ('expired-pending', self.now - 30 * 86400),
            ])
            for status in ('paid', 'pending'):
                con.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)',
                    ('expired-' + status, 'local-fixture-' + status, 'individual',
                     'fixture-fingerprint', self.now - 30 * 86400,
                     'fixture-provider-id', 'fixture-pix', status, self.now))
            original_orders = [tuple(row) for row in con.execute('SELECT * FROM orders ORDER BY session')]
        checkout.LAST_SESSION_CLEANUP = 0
        checkout.cleanup_sessions(self.now)
        with checkout.db() as con:
            sessions = {row['token'] for row in con.execute('SELECT token FROM sessions')}
            remaining_orders = [tuple(row) for row in con.execute('SELECT * FROM orders ORDER BY session')]
        self.assertEqual(sessions, {'active-anonymous', 'expired-paid', 'expired-pending'})
        self.assertEqual(remaining_orders, original_orders)

    def test_cleanup_is_throttled_and_runs_again_after_an_hour(self):
        with checkout.db() as con:
            con.execute('INSERT INTO sessions VALUES (?,?)', ('old', self.now - 8 * 86400))
        checkout.LAST_SESSION_CLEANUP = self.now
        checkout.cleanup_sessions(self.now + 3599)
        with checkout.db() as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 1)
        checkout.cleanup_sessions(self.now + 3600)
        with checkout.db() as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 0)

    def test_startup_applies_retention_without_contacting_the_provider(self):
        with checkout.db() as con:
            con.execute('INSERT INTO sessions VALUES (?,?)', ('old', self.now - 8 * 86400))
        checkout.LAST_SESSION_CLEANUP = 0
        with patch.object(checkout, 'provider', side_effect=AssertionError('Unexpected external call')):
            checkout.initialize()
        with checkout.db() as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
