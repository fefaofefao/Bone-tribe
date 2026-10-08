# Bone Tribe — Documento de Design do Jogo

Oct 8, 2026 · @Fernando Martins Sampaio

## Visão geral

Bone Tribe é um roguelite de eventos para celular em que o Ossinho, um esqueleto, monta o próprio corpo com os ossos dos monstros que derrota. Cada partida termina com uma criatura única, e é essa criatura que vira o gancho de vídeo e de retenção.

| Item | Definição |
| --- | --- |
| Gênero | Roguelite de eventos com combate automático, no formato de Capybara Go |
| Partida | 6 a 8 minutos, jogável com uma mão, tela em retrato |
| Plataforma | Android (Google Play) |
| Mercados | EUA como prioridade de receita; Brasil e América Latina como base de público |
| Idiomas | Português (pt-BR), inglês (en-US) e espanhol (es-419) |
| Monetização | Híbrida: anúncios recompensados e compras no app |
| Universo | Compartilhado com Reino dos Ossos, para um jogo divulgar o outro |

**Pilares de design**

1. **O corpo é a build.** Toda decisão importante aparece no corpo do personagem, nunca só em números.
2. **Cada partida é uma história curta.** Eventos escritos, com humor leve e mistério, dão motivo para jogar "só mais uma".
3. **Sessões curtas, uma mão.** Tudo se resolve com toques simples; o combate roda sozinho.
4. **Momentos compartilháveis.** O jogo gera sozinho o cartão e o vídeo da criatura final, pronto para postar.

**Nome e títulos na loja**

A marca Bone Tribe é a mesma nos três idiomas; só as palavras-chave do título e o nome do mascote mudam. Todos os títulos cabem no limite de 30 caracteres da Google Play.

| Idioma | Título na loja | Caracteres | Nome do mascote |
| --- | --- | --- | --- |
| Inglês (en-US) | Bone Tribe: Skeleton Roguelike | 30 | Bonesy |
| Português (pt-BR) | Bone Tribe: RPG de Esqueleto | 28 | Ossinho |
| Espanhol (es-419) | Bone Tribe: RPG de Esqueleto | 28 | Huesito |

O ID do pacote é com.bonetribe.game. Ele não pode ser mudado depois da publicação. Antes do lançamento, confirme que o nome está livre na Google Play, no domínio e nos registros de marca do INPI e do USPTO.

## Direção de arte

O visual é 2D pintado à mão com animação esquelética, num tom fofo e sombrio: um esqueletinho carismático em masmorras escuras iluminadas por velas. 2D de alta qualidade é onde um desenvolvedor solo com IA consegue o melhor resultado, e roda bem nos celulares Android mais simples, comuns no Brasil e na América Latina.

**Por que animação esquelética**

Na animação esquelética 2D (Skeleton2D do Godot ou Spine), cada parte do corpo é um sprite separado preso a um esqueleto de animação. Isso combina perfeitamente com o jogo: trocar um osso é só trocar a imagem daquele encaixe, e todas as animações continuam funcionando. O corpo montável fica bonito e barato de produzir.

**Paleta por família**

Os ossos são cor de marfim com contorno escuro. A família aparece na aura e nos detalhes, para o jogador reconhecer a build num relance.

| Família | Cor da aura | Detalhe visual |
| --- | --- | --- |
| Fera | Âmbar | Pelos e garras nas pontas dos ossos |
| Inseto | Verde-ácido | Brilho de quitina e gotas de veneno |
| Marinho | Turquesa | Cracas, algas e bolhas |
| Dragão | Vermelho-fogo | Brasas e escamas queimadas |
| Construto | Azul-aço | Runas gravadas que pulsam |
| Sombra | Roxo | Fumaça e olhos brilhando |

**O que faz o jogo parecer caro**

- **Luz 2D dinâmica:** velas, auras e sopros de fogo iluminam o cenário em tempo real.
- **Encaixe cinematográfico:** a câmera aproxima, o osso voa até o corpo, há um brilho, um tremor leve e vibração no celular.
- **Transformação em câmera lenta:** ao completar uma forma, a tela escurece, o Ossinho flutua e o nome da forma aparece com efeito.
- **Partículas:** pó de osso, faíscas, poeira em cada passo e brasas no ar.
- **Golpes animados:** dano saltando na tela, críticos maiores e inimigos se desmontando em ossos ao morrer.
- **Interface polida:** botões com animação ao toque, transições suaves e ícones desenhados no mesmo estilo.

**Produção da arte com IA**

1. Criar uma folha de estilo com 8 a 10 imagens de referência aprovadas: personagem, cenário e um osso de cada família.
2. Gerar cada osso sempre no mesmo ângulo, escala e iluminação, usando a folha de estilo como referência.
3. Recortar, limpar e exportar em resolução 2x para telas de alta densidade.
4. Montar tudo no esqueleto de animação e testar a silhueta com todos os encaixes preenchidos.

O maior risco honesto é a consistência: imagens geradas por IA tendem a variar de estilo entre si. Para um resultado realmente profissional, vale contratar um artista freelancer só para as peças que mais aparecem (ícone da loja, o Ossinho base e os chefes) e usar IA no restante.

**Metas técnicas:** 60 quadros por segundo em celulares intermediários, com uma opção de qualidade reduzida que desliga a luz dinâmica e as partículas extras em aparelhos fracos.

## Mecânica central: o corpo montável

O Ossinho tem 7 encaixes e começa cada partida só com um crânio e costelas básicos. Os outros 5 encaixes começam vazios e são preenchidos com ossos que caem dos monstros derrotados.

| Encaixe | Começa com | O que define |
| --- | --- | --- |
| Crânio | Crânio básico | Crítico e habilidades especiais |
| Costelas | Costelas básicas | Vida e defesa |
| Braço esquerdo | Vazio | Ataque e efeitos de golpe |
| Braço direito | Vazio | Ataque e efeitos de golpe |
| Pernas | Vazio | Velocidade, esquiva e ordem de ataque |
| Costas | Vazio | Asas ou carapaça: ações extras ou reflexo de dano |
| Cauda | Vazio | Efeitos contínuos, como veneno ou regeneração |

**Regras dos ossos**

- **Origem.** Cada monstro solta ossos da parte do corpo que ele tem. Uma aranha solta patas, um morcego solta asas. O jogador aprende a caçar o monstro certo para a peça que quer.
- **Encaixe ou trituração.** Se o encaixe está vazio, o osso entra direto. Se está ocupado, o jogador escolhe entre trocar ou triturar o osso em pó de osso, a moeda da partida.
- **Família.** Todo osso pertence a uma de 6 famílias: Fera, Inseto, Marinho, Dragão, Construto e Sombra. As famílias ativam sinergias e formas (ver seção de sinergias).
- **Visual.** Cada osso troca o sprite do seu encaixe, e a raridade aumenta o tamanho. A silhueta muda a cada peça nova, então o progresso é visível num relance.
- **Encaixes extras.** Ossos lendários raros abrem encaixes a mais. A Coluna de Hidra dá um terceiro braço; esse tipo de momento é o que vira vídeo.
- **Rejeição.** Famílias opostas, como Dragão (fogo) e Marinho (água), funcionam juntas mas ficam instáveis: dão +25% de dano e 10% de chance por combate de um osso cair. É uma aposta de risco e recompensa que o jogador escolhe fazer.

## Ciclo da partida

Uma partida dura 6 a 8 minutos e se repete em andares de 10 eventos com um chefe no fim. O combate é automático; o jogador decide nas escolhas, nos ossos e nas habilidades.

&#91;embedded content: ciclo da partida · cada andar tem 10 eventos e 1 chefe\]

Ao morrer, o jogador pode reviver uma vez com um anúncio recompensado. Se não reviver, a partida termina, o Cartão da Criatura é gerado e o pó de osso vira melhorias permanentes para a próxima tentativa.

## Catálogo de ossos (MVP)

O MVP tem 20 ossos: 12 comuns, 5 raros e 3 lendários, cobrindo todos os encaixes e as 6 famílias. Os lendários só caem de chefes.

| Encaixe | Osso | Monstro de origem | Efeito | Família | Raridade |
| --- | --- | --- | --- | --- | --- |
| Crânio | Crânio de Lobo | Lobo das Criptas | +15% de chance de crítico | Fera | Comum |
| Crânio | Crânio de Ciclope | Ciclope Ossudo | Raio ocular a cada 3 turnos, 150% de dano | Construto | Raro |
| Crânio | Crânio de Dragão | Dragão Ancião (chefe) | Sopro de fogo em todos os inimigos a cada 4 turnos | Dragão | Lendário |
| Costelas | Costelas de Tartaruga | Tartaruga de Pedra | +30% de defesa | Marinho | Comum |
| Costelas | Gaiola de Golem | Golem Esquecido (chefe) | Escudo de 20% da vida no início de cada combate | Construto | Raro |
| Braço | Garra de Urso | Urso Cadavérico | Golpes causam sangramento | Fera | Comum |
| Braço | Pinça de Caranguejo | Caranguejo Abissal | 20% de chance de atordoar | Marinho | Comum |
| Braço | Ferrão de Vespa | Vespa Ossuda | Ataques aplicam veneno | Inseto | Comum |
| Braço | Lâmina de Louva-a-deus | Louva-a-deus Gigante | Ataca 2 vezes por turno, 60% de dano cada | Inseto | Raro |
| Braço | Punho de Golem | Golem Esquecido (chefe) | Soco de 200% de dano a cada 4 turnos | Construto | Raro |
| Pernas | Patas de Aranha | Aranha Tecelã | +25% de esquiva | Inseto | Comum |
| Pernas | Patas de Gafanhoto | Gafanhoto de Ossos | Evita 15% das armadilhas e ataca primeiro no 1º turno | Inseto | Comum |
| Pernas | Pernas de Centauro | Centauro Ossudo | Sempre ataca primeiro | Fera | Raro |
| Costas | Asas de Morcego | Morcego Vampiro | Roubo de vida de 10% | Sombra | Comum |
| Costas | Carapaça de Besouro | Besouro Blindado | Reflete 15% do dano recebido | Inseto | Comum |
| Costas | Asas de Dragão | Dragão Ancião (chefe) | Uma ação extra a cada 5 turnos | Dragão | Lendário |
| Cauda | Cauda de Escorpião | Escorpião das Dunas | Veneno acumulativo | Inseto | Comum |
| Cauda | Cauda de Lagarto | Lagarto de Cinzas | Regenera 3% da vida por turno | Dragão | Comum |
| Cauda | Cauda de Rato | Rei Rato (chefe) | +20% de pó de osso | Sombra | Comum |
| Extra | Coluna de Hidra | Hidra (chefe secreto) | Abre um terceiro braço | Dragão | Lendário |

## Sinergias e formas

Juntar ossos da mesma família dá bônus com 2 peças e transforma o Ossinho numa forma nova com 4 peças. A forma muda o visual inteiro (cor, aura e postura) e ganha um nome, o que torna o momento fácil de mostrar em vídeo.

| Família | Bônus com 2 peças | Forma com 4 peças | Poder da forma |
| --- | --- | --- | --- |
| Fera | +10% de ataque | Lobisomem de Osso | Abaixo de 30% de vida, o ataque dobra |
| Inseto | +20% de dano de veneno | Rainha Enxame | Invoca 2 insetos de osso no início de cada combate |
| Marinho | +15% de defesa | Leviatã | A cada 5 turnos, uma onda atordoa todos os inimigos |
| Dragão | +20% de dano de fogo | Wyrm Ósseo | Sopro de fogo em todos os inimigos a cada 3 turnos |
| Construto | +15% de escudo | Colosso | Imune ao primeiro golpe de cada combate; o tamanho dobra |
| Sombra | +5% de roubo de vida | Lich | Revive uma vez por partida com 50% da vida |

**Formas secretas**

Além das formas por família, existem receitas escondidas com ossos específicos. O jogo não as revela: elas são descobertas jogando e ficam registradas num Bestiário de Formas com silhuetas escuras para as que faltam. Exemplos para o MVP:

- **Manticora Noturna:** Crânio de Lobo, Asas de Morcego e Cauda de Escorpião. Cada crítico aplica veneno.
- **Quimera:** ossos de 5 famílias diferentes ao mesmo tempo. +8% em todos os atributos por família equipada.
- **Cavaleiro Abissal:** Pinça de Caranguejo, Carapaça de Besouro e Pernas de Centauro. Contra-ataca todo golpe bloqueado.

Formas secretas alimentam conversa na comunidade e vídeos do tipo "descobri uma forma que ninguém conhece". Novas receitas a cada atualização mantêm esse interesse vivo com custo baixo.

## Eventos

O MVP tem 60 eventos, sorteados pelos pesos abaixo, com tom de humor leve e mistério. A IA escreve os textos nos 3 idiomas, e cada evento é revisado por alguém antes de entrar no jogo.

| Tipo | Peso | Exemplo |
| --- | --- | --- |
| Combate | 45% | Três ratos-esqueleto disputam um queijo petrificado. Eles param e olham para você. |
| Escolha | 20% | Uma bruxa oferece um osso brilhante em troca de metade da sua vida. Aceitar ou recusar? |
| Baú ou armadilha | 10% | Um baú range sozinho. Pode ser tesouro, pode ser um mímico com fome. |
| Mercador | 8% | O Coveiro Ambulante vende ossos usados: "garantia de 7 dias ou seu crânio de volta". |
| Aliado | 5% | Um esqueleto preso numa jaula pede ajuda. Libertar custa pó de osso, mas ele luta ao seu lado. |
| Altar de troca | 5% | O altar aceita um osso seu e devolve um de outra família, sem dizer qual. |
| Descanso | 5% | Uma fogueira de velas azuis: cure 30% da vida ou melhore um osso em um nível. |
| Raro | 2% | Seu reflexo no lago tem um osso a mais. Ele estende a mão. |

**Eventos que leem o corpo**

Parte dos eventos muda conforme os ossos equipados, e essa é a principal inovação narrativa. O jogador sente que o corpo que montou importa fora do combate.

- Com **Asas**, dá para sobrevoar um abismo e pular 3 eventos direto para um baú.
- Com **Patas de Aranha**, uma teia que prenderia o jogador vira um atalho.
- Com **Pinça de Caranguejo**, dá para cortar as correntes de um aliado sem pagar.
- Com o **Crânio de Dragão**, os monstros pequenos fogem, e a opção "intimidar" aparece em vários eventos.

No MVP, cerca de 15 dos 60 eventos têm uma opção extra ligada ao corpo.

## Inimigos, chefes e companheiros

O capítulo 1 tem 14 monstros comuns, um para cada osso comum e raro do catálogo, e 3 chefes nos andares 10, 20 e 30. Cada chefe dá seu osso garantido na primeira vitória e 10% de chance nas seguintes.

| Andar | Chefe | Mecânica | Recompensa |
| --- | --- | --- | --- |
| 10 | Rei Rato | Invoca 2 ratos a cada 3 turnos; ensina a priorizar alvos | Cauda de Rato |
| 20 | Golem Esquecido | Escudo que só quebra com 3 golpes seguidos; ensina ataques múltiplos | Gaiola de Golem ou Punho de Golem |
| 30 | Dragão Ancião | Sopro que dobra de dano se o jogador não tiver defesa contra fogo | Crânio de Dragão ou Asas de Dragão |
| Secreto | Hidra | Aparece só se o jogador vencer o Dragão com a forma Wyrm Ósseo | Coluna de Hidra |

**O Caçador de Ossos (rival recorrente)**

Um esqueleto rival que também coleta ossos e reaparece entre as partidas. Se o Ossinho morre, o Caçador rouba o melhor osso que ele carregava e passa a usá-lo no próprio corpo. Nas partidas seguintes, o Caçador surge como chefe opcional vestindo os ossos roubados; vencer devolve o osso com um nível a mais.

Isso transforma a derrota em uma história de vingança e cria um vilão que cada jogador constrói sem perceber. É o tipo de memória que faz o jogador voltar no dia seguinte.

**Companheiros (3 no MVP)**

| Companheiro | Papel | Habilidade |
| --- | --- | --- |
| Ossudo, o cão esqueleto | Coletor | 15% de chance de trazer um osso extra após cada combate |
| Lumi, a vela fantasma | Cura | Cura 8% da vida do Ossinho a cada 3 turnos |
| Bigorna, o ferreiro | Forja | Uma vez por partida, sobe um osso de comum para raro |

O jogador leva 1 companheiro por partida. Cada um sobe de nível com pó de osso, e os personagens podem aparecer em Reino dos Ossos como referência cruzada.

## Progressão permanente e história

Entre as partidas, o jogador fortalece o Ossinho de 4 formas. Nenhuma delas troca o corpo montado na partida, que sempre recomeça do zero; elas só tornam cada nova tentativa mais forte e variada.

| Sistema | Como funciona | Moeda |
| --- | --- | --- |
| Ossuário | Melhorias permanentes de vida, ataque, defesa e chance de osso cair | Pó de osso |
| Coleção de ossos | Álbum com todos os ossos já encontrados; completar uma família dá um bônus permanente de 5% | Descoberta |
| Relíquias | 4 espaços (amuleto, anel, capa e lanterna), com raridade e níveis | Pó de osso e baús |
| Ossos iniciais | Um osso já descoberto pode ser escolhido para começar a partida encaixado | Desbloqueio na Coleção |

**História em capítulos**

O mistério central é quem o Ossinho foi em vida. Cada chefe derrotado devolve um fragmento de memória, mostrado numa cena curta de 3 a 4 quadros. A revelação final liga o Ossinho ao passado do Reino dos Ossos.

1. **A Cripta Esquecida** (MVP): o despertar e os primeiros ossos.
2. **O Pântano das Costelas:** monstros marinhos e insetos gigantes.
3. **A Biblioteca Afogada:** o primeiro nome do Ossinho aparece num livro.
4. **A Forja dos Gigantes:** constructos e a origem do Caçador de Ossos.
5. **O Trono Vazio:** a revelação sobre quem ele era.

Cada capítulo novo traz monstros, ossos, uma família de formas secretas e eventos próprios. Lançar um capítulo a cada 6 a 8 semanas mantém os jogadores ativos sem exigir um ritmo de produção impossível para um desenvolvedor solo.

## Coleção de itens e recompensas de login

**Gabinete de Curiosidades**

Além dos ossos, o Ossinho coleciona objetos curiosos que dão bônus permanentes. Eles caem de baús, eventos raros e chefes, e ficam expostos numa estante no Ossuário, que vai se enchendo visualmente. O MVP tem 30 itens organizados em 10 conjuntos de 3.

| Item | Onde cai | Bônus permanente | Conjunto |
| --- | --- | --- | --- |
| Vela Derretida | Baús | +2% de vida | Cripta |
| Moeda Furada | Mercador | +3% de pó de osso | Cripta |
| Dente de Ouro | Rei Rato | +2% de chance de crítico | Cripta |
| Pá Enferrujada | Eventos de escolha | +5% de chance de osso cair | Coveiro |
| Lanterna Velha | Baús | +5% de chance de evento raro | Coveiro |
| Mapa Rasgado | Evento raro | Revela o tipo do próximo evento | Coveiro |

- **Conjuntos:** completar os 3 itens de um conjunto dá um bônus extra. Cripta: +5% de ataque. Coveiro: um baú garantido por andar.
- **Estrelas:** itens repetidos sobem de 1 a 5 estrelas, e cada estrela aumenta o bônus do item em 50%.
- **Silhuetas:** itens que faltam aparecem como silhuetas na estante, dando ao jogador um objetivo claro de coleta.

**Bônus dos primeiros 7 dias**

Um calendário especial para jogadores novos, com o prêmio mais valioso no 7º dia para incentivar a volta ao longo da primeira semana. Conta dias com login, não dias seguidos: quem falta um dia não perde o progresso.

| Dia | Recompensa |
| --- | --- |
| 1 | 500 de pó de osso |
| 2 | 50 diamantes |
| 3 | Baú de curiosidades raro |
| 4 | 100 diamantes |
| 5 | Relíquia rara |
| 6 | 150 diamantes |
| 7 | Companheiro Bigorna e a skin exclusiva Ossinho Recém-Desperto |

**Bônus de login diário**

Depois da primeira semana, entra um calendário de 28 dias que recomeça a cada ciclo. Todo dia dá algo pequeno, como pó de osso, um baú comum ou 10 diamantes. Os dias 7, 14 e 21 dão 50 diamantes ou um baú raro, e o dia 28 dá um item de curiosidade garantido. Como no calendário inicial, conta dias com login, não dias seguidos.

A data do login deve vir do servidor (Firebase), não do relógio do celular, para impedir que alguém adiante a data e colete todas as recompensas de uma vez.

## Inovações extras

Além do corpo montável, 6 mecânicas diferenciam o Ossinho dos concorrentes. As 4 primeiras entram no MVP; as 2 últimas exigem servidor e ficam para a fase 2.

| Inovação | O que é | Por que importa | Fase |
| --- | --- | --- | --- |
| Cartão da Criatura | No fim de cada partida, o jogo gera uma imagem e um vídeo de 8 segundos da criatura montada, com um nome automático como "Lobo-Aranha Flamejante" e o botão de compartilhar | Cada jogador vira um divulgador; o vídeo já sai no formato vertical das redes, com o nome do jogo | MVP |
| Eventos que leem o corpo | Opções extras em eventos conforme os ossos equipados | O corpo importa fora do combate e cada partida conta uma história diferente | MVP |
| Caçador de Ossos | Rival que rouba ossos quando o jogador morre e reaparece usando-os | A derrota vira motivo para voltar, não para desistir | MVP |
| Formas secretas | Receitas escondidas registradas no Bestiário de Formas | Gera descoberta, conversa e vídeos na comunidade | MVP |
| Fantasmas de outros jogadores | A criatura final de outros jogadores aparece como chefe-fantasma na sua partida; vencer dá um osso dela | Cria a sensação de um mundo vivo sem multiplayer em tempo real | Fase 2 |
| Cripta do Dia | Uma partida diária com a mesma sorte para todos e ranking de quem foi mais longe | Dá um motivo para abrir o jogo todo dia e comparar com amigos | Fase 2 |

O Cartão da Criatura é a inovação mais importante para o crescimento orgânico, e vale caprichar nele desde o primeiro protótipo: animação da criatura girando, nome em destaque, logo do jogo e um texto de desafio como "Consegue montar algo pior?".

## Monetização

A receita vem de anúncios recompensados e de compras no app, sem sistema de energia e sem vender poder em excesso. Avaliações de "pague para ganhar" derrubam o ranqueamento na Google Play, e o jogador que se diverte sem pagar é quem assiste aos anúncios.

**Anúncios recompensados**

| Recompensa | Limite | Onde aparece |
| --- | --- | --- |
| Reviver com 50% da vida | 1 por partida | Na tela de morte |
| Dobrar o pó de osso | 1 por partida | Na tela de fim de partida |
| Trocar as 3 opções de habilidade | 3 por partida | Na escolha ao subir de nível |
| Abrir baú extra | 3 por dia | No Ossuário |

Anúncios intersticiais (forçados) só aparecem a partir da 3ª partida, no máximo um a cada 3 minutos, sempre entre partidas e nunca no meio de um combate.

**Compras no app**

| Produto | Conteúdo | Preço EUA | Preço Brasil | Quando oferecer |
| --- | --- | --- | --- | --- |
| Kit das primeiras 24 horas | 300 diamantes, a relíquia Lanterna do Coveiro, a skin Ossinho Lua de Âmbar e 1.000 de pó de osso | US$ 1,99 | R$ 4,90 | Ao fim da 1ª partida, só nas primeiras 24 horas |
| Remover anúncios | Fim dos intersticiais e +10% de pó de osso permanente | US$ 4,99 | R$ 9,90 | Após o 10º intersticial visto |
| Cartão do Coveiro (mensal) | 30 diamantes e pó de osso por dia, 1 reviver grátis por dia e 1 baú raro por semana, por 30 dias | US$ 4,99 | R$ 9,90 | Na loja, sempre visível |
| Skins | Estilos visuais aplicados a todos os ossos: dourado, neon, pirata, cristal | US$ 1,99 a 3,99 | R$ 4,90 a 9,90 | Na loja e no Cartão da Criatura |
| Pacote apoiador | Skin exclusiva Ossinho Fundador e nome nos créditos | US$ 9,99 | R$ 24,90 | Na loja, após o capítulo 1 |

Os preços são pontos de partida e devem ser configurados por país na Play Console. As skins ganham vitrine natural no Cartão da Criatura: quem vê um Ossinho dourado num vídeo quer o seu.

## Diamantes e loja

Os diamantes são a moeda premium do jogo: caem de chefes e de recompensas diárias, e também podem ser comprados. Como o jogador ganha diamantes jogando, a loja não parece exclusiva de quem paga, e quem compra só acelera o caminho.

**De onde vêm os diamantes**

| Fonte | Quantidade |
| --- | --- |
| Rei Rato | 10 na 1ª vitória, 3 nas seguintes |
| Golem Esquecido | 20 na 1ª vitória, 5 nas seguintes |
| Dragão Ancião | 30 na 1ª vitória, 8 nas seguintes |
| Hidra (secreta) | 100 na 1ª vitória |
| Anúncio recompensado na loja | 5 por anúncio, até 3 por dia |
| Calendários de login | Ver a seção de recompensas de login |
| Compra | Pacotes abaixo |

**Pacotes de diamantes**

| Pacote | Diamantes | Preço EUA | Preço Brasil |
| --- | --- | --- | --- |
| Punhado | 100 | US$ 0,99 | R$ 2,90 |
| Saco | 550 | US$ 4,99 | R$ 9,90 |
| Baú | 1.200 | US$ 9,99 | R$ 19,90 |
| Cofre | 2.600 | US$ 19,99 | R$ 39,90 |

**Aba de loja (itens por diamantes)**

| Item | Preço | O que faz |
| --- | --- | --- |
| Reviver extra | 30 | Revive sem assistir anúncio |
| 1.000 de pó de osso | 50 | Acelera as melhorias do Ossuário |
| Osso inicial raro | 80 | Começa a próxima partida com um osso raro à escolha |
| Baú de curiosidades raro | 150 | Um item do Gabinete de Curiosidades, raro ou melhor |
| Relíquia rara | 200 | Uma relíquia rara aleatória |
| Companheiro Lumi | 400 | Libera o companheiro antes de encontrá-lo no jogo |
| Skins | 300 a 600 | Estilos visuais para todos os ossos |
| Ofertas do dia | Variado | 3 itens com desconto que mudam todo dia à meia-noite, pelo horário do servidor |

Baús com conteúdo aleatório precisam mostrar a chance de cada raridade antes da compra. A Google Play exige essa transparência em jogos com itens aleatórios pagos, e ela também evita avaliações negativas.

**Kit das primeiras 24 horas**

Uma oferta única que aparece ao fim da primeira partida e some 24 horas depois da instalação, com um cronômetro visível no ícone da loja. Ela substitui o antigo pacote inicial.

- **Conteúdo:** 300 diamantes, a relíquia rara Lanterna do Coveiro, a skin exclusiva Ossinho Lua de Âmbar e 1.000 de pó de osso.
- **Preço:** US$ 1,99 nos EUA e R$ 4,90 no Brasil, mostrando claramente quanto o jogador economiza em relação aos itens comprados separadamente.
- **Uma compra por conta:** depois de comprado ou expirado, não volta.

**Como funciona na Google Play:** o kit é cadastrado na Play Console como um produto único comum, com preços por país. A Google Play cuida do pagamento, mas não controla o prazo de 24 horas: quem controla é o jogo, que registra no servidor o momento da primeira abertura e só mostra o kit dentro do prazo. Usar o horário do servidor impede que alguém volte o relógio do celular para reabrir a oferta. Vale conferir na Play Console se as ofertas com desconto para produtos únicos estão disponíveis na sua conta, porque elas ajudam a exibir o preço promocional de forma oficial.

## Valores de equilíbrio

Os números abaixo são valores iniciais para o protótipo, não finais. A meta é que uma partida dure 6 a 8 minutos, que o primeiro chefe seja vencido entre a 2ª e a 3ª partida e que o capítulo 1 leve de 2 a 3 dias de jogo casual.

**Atributos e crescimento** (n = andar, L = nível, k = nível da melhoria)

```latex
\begin{aligned}
\text{Ossinho: vida} &= 100,\quad \text{ataque} = 10,\quad \text{defesa} = 0 \\
\text{Vida do inimigo} &= 30 \times 1{,}12^{\,n} \\
\text{Ataque do inimigo} &= 5 \times 1{,}10^{\,n} \\
\text{Chefe} &= 8 \times \text{vida e } 1{,}5 \times \text{ataque do inimigo do andar} \\
\text{XP para o nível } L &= 20 \times L^{1{,}5} \\
\text{Custo da melhoria no Ossuário} &= 50 \times 1{,}25^{\,k}
\end{aligned}
```

**Chances e recompensas**

| Parâmetro | Valor inicial |
| --- | --- |
| Chance de osso comum cair de um monstro | 25% |
| Chance de osso raro cair de um monstro | 5% |
| Osso lendário do chefe | 100% na 1ª vitória; 10% depois |
| Defesa | Reduz o dano em defesa ÷ (defesa + 50) |
| Crítico | 5% de chance base, 150% de dano |
| Pó de osso no fim da partida | 10 por andar alcançado + 50 por chefe vencido |
| Escolhas de habilidade por nível | 1 entre 3 opções |
| Turnos máximos por combate comum | 15 (depois disso, o inimigo foge) |

O teste que valida o equilíbrio é simples: 5 pessoas que nunca jogaram devem vencer o Rei Rato até a 3ª partida, e nenhuma deve vencer o Dragão Ancião no primeiro dia. Se isso não acontecer, ajuste primeiro os multiplicadores 1,12 e 1,10.

## MVP, métricas e lançamento

O MVP é o capítulo 1 completo, com tudo o que precisa para medir retenção e receita antes de investir em mais conteúdo.

**Escopo do MVP**

- [ ] Corpo montável com 7 encaixes, troca, trituração e rejeição
- [ ] 20 ossos, 6 formas de família e 3 formas secretas
- [ ] 14 monstros comuns, 3 chefes e a Hidra secreta
- [ ] 60 eventos nos 3 idiomas, cerca de 15 deles ligados ao corpo
- [ ] Caçador de Ossos
- [ ] 3 companheiros, Ossuário, Coleção de ossos, Gabinete de Curiosidades com 30 itens e 4 espaços de relíquias
- [ ] Cartão da Criatura com imagem e vídeo de 8 segundos; calendários de login de 7 e de 28 dias
- [ ] Anúncios recompensados, intersticiais limitados, compras do app, diamantes, aba de loja e Kit das primeiras 24 horas
- [ ] Firebase para medir retenção, sessões e receita por jogador, e para fornecer o horário do servidor aos logins e ofertas

**Metas para seguir em frente**

| Métrica | Meta | Se ficar abaixo |
| --- | --- | --- |
| Retenção no dia 1 | 40% ou mais | Rever as primeiras 2 partidas e o ritmo do 1º osso |
| Retenção no dia 7 | 15% ou mais | Rever progressão do Ossuário e o Caçador de Ossos |
| Partidas por dia por jogador | 4 ou mais | Encurtar partidas ou dar mais recompensa no fim |
| Jogadores que veem anúncio recompensado | 30% ou mais por dia | Tornar as recompensas mais visíveis e valiosas |
| Jogadores que compram algo | 1% ou mais | Rever preços e o momento do Kit das primeiras 24 horas |
| Cartões compartilhados | 5% das partidas finalizadas | Melhorar o visual e o texto do Cartão da Criatura |

Essas metas são referências aproximadas do gênero, não garantias. Abaixo delas, vale ajustar o jogo antes de gastar com anúncios.

**Ordem de lançamento**

1. **Protótipo do corpo montável:** um andar com 5 ossos e o Cartão da Criatura. Gravar vídeos e testar nas redes antes de seguir.
2. **MVP completo:** o capítulo 1 com todo o escopo acima.
3. **Teste fechado na Google Play:** 12 testadores por 14 dias, exigência para contas pessoais novas.
4. **Lançamento suave no Brasil e no México:** público mais barato de alcançar, para medir retenção com um orçamento pequeno de anúncios.
5. **Lançamento global com foco nos EUA:** só depois de bater as metas de retenção, com vídeos curtos e anúncios recompensados ajustados.

## Prompt para o Claude Code

O prompt abaixo pede só o protótipo da etapa 1, para validar a ideia nas redes antes de construir o MVP. Copie o bloco inteiro e cole no Claude Code, junto com este documento.

```markdown
Você vai criar o PROTÓTIPO do jogo mobile Bone Tribe (Android, tela em retrato), conforme o documento de design anexo. Use exatamente os nomes, IDs e textos definidos aqui. Não invente nomes genéricos (Item1, Boss, Enemy, Skin1, MyGame, com.example) em nenhum lugar: código, arquivos, pastas, cenas ou textos.

PROJETO
- Motor: Godot 4 (versão estável mais recente) com GDScript.
- Nome do projeto Godot: BoneTribe.
- ID do pacote Android: com.bonetribe.game
- O repositório já está criado e conectado a este projeto. Trabalhe nele e configure o build do AAB via GitHub Actions.

ESTRUTURA DE PASTAS E ARQUIVOS
- res://data/bones.json, res://data/monsters.json, res://data/events.json, res://data/forms.json, res://data/levelup.json
- res://i18n/pt_BR.csv, res://i18n/en_US.csv, res://i18n/es_419.csv
- res://scenes/TitleScreen.tscn, res://scenes/Run.tscn, res://scenes/Ossinho.tscn, res://scenes/CreatureCard.tscn
- res://art/bones/, res://art/monsters/, res://art/ui/

PERSONAGEM
- Chave de tradução hero_name: Ossinho (pt_BR), Bonesy (en_US), Huesito (es_419).
- Ossinho.tscn usa Skeleton2D com 7 encaixes, nesta ordem e com estes IDs: slot_skull, slot_ribs, slot_arm_left, slot_arm_right, slot_legs, slot_back, slot_tail.
- Começa com bone_skull_basic e bone_ribs_basic; os outros 5 encaixes começam vazios.

OSSOS DO PROTÓTIPO (bones.json)
| ID | Nome pt_BR | Encaixe | Monstro que solta | Efeito |
| bone_skull_wolf | Crânio de Lobo | slot_skull | monster_crypt_wolf (Lobo das Criptas) | +15% de chance de crítico |
| bone_claw_bear | Garra de Urso | slot_arm_left ou slot_arm_right | monster_corpse_bear (Urso Cadavérico) | golpes causam sangramento |
| bone_legs_spider | Patas de Aranha | slot_legs | monster_weaver_spider (Aranha Tecelã) | +25% de esquiva |
| bone_wings_bat | Asas de Morcego | slot_back | monster_vampire_bat (Morcego Vampiro) | roubo de vida de 10% |
| bone_tail_scorpion | Cauda de Escorpião | slot_tail | monster_dune_scorpion (Escorpião das Dunas) | veneno acumulativo |
| bone_tail_rat | Cauda de Rato | slot_tail | boss_rat_king (Rei Rato) | +20% de pó de osso |

ANDAR DO PROTÓTIPO
1. Andar único chamado A Cripta Esquecida (chave floor_forgotten_crypt), com 10 eventos sorteados: combate 60%, escolha 20%, baú 20%.
2. Use os textos de evento da seção Eventos do documento (ratos-esqueleto, bruxa do osso brilhante, baú que range) e crie mais 5 no mesmo tom, nos 3 idiomas.
3. Combate automático por turnos: Ossinho com vida 100 e ataque 10; inimigo do andar 1 com vida 34 e ataque 5,5 (fórmulas do documento).
4. Ao pegar um osso para um encaixe ocupado: botões Trocar (chave btn_swap) e Triturar (chave btn_crush). Triturar dá pó de osso.
5. Cada osso troca o sprite do seu encaixe na hora: a câmera aproxima, o osso voa até o corpo, brilha, dá um tremor leve e o celular vibra.
6. Subida de nível com 1 entre 3 bônus (levelup.json): Medula Forte (+10% de vida máxima), Fêmur Afiado (+10% de ataque), Olho Vazio (+5% de chance de crítico).
7. Chefe no fim: boss_rat_king (Rei Rato), que invoca 2 ratos a cada 3 turnos e solta bone_tail_rat.
8. Forma secreta form_night_manticore (Manticora Noturna): ativa ao ter bone_skull_wolf, bone_wings_bat e bone_tail_scorpion ao mesmo tempo. Efeito: cada crítico aplica veneno. A tela escurece, o Ossinho flutua em câmera lenta e aparece o texto da chave form_discovered: Forma secreta descoberta: Manticora Noturna!

CARTÃO DA CRIATURA (CreatureCard.tscn)
- Mostra a criatura montada girando, o logo Bone Tribe e um botão Compartilhar (chave btn_share) que exporta a imagem em 1080x1920.
- Nome da criatura = palavra do crânio + hífen + palavra das pernas + adjetivo da cauda. Cada osso tem no bones.json os campos name_part e adjective nos 3 idiomas. Exemplo de resultado: Lobo-Aranha Venenoso.
- Encaixe vazio usa a palavra Osso (pt_BR), Bone (en_US) ou Hueso (es_419).
- Texto de desafio da chave card_challenge: Consegue montar algo pior?

MODO DEMONSTRAÇÃO
- Ativa com toque longo de 3 segundos no logo Bone Tribe da TitleScreen.
- Joga sozinho, preenche todos os encaixes e força a Manticora Noturna, para eu gravar vídeos.

TEXTOS
- Todo texto visível vem dos arquivos de res://i18n/. Nada de texto fixo no código.

ARTE
- Siga a seção Direção de arte: 2D pintado à mão, Skeleton2D com um sprite por encaixe, luz 2D dinâmica e partículas. O visual é prioridade.
- Enquanto a arte final não chega, crie placeholders com o mesmo ID do osso no nome do arquivo (ex.: res://art/bones/bone_skull_wolf.png), no tamanho, ângulo e ponto de encaixe finais, para trocar só a imagem sem mudar código.

FORA DO PROTÓTIPO (não faça agora)
- Anúncios, compras, diamantes, aba de loja, Kit das primeiras 24 horas, calendários de login, Gabinete de Curiosidades, Ossuário, companheiros, Caçador de Ossos, capítulos e Firebase. Deixe a estrutura de dados e de salvamento preparada para eles.

ENTREGA
- Dados de ossos, monstros, eventos, formas e bônus em JSON, não no código.
- README explicando como rodar, como gerar o AAB e como adicionar um osso novo editando só o bones.json.
```
