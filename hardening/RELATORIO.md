# Análise dos logs e proteções da LP

## Conclusão

Analisei os 10.174 registros do CSV preservado. Há sequências compatíveis com varreduras de credenciais, backups e sistemas que não fazem parte da LP atual. Não encontramos nesses registros prova de invasão bem-sucedida ou de leitura de arquivo privado. Essa ausência não comprova que nunca houve incidente: faltam corpos de resposta, histórico do sistema e eventos completos da borda.

Nós separamos 7.927 consultas locais periódicas das demais requisições. Elas usam loopback, curl e intervalos próximos de 30 segundos, um padrão compatível com healthcheck. Não as contamos como ataque. As 304 requisições classificadas como sondagens tiveram 235 respostas 404 e 69 redirecionamentos 301; nenhuma teve 200 nesses caminhos. Um 301 não significa entrega do arquivo. O destino de cada redirecionamento não aparece no CSV.

## Evidência e limites

O CSV tem registros gerais entre 03/09/2026 e 20/09/2026, em UTC. Os acessos HTTP extraídos abrangem 17/09/2026 a 20/09/2026. São 9.993 linhas de acesso interpretadas, oito eventos operacionais do servidor e 173 eventos do túnel. A instalação histórica era Apache/PHP, com checkout; a atual é uma LP estática em Nginx. Não atribuímos automaticamente o comportamento antigo à instalação atual.

Não existe campo Host nos acessos antigos. Assim, não podemos comprovar quais subdomínios foram tentados. Os exemplos `/wp/`, `/wordpress/` e `/geoserver/` são caminhos, não subdomínios. No estado atual, o túnel aceita apenas o domínio principal e www; o teste de uma URL de subdomínio não publicado correspondeu à regra final 404, sem requisição a esse subdomínio.

Agrupamos os casos por `cf_ip` quando disponível, em vez do endereço interno do proxy. A integridade desse cabeçalho na configuração histórica não foi comprovada. Cada rótulo abaixo representa um agrupamento de origem, não uma pessoa identificada. Não atribuímos nome, país, intenção individual nem organização. Não bloqueamos IPs adicionais por inferência.

## Contagem cautelosa

| Grupo | Requisições | Leitura |
|---|---:|---|
| Consultas locais | 7.927 | Compatíveis com verificação operacional |
| Sondagem de configuração, credenciais e backups | 175 | 108 respostas 404; 67 redirecionamentos |
| Sondagem de CMS e frameworks | 129 | 127 respostas 404; dois redirecionamentos |
| Demais acessos | 1.762 | Uso normal ou inconclusivo; não classificados automaticamente como humanos ou maliciosos |

Buscas isoladas por favicon, robots.txt, manifest e `.well-known/traffic-advice` não foram tratadas como ataque. User-Agent de navegador, robô ou ferramenta não autentica a origem. Acessos aos antigos endpoints de compra que retornaram 200 não foram rotulados como invasão sem conhecer a transação e o corpo da resposta.

## Casos com sequência de sondagem

| Origem pseudonimizada | Intervalo UTC do agrupamento | Total do agrupamento | Sondagens classificadas | Respostas das sondagens |
|---|---|---:|---:|---|
| Origem 01 | 2026-09-17T17:16:24.586Z → 2026-09-17T18:01:19.881Z | 135 | 126 | 301: 66, 404: 60 |
| Origem 02 | 2026-09-18T07:48:01.053Z → 2026-09-18T07:48:01.920Z | 3 | 3 | 301: 1, 404: 2 |
| Origem 03 | 2026-09-18T13:51:37.795Z → 2026-09-18T14:53:25.009Z | 32 | 26 | 404: 26 |
| Origem 04 | 2026-09-18T19:32:56.765Z → 2026-09-18T19:57:21.069Z | 10 | 8 | 404: 8 |
| Origem 05 | 2026-09-19T05:42:12.948Z → 2026-09-19T05:44:41.278Z | 143 | 115 | 404: 115 |
| Origem 06 | 2026-09-19T09:58:26.905Z → 2026-09-19T09:58:53.189Z | 9 | 7 | 404: 7 |
| Origem 07 | 2026-09-19T12:36:56.353Z → 2026-09-19T12:37:05.578Z | 16 | 13 | 404: 13 |

Os detalhes auditáveis, exemplos de caminhos e índices dos registros estão em [analysis.json](analysis.json). São sete agrupamentos com pelo menos três solicitações classificadas; há ocorrências isoladas fora dessa tabela. Os índices são registros lógicos do CSV, excluindo o cabeçalho, e não linhas físicas. Nenhum IP completo ou conteúdo de query foi incluído no relatório.

## Proteções aplicadas

1. **Cloudflare:** adicionada e confirmada como ativa a regra “AcessosFit - sondagens de credenciais e sistemas ausentes”, ID `544ed96ef805422f8cce7b9a66559b32`. Ela complementa as duas regras anteriores com caminhos de credenciais, depuração e aplicações ausentes observados no CSV. Escopo restrito a `acessosfitness.online` e `www.acessosfitness.online`. A ação é bloquear. Teste benigno em um caminho fictício sob `/debug/` recebeu 403 e não apareceu no log da origem.
2. **Origem:** Nginx só entrega os 16 arquivos explicitamente autorizados da LP, a página raiz e robots.txt. Um arquivo colocado por engano na pasta pública não é servido sem inclusão explícita. Arquivos novos de uma futura versão precisam entrar no mapa do `nginx.conf`.
3. **Hosts e métodos:** hosts desconhecidos recebem 404; somente GET e HEAD atendem a LP. POST recebe 405 porque a página atual não recebe formulários ou pagamentos. Se isso mudar, a configuração precisa ser revisada.
4. **Isolamento:** raiz dos dois containers em modo somente leitura e elevação adicional de privilégios impedida. Nginx usa áreas temporárias específicas; essa configuração não equivale a execução sem root ou proteção contra toda falha do runtime. Nenhum socket Docker ou diretório de documentos está montado no servidor web.
5. **Privacidade operacional:** access logs novos incluem hostname e caminho para permitir distinguir futuros casos, mas omitem query strings, Referer, cookies e Authorization. IP de cliente e User-Agent ainda são dados operacionais e permanecem privados. Rotação limitada a três arquivos de 10 MB por container, sem promessa de retenção temporal. Error logs podem ter outros campos e não receberam uma garantia geral de anonimização.
6. **Credencial do túnel:** permanece fora da imagem e da pasta pública, montada como secret somente no conector. Permissões NTFS limitadas ao usuário atual, SYSTEM e administradores; pastas de análise e segredo não fazem parte do contexto permitido no Dockerfile.
7. **Navegador:** cabeçalhos para impedir enquadramento da página, interpretação incorreta de tipos e uso de objetos incorporados; política de referência reduz o compartilhamento de caminhos com outros sites. Não foi criada política de scripts que impedisse futuras tags de anúncio.

## O que foi preservado e por quê

Preservamos DNS, túnel, conteúdo comercial e as duas regras antigas. A regra antiga de ASN/faixas continua ativa; o CSV não tem dados suficientes para concluir que toda essa faixa seja maliciosa. Não ampliamos esse tipo de bloqueio. Sua precisão exige dados de eventos e falsos positivos, que não são demonstrados por esses logs.

Não impusemos CAPTCHA universal, modo sob ataque, bloqueio por país, por User-Agent ou limite agressivo por IP. Esses mecanismos podem afetar clientes em redes compartilhadas e verificadores de anúncios. A amostra não demonstra um volume que justifique limitar toda a página: o maior grupo destacado fez 143 requisições em aproximadamente 148 segundos. Priorizamos negar recursos não utilizados.

O robots.txt permite rastreamento da LP; não é mecanismo de segurança nem lista de arquivos secretos. Não acrescentamos liberação por simples texto “Googlebot”, pois qualquer cliente pode declarar esse nome. A aprovação e os acessos reais do Google Ads não foram testados nesta tarefa.

## Validação realizada

- Configuração Nginx e Compose válidas antes da atualização; containers ativos depois dela, LP healthy.
- 38 verificações pontuais aprovadas, incluindo igualdade de hash dos arquivos servidos, métodos, hosts, ausência de arquivos privados, cabeçalhos, omissão de marcadores fictícios de query/cookie/autorização nos access logs, flags de isolamento e rotação.
- HTTPS principal e www, páginas e CSS com HTTP 200 usando PowerShell; URL com UTM/gclid aceita pelo servidor. Navegador real abriu a LP; o Brave removeu gclid da barra por comportamento fora do código alterado. Não foi validada atribuição de conversões.
- Cliente Python urllib recebeu 403 em uma consulta pública normal; PowerShell e navegador receberam a LP. Não atribuímos essa diferença automaticamente à nova regra nem alteramos a proteção para fazer o teste passar. A nova expressão não corresponde à raiz. Registramos o limite: não há garantia de aceitação de todos os clientes automatizados.
- Bloqueio de borda 403 comprovado em caminho fictício; ausência do caminho no access log confirma que aquele teste não chegou ao Nginx.
- Testes funcionais locais repetidos em seis larguras, FAQ pelo teclado, CTA fixo, texto ampliado e JavaScript desativado passaram. Não houve replay de payloads de exploração do CSV nem teste de carga.

Resultados técnicos: [verification.json](verification.json). Scripts [analyze_logs.py](analyze_logs.py) e [verify_protections.py](verify_protections.py).

## Limites e manutenção

Uma LP pública permite leitura de seu texto, fotos e HTML; não podemos prometer impedir todo robô de copiar conteúdo público. As medidas reduzem a superfície e impedem a entrega dos arquivos não autorizados, mas não garantem ausência absoluta de ataques. Não fizemos auditoria do Windows, das outras contas, de outros projetos ou dos computadores de clientes.

O token do túnel foi compartilhado na conversa anterior. Ele não aparece neste relatório nem na página; rotacioná-lo no Cloudflare e atualizar o secret local é uma medida adicional apropriada se a conversa tiver sido compartilhada. Não rotacionamos credenciais automaticamente nesta tarefa.

Site continua dependente deste computador, internet e Docker. Para manter as proteções em novas versões, atualizar o mapa de arquivos do Nginx e executar as verificações antes de publicar. Um novo formulário ou checkout exige revisar métodos e rotas; não basta copiar arquivos.

## Reversão

Backups anteriores às mudanças locais estão em `backup/`, sem credenciais. Para reverter a mudança local, restaurar os três arquivos de configuração dessa pasta e reconstruir usando ambos os arquivos Compose, conforme README do projeto. Isso também remove as proteções locais novas e deve ser reservado a regressão confirmada. A regra nova pode ser desabilitada pelo seu ID no Cloudflare, preservando as duas anteriores. Não existe necessidade observada de reversão neste momento.
