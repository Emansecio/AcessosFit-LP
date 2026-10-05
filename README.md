# AcessosFit — implantação isolada

Checkout `/comprar` implementado: veja [CHECKOUT.md](CHECKOUT.md) para operação, testes, proteção de credenciais e limitação do teste financeiro real. Fonte em `site/comprar` e `checkout`. Preserve essas pastas nas próximas atualizações da LP.

Somente a LP pública foi copiada para `site/`. Não contém atendimentos nem documentos do projeto original. Fonte editorial e gerador continuam em `C:\Users\Thiago Emanuel\Documents\AcessosFit-Brain\Site`.

## Revisão de conversão para WhatsApp — publicada em 05/10/2026

Pedido de Thiago: aumentar a conversão para o WhatsApp sem alterar fatos, preços, condições ou o produto e sem CNPJ. Base medida antes da mudança (29/09 a 05/10, origem `ads-tagged`): 143 visualizações e 40 cliques em WhatsApp, cerca de 28% em contagem de eventos. Família teve 16 cliques e Individual, 4. Carregamentos de `app.js` por pessoas (sem robôs) nos logs disponíveis: Android 48%, iPhone 37%, computador 15%. No iPhone: Safari 59%, app do Google 24%, Chrome 17%. Três dos 57 cliques foram o mesmo botão repetido em 8 a 27 segundos, sinal possível de WhatsApp que não abriu no primeiro toque.

- Todos os botões têm o ícone do WhatsApp; a seta ↗ saiu. O topo tem um botão WhatsApp (`topo`) ao lado de “Preços”. No desktop, o botão fixo aparece flutuante no canto, com a mesma regra de exibição do celular.
- Abaixo do botão inicial e na chamada final, três fatos já afirmados na página: consulta antes de pagar, início em até 24 horas após Pix e nomes confirmados e seis meses de garantia de substituição. O botão inicial e as garantias cabem na primeira tela de 390×664 px.
- Família mostra a divisão por quatro pessoas: R$ 50 de ativação para cada uma.
- A seção de academias veio para logo depois dos preços e ganhou um campo opcional. O texto digitado só entra na mensagem do WhatsApp e não é enviado ao site. Sem JavaScript, o campo some e o botão abre a mensagem padrão. O evento é `consulta` com o campo preenchido e `academia` sem preenchimento.
- O funcionamento passou a ter quatro passos (consulta, Pix, até 24 horas, mensalidade no app). A FAQ ganhou “Quanto custa a mensalidade do Wellhub?”, com resposta tirada da seção de academias, e um convite ao WhatsApp no fim (`faq`).
- As mensagens pré-preenchidas ficaram mais curtas. As de academia terminam pedindo “Academia, unidade e cidade:”: os registros mostram leads completando a mensagem antes de enviar. Nenhuma mensagem usa os termos que o `webhook_runner.py` lê como cliente existente. Os padrões de intenção do runner pertencem a uma LP anterior; esta versão continua caindo no fallback de adesão, como a atual.
- Eventos `consulta`, `faq` e `topo` acrescentados ao `app.js` e às três listas de `nginx.conf`. Os eventos continuam sem identificador de pessoa e sem o texto digitado.
- Verificação: `test-local.cjs` ampliado e aprovado em 320, 375, 390, 430, 768 e 1440 px, sem rolagem horizontal. Também passaram FAQ pelo teclado, CTA na primeira tela, campo de academia, botão fixo, texto a 200% e uso sem JavaScript. Imagem de teste separada (porta 8099, rede do compose) com `nginx -t` aprovado, eventos novos 204, GET no evento 405, `/comprar/` 200 e cliques reais gerando `consulta` e `topo`. A imagem de teste foi removida. Backup anterior em `hardening/lp-backup-20261005-before-cro/`.
- Horário informado por Thiago: segunda a sexta, das 10h às 20h. A linha “Respondemos de seg. a sex., das 10h às 20h.” aparece abaixo do botão inicial, no campo de academia, na chamada final e na barra fixa do celular. Fora desse horário (UTC−3, inclusive sábado e domingo), `app.js` troca o texto por “Pode enviar agora. Respondemos de seg. a sex., das 10h às 20h.”. Não há aviso de “aberto agora”, porque feriados não estão definidos.
- Em aparelhos de toque (`pointer: coarse`), `app.js` retira `target=_blank` dos links do WhatsApp para abrir na mesma aba; sem JavaScript, continua `_blank`. Motivo: navegadores embutidos, como o app do Google no iPhone, podem não abrir o app ou deixar uma aba vazia com links de nova aba. Também entrou `preconnect` para `wa.me`, e o efeito de hover agora vale só em dispositivos com mouse, para não ficar preso após o toque no iPhone. Teste ampliado com contexto de celular e verificação do horário. Para avaliar depois de publicar, observar se diminuem os toques repetidos no mesmo botão em poucos segundos.
- Publicação autorizada por Thiago e feita em 05/10/2026 por volta de 06:19 UTC. Somente o serviço `lp` foi reconstruído e recriado (`up -d --build --no-deps lp`); checkout e túnel não foram alterados. O container ficou healthy. No domínio, `/`, CSS/JS com hash novo, imagens, `sitemap.xml`, `robots.txt` e `/comprar/` retornaram 200; `www` retornou 301 para o domínio principal; o POST do evento `topo` retornou 204 e o GET, 405. `test-local.cjs` passou contra https://acessosfitness.online nas seis larguras, sem erros. **Eventos de teste a descontar:** entre 06:19:40 e 06:20:10 UTC, um `unattributed/topo` e as `unattributed/page-view` geradas pelos testes. Para avaliar o efeito, comparar os eventos `ads-tagged` por botão a partir de 05/10 com a base acima e observar se diminuem os toques repetidos no mesmo botão.

## Abertura e medição da LP — 29/09/2026

- A primeira tela móvel mostra os preços de ativação (Individual R$ 150 e Família R$ 200), pagamento por Pix e mensalidade Wellhub separada. O botão inicial convida a consultar academia e plano; a mensagem preenchida no WhatsApp corresponde a essa consulta. O aviso sobre o formato do cadastro continua antes dos cartões.
- Os nove links para WhatsApp têm `data-cta`. `app.js` registra uma visualização quando executa e um evento por clique via `POST /lp-events/<origem>/<evento>`, sem impedir a abertura do WhatsApp. `ads-tagged` significa apenas que a URL chegou com `gclid`, `gbraid`, `wbraid` ou UTM Google/CPC; sem esses marcadores, a origem é `unattributed`. Não há identificador de pessoa, clique do anúncio ou campanha nos eventos.
- `events.log`, no volume privado do Nginx, guarda somente horário UTC, caminho do evento e status. A rotação usa a retenção configurada de 30 dias. Para uma contagem rápida do arquivo corrente: `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' exec acessosfit-lp-lp-1 cat /var/log/nginx/private/events.log | ConvertFrom-Json | Group-Object event | Select-Object Name,Count`. As verificações desta implantação geraram eventos de teste em 29/09.
- Visualização e clique são contagens de eventos, não visitantes únicos. O site não observa se a mensagem foi enviada no WhatsApp nem se houve compra; essas etapas exigem comparação com os contatos e pagamentos recebidos. Não há evento de conversão Google Ads configurado.
- O gerador usa o hash de `styles.css` e `app.js` nas URLs do HTML para evitar CSS/JS antigos em cache. Somente o serviço `lp` foi recriado. Após a publicação, o domínio retornou HTTP 200 com os novos textos e arquivos; `/comprar/` permaneceu 200 e `www` redirecionou 301. O navegador confirmou 320, 390, 768 e 1440 px sem rolagem horizontal, preço e CTA na primeira tela móvel, botão fixo na seção de preços e sua ocultação na chamada final. `POST` válido do evento retornou 204, `GET` na rota retornou 405 e rota desconhecida retornou 404. Backup anterior em `hardening/lp-backup-20260929-before-conversion/`.

## SEO e prévia de links — 29/09/2026

- `www.acessosfitness.online` responde 301 para `https://acessosfitness.online` (caminho e query preservados); a LP tem `<link rel="canonical">`.
- `sitemap.xml` publicado e citado no `robots.txt`; `og-1200x630.jpg` e tags Open Graph para a prévia no WhatsApp. Ambos incluídos em `lp_public_file`.
- Copy: preço na primeira linha de “Quanto custa a ativação?”, seção de academias renomeada para “Funciona na minha academia?” e FAQ com prazo de até 24 horas após Pix e nomes confirmados (prazo informado por Thiago).
- Fonte editorial alterada junto (`build.py` e `copy-proposta-v1.md`); `index.html`, `sitemap.xml` e a imagem OG vieram de `dist/`. Somente o serviço `lp` foi recriado. Backup anterior em `hardening/lp-backup-20260929-before-seo/`.

## Atualização da LP — 24/09/2026

O aviso “Sobre o cadastro” foi publicado antes dos cartões de preço em `site/index.html`, com seu estilo em `site/styles.css`. Apenas esses dois arquivos da LP foram copiados da fonte editorial; `site/comprar/`, o backend e as configurações de Nginx/Cloudflare permaneceram iguais.

Somente o serviço `lp` foi reconstruído e recriado. Nginx e container saudáveis; domínio principal e `www` retornaram HTTP 200 com o aviso e CSS atualizado. A rota `/comprar/` permaneceu acessível. Navegador verificado em 320, 390, 768 e 1440 px sem rolagem horizontal; aviso antes dos planos no celular e desktop. Backup anterior em `hardening/lp-backup-20260924-before-cadastro/`.

## Estado em 21/09/2026

Após reinicialização do Windows, Docker Engine disponível. Build e execução concluídos; container acessosfit-lp-lp-1 healthy em http://127.0.0.1:8080. Cloudflare conectado pelo túnel existente acessofit-pc; publicação HTTPS validada nos domínios principal e www.

Diagnóstico local: o Windows detecta hipervisor ativo. WMI lista VirtualMachinePlatform, WSL e Hyper-V Hypervisor instalados, mas o log Docker registra “Virtual Machine Platform not enabled”. WSL relata virtualização indisponível. Serviço/arquivo vmcompute ausentes. Há reinicialização pendente no Component Based Servicing e no Windows Update. DISM e leitura BCD exigiram elevação e não puderam completar nesta sessão. Esses resultados não permitem atribuir a causa à BIOS; reavaliar após reiniciar o Windows.

## Após o Docker Engine funcionar

No PowerShell, nesta pasta:

```powershell
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' compose -f compose.yaml -f compose.tunnel.yaml up -d --build
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' compose -f compose.yaml -f compose.tunnel.yaml ps
```

Abrir http://127.0.0.1:8080. A porta está limitada ao computador local, pronta para uma etapa posterior de tunnel. Verificar resposta, imagens e estado healthy antes de publicar.

Arquivos do projeto ficam no D:. Imagens e discos internos do Docker continuam no local configurado no Docker Desktop; não foram movidos. A imagem base usa nginx:stable-alpine; registrar o digest efetivamente utilizado quando for possível baixá-la e testar o build.

Mudanças posteriores da LP precisam ser copiadas novamente para `site/` e reconstruídas com o comando acima. O servidor inclui compressão de HTML/CSS/JS e cache de uma hora para imagens; HTML revalidado a cada acesso.

## Validação do container

Nginx -t aprovado; HTTP 200; compressão gzip de CSS confirmada; cache de imagens confirmado. Testes Playwright executados contra a porta 8080 em seis larguras (320 a 1440 px), FAQ pelo teclado, links, sticky, texto ampliado e uso sem JavaScript passaram. Resultados em qa/results.json. Acesso limitado ao computador local.

Imagem base utilizada: nginx:stable-alpine@sha256:ef8676b33d681f272ba429b27658bdd7e640963279714c96bddf1dc76307f7b6.

O Docker voltou a funcionar após reiniciar, sem alteração de BIOS nesta tarefa.

## Publicação Cloudflare concluída — 21/09/2026

Endereços: https://acessosfitness.online/ e https://www.acessosfitness.online/. Ambos retornaram HTTP 200 com o conteúdo da LP. Navegação, FAQ e carregamento de imagens verificados no navegador; CSS, JS e fundos também retornaram 200.

Túnel existente d0b55844-4f2e-4ec2-b122-0dc5b77ba837 reutilizado, sem alteração de DNS ou das regras de segurança. LP tem alias interno site; conector usa compose.tunnel.yaml e cloudflared.yml. Credencial em secrets/tunnel-token, fora da pasta pública, ignorada pelo Git e não copiada para a imagem. Quatro conexões registradas. Para operar o projeto, usar os dois arquivos Compose conforme comandos acima.

Disponibilidade depende deste computador ligado, conectado à internet e com Docker em execução. restart: unless-stopped reinicia os containers quando o Docker inicia; não configura inicialização do Docker Desktop antes do login no Windows.

## Proteções implementadas após análise dos logs

Relatório: [hardening/RELATORIO.md](hardening/RELATORIO.md). Regra adicional de WAF ativa, allowlist de arquivos e hosts no Nginx, GET/HEAD somente, access logs sem query/cookies/Authorization e com hostname, rotação de logs, containers com raiz somente leitura e no-new-privileges. Credencial com permissões NTFS limitadas. Backups de configuração em hardening/backup/.

Ao acrescentar arquivos públicos, atualizar o mapa lp_public_file em nginx.conf. Ao introduzir formulários, endpoints ou tracking, revisar as restrições e testar antes de publicar. As pastas hardening e secrets não são servidas nem copiadas para a imagem. Não ampliar bloqueios de IP/país/User-Agent sem evidência de impacto e de falsos positivos.
