# Privacidade aplicada em 22/09/2026

Escopo autorizado: HTTPS, TLS/HSTS, retenção e acesso aos logs, execução sem root e redução de capabilities. A rede compartilhada, as portas, o conteúdo público e os contratos do checkout foram preservados.

## Cloudflare

- Sempre usar HTTPS: ativado; domínio principal e www redirecionam HTTP para HTTPS.
- TLS mínimo: 1.2. TLS 1.3 permanece ativado.
- HSTS: max-age=2592000 (um mês, menor prazo disponível no painel).
- includeSubDomains e preload permanecem desligados. O cabeçalho foi validado no domínio principal e no www.
- Manter HTTPS disponível durante o prazo do HSTS, inclusive em uma eventual migração de provedor.

## Containers e logs

- Nginx: usuário/grupo 101:101, incluindo processo principal; cap_drop ALL.
- Cloudflared: usuário 65532:65532; cap_drop ALL.
- Checkout: mantém usuário 10001:10001 e cap_drop ALL.
- Todos mantêm read_only e no-new-privileges. Rede acessosfit-lp_default e porta 127.0.0.1:8080 permanecem iguais.
- A base Nginx foi fixada no mesmo digest anteriormente utilizado. Foi acrescentado logrotate do repositório oficial Alpine para implementar a retenção.
- Logs de acesso e erro do Nginx ficam no volume privado acessosfit-lp_lp_logs, em /var/log/nginx/private. Diretório 0700 e arquivos 0600, pertencentes ao usuário 101.
- Retenção máxima de 30 dias, verificada a cada minuto. A rotação diária ou ao ultrapassar 1 MiB mantém no máximo 30 arquivos por log; sob tráfego alto, o limite de tamanho pode resultar em retenção menor. A verificação por minuto permite uma tolerância operacional de até um minuto.
- Arquivos rotacionados são comprimidos, exceto o mais recente, preservado até a próxima rotação. Se a manutenção falhar, o processo encerra para que a política de reinício sinalize e recupere o serviço, em vez de ignorar a falha.
- O formato de acesso preserva IP, navegador e identificadores necessários para diagnóstico; continua omitindo query string, referer, cookies e Authorization.
- Os logs anteriores do container Nginx foram preservados em legacy.log no mesmo volume e entram na mesma política de retenção.
- docker logs da LP passa a mostrar apenas mensagens do supervisor e inicialização. Os logs operacionais de Docker/Cloudflared continuam com o limite existente de três arquivos de 10 MiB. A retenção local não altera registros mantidos pela Cloudflare ou pela operadora de pagamentos.

Consulta administrativa dos acessos, sem publicar o volume:

```powershell
docker exec acessosfit-lp-lp-1 tail -n 100 /var/log/nginx/private/access.log
```

## Sessões e pedidos

- Sessões com sete dias ou mais e sem pedido associado são removidas na inicialização e em verificações de saúde, no máximo uma vez por hora.
- Sessões ligadas a pedidos e todos os campos dos pedidos são preservados. Não foi estabelecido um prazo de exclusão para registros financeiros.
- A expiração do cookie e o comportamento de autenticação permanecem em sete dias.
- A limpeza é lógica no SQLite; não representa uma garantia de apagamento forense ou de anonimato.

## Validação realizada

- Compose válido, build concluído e configuração Nginx válida.
- Três testes isolados, sem rede e com banco temporário: retenção nas fronteiras de idade, preservação integral dos pedidos, intervalo de limpeza e execução na inicialização.
- Container temporário confirmou UID 101, capabilities efetivas zeradas, diretório 0700, arquivos 0600, rotação e reabertura dos logs.
- Rotina real de retenção removeu um arquivo de teste vencido e preservou um recente.
- Todos os arquivos públicos foram comparados com a imagem anterior: conteúdo idêntico.
- Após publicação: LP e checkout saudáveis, túnel com quatro conexões registradas, HTTP 301 para HTTPS, HTTPS 200 e HSTS presente.
- Cookie do checkout confirmado como Secure, HttpOnly e SameSite=Strict; respostas privadas mantêm no-store.
- Nove pedidos existentes permaneceram idênticos imediatamente após o deploy, comprovado por contagem e hash do conjunto completo de registros, sem exibir seus conteúdos.
- LP e checkout verificados no navegador em larguras de 390 e 1440 px, sem transbordamento horizontal. Não foi criada nem paga uma cobrança.

## Reversão preservada

- Configurações anteriores: privacy-backup-20260922-045953, nesta pasta.
- Imagem anterior da LP: acessosfit-lp-lp:rollback-privacy-20260922.
- Imagem anterior do checkout: acessosfit-lp-checkout:rollback-privacy-20260922.
- O volume checkout_data permanece existente. Uma reversão de aplicação não deve excluir volumes ou pedidos.
- A cópia de configurações não contém o conteúdo dos segredos. A limpeza de sessões expiradas sem pedido não é desfeita pela reversão da imagem.
