# Checkout AcessosFit — 21/09/2026

URL: https://acessosfitness.online/comprar. Caminho no mesmo domínio, sem navegação de entrada na LP. Confirmação em /comprar/confirmacao, acessível somente como estado confirmado pela API; abrir a URL sozinha não confirma uma compra.

## Operação

- Individual: R$ 150; Família: R$ 200, até quatro pessoas. Preços definidos no servidor.
- Pix de ativação à AcessosFit. Mensalidade do Wellhub paga à parte no app.
- Nome e CPF do pagador enviados pelo backend à SagacePay. Não são gravados em texto no banco local, armazenamento do navegador ou logs do backend.
- Sessão em cookie HttpOnly, Secure em HTTPS, SameSite=Strict, válida por sete dias. Não compartilhar cookies. Retorno no mesmo navegador recupera o pedido. Outro navegador precisa do atendimento para localizar a compra na operadora.
- QR com validade conservadora de 30 minutos, sem serviços externos de QR. Após expiração ou falha, encaminhamento ao suporte, sem gerar outra cobrança automaticamente.
- Confirmação consulta GET /sales/:id na SagacePay, verifica ID, valor e referência quando retornada. Polling de 15 segundos com aba ativa; limite mínimo de 12 segundos no servidor.
- Não há webhook público nesta versão. A confirmação funciona por consulta autenticada. Se o navegador estiver fechado, a transação segue registrada na SagacePay e é reconciliada ao reabrir a página com a mesma sessão. Mensagem no WhatsApp não substitui conferência financeira no painel.
- Botão de WhatsApp abre mensagem editável com opção, valor e referência; não envia automaticamente.

## Arquivos e deploy

Fonte do checkout: `site/comprar/` e `checkout/server.py`, neste projeto isolado. A fonte editorial da LP permanece no projeto original. Ao atualizar a LP, preservar `site/comprar/`; não sobrescrever todo o diretório `site` com uma cópia limpa da LP.

Backend Python em serviço Docker `checkout`, sem porta publicada, usuário 10001, filesystem somente leitura. SQLite persistente no volume `acessosfit-lp_checkout_data`. **Não usar `docker compose down -v`**, pois apagaria os pedidos. O volume reside no armazenamento do Docker Desktop; os fontes estão no D:.

Chave em `secrets/sagacepay-key`, montada como Docker secret. Nunca copiar para `site`, frontend, Git, relatórios ou imagens. O build usa contextos com allowlist e não inclui os secrets. Para trocar chave: substituir o conteúdo desse arquivo e recriar somente o serviço checkout. Preservar os dois arquivos Compose nas operações.

Nginx permite apenas rotas exatas do checkout, POST exclusivamente em /comprar/api/create, rate limit específico, cabeçalhos no-store e CSP na página. A LP continua sem endpoint de compra ou botão novo. Regras Cloudflare existentes foram preservadas.

## Fonte técnica

Documentação consultada: https://sub.sagacepay.com/docs. Base documentada e autenticada: https://sagacepay.com/api. Header x-api-key; POST /sales com amount em reais, customer.document, idempotency-key e externalId; GET /sales/:id para verificação. Nenhum saque realizado. Cópia da documentação pública em qa/sagacepay-docs.html.

## Validações

- Testes unitários em checkout/test_checkout.py executados em container sem rede e sem credenciais. Cobrem preços, duplicação/idempotência, timeout, dados inválidos, sessão, persistência, confirmação, divergência de valor/ID, estorno/expiração e rejeição de origem externa.
- Navegador Edge/Playwright: 320, 375, 390, 430, 768 e 1440 px; seleção, formulário, overflow e erros JS. Estados Pix, recarga, confirmação, WhatsApp e estorno exercitados com respostas interceptadas exclusivamente no navegador de teste. Esses testes não geraram cobranças na operadora.
- URL pública carregou, cookie seguro validado, nenhuma ligação para checkout adicionada na LP. API real autenticada em consultas de leitura, inclusive de dentro do container.
- Nginx validado e serviços healthy.

Limitação pendente: gerar cobrança com dados reais do pagador e confirmar um Pix efetivamente pago. Não foi criada uma cobrança com identidade inventada nem efetuado pagamento. Sem chave de sandbox fornecida, esta última verificação deve ser feita pelo titular diretamente na página. A autenticação e os testes isolados não substituem esse teste financeiro real.
