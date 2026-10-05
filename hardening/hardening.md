# Security Hardening Review: AcessosFit

## Evidence Basis

Analisamos o CSV histórico Docker de 10.174 registros, preservado e identificado por hash em [context.md](context.md). A análise detalhada está em [RELATORIO.md](RELATORIO.md). Há drift conhecido: origem antiga Apache/PHP, origem atual Nginx estático.

## Constraints

Precisamos preservar visitas, WhatsApp, parâmetros de anúncio e regras anteriores. Não podemos confundir healthchecks e navegação incompleta com ataques, nem atribuir a pessoa a partir de IP/User-Agent.

## Opportunity Portfolio

Não identificamos oportunidade estrutural que justifique novo serviço ou arquitetura. A separação entre pasta pública e segredo já existe. Controles locais e um complemento específico de WAF são proporcionais às sondagens observadas.

## Recommendation Summary

Recomendo manter o desenho atual e restringir o que ele serve. Assim reduzimos exposição acidental sem adicionar autenticação ou desafio universal para compradores. O usuário autorizou implementação; controles foram aplicados e verificados conforme [RELATORIO.md](RELATORIO.md). O custo de manutenção é atualizar a lista de arquivos autorizados quando a LP mudar. Não medimos ganho de latência ou memória; não adicionamos um novo processo à arquitetura existente. O WAF evita que os caminhos correspondentes cheguem à origem, mas não identifica todo robô que navegue normalmente.

## Next Decisions

Nenhuma decisão bloqueia esta entrega. Rotação futura da credencial deve ser coordenada se a conversa tiver sido compartilhada. Mudanças de checkout, tracking e novos arquivos exigem revisar as restrições antes da próxima publicação. Limites de verificação estão no relatório.
