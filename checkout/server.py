"""AcessosFit checkout. Provider credentials and payment decisions stay server-side."""
import hashlib
import io
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.request
import urllib.error
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = os.getenv('DB_PATH', '/data/orders.sqlite3')
API = 'https://sagacepay.com/api'
KEY_FILE = os.getenv('API_KEY_FILE', '/run/secrets/sagacepay_key')
PLANS = {'individual': (150, 'Individual'), 'familia': (200, 'Família')}
ORIGINS = {'https://acessosfitness.online', 'https://www.acessosfitness.online',
           'http://127.0.0.1:8080', 'http://localhost:8080'}
LOCK = threading.RLock()
BUSY = set()
SESSION_LIFETIME = 7 * 86400
LAST_SESSION_CLEANUP = 0.0


@contextmanager
def db():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


def initialize():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with db() as con:
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('''CREATE TABLE IF NOT EXISTS sessions
          (token TEXT PRIMARY KEY, created REAL NOT NULL)''')
        con.execute('''CREATE TABLE IF NOT EXISTS orders
          (session TEXT PRIMARY KEY, reference TEXT UNIQUE NOT NULL, plan TEXT NOT NULL,
           fingerprint TEXT NOT NULL, created REAL NOT NULL, sale TEXT, pix TEXT,
           status TEXT NOT NULL, checked REAL DEFAULT 0)''')
    cleanup_sessions()


def cleanup_sessions(now=None):
    """Expire anonymous sessions only; preserve every order and its session."""
    global LAST_SESSION_CLEANUP
    now = time.time() if now is None else now
    with LOCK:
        if now - LAST_SESSION_CLEANUP < 3600:
            return
        with db() as con:
            con.execute('''DELETE FROM sessions WHERE created <= ?
                AND NOT EXISTS (SELECT 1 FROM orders WHERE orders.session = sessions.token)''',
                (now - SESSION_LIFETIME,))
        LAST_SESSION_CLEANUP = now


class CheckoutError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status


def provider(path, payload=None, reference=None):
    with open(KEY_FILE, encoding='utf-8') as stream:
        key = stream.read().strip()
    headers = {'x-api-key': key, 'Accept': 'application/json'}
    if reference:
        headers['idempotency-key'] = reference
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(API + path, headers=headers,
        data=None if payload is None else json.dumps(payload).encode())
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read(128_000))
        if not isinstance(result, dict):
            raise ValueError('Unexpected provider shape')
        return result
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        # Never log provider bodies, buyer information or credentials.
        raise CheckoutError('Não conseguimos consultar a operadora agora. Aguarde alguns segundos e tente novamente. Seu pedido foi preservado.', 502)


def valid_cpf(cpf):
    if not re.fullmatch(r'\d{11}', cpf) or len(set(cpf)) == 1:
        return False
    for length in (9, 10):
        digit = (sum(int(cpf[i]) * (length + 1 - i) for i in range(length)) * 10) % 11
        if int(cpf[length]) != (0 if digit == 10 else digit):
            return False
    return True


def verified(data, order, creating=False):
    sid = data.get('id')
    try:
        correct_amount = Decimal(str(data.get('amount'))) == Decimal(PLANS[order['plan']][0])
    except InvalidOperation:
        correct_amount = False
    if not isinstance(sid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{8,100}', sid) or not correct_amount:
        raise CheckoutError('A cobrança precisa ser conferida pelo atendimento. Não efetue o pagamento.', 502)
    if not creating and sid != order['sale']:
        raise CheckoutError('Não foi possível conferir este pagamento.', 502)
    if data.get('externalId') not in (None, order['reference']):
        raise CheckoutError('Não foi possível conferir a referência do pedido.', 502)
    if data.get('status') not in ('pending', 'paid', 'failed', 'expired', 'refunded'):
        raise CheckoutError('O pagamento ainda está em conferência. Tente novamente.', 502)
    return sid


def get_order(session):
    with db() as con:
        row = con.execute('SELECT * FROM orders WHERE session=?', (session,)).fetchone()
    return dict(row) if row else None


def public_order(order):
    if not order:
        return {'order': None}
    result = {k: order[k] for k in ('reference', 'plan', 'status')}
    result['amount'] = PLANS[order['plan']][0]
    result['expiresAt'] = int((order['created'] + 1800) * 1000)
    # A paid status never comes from a browser parameter or an unverified webhook.
    result['pixCode'] = order['pix'] if order['status'] == 'pending' and time.time() < order['created'] + 1800 else None
    return {'order': result}


def create_order(session, body):
    if body.get('acknowledged') is not True:
        raise CheckoutError('Confirme que leu as condições da ativação.')
    plan = body.get('plan')
    name = body.get('name', '')
    document = body.get('document', '')
    if plan not in PLANS or not isinstance(name, str) or not isinstance(document, str):
        raise CheckoutError('Escolha uma opção e informe seus dados.')
    name = ' '.join(name.split())
    document = re.sub(r'[.\-\s]', '', document)
    if len(name) < 3 or len(name) > 120 or not valid_cpf(document):
        raise CheckoutError('Confira o nome e informe um CPF válido do pagador.')
    fingerprint = hashlib.sha256((plan + ':' + name + ':' + document).encode()).hexdigest()
    with LOCK:
        if session in BUSY:
            raise CheckoutError('Seu pedido está sendo processado. Aguarde alguns segundos.', 409)
        order = get_order(session)
        if order and order['sale']:
            return public_order(order)
        if order and (order['fingerprint'] != fingerprint or time.time() - order['created'] > 23 * 3600):
            raise CheckoutError('Já existe um pedido em conferência neste navegador. Mantenha os dados originais ou fale com o atendimento.', 409)
        if order and time.time() - order['checked'] < 10:
            raise CheckoutError('Aguarde alguns segundos antes de tentar novamente.', 429)
        if not order:
            with db() as con:
                con.execute('INSERT INTO orders(session,reference,plan,fingerprint,created,status) VALUES(?,?,?,?,?,?)',
                    (session, 'AF-' + secrets.token_hex(12), plan, fingerprint, time.time(), 'creating'))
            order = get_order(session)
        with db() as con:
            con.execute('UPDATE orders SET checked=? WHERE session=?', (time.time(), session))
        BUSY.add(session)
    try:
        data = provider('/sales', {'amount': PLANS[plan][0],
            'description': 'AcessosFit — ativação ' + PLANS[plan][1],
            'expirationInSeconds': 1800, 'externalId': order['reference'],
            'customer': {'name': name, 'document': document}}, order['reference'])
        sid = verified(data, order, creating=True)
        pix = data.get('pixCode')
        if not isinstance(pix, str) or not 20 <= len(pix) <= 4096:
            raise CheckoutError('A operadora ainda não retornou o código Pix. Tente novamente com os mesmos dados.', 502)
        with db() as con:
            # Paid creation responses are reconciled independently on the next GET.
            con.execute('UPDATE orders SET sale=?,pix=?,status=?,checked=0 WHERE session=?',
                        (sid, pix, 'pending', session))
        return public_order(get_order(session))
    finally:
        with LOCK:
            BUSY.discard(session)


def refresh(session):
    order = get_order(session)
    if not order or not order['sale']:
        return public_order(order)
    with LOCK:
        if session in BUSY or time.time() - order['checked'] < 12:
            return public_order(order)
        BUSY.add(session)
    try:
        data = provider('/sales/' + order['sale'])
        verified(data, order)
        with db() as con:
            con.execute('UPDATE orders SET status=?,checked=? WHERE session=?',
                        (data['status'], time.time(), session))
        return public_order(get_order(session))
    finally:
        with LOCK:
            BUSY.discard(session)


class Handler(BaseHTTPRequestHandler):
    server_version = 'Checkout'

    def log_message(self, *_):
        pass

    def respond(self, status, body, content_type='application/json; charset=utf-8', cookie=None):
        raw = json.dumps(body, ensure_ascii=False).encode() if isinstance(body, dict) else body
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store, private')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def session(self, create=False):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
            token = cookies['af_checkout'].value if 'af_checkout' in cookies else ''
        except Exception:
            token = ''
        digest = hashlib.sha256(token.encode()).hexdigest()
        with db() as con:
            found = con.execute('SELECT created FROM sessions WHERE token=?', (digest,)).fetchone()
        if found and time.time() - found['created'] < SESSION_LIFETIME:
            return digest, None
        if not create:
            raise CheckoutError('Sua sessão expirou. Recarregue a página para continuar.', 401)
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with db() as con:
            con.execute('INSERT INTO sessions VALUES (?,?)', (digest, time.time()))
        local = self.headers.get('Host') in ('127.0.0.1:8080', 'localhost:8080')
        cookie = f'af_checkout={token}; Path=/comprar; HttpOnly; SameSite=Strict; Max-Age=604800'
        if not local:
            cookie += '; Secure'
        return digest, cookie

    def do_GET(self):
        try:
            if self.path == '/health':
                cleanup_sessions()
                return self.respond(200, {'ok': True})
            if self.path == '/comprar/api/session':
                session, cookie = self.session(create=True)
                return self.respond(200, public_order(get_order(session)), cookie=cookie)
            session, _ = self.session()
            if self.path == '/comprar/api/status':
                return self.respond(200, refresh(session))
            if self.path == '/comprar/api/qr':
                order = get_order(session)
                if not order or not order['pix'] or order['status'] != 'pending' or time.time() >= order['created'] + 1800:
                    raise CheckoutError('Código indisponível.', 404)
                import qrcode
                import qrcode.image.svg
                qr = qrcode.make(order['pix'], image_factory=qrcode.image.svg.SvgPathImage, border=4)
                out = io.BytesIO()
                qr.save(out)
                return self.respond(200, out.getvalue(), 'image/svg+xml')
            raise CheckoutError('Não encontrado.', 404)
        except CheckoutError as error:
            self.respond(error.status, {'error': error.message})
        except Exception:
            self.respond(500, {'error': 'Não foi possível concluir. Tente novamente ou fale com o atendimento.'})

    def do_POST(self):
        try:
            if self.path != '/comprar/api/create':
                raise CheckoutError('Não encontrado.', 404)
            origin = self.headers.get('Origin')
            expected = ('http://' if self.headers.get('Host') in ('127.0.0.1:8080', 'localhost:8080') else 'https://') + self.headers.get('Host', '')
            if origin not in ORIGINS or origin != expected or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise CheckoutError('Requisição inválida.', 403)
            session, _ = self.session()
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise CheckoutError('Dados inválidos.', 400)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise CheckoutError('Dados inválidos.')
            self.respond(200, create_order(session, body))
        except CheckoutError as error:
            self.respond(error.status, {'error': error.message})
        except (ValueError, TypeError):
            self.respond(400, {'error': 'Dados inválidos.'})
        except Exception:
            self.respond(500, {'error': 'Não foi possível concluir. Seu pedido foi preservado. Tente novamente.'})


if __name__ == '__main__':
    initialize()
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
