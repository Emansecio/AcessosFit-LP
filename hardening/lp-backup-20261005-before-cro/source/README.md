# Landing page AcessosFit: decisões e andamento

Registro consolidado do que foi aprovado nesta conversa. A página foi implementada, executada e revisada localmente em 21/09/2026, depois publicada em https://acessosfitness.online/. Em 24/09/2026, o aviso “Sobre o cadastro” foi aplicado também ao site ativo, antes dos cartões de preço. Em 29/09/2026, preço e Pix passaram à primeira tela móvel, o primeiro botão passou a convidar à consulta de academia e plano, e a LP ganhou medição anônima de visualizações e cliques em WhatsApp. A fonte editorial e a prévia estão em `dist/`; a implantação está registrada em `D:\AcessosFit-LP\README.md`. Instruções e limites da validação local de 21/09 constam em [EXECUCAO.md](EXECUCAO.md). Após delegação expressa de Thiago, três agentes revisaram os detalhes editoriais e o agente principal consolidou as escolhas em [decisoes-equipe.md](decisoes-equipe.md).

## Objetivo

Receber visitantes de anúncios do Google Ads voltados à busca por Gympass para pessoa física. A página será mobile first, com atenção à leitura, ao carregamento e ao uso em iPhone e Android.

WhatsApp é o canal de dúvidas e vendas. O objetivo dos botões principais é iniciar ou continuar o atendimento com o assunto correspondente. Compra direta na landing page não foi escolhida como ação principal.

## Medição desde 29/09/2026

`dist/app.js` registra visualização e cliques dos nove links de WhatsApp no endpoint privado `/lp-events/` do Nginx publicado. A prévia com `py -m http.server` não implementa esse endpoint e responde 501 aos beacons; ela serve para revisão visual. Os eventos não comprovam mensagem enviada ou venda e não configuram conversão no Google Ads. Origem com marcador de anúncio e origem sem marcador são registradas separadamente; detalhes e comando de leitura estão em `D:\AcessosFit-LP\README.md`.

## Decisões aprovadas

Escolhas de Thiago: 1A, 2A, 3A, 4C, 5A e 6A.

| Tema | Decisão |
|---|---|
| Canal principal | WhatsApp para dúvidas e vendas |
| Título | Procurando Gympass para pessoa física? |
| Primeira tela mobile | Título, explicação curta, preço de ativação e botão; modelo mostrando o celular abaixo |
| Sequência | Abertura, funcionamento, custos, academias, garantia e FAQ |
| Opções | Individual e Família em cartões empilhados no celular, sem prioridade visual aprovada entre eles |
| Cobranças | Explicitar que a AcessosFit recebe a ativação e que a mensalidade é paga diretamente no app Wellhub |
| Prints | Não utilizar, por decisão posterior de Thiago; seção de conversas removida |
| Visual | Paleta quente, fotografias e fundos fotográficos, evitando uma página composta apenas de cores chapadas |
| Linguagem | Natural, direta, revisada com humanizer; oferta concreta e verbos de ação |

## Copy da abertura atual

### Procurando Gympass para pessoa física?

Acesso ao Wellhub nas opções Individual (1 pessoa) e Família (até 4).

Ativação por Pix; mensalidade à parte. **Individual R$ 150 · Família R$ 200**.

Botão: **Consultar academia e plano no WhatsApp**

Texto abaixo do botão: **Ativação com a AcessosFit. Mensalidade separada, paga diretamente no app Wellhub.**

A modelo mostrando o celular aparece abaixo desse conjunto. O texto sobre pagamentos deve ter leitura confortável no celular.

A abertura e a seção de funcionamento abaixo estão aprovadas. Thiago confirmou os botões “Quero o Individual” e “Quero o Família”. Os demais textos foram consolidados por decisão editorial delegada à equipe. Posteriormente, Thiago decidiu não usar prints; a seção de conversas e a prova inicial foram removidas.

## Copy de funcionamento aprovada

Thiago escolheu combinar as opções A e C e aprovou o texto resultante.

### Como funciona o acesso pela AcessosFit?

A AcessosFit trabalha com vagas cedidas por empresas parceiras quando os colaboradores não utilizam o benefício.

Você paga a ativação à AcessosFit. A mensalidade do plano é paga diretamente ao Wellhub, no aplicativo.

Pelo WhatsApp, explicamos as condições do acesso e o que você recebe na contratação.

Botão: **Tirar minhas dúvidas no WhatsApp**

## Paleta e aplicação

| Papel | Cor |
|---|---|
| Fundo creme | `#FBF8F1` |
| Superfícies areia | `#F3ECE1` |
| Branco de apoio | `#FFFFFF` |
| Títulos índigo | `#413E65` |
| Texto principal | `#2A2A2A` |
| Texto secundário discreto | `#7A7570` |
| Ação principal framboesa | `#D83A56` |
| Ação secundária roxa | `#4F4789` |
| Acento lavanda | `#9078F8` |
| Acento lima | `#C5E766` |
| Acento rosa | `#F8A8B6` |

Usar a mesma cor framboesa para a ação principal ao longo da página. Reservar roxo para ações secundárias. Usar as cores de acento pontualmente. O verde das roupas e da vegetação já aparece nas fotografias.

As regras completas estão em [direcao-visual.md](direcao-visual.md). Contraste, recortes e comportamento responsivo foram revisados localmente; escopo e limites estão em [EXECUCAO.md](EXECUCAO.md).

## Imagens criadas e salvas

As seis imagens foram geradas com imagegen e aceitas como materiais para a página. Os originais PNG estão em `imagens/`; quatro foram selecionadas e exportadas para WebP em `dist/assets/`. A ferramenta não expôs seleção ou confirmação da versão GPT Image 2.5 solicitada.

| Arquivo | Conteúdo e uso previsto |
|---|---|
| [01-modelo-entrada-v1.png](imagens/01-modelo-entrada-v1.png) | Modelo mostrando o celular na entrada da academia; abertura |
| [02-celular-checkin-v1.png](imagens/02-celular-checkin-v1.png) | Detalhe do aparelho; apoio à explicação de funcionamento |
| [03-intervalo-treino-v1.png](imagens/03-intervalo-treino-v1.png) | Modelo no intervalo do treino; seção intermediária |
| [04-background-academia-v1.png](imagens/04-background-academia-v1.png) | Fundo horizontal de academia com área livre à esquerda |
| [05-background-treino-mobile-v1.png](imagens/05-background-treino-mobile-v1.png) | Fundo vertical de treino com área escura superior para texto |
| [06-background-equipamentos-v1.png](imagens/06-background-equipamentos-v1.png) | Fundo horizontal de equipamentos; transição ou chamada final |

Os prompts estão em [prompts-v1.md](prompts/prompts-v1.md) e [prompts-backgrounds-v1.md](prompts/prompts-backgrounds-v1.md). As cenas e telas geradas são ilustrativas. Prints de atendimento não serão utilizados.

## Materiais analisados e aprendizados para a página

Foram consultados a política comercial, FAQs, fluxos, referências, materiais visuais, relatórios e registros locais de atendimento. O relatório `Relatorio-Leads-PROFUNDO-v2-2026-09-20.md` indicado na Área de Trabalho foi lido integralmente. Não se trata de uma auditoria nova de todas as conversas ou pagamentos.

O relatório reúne 55 históricos selecionados, incluindo recompras e suporte. Ele serve para identificar dúvidas; suas contagens não constituem uma taxa representativa de conversão de anúncios nem comprovam o efeito de uma alteração na página.

Pontos aproveitados na proposta:

- Explicar quem recebe cada pagamento e o custo inicial.
- Esclarecer o formato Família e as mensalidades de cada participante.
- Facilitar a consulta de academia por unidade e cidade.
- Explicar funcionamento e cadastro antes da contratação.
- Separar prazo de entrega, duração do acesso e garantia.
- Levar o assunto escolhido na página para a conversa no WhatsApp.

Esses pontos orientam a proposta. Não significam que toda redação sugerida foi aprovada, nem autorizam executar recomendações operacionais presentes nos relatórios.

## Referência comercial da proposta

Thiago atualizou os preços nesta conversa: Individual R$ 150 e Família R$ 200 para até quatro participantes, com ativação somente por Pix. Esses são os valores vigentes para a nova LP e substituem os preços anteriores no material do site. A mensalidade é paga separadamente, diretamente no app Wellhub. A política comercial consultada registra seis meses de garantia para novas compras; os 12 meses citados em históricos pertencem a condições anteriores.

Thiago descreveu as vagas como cedidas por empresas parceiras quando os colaboradores não querem utilizar o benefício. A redação da seção de funcionamento foi aprovada conforme o bloco acima.

Os preços acima foram definidos expressamente por Thiago nesta conversa. A documentação comercial fora de `Site/` não foi alterada nesta etapa; para preços da nova LP, prevalece essa atualização. Outras condições continuam referenciadas em `../Politica Comercial.md` e nos compromissos efetivamente aplicáveis. Nenhum prazo de entrega novo foi criado.

## WhatsApp e rodapé confirmados

Número informado por Thiago para a landing page: **5538992026240**.
Exibição: **+55 (38) 99202-6240**.
Link-base: [Conversar no WhatsApp](https://wa.me/5538992026240).

Rodapé definido: nome AcessosFit e contato WhatsApp. Thiago informou não dispor dos demais dados. Não incluir CNPJ, razão social, endereço ou links de termos/privacidade sem conteúdo e destino fornecidos. Não criar links vazios. Esta decisão define o conteúdo disponível, não valida condições jurídicas de publicação.

## Pendências

1. Prints cancelados por Thiago. Não há seleção ou edição de prints pendente.
2. Rodapé resolvido editorialmente: AcessosFit e WhatsApp informado. Demais dados e documentos não disponíveis; não serão inventados ou exibidos como se existissem.
3. Confirmar prazo de entrega somente se for publicada uma duração específica; a copy orienta consultar antes de pagar.
4. Links e mensagens de WhatsApp por contexto implementados e verificados localmente.
5. Implementação, otimização das fotos e testes locais concluídos. Validação em Safari/iPhone e aparelhos físicos ainda não realizada.

Na etapa local de 21/09, publicação e alterações de campanha não foram realizadas. A LP foi publicada posteriormente por Docker e Cloudflare; a atualização do aviso de cadastro no site ativo ocorreu em 24/09/2026, sem alterar a campanha. FAQ reduzida de dez para seis perguntas e revisão em conselho registrada em [CONSELHO-LP.md](CONSELHO-LP.md).

## Como continuar o trabalho

- A copy e os detalhes editoriais foram consolidados após revisão em equipe autorizada por Thiago. Prints foram cancelados. Preservar essa decisão e as demais aprovações na página já implementada.
- Apresentar escolhas em texto com letras A, B e C quando necessário. Thiago informou que as opções interativas estavam desaparecendo rapidamente.
- Trabalhar por partes e preservar as decisões aprovadas.
- Não fazer pesquisas externas para investigar a operação. Usar os materiais fornecidos e perguntar a Thiago quando faltar informação indispensável.
- Análise e discussão de copy não autorizam implementação, alteração de atendimento, envio de mensagens ou publicação.

## Arquivos de referência

- [Estrutura aprovada](estrutura-aprovada.md)
- [Direção visual](direcao-visual.md)
- [Copy consolidada](copy-proposta-v1.md)
- [Decisões da revisão em equipe](decisoes-equipe.md)
- [Notas editoriais e pendências da copy](notas-copy-v1.md)
