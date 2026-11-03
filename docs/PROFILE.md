# Manutenção do perfil

## Referência e identidade

A referência local WevcastDEV foi consultada em modo de leitura: README, dark.svg,
light.svg, projects.json e .github/workflows/snake.yml. Os PDFs da referência não
foram tratados como instruções desta tarefa.

A arquitetura reaproveita a ideia de `<picture>` por tema, estatísticas em cards,
cobrinha e links envolvendo imagens. Os desenhos, textos, contatos e projetos são
originais do perfil CristianoVieira1. Não há terminal, retrato copiado ou endpoint
privado do autor. O projects.json da referência é um catálogo; não há workflow no
repositório fornecido que o utilize. Aqui, projects.json documenta os quatro
projetos; alterações nesse catálogo exigem atualizar os cards e o README também.

## Primeira execução (não realizada nesta tarefa)

1. Publicar os arquivos revisados no repositório CristianoVieira1/CristianoVieira1,
   na branch padrão. Nenhum commit ou push foi realizado nesta tarefa.
2. Na aba **Actions**, habilitar os workflows caso o GitHub solicite.
3. Executar manualmente **Atualizar estatísticas do perfil** e
   **Atualizar cobrinha de contribuições**, usando **Run workflow**.
4. Aguardar os commits dos arquivos gerados em assets/stats/ e assets/snake-*.svg.

Não é necessário PAT, segredo adicional, branch output, deploy ou serviço próprio.
O GITHUB_TOKEN fornecido automaticamente recebe contents:write somente no job que
publica os SVGs. Proteções de branch ou políticas da organização podem bloquear o
push do bot; nesse caso, autorizar esse fluxo de atualização conforme a política do
repositório antes de executar novamente. As Actions usam a branch padrão e não
são disparadas por push.

Os cards e a cobrinha entregues são placeholders explícitos, sem números
estimados. Eles são substituídos somente após a primeira execução bem-sucedida.
As rotinas diárias estão configuradas para 05:15 e 05:45 UTC (02:15 e 02:45 em
São Paulo, UTC−3); o GitHub pode atrasar execuções agendadas.

## Estatísticas e fontes

- `.github/scripts/update_activity.py`: biblioteca padrão do Python, APIs REST e
  GraphQL oficiais do GitHub, sem endpoints de imagens externos.
- **GitHub Streak:** calendário retornado por contributionsCollection, período
  indicado no card (aproximadamente um ano). A maior sequência é limitada a esse
  período. A sequência atual aceita hoje ou ontem como último dia ativo, em UTC.
  Os números seguem a visibilidade do calendário exposto pelo GitHub; contribuições
  privadas anonimizadas podem aparecer conforme a configuração do perfil.
- **GitHub Statistics:** repositórios públicos e seguidores; estrelas e forks
  recebidos nos repositórios próprios públicos, excluindo repositórios que são forks.
- **Top Languages:** percentual dos bytes retornados pelos endpoints de linguagens
  dos repositórios públicos próprios, com paginação e exclusão de forks. Exibe as
  cinco primeiras linguagens; elas não precisam somar 100%. Não mede domínio técnico.
- Os cards recebem data/período. Falhas de API interrompem a atualização antes da
  escrita; os últimos arquivos disponíveis permanecem publicados. Consultar a aba
  Actions quando houver falha ou dados antigos. Usuários com muitos repositórios
  podem atingir limites de API.

A instância pública do github-readme-stats é descrita pelo próprio projeto como
best-effort. Por isso a implementação usa arquivos locais em vez de copiar a
instância Vercel do autor de referência:
https://github.com/anuraghazra/github-readme-stats

## Animação

`.github/workflows/snake.yml` usa `Platane/snk/svg-only@v3` com o usuário explícito
CristianoVieira1, duas paletas e publicação no próprio diretório assets/. Não cria
branch adicional nem habilita GitHub Pages. O script freeze_snake.py cria versões
estáticas desabilitando as animações CSS geradas pelo snk. O README as seleciona
com prefers-reduced-motion.

Documentação da ferramenta: https://github.com/Platane/snk

## Estrutura visual e edição

- assets/hero-{dark,light}.svg: banners desktop; variantes -mobile para telas estreitas.
- assets/stack/: quatro cards de especialidades por tema.
- assets/projects/: quatro produtos por tema. Jobtto tem maior destaque.
- assets/social/: cinco botões por tema, com símbolos vetoriais tipográficos discretos.
- assets/stats/: cards individuais e composições desktop/mobile geradas pela Action.
- assets/snake-*.svg: animação e alternativas estáticas.

Os SVGs de identidade são estáticos e editáveis como texto. Não usam fontes
remotas, scripts ou imagens incorporadas. Não foram atribuídas tecnologias a
projetos específicos sem documentação. NestJS, Laravel e Docker não foram
incluídos porque não aparecem no README de origem. Firebase e as demais
tecnologias já documentadas foram preservadas.

Os assets antigos substituídos e seus geradores foram removidos. O diretório
archive/ continua preservado como histórico. Os arquivos duplicados de workflows/
foram removidos somente quando idênticos às cópias em archive/workflows/.

## Limitações e checklist visual pendente

Foi realizada apenas revisão estática de conteúdo, caminhos e alterações. Nenhum
teste, renderização, servidor, aplicativo, build ou workflow foi executado.

O GitHub controla o CSS externo aos SVGs. As fontes podem variar entre sistemas.
Os cards de stack e projetos usam largura natural e podem quebrar de linha;
o GitHub limita imagens à largura disponível. O banner e o conjunto de
estatísticas têm versões mobile. A seleção de tema e movimento depende do
suporte do cliente a `<picture>` e media queries; há fallback claro.
Os links são âncoras externas às imagens, pois SVGs no README não são interfaces
interativas. Orderflow não recebe link porque nenhum endereço foi confirmado.

Verificações para realizar depois, sem terem sido executadas nesta tarefa:

- [ ] Desktop: contraste, distribuição dos cards e destaque do Jobtto.
- [ ] Mobile: banner alternativo, quebra dos cards e legibilidade das estatísticas.
- [ ] Alternar temas claro e escuro, verificando todos os conjuntos de SVGs.
- [ ] Ativar preferência de movimento reduzido e conferir alternativa estática.
- [ ] Após a primeira Action: verificar datas e substituição dos placeholders.
- [ ] Conferir destinos de portfólio, Jobtto, Gaúcho Tech e contatos no GitHub.
