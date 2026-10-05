"""Gera HTML do template, FAQ do markdown e WebP das imagens locais."""
from pathlib import Path
from html import escape
from hashlib import sha256
from urllib.parse import quote
import re
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
(OUT / 'assets').mkdir(parents=True, exist_ok=True)
image_dimensions = {}
for name, source in [('entrada', '01-modelo-entrada-v1.png'), ('checkin', '02-celular-checkin-v1.png'), ('academia', '04-background-academia-v1.png'), ('treino', '05-background-treino-mobile-v1.png')]:
    with Image.open(ROOT / 'imagens' / source) as original:
        for width in (480, 800, 1280):
            im = original.convert('RGB')
            im.thumbnail((width, 1800))
            im.save(OUT / 'assets' / f'{name}-{width}.webp', quality=78, method=6)
            image_dimensions[(name, width)] = im.size

# Prévia de links (WhatsApp e redes): JPG 1200x630, formato mais compatível que WebP.
OG_TOP = 0.18
with Image.open(ROOT / 'imagens' / '01-modelo-entrada-v1.png') as original:
    im = original.convert('RGB')
    scale = 1200 / im.width
    im = im.resize((1200, round(im.height * scale)), Image.LANCZOS)
    top = round((im.height - 630) * OG_TOP)
    im.crop((0, top, 1200, top + 630)).save(OUT / 'assets' / 'og-1200x630.jpg', quality=82, optimize=True, progressive=True)

SITE_URL = 'https://acessosfitness.online/'

copy = (ROOT / 'copy-proposta-v1.md').read_text(encoding='utf-8')
faq = copy.split('## Perguntas frequentes')[1].split('## Chamada final')[0]
questions = re.findall(r'### (.*?)\n\n(.*?)(?=\n\n### |\Z)', faq.strip(), re.S)
faq_html = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a.strip())}</p></details>' for q, a in questions)

def cta(label, message='Olá! Quero solicitar minha ativação. Pode me explicar as condições?', cls='button', ident='', track=''):
    attrs = f' id="{escape(ident)}"' if ident else ''
    attrs += f' data-cta="{escape(track)}"' if track else ''
    return f'<a{attrs} class="{cls}" href="https://wa.me/5538992026240?text={quote(message)}" target="_blank" rel="noopener noreferrer">{label}<span aria-hidden="true">↗</span></a>'

def photo(name, alt, eager=False):
    sources = ', '.join(f'assets/{name}-{size}.webp {image_dimensions[(name, size)][0]}w' for size in (480, 800, 1280))
    width, height = image_dimensions[(name, 800)]
    return f'<img src="assets/{name}-800.webp" srcset="{sources}" sizes="(max-width: 760px) calc(100vw - 40px), (max-width: 1000px) 46vw, 560px" alt="{alt}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async" width="{width}" height="{height}">'

whatsapp_icon = '<svg class="contact-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 11.5a8.5 8.5 0 0 1-12.7 7.4L3 20l1.1-4.8A8.5 8.5 0 1 1 20.5 11.5Z"/><path d="m8 7 2 3-1.3 1.3a10 10 0 0 0 4 4L14 14l3 2c-1 3-4 1-6-1s-5-6-3-8Z"/></svg>'
css_version = sha256((OUT / 'styles.css').read_bytes()).hexdigest()[:12]
js_version = sha256((OUT / 'app.js').read_bytes()).hexdigest()[:12]

page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>AcessosFit | Ativação Individual e Família</title>
<meta name="description" content="Conheça a ativação de acesso ao Wellhub pela AcessosFit. Individual por R$ 150 ou Família por R$ 200. Mensalidade separada, paga no aplicativo.">
<link rel="canonical" href="{SITE_URL}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="AcessosFit"><meta property="og:url" content="{SITE_URL}"><meta property="og:title" content="Procurando Gympass para pessoa física? | AcessosFit"><meta property="og:description" content="Acesso ao Wellhub nas opções Individual, por R$ 150, ou Família, por R$ 200 para até quatro pessoas. Mensalidade separada, paga no aplicativo."><meta property="og:image" content="{SITE_URL}assets/og-1200x630.jpg"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Cena ilustrativa de uma mulher com o celular na entrada da academia."><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF8F1"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css?v={css_version}"><script src="app.js?v={js_version}" defer></script></head>
<body><a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="wrap header"><a class="brand" href="#" aria-label="AcessosFit — início">acessos<span>fit</span><i aria-hidden="true">✳</i></a><nav aria-label="Navegação principal"><a href="#opcoes">Ver opções</a><a href="#duvidas">Dúvidas</a></nav></header>
<main id="conteudo">
<section class="wrap hero" aria-labelledby="titulo"><div class="hero-copy"><p class="eyebrow">SEU PRÓXIMO TREINO COMEÇA AQUI</p><h1 id="titulo">Procurando Gympass para <em>pessoa física?</em></h1><p class="intro">Acesso ao Wellhub nas opções Individual (1 pessoa) e Família (até 4).</p><p class="hero-cost"><span>Ativação por Pix; mensalidade à parte</span> <strong>Individual R$ 150</strong> · <strong>Família R$ 200</strong></p>{cta('Consultar academia e plano no WhatsApp', 'Olá! Quero consultar minha academia e saber o plano, a mensalidade e as condições de ativação.', ident='hero-cta', track='hero')}<p class="micro">Ativação com a AcessosFit.<br>Mensalidade separada, paga diretamente no app Wellhub.</p></div><figure class="hero-photo">{photo('entrada','Cena ilustrativa de uma mulher com o celular na entrada da academia.', True)}<figcaption><span>Individual ou Família</span><strong>O treino cabe na sua rotina.</strong></figcaption><span class="image-label">Imagem ilustrativa</span></figure></section>
<section class="pricing section" id="opcoes"><div class="wrap"><div class="section-intro"><p class="eyebrow">ESCOLHA SUA OPÇÃO</p><h2>Quanto custa a ativação?</h2><p>R$ 150 no Individual e R$ 200 no Família, pagos à AcessosFit somente por Pix. A mensalidade Wellhub é separada e paga diretamente no aplicativo, conforme o plano escolhido.</p><p class="format-note"><strong>Sobre o cadastro:</strong> O acesso usa uma vaga cedida por empresa parceira. O nome e o CPF vinculados ao acesso são os da vaga cedida. Converse com a AcessosFit sobre esse formato antes de pagar.</p></div><div class="plans"><article class="plan"><div class="plan-heading"><h3>Individual</h3><span>Para uma pessoa</span></div><p class="price"><span>R$</span> 150</p><p class="price-label">de ativação para uma pessoa</p><div class="plan-content"><p>Ativação paga à AcessosFit <strong>somente por Pix.</strong></p><p>Você paga sua mensalidade diretamente no app Wellhub.</p></div>{cta('Quero o Individual','Olá! Quero solicitar o Individual de R$ 150. Pode me explicar a ativação e a mensalidade do Wellhub?', track='individual')}</article><article class="plan"><div class="plan-heading"><h3>Família</h3><span>Até quatro pessoas</span></div><p class="price"><span>R$</span> 200</p><p class="price-label">de ativação para até quatro pessoas</p><div class="plan-content"><p>Por R$ 50 a mais que o Individual, você ativa até quatro acessos. Cada participante paga sua mensalidade separadamente no app Wellhub.</p><p>Cada participante tem um acesso separado e escolhe seu plano no aplicativo.</p><p>Ativação paga à AcessosFit <strong>somente por Pix.</strong></p></div>{cta('Quero o Família','Olá! Quero solicitar o Família de R$ 200 para até quatro pessoas. Pode me explicar a ativação e as mensalidades de cada participante?', track='familia')}</article></div><p class="cost-note">Seu custo inicial é a ativação mais a mensalidade escolhida. No Família, some as mensalidades de quem vai participar.</p></div></section>
<section class="how section wrap" id="funcionamento"><div class="how-photo">{photo('checkin','Imagem ilustrativa de celular exibindo uma tela de check-in.')}<span class="image-label">Imagem ilustrativa</span></div><div><p class="eyebrow">ENTENDA A CONTRATAÇÃO</p><h2>Como funciona o acesso pela AcessosFit?</h2><p>A AcessosFit trabalha com vagas cedidas por empresas parceiras quando os colaboradores não utilizam o benefício.</p><div class="payment-flow"><div><span class="step">01</span><p><strong>Ativação</strong><span>Você paga à AcessosFit.</span></p></div><div><span class="step">02</span><p><strong>Mensalidade do plano</strong><span>Você paga diretamente ao Wellhub, no aplicativo.</span></p></div></div><p>Pelo WhatsApp, consulte sua academia e confirme o plano e as condições do acesso antes de pagar.</p>{cta('Tirar minhas dúvidas no WhatsApp','Olá! Quero tirar dúvidas sobre as condições do acesso pela AcessosFit.','text-link', track='duvidas')}</div></section>
<section class="academy section wrap"><div class="academy-panel"><p class="eyebrow">SUA ACADEMIA, SEU PLANO</p><h2>Funciona na<br>minha academia?</h2><p>Depende do plano escolhido no app Wellhub, porque cada plano dá acesso a uma rede diferente de academias. Envie o nome da academia, a unidade e a cidade pelo WhatsApp para consultar qual plano atende ao local onde você quer treinar.</p>{cta('Consultar minha academia','Olá! Quero consultar qual plano atende à minha academia. Vou informar o nome, a unidade e a cidade.', track='academia')}<span class="image-label">Imagem ilustrativa</span></div></section>
<section class="support section wrap" id="duvidas"><div class="guarantee"><p class="eyebrow">GARANTIA E ATENDIMENTO</p><h2>Como funciona<br>a garantia?</h2><p>Novas compras têm <strong>seis meses de garantia de substituição</strong>, contados a partir da compra original. Se houver um problema com o acesso nesse período, fale com a AcessosFit pelo WhatsApp.</p>{cta('Perguntar sobre a garantia','Olá! Quero entender a garantia de substituição e as condições antes de contratar.','text-link', track='garantia')}</div><div class="faq"><h2>Perguntas frequentes</h2>{faq_html}</div></section>
<section class="wrap final-section" id="contato"><div class="final-panel"><div><p class="eyebrow">VAMOS CONVERSAR?</p><h2>Escolheu<br>sua opção?</h2><p>Fale com a AcessosFit pelo WhatsApp para tirar suas dúvidas e solicitar a ativação.</p>{cta('Quero ativar meu acesso', ident='final-cta', track='final')}<p class="micro">Ativação com a AcessosFit.<br>Mensalidade diretamente no app Wellhub.</p></div><span class="image-label">Imagem ilustrativa</span></div></section>
</main><footer class="wrap footer"><a class="brand" href="#">acessos<span>fit</span><i aria-hidden="true">✳</i></a><div class="footer-contact"><a class="text-link" data-cta="rodape" href="https://wa.me/5538992026240" target="_blank" rel="noopener noreferrer">{whatsapp_icon}<span>Conversar no WhatsApp</span><span aria-hidden="true">↗</span></a></div></footer>
<div class="sticky-cta" hidden>{cta('Conversar no WhatsApp', track='fixo')}</div></body></html>'''
(OUT / 'index.html').write_text(page, encoding='utf-8')
(OUT / 'sitemap.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE_URL}</loc></url>
</urlset>
''', encoding='utf-8')
(OUT / 'assets' / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#D83A56"/><text x="32" y="44" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="40" fill="white">a</text></svg>', encoding='utf-8')
print(f'Gerado: {OUT}; {len(questions)} perguntas frequentes.')
