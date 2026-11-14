# Decisões de implementação

Registro das escolhas feitas onde o GDD (docs/GDD.md) é ambíguo ou silencioso.
Regra geral: a opção mais simples que siga o GDD.

## Projeto e build

- **Godot 4.7.2 estável** (versão estável mais recente disponível em 08/10/2026), renderizador
  *Compatibility* (OpenGL ES 3), que tem luz 2D e roda nos Android mais simples.
- **Resolução base 720x1280** em retrato, `stretch = canvas_items`, `aspect = expand`.
  As texturas são produzidas em 2x e desenhadas com escala 0,5.
- **Build do AAB**: GitHub Actions baixa o Godot e os templates oficiais, instala o
  template de build Android (gradle) e exporta `build/BoneTribe.aab`. Sem keystore de
  release nos secrets, o CI assina com uma chave temporária (o AAB serve para teste,
  não para a Play Store). Secrets esperados: `ANDROID_RELEASE_KEYSTORE_BASE64`,
  `ANDROID_RELEASE_KEYSTORE_USER`, `ANDROID_RELEASE_KEYSTORE_PASSWORD`.
- **Locale es_419**: o Godot normaliza `es_419` para `es`. O arquivo continua sendo
  `res://i18n/es_419.csv`, e a tradução gerada é registrada com o locale `es`
  (vale para toda a América Latina e para outros espanhóis como fallback).
- **i18n**: os três CSV em `res://i18n/` são a fonte da verdade. `tools/i18n.py`
  apenas insere linhas nos três de uma vez e valida chaves faltando ou vazias.
- **Fontes**: Fredoka (texto) e Pirata One (títulos), ambas SIL OFL, em `res://art/fonts/`.
- **Interface montada por código** a partir de um tema único (`Style`), com cenas
  `.tscn` enxutas. Isso evita arquivos de cena gigantes escritos à mão e mantém todos
  os textos vindo das chaves de tradução.

## Protótipo (Passo 2)

### Estrutura da partida
- **Andar = um evento.** O índice `n` das fórmulas é o número do evento na partida. Assim
  "inimigo do andar 1 com vida 34" e "chefes nos andares 10, 20 e 30" ficam coerentes:
  cada bloco de 10 andares termina num chefe. O protótipo tem 10 andares e o Rei Rato no 10º
  (`balance.json -> run.prototype_mode`).
- **Pesos do protótipo**: combate 60%, escolha 20%, baú 20% (`prototype_event_weights`).

### Equilíbrio (validado com `tests/BalanceSim.tscn`)
O GDD manda ajustar primeiro os multiplicadores 1,12 e 1,10. Valores atuais:

| Parâmetro | GDD | Atual | Motivo |
| --- | --- | --- | --- |
| Vida do inimigo | 30 × 1,12^n | 32 × 1,05^n | Andar 1 continua com 33,6 (34) de vida |
| Ataque do inimigo | 5 × 1,10^n | 5,238 × 1,05^n | Andar 1 continua com 5,5 de ataque |
| Chefe | 8× vida, 1,5× ataque | 5× vida, 1,2× ataque | Com 8× ninguém vencia o Rei Rato |
| XP por abate | — | 14 + 4n | O GDD não define; ~4 níveis por partida |
| Osso comum / raro | 25% / 5% | 35% / 8% | Mais ossos = o corpo muda mais por partida |
| Cura ao subir de nível | — | 25% da vida | Sem cura, as partidas acabavam no andar 7 |
| Rato-Esqueleto (lacaio) | — | 30% vida, 35% ataque | Invocados em grupo pelo Rei Rato |

Resultado da simulação (60 jogadores novos, gastando o pó no Ossuário entre partidas):
1ª vitória sobre o Rei Rato em média na **partida 2,5**; 16% vencem na 1ª partida e
80% até a 4ª. Meta do GDD: vencer o Rei Rato até a 3ª partida.

### Regras
- **Ossos têm atributos de base** além do efeito do GDD (braços dão ataque, pernas dão
  velocidade etc.), seguindo a tabela "O que define" de cada encaixe.
- **Defesa em %**: "+30% de defesa" vira +30 pontos de defesa (a defesa base é 0, então
  porcentagem sobre zero não faria nada). A redução segue o GDD: defesa ÷ (defesa + 50).
- **Sinergia Construto "+15% de escudo"**: escudo de 15% da vida no início do combate.
- **Trocar** um osso tritura automaticamente o antigo em pó de osso.
- **Braços**: o osso entra no primeiro braço vazio; com os dois ocupados, o jogador escolhe
  qual trocar ou tritura.
- **Opções ligadas ao corpo** só aparecem quando o osso está equipado e ganham destaque
  (botão cor de vela com o ícone do osso).
- **Alvo**: o Ossinho ataca o primeiro inimigo; tocar num inimigo muda o foco.
- **Golem Esquecido**: o escudo reduz o dano em 75% e quebra com 3 golpes no mesmo turno.
- **Dragão Ancião**: "defesa contra fogo" = ter qualquer osso Dragão ou Marinho.
- **Sem pernas** o Ossinho fica mais baixo e anda aos pulinhos; as pernas o erguem.
- **Nome da criatura**: os campos `name_part` e `adjective` do `bones.json` guardam *chaves*
  de tradução (a regra "todo texto visível em res://i18n/" vale sobre o prompt). Ossos básicos
  contam como encaixe vazio ("Osso"). A cauda vazia usa o adjetivo "Ossudo" (Bony/Huesudo).
  A ordem das palavras vem da chave `creature_name_format` (em inglês o adjetivo vem antes:
  "Venomous Wolf-Spider").
- **Compartilhar** salva o PNG 1080x1920 em `user://cards/`. O envio nativo para outros apps
  exige um plugin Android, que fica para quando os SDKs reais entrarem.
- **Modo demonstração**: sequência fixa em `balance.json -> demo`, escolhas automáticas,
  Ossinho reforçado e revive garantido, para gravar vídeos sem falhas.

## Catálogo completo (Passo 3)

- **Partida completa**: 30 andares (eventos), chefes nos andares 10 (Rei Rato), 20 (Golem
  Esquecido) e 30 (Dragão Ancião). Quem vence o Dragão com o Wyrm Ósseo ativo destrava o
  andar 31 com a Hidra. O protótipo de 10 andares continua disponível (`run.prototype_mode`)
  e é usado pelo modo demonstração.
- **Peças de família**: com 20 ossos, Sombra tem só 2 ossos e Marinho 3, e os ossos de Dragão
  que formariam o Wyrm só caem do próprio Dragão. Para todas as formas serem possíveis:
  osso **lendário conta 2 peças** e **cada nível acima do 1 soma +1 peça**
  (`balance.json -> forms_rule`). Isso também dá peso às melhorias de osso (descanso,
  Bigorna, Caçador de Ossos). Sinergias de 2 peças usam a mesma contagem.
- **Duas Lâminas de Louva-a-deus** somam golpes (1 + 1 + 1 = 3 golpes de 60%), o que quebra o
  escudo do Golem num turno, como o GDD pede ("ensina ataques múltiplos").
- **Colosso**: "o tamanho dobra" foi feito como 1,8× para o corpo caber na tela em retrato.
- **Ciclope Ossudo** dispara um raio ocular a cada 3 turnos; **Lagarto de Cinzas** regenera;
  **Hidra** morde 3 vezes por turno e regenera 3% por turno.
- **Chefes soltam um osso** sorteado entre os seus (Gaiola ou Punho de Golem; Crânio ou Asas
  de Dragão): garantido na 1ª vitória e 10% depois. Diamantes por chefe conforme o GDD.
- **Quimera** aparece com frequência quando o corpo está cheio de famílias variadas
  (+8% por família, como no GDD); o equilíbrio dos chefes finais já considera isso.
- **Equilíbrio dos chefes** (simulação de 50 jogadores × 12 partidas, antes das relíquias e
  companheiros): Rei Rato 1ª vitória na partida ~3; Golem ~6,5; Dragão 0% na 1ª partida e
  1ª vitória média na partida ~7. Multiplicadores por chefe em `monsters.json`.

## Eventos (Passo 4)

- **60 eventos** sorteados pelos pesos do GDD: combate 23, escolha 13, baú/armadilha 7,
  mercador 5, aliado 3, altar de troca 3, descanso 3, raro 3. Os 3 exemplos do GDD do
  protótipo e os 4 da tabela de tipos (Coveiro Ambulante, esqueleto na jaula, altar, fogueira
  de velas azuis, reflexo no lago) estão entre eles.
- **Exatamente 15 eventos ligados ao corpo** (o GDD diz "cerca de 15"; o pedido diz 15):
  Asas sobrevoam o abismo e pulam 3 andares direto para um baú; Patas de Aranha transformam a
  teia em atalho; Pinça de Caranguejo corta as correntes do aliado de graça; Crânio de Dragão
  traz a opção "Intimidar" em 3 eventos; e mais 8 (Pernas de Centauro, Punho de Golem, Crânio de
  Ciclope, 2 peças Marinhas, Lâmina de Louva-a-deus, 2 peças de Inseto, ossos de Dragão,
  Carapaça de Besouro, Patas de Gafanhoto).
- **Voar sobre o abismo** nunca pula um chefe: o salto para no andar anterior.
- **Mercador**: vende 3 ossos comuns/raros por pó da partida (35/90). O mercador encapuzado
  pode vender um lendário **já descoberto** na Coleção (220). Isso deixa o Wyrm Ósseo — e a
  Hidra — possível antes de vencer o Dragão, sem quebrar "lendários só caem de chefes" na
  primeira vez.
- **Altar de troca**: o osso novo é de outra família e, quando existe, do mesmo encaixe, para o
  jogador não ficar com um osso que não pode usar. O nível do osso entregue é mantido.
- **Aliados** (Esqueleto Liberto, Escudeiro Perdido, Cão Fantasma) lutam até o fim da partida,
  atacam todo turno e não são alvo dos inimigos.
- **Armadilhas** tiram uma porcentagem da vida máxima; as Patas de Gafanhoto evitam 15%.
- Cada evento pode ter um **cenário** (`prop`) desenhado no lugar do inimigo: Coveiro, bruxa,
  jaula, altar, fogueira azul, baú, caixão, apostador, lago, fonte, abismo, portão e gato.

## Meta-progressão (Passo 5)

- **Hub com abas** (Início, Ossuário, Coleção, Loja) na própria tela de título.
- **Ossuário**: vida (+5%/nível), ataque (+5%/nível), defesa (+1/nível) e "faro de ossos"
  (+1% de chance de osso cair/nível); custo 50 × 1,25^k (GDD), até o nível 30.
- **Coleção**: completar uma família dá +5% permanente em vida, ataque e defesa. Um osso
  descoberto pode começar a partida encaixado: comuns são livres; raros e lendários gastam uma
  ficha "Osso inicial raro" (loja, Passo 6).
- **Bestiário de Formas**: formas de família mostram a dica ("4 peças de Fera"); as secretas
  aparecem como silhueta e "???" até serem descobertas.
- **Relíquias**: 12 relíquias (3 por espaço: comum, rara, lendária), nível até 10
  (+15% do bônus por nível, custo 80 × 1,4^(nível−1)). Fontes: Baú de ossos do Ossuário
  (300 de pó ou anúncio, 3 por dia), loja e calendário. As chances do baú aparecem antes de abrir.
  A relíquia rara do Kit é a **Lanterna do Coveiro**.
- **Gabinete de Curiosidades**: 30 itens em 10 conjuntos; os 6 itens e 2 bônus de conjunto do
  GDD foram mantidos; os outros 24 seguem o mesmo padrão. Itens repetidos sobem de 1 a 5
  estrelas (+50% do bônus por estrela). O Mapa Rasgado mostra o ícone do próximo evento na
  barra superior. O conjunto Coveiro garante um baú a cada bloco de 10 andares.
- **Companheiros**: Ossudo (disponível desde o início), Lumi (encontrada no Santuário de Velas
  ao levar uma vela, ou comprada na loja) e Bigorna (dia 7 do calendário de boas-vindas).
  Sobem até o nível 10 com pó de osso. A Bigorna aparece como um botão nos eventos enquanto
  tiver forjas (1 por partida, +1 a cada 5 níveis).
- **Caçador de Ossos**: ao morrer, ele rouba o osso de maior raridade (e nível) e o guarda (até 7).
  Nas partidas seguintes há ~60% de chance de ele aparecer uma vez (andares 4–27) como chefe
  opcional, desenhado com o mesmo esqueleto do Ossinho vestindo os ossos roubados e um capuz.
  Vencer devolve o osso mais recente com +1 nível e dá pó de osso.

## Loja, diamantes e calendários (Passo 6)

- **Serviços simulados**: `Backend` (Firebase), `Ads` (AdMob) e `Billing` (Google Play Billing)
  são fachadas com provedores simulados em `scripts/services/`. Para o lançamento, basta
  escrever provedores reais com os mesmos métodos; nenhum SDK ou credencial foi adicionado.
  A loja avisa que as compras são simuladas.
- **Horário do servidor** em tudo que é recompensa: calendários, ofertas do dia (trocam à
  meia-noite UTC), Kit 24h, limites diários de anúncios e assinatura. No simulado, o "servidor"
  é o relógio do sistema com um deslocamento de teste (`Backend.debug_advance`).
- **Calendário de 7 dias** exatamente como no GDD (500 de pó, 50, baú de curiosidades raro, 100,
  relíquia rara, 150, Bigorna + skin Ossinho Recém-Desperto). Depois, o **ciclo de 28 dias**:
  dias comuns alternam pó, baú comum e 10 diamantes; dia 7 = 50 diamantes, dia 14 = baú raro,
  dia 21 = 50 diamantes, dia 28 = item de curiosidade garantido. Um resgate por dia do servidor,
  contando dias com login (faltar não zera).
- **"Raro" no Gabinete**: os itens não têm raridade no GDD; os que caem de chefes e de eventos
  raros contam como raros para o "Baú de curiosidades raro".
- **Kit das primeiras 24 horas**: aparece ao fim da 1ª partida (abre a aba Loja uma vez) e some
  24 h depois da primeira abertura, pelo horário do servidor; cronômetro visível na aba Loja;
  uma compra por conta. Mostra o valor equivalente (850 diamantes) e a economia.
- **Chances visíveis** antes de comprar itens aleatórios (baú de curiosidades raro, relíquia
  rara, baú de ossos), como exige a Google Play.
- **Trocar as 3 opções de habilidade** (anúncio, 3 por partida) exigia mais que 3 bônus de
  nível: foram criados 7 novos no mesmo estilo (Costelas de Ferro, Joelhos Ligeiros, Mandíbula
  Faminta, Tutano Quente, Falange da Sorte, Crânio Pesado, Ossos Grossos).
- **Reviver**: anúncio (1 por partida), Reviver extra (item de 30 diamantes, estocável), reviver
  grátis diário do Cartão do Coveiro, ou pagar 30 diamantes na hora.
- **Intersticiais** só a partir da 3ª partida, no máximo 1 a cada 3 minutos, sempre ao voltar
  ao hub (nunca em combate). Depois do 10º, aparece a oferta de remover anúncios
  (que também dá +10% de pó permanente).
- **Skins** pintam todos os ossos (tom e transparência) no jogo, no hub e no Cartão da Criatura.
  Dourado, Neon, Pirata e Cristal estão à venda por diamantes (300–600) ou dinheiro;
  Recém-Desperto vem do dia 7, Lua de Âmbar do Kit e Fundador do Pacote apoiador
  (oferecido depois de vencer o Dragão Ancião, fim do capítulo 1).

## Preparação para publicação
- **APKs só pelo GitHub Actions**, a pedido do dono do projeto (regra registrada em `CLAUDE.md`).
- `version/code` = número da execução do workflow + 100, para nunca repetir na Play Console; `version/name` vem de `config/version` ou da tag `vX.Y.Z`.
- Ganchos `BT_*` passam por `Dev.env()`, que devolve vazio fora de build de depuração: nenhum atalho de teste chega ao jogador.
- O item "Privacidade" só aparece no menu quando `data/app.json` tiver `privacy_url`, para não exibir um botão que não faz nada.
- `store/` tem `.gdignore` e está no filtro de exportação: as imagens da loja não entram no APK.
- Painel de combate: largura total para os cartões de inimigo, altura que acompanha o conteúdo (250 a 560 px) e registro com as 4 últimas ações, em resposta ao retorno de que o painel antigo tinha muito espaço vazio.
- A permissão `INTERNET` continua desligada enquanto os serviços forem simulados; liga junto com os SDKs reais.

## Loja e skins (revisão antes do lançamento)
- **Bug corrigido:** os ossos ficam dentro de nós Bone2D, que não repassam o material; o shader do Ossinho nunca chegava aos ossos. Por isso as skins antigas (só tingimento) pareciam iguais e o piscar de dano e a cor das formas não apareciam. Agora cada sprite de osso recebe o material diretamente.
- **Skins com identidade própria** (shader `art/shaders/flash.gdshader` + `data/skins.json -> style`): paleta por luminância, contorno brilhante (com pulso), faixa de brilho que atravessa o corpo e faíscas. Dourado = ouro com brilho; Neon = ossos escuros com contorno ciano pulsando; Pirata = ossos curtidos + chapéu tricórnio e tapa-olho; Cristal = translúcido com faíscas; Recém-Desperto = brilho verde; Lua de Âmbar = âmbar + amuleto de lua; Fundador = violeta + coroa. Na qualidade baixa as faíscas são desligadas.
- **Acessórios** (`data/accessories.json`, arte em `art/skins/`, gerada por `tools/gen_skin_accessories.py`) presos ao crânio, acompanham as animações.
- **Prévia na loja** maior, com um corpo completo montado, para mostrar que a skin vale para todos os ossos; cada skin tem descrição.
- **Cartão da Criatura** com vitrine de skins (GDD: "na loja e no Cartão da Criatura"): troca entre as skins que o jogador tem antes de compartilhar e botão "Mais skins" que abre a loja.
- **Pacote apoiador:** o apoiador escreve o nome que aparece nos créditos do jogo (campo nos Créditos).
- **Segurança:** na versão de loja do Android, os provedores simulados nunca aprovam compra nem entregam recompensa de anúncio; se o plugin real não carregar, a loja avisa que está indisponível.
- Texto "compras simuladas neste protótipo" trocado por "Pagamento seguro pela Google Play".
- APK com bibliotecas nativas comprimidas (o AAB não muda: a Play entrega só a parte de cada aparelho).

## Mais variações de ossos (pedido do dono do projeto)
- O catálogo passou de 20 para **67 ossos**: **11 opções por parte do corpo** (crânio, costelas, braços, pernas, costas e cauda), além do básico. O GDD previa 20 no MVP; a expansão foi pedida explicitamente.
- Nenhum monstro novo: cada osso novo vem de um monstro que já existe e **tem aquela parte** (regra "Origem" do GDD) — ex.: o Lobo das Criptas agora solta crânio, costelas, garra, patas e cauda. Os chefes ganharam ossos raros/lendários (Pernas e Cauda de Golem, Cetro e Peito do Rei Rato, Cauda de Dragão).
- **Quedas:** um monstro comum sorteia **uma** das partes que tem e testa a chance pela raridade dela (no máximo um osso por monstro). Assim, mais variações não aumentam a quantidade de ossos por partida.
- **Equilíbrio:** os atributos dos ossos novos foram calibrados na simulação (`tests/BalanceSim.tscn`, 40 jogadores x 6 partidas). Na 1ª versão o jogo ficou mais difícil (os ossos novos diluíam os antigos); com +50% nos atributos a curva voltou à de antes: Rei Rato 95%, Golem 85%, Dragão 32% dos jogadores vencem até a 6ª partida.
- Novas habilidades periódicas: Garra flamejante (fogo), Enxurrada de ratos e Chuva de flechas (atingem todos), Pancada de cauda.
- Arte (placeholder no estilo do jogo, tamanho e pivô finais) em `tools/art_extra_head.py`, `tools/art_extra_limbs.py` e `tools/art_extra_back.py`, chamada por `tools/gen_art.py bones`.

## Revisão de UX (telas e painéis)
- **Tela inicial:** o bloco de baixo cresce para cima a partir das abas, então o botão **Jogar** nunca fica escondido (antes ficava cortado atrás da barra de abas). Companheiro e osso inicial viraram dois cartões lado a lado, tocáveis, que abrem o Ossuário e a Coleção. Abaixo do Jogar aparece o recorde ("Seu recorde: andar N") ou um convite na primeira vez. O calendário virou um botão flutuante "Prêmios" com ponto vermelho quando há recompensa. A barra do topo ficou só com as moedas e "⚙ Opções"; o idioma passou a ser o primeiro item de Opções.
- **Painel da partida:** sem altura mínima grande. Ele cresce na hora quando entra conteúdo (botões nunca cortados) e encolhe suave quando sai; se não há conteúdo (título do andar, transições), o painel some em vez de ficar vazio.
- Princípios usados: ação principal grande e na zona do polegar; nenhuma área vazia reservada; informação secundária compacta e tocável; um só ponto de configurações; avisos (ponto vermelho) só quando há algo a fazer.
- **Rolagem por toque em qualquer ponto** (`scripts/ui/touch_scroll.gd`, usada nas abas do menu e no painel da partida): arrastar sobre botões, cartões e textos rola a página; o toque no botão é cancelado quando o dedo passa de 14 px; ao soltar, a rolagem continua com inércia. Um toque curto continua funcionando como toque. Coberto por teste automático (arrastar sobre botão rola e não aperta; toque curto aperta).
- **Menu de batalha mais alto:** elementos maiores (cartões de inimigo 132 px, retrato 84, números 22, registro 19) e altura mínima de 340 px, testada contra 280 e 400: o topo do painel fica a ~50 px dos pés dos personagens (antes ~170), mantendo um respiro sem sobrar espaço dentro do painel.
- Texto dos eventos aparece com um esmaecer suave já no tamanho final (antes "digitava" e o painel mudava de altura a cada linha).

## Firebase (Analytics + Remote Config)
- Não existe plugin oficial do Firebase para Godot. Fizemos um **plugin Android próprio** (`addons/bonetribe_firebase/android/BoneTribeFirebase.java`, plugin v2 do Godot) que é copiado para o projeto Gradle e compilado junto com o app; o plugin do editor (`addons/bonetribe_firebase/plugin.gd`) adiciona as dependências `firebase-analytics` e `firebase-config` e o plugin `google-services` do Gradle **só quando existe** `addons/bonetribe_firebase/google-services.json`.
- O `google-services.json` vem do secret `FIREBASE_GOOGLE_SERVICES_JSON` do GitHub e nunca vai para o repositório. Sem o secret, o build é igual ao anterior e o workflow compila uma vez com uma configuração de exemplo (`tools/firebase_config_exemplo.json`, não publicada) para garantir que a integração continua compilando.
- Os 23 eventos do jogo passam pelo mesmo `Backend.log_event` de antes. O provedor do Firebase envia o evento original e também o equivalente padrão do GA4 (`level_start`, `level_end` com `success` e `floor`, `earn_virtual_currency`, `spend_virtual_currency`, `tutorial_complete`, `share`), que alimentam os relatórios prontos do Google Analytics.
- Receita de compras e anúncios não é enviada pelo jogo: vem do vínculo do Firebase com a Play Console e o AdMob (evita contar em dobro).
- Crashlytics ficou de fora nesta versão: exige o plugin do Gradle com ID de build; sem ele o app fecha ao abrir. Entra numa próxima atualização.
- `Backend.remote_config(chave, padrão)` lê o Remote Config com o tipo do valor padrão (número, texto, verdadeiro/falso ou JSON).

## 10 torres (dificuldade constante até o fim)
- **Por quê:** com 30 andares, quem joga 2 a 3 dias vence o Dragão e o jogo fica fácil. Agora os 30 andares são a **Torre 1** e o jogo vai até a **Torre 10**.
- **Como funciona:** cada torre repete os 30 andares, chefes e eventos, com inimigos mais fortes (vida x1,35 / ataque x1,22 na Torre 2 ... vida x4,15 / ataque x2,98 na Torre 10; vale para monstros, chefes, Caçador e aliados) e mais pó de osso (x1,5 ... x5,5). Vencer o Dragão Ancião da torre libera a próxima, já a deixa selecionada e paga diamantes na 1ª vez (30, 45, ... 165). Qualquer torre liberada pode ser jogada de novo (o seletor da tela inicial passa por elas e mostra a próxima trancada e o que falta). Perfis antigos que já venceram o Dragão começam com a Torre 2 liberada.
- **Ossuário:** o custo antigo (50 x 1,25^k, máximo 30) explodia e travava a evolução. Novo: 20 x (k+1)^1,3, até o nível 120 por atributo, para sempre haver melhoria possível rumo à próxima torre. Os ganhos por nível não mudaram.
- **Calibração** (`tests/BalanceSim.tscn -- mode=towers`, 16 jogadores simulados que só usam o Ossuário, sem relíquias, companheiros nem Gabinete): 1ª vitória na Torre 1 por volta da partida 8; Torre 2 ~18; 3 ~31; 4 ~46; 5 ~66; 6 ~85; 7 ~108; 8 ~133; 9 ~160; 10 ~180. Em todas as torres 87% a 97% das partidas terminam em derrota, então o jogador sempre tem um desafio e um motivo para melhorar. Jogadores reais, com relíquias e companheiros, avançam mais rápido que a simulação.
- **Tela:** seletor "‹ Torre N · Nome ›" acima do Jogar (com o recorde da torre), "Torre N · Andar X/30" no topo da partida, nome da torre na entrada, cor do ambiente própria de cada torre, aviso de torre vencida/liberada no fim da partida e torre no Cartão da Criatura.
- **Analytics:** `run_start`/`run_end` levam `tower`; no GA4 `level_name` vira `tower_N`; novo evento `tower_clear`.

## Versão 1.1.0: mais torres, mais monstros, save protegido
- **Save protegido:** o save tem número de versão (`Profile.SAVE_VERSION`, hoje 2) e passa por `Profile._migrate()` ao abrir. Campos novos entram com valor padrão; nada é apagado ou zerado. Teste automático carrega um save da versão 1 e confere moedas, Ossuário, coleção, torres, skins, relíquias e compras.
- **Famílias completas são para sempre:** os ossos novos entraram nas 6 famílias. Para ninguém perder o bônus de +5%, quem já tinha a família completa com os ossos antigos fica com ela completa (`families_done` no save), e daqui em diante completar uma vez basta.
- **20 torres** em 3 regiões de chefes: Torres 1–3 (Rei Rato, Golem, Dragão Ancião), 4–6 (Matriarca Carniçal, Titã de Gelo, Serpe de Magma), 7–10 (Beemote do Pântano, Lich do Sino, Dragão de Obsidiana); 11–20 repetem as regiões com inimigos mais fortes. Vencer o chefe do andar 30 libera a próxima torre (antes era sempre o Dragão).
- **16 monstros novos:** 4 desde a Torre 1 (aparecem a partir dos andares 9–16, para dar variedade no começo), 6 a partir da Torre 4 e 6 a partir da Torre 7 (aparecem 50% mais nas suas torres para serem vistos). **35 ossos novos** (102 no total). Ossos de monstros das torres altas só caem (inclusive em baús, mercador e altar) a partir daquela torre e aparecem na Coleção com a etiqueta **#Torre N**.
- **Calibração:** com os ossos novos, os jogadores ficaram mais fortes e as Torres 4–10 ficaram mais fáceis; os monstros e chefes das regiões 2 e 3 ganharam +20% de vida e +12% de ataque para manter a curva anterior (1ª vitória na Torre 1 ~8 partidas, 4 ~39, 7 ~87, 10 ~180 na simulação só com Ossuário). Ossuário vai até o nível 200.
- **Osso igual:** se cair o mesmo osso que está equipado, com poder igual ou menor (nível e raridade da Bigorna), ele é triturado na hora com o aviso "Mesmo osso: … Triturando…"; se for mais forte, troca direto e tritura o antigo. Com encaixe livre (braços), ele continua sendo encaixado.
- **Ganho do +1:** subir um osso mostra os atributos antes → depois, o poder total (+25% por nível) e quantas peças da família ele passa a contar. O cartão do osso mostra os atributos reais quando ele tem nível ou raridade melhorada.
- **Vida fora de sincronia (correção):** o combate calcula a rodada inteira de uma vez; a barra sobre o monstro e o painel liam a vida em momentos diferentes. Agora cada acontecimento leva a vida de todos naquele instante (`hps`), e tela, painel e HUD mostram o mesmo valor golpe a golpe.
- **Estatísticas** (Opções e Coleção): partidas, torres vencidas e recorde por torre, chefes derrotados (cada um), coleção e famílias. Monstros derrotados, andares, derrotas, pó ganho, ossos triturados e tempo de jogo contam a partir da 1.1 (o save antigo não tinha esses números).

## Versão 1.2.0: som, missões, notificações, pó offline e tutorial
- **Som sincronizado com a tela:** 55 efeitos e 4 músicas (início, cripta, combate, chefe), gerados por `tools/gen_audio.py` (placeholders sintetizados; troque pelo arquivo final mantendo o nome). O autoload `Audio` deixa todos os efeitos carregados na memória e cada som tem seu reprodutor com várias vozes, então tocar é imediato. Cada `Audio.play` fica na mesma linha do efeito visual que acompanha (número de dano, tremor, explosão de ossos, encaixe), sem nenhuma espera entre os dois: o golpe tem o impulso no começo da animação e o impacto no quadro do dano. Um teste automático confere isso em todo o `run.gd`. A música abaixa nos momentos grandes (chefe, transformação, Caçador), troca com transição suave e para durante anúncios. Opções: efeitos e música separados.
- **Missões:** 3 diárias e 3 semanais (`data/missions.json`), trocadas pela hora do servidor; cada uma conta uma estatística (monstros, partidas, chefes, andares, ossos triturados/encaixados, níveis, formas). O pó da recompensa acompanha a torre mais alta liberada. Botão "Missões" na tela inicial com aviso quando há resgate; aviso no topo da partida quando uma missão é concluída.
- **Notificações locais:** plugin Android próprio (`addons/bonetribe_notify`), sem servidor e sem dados saindo do aparelho, por isso a política de privacidade não muda. Ao sair do jogo agenda: prêmio diário/missões novas (10 min depois da virada do dia), saco de pó do Ossudo cheio (8 h) e o Caçador com um osso seu (20 h). Ao voltar, cancela. A permissão do Android 13+ é pedida uma vez, depois da 1ª partida (nunca ao abrir o jogo). Desligável nas Opções.
- **Pó offline:** o Ossudo junta 50 de pó por hora × o pó da torre mais alta liberada, até 8 horas (ausências de 10 min ou mais, só depois da 1ª partida). Ao voltar: coletar ou dobrar com anúncio (3 por dia).
- **Tutorial guiado:** 9 dicas na partida (escolhas, combate, mira, encaixe, família, trocar/triturar, nível, chefe, forma), uma vez cada, nas 3 primeiras partidas, num balão do Ossudo que não pausa o jogo; e 2 na tela inicial (Ossuário depois da 1ª partida, com o botão pulsando; seletor de torres quando a 2ª abre). Cada dica vista vai para o Analytics (`tutorial_step`).


## Versão 1.2.1: falha ao fechar no Android 16
- **Sintoma (Play Console):** falha `std::__ndk1::recursive_mutex::lock()` em `libc++_shared.so`, ~45% dos usuários. Rastreamento: `GodotLib.step` (thread de renderização) → `pthread_mutex_lock` → `HandleUsingDestroyedMutex` → `abort`. Ou seja, o motor ainda desenhava um quadro enquanto o encerramento do processo já tinha destruído as travas globais. O Android 16 aborta nesse caso (versões antigas ignoravam).
- **Causa:** o botão Voltar do Android encerrava o jogo (padrão do Godot `application/config/quit_on_go_back=true`), e o encerramento do Godot no Android cai nessa corrida.
- **Correção:** `quit_on_go_back=false`; o `Router` trata `NOTIFICATION_WM_GO_BACK_REQUEST` salvando o perfil e mandando o app para o segundo plano (`moveTaskToBack`), igual ao botão Início. O jogo nunca encerra o próprio processo; quem fecha é o Android, sem relatório de falha. Teste `test_19_android_exit`.
- Não muda nada no jogo nem no save.

## Versão 1.3.0: status na partida, torres 21–40, eventos novos e correções
- **Corpo quebrado depois do anúncio (correção):** ao reviver, `reassemble()` só religava a animação parada; a coluna continuava deitada (90° da queda) e, se o jogador voltasse do anúncio antes da queda terminar, as peças seguiam caindo. Agora a queda é interrompida e cada peça volta para o lugar (posição, rotação e corpo). Teste em `test_20_update_1_3`.
- **Status durante a partida:** botão "Status" no canto superior esquerdo abre atributos (vida, ataque, defesa, crítico, dano crítico, esquiva, velocidade e os extras que o jogador tiver), forma ativa, peças por família e ossos equipados. O jogo pausa enquanto a tela está aberta (os temporizadores da partida respeitam a pausa).
- **Estatísticas numa linha:** o número ficava sem largura e quebrava letra por letra. Rótulo à esquerda (corta com "…") e número à direita, sem quebra, em faixas alternadas; torres mostram "andar recorde/30 · ×vitórias".
- **Ganho da melhoria:** cada companheiro mostra "Agora: …" e "Nível N: …" com as mesmas fórmulas do jogo (a Bigorna mostra o próximo nível em que ganha uma forja, porque ela só muda a cada 5 níveis). As melhorias do Ossuário mostram o valor do próximo nível.
- **Torres 21–40:** mesma progressão (+0,35 vida, +0,22 ataque, +0,5 pó por torre; diamantes +15). Misturam os chefes das 3 regiões (andar 10: Rei Rato/Matriarca/Beemote; 20: Golem/Titã/Lich; 30: um dos dragões) sem repetir as combinações das regiões originais. Cada uma tem uma **maldição** (`curses` em `data/towers.json`) aplicada a todos os inimigos, lacaios e Caçador (não aos aliados): veneno, sangria ou atordoamento ao golpe, velocidade/esquiva, roubo de vida, reflexo, crítico, +20% de vida ou regeneração. A maldição aparece no seletor de torres e no início da partida.
- **Save:** quem já venceu a última torre que existia ganha a seguinte liberada ao abrir o jogo (sem precisar vencê-la de novo). Nada mais muda no save.
- **5 tipos de evento novos (16 eventos):** Elite (monstro dourado +70% vida, +30% ataque, ×2 experiência, recompensa rara garantida), Aposta (dobra ou metade do pó, crânios virados, roleta), Santuário (escolher uma bênção; pacto sombrio com preço; poço dos desejos), Enigma (charadas da esfinge com 3 respostas que funcionam nos 3 idiomas) e Arena (ondas seguidas com prêmio crescente). Pesos: combate 45→35, escolha 20→17, baú 10→9, mercador 8→7, aliado 5→4, altar 5→4; novos: elite 4, aposta 3, santuário 4, enigma 3, arena 3. Na simulação, a 1ª vitória sobre cada chefe continua na mesma partida média (Rei Rato 2,9; Golem 3,5–3,7; Dragão 3,9–4,5).
- Ferramentas: `BT_STATUS=s` abre o Status depois de s segundos; `BT_EVENT=id` força um evento no 1º andar (só em depuração). Ícones dos tipos novos em `tools/art_events_v13.py`.
- **Falha ao fechar (Android 16), 2ª parte:** o Play Console mostrou 4 grupos da mesma falha (`FORTIFY: pthread_mutex_lock called on a destroyed mutex`, ~90 usuários) sempre em `GodotLib.step` na linha de renderização. A 1.2.1 resolveu o botão Voltar; os outros caminhos de fechamento (arrastar o app na lista de recentes, o sistema encerrar a Activity) ainda passavam pelo desmonte nativo do Godot, que destrói travas globais enquanto um quadro ainda é desenhado. Agora o projeto tem a própria Activity (`android_template/GodotApp.java`, copiada pelo workflow para o modelo de build): em `onDestroy` com o app fechando, e em `onGodotForceQuit`, o processo é encerrado direto (`Process.killProcess`), sem o desmonte. O perfil já foi salvo em `onPause` (notificação `APPLICATION_PAUSED`), que sempre vem antes. O workflow exporta duas vezes: a 1ª instala o modelo, a 2ª usa a Activity trocada; o passo de verificação confere que ela está no APK.
- **Continuar a partida:** a partida é gravada no começo de cada andar em `user://run_save.json` (arquivo separado; o perfil não muda, só ganha `best_body`). A gravação inclui o estado do sorteio, então fechar o app e continuar repete o mesmo evento (não dá para trocar evento ruim). Ela é apagada na morte (antes da tela de reviver, para fechar o app ali não salvar a vida) e no fim da partida (antes de pagar o pó, para nunca pagar duas vezes). Foto com osso/torre/melhoria que não existe mais, versão diferente ou arquivo corrompido é descartada. Na tela inicial: "Continuar · Torre X · Andar Y"; "Nova partida" pede confirmação. Gravação escrita num arquivo temporário e trocada de uma vez.
- **Acabamento visual:** brilho no toque dos botões (além do encolher que já existia); feixe de luz da cor da raridade quando cai osso raro ou lendário (lendário treme a tela); o esqueleto pisca e vira a cabeça para os inimigos no combate; cenário por região (`theme` em `data/towers.json`: cripta com brasas, gelo com neve, pântano com esporos, torres amaldiçoadas com névoa e luzes roxas); etiqueta da maldição fixa no topo da partida (tocar mostra o efeito); elite com coroa e faíscas; crítico maior com "!" e tranco; cura sobe em arco; tela inicial mostra o corpo da partida recorde quando não há osso inicial escolhido; Coleção com moldura da cor da raridade e brilho nos lendários. O painel de eventos já se ajustava ao texto (o vazio visto era o instante antes dos botões aparecerem).
- Testes do GitHub com limite de tempo (`timeout 1500`): um erro de script na cena de testes faz o passo falhar em vez de travar.

## Versão 1.3.1: correção de falhas do Play Console
- Rastreamentos sem símbolos foram lidos com a biblioteca oficial `libgodot_android.so` do modelo 4.7.2 (mesmo Build ID `270121fe…`): cada endereço foi ligado à sua função pelo `.eh_frame` e pelos textos de erro que a função usa (`tools`: ver histórico; script em scratchpad).
- **Falha `GodotLib_step` → `Node::queue_free` (2 grupos):** temporizador do laço do AdMob → `Ads.show_rewarded` → lambda do botão "Dobrar" do pó offline → `close` → `bg.queue_free()` num popup já destruído. Enquanto o anúncio carregava, "Coletar" continuava ativo; tocar nele fechava o popup, e o fim do anúncio fechava de novo (e tentava coletar de novo). Correções: (1) `Widgets.busy_overlay` bloqueia a tela com "Carregando anúncio…/Abrindo o Google Play…" durante todo anúncio recompensado e compra; (2) um anúncio por vez (`Ads._showing`); (3) o popup fecha uma vez só e confere `is_instance_valid`; (4) o mesmo cuidado no pó dobrado do fim da partida, reviver, trocar opções de nível e popup de oferta. Teste `test_23` reproduz o toque em "Coletar" com o anúncio carregando.
- **Falha no driver de vídeo (MediaTek mt6855, `glLinkProgram` dentro de "Update GPUParticles"):** o driver cai ao compilar o shader de processamento das `GPUParticles2D`. Todas as partículas do jogo agora são `CPUParticles2D` (`Particles.to_cpu` converte a configuração; aparência igual). O teste confere que nenhuma cena cria partícula de GPU.
- Texto: "Crânio do meio" / "Cráneo del medio" no evento da aposta.

## Versão 1.4.0: conteúdo, usos de diamante, Ossuário avançado e correções
- **Saves:** nenhum campo antigo muda. Entram com valor padrão `review`, `missions.swap_day` e os níveis das melhorias avançadas (0). Migração de segurança: quem tinha todos os ossos antigos de uma família continua com a família completa mesmo com os ossos novos (`families_done`). Teste `test_24` carrega um save no formato da 1.3.
- **Raio pelos olhos (bug):** a animação do `eye_beam` saía sempre da caveira do Ossinho, mesmo quando quem usava era o inimigo (Lich do Sino, Ciclope, Peixe-Lanterna). O dano estava certo; o desenho agora sai de quem atirou (vermelho para inimigo).
- **Velocidade do combate (bug antigo):** o botão x1/x2 era ancorado à direita antes de a tela ter tamanho e ficava fora dela. Agora aparece ao lado de **Desistir**.
- **Desistir:** botão no canto superior direito; pausa, pede confirmação e termina como derrota (pó dos andares, Caçador pode levar um osso) para não virar fuga do Caçador. O registro do fim da partida (`_record_run_end`) acontece uma vez só. O `Router` roda mesmo com o jogo pausado.
- **Cartão da Criatura estreito (bug):** o giro "3D" encolhe a largura do esqueleto; a foto para compartilhar agora é tirada com ele de frente (`capture_card`).
- **Status:** cada osso equipado mostra a descrição e, se subiu de nível ou de raridade, os valores de agora.
- **Relíquias:** mostram "Próximo nível: Ataque 5% → 6%" (mesma conta do jogo).
- **Avaliação no Google Play (In-App Review):** plugin `addons/bonetribe_review` (biblioteca `com.google.android.play:review`). Pede ao voltar de uma partida em que venceu um chefe ou liberou torre, a partir da 3ª partida; no máximo 2 vezes, com 45 dias entre elas; nesse retorno não mostra o intersticial. A política de privacidade não muda (a janela é do Google Play).
- **Usos de diamante (conveniência, com limite):** trocar as opções de nível (5, até 3 por partida, além do anúncio), outro evento no andar (8, até 3 por partida), trocar uma missão diária (10, uma por dia), dobrar o pó offline (20, divide o limite diário com o anúncio) e dobrar o pó do fim da partida (15, alternativa ao anúncio). Preços em `data/shop.json → diamond_uses`. O "resgatar osso do Caçador" ficou de fora: fora da partida não há onde guardar o osso sem mexer no osso inicial e no save.
- **Ossuário avançado:** Crítico (+0,5%/nível, máx. 20), Dano crítico (+2%, 20), Esquiva (+0,4%, 20), Roubo de vida (+0,4%, 20) e Regeneração (+0,1%/turno, 15). Aparecem depois de vencer a Torre 1 e custam bem mais que as básicas (custo 150–220 × nível^1,45–1,5), para o começo do jogo continuar igual. Valores com uma casa decimal quando preciso (vírgula em pt/es).
- **Conteúdo:** 6 monstros, 3 chefes e 15 ossos (arte em `tools/art_wave3_monsters.py` e `tools/art_wave3_bones.py`), 7 formas secretas. Chefes novos nas torres 14–20 e 21–40 no lugar de chefes repetidos. Equilíbrio (simulação com 100 jogadores × 6 partidas, sem os monstros novos → com eles e ajustados): Rei Rato 92% → 90%, Golem 73% → 69%, Dragão 33% → 33%; modo torres continua chegando na Torre ~10,6 em 200 partidas. Escaravelho e Cavaleiro foram suavizados (defesa 5/6, vida 1,0/1,1) e a Rainha Aranha/Kraken ajustados à força dos chefes que substituem.
- Ferramenta: `BT_QUIT=s` abre "Desistir" e confirma (teste do caminho inteiro).
- **Vida mostrada x curas pequenas (bug antigo):** roubo de vida, regeneração e cura do companheiro abaixo de 1 PV mudavam a vida sem evento, e a barra ficava até 1 PV atrás até o próximo golpe. Agora corrigem a vida do último evento (`_sync_last`), sem número "+0" na tela. Só afeta a exibição; as contas do combate não mudam.
- **Combate x2 por anúncio recompensado:** o botão x1/x2 mostra "x2 AD"; o toque pausa e oferece um anúncio que libera o x2 até o fim da partida (guardado em `state.flags.speed_x2`, continua ao retomar). Quem comprou "sem anúncios" ou tem assinatura ativa usa direto. A opção salva `fast_combat` só vale quando o x2 está liberado. Na 1.3 o botão estava fora da tela, então ninguém perde algo que usava.
- **Espinha de Serpente → Cauda de Serpente:** o osso fica no encaixe de cauda e é desenhado deitado no chão, como as outras caudas; o nome "espinha" fazia parecer um osso do corpo deitado. Ficou na cauda (no encaixe de coluna seria um bônus grátis, porque só a Coluna de Hidra usa esse encaixe). O ID continua `bone_spine_serpent`. Conferido o esqueleto com cada um dos 117 ossos, antes e depois de cair e remontar: nenhum outro osso fica deitado.
- **Modo Infinito:** andares sem fim; cada andar mais forte (fórmula normal com o andar real, ~5% por andar, sem teto). Libera ao vencer o Rei Rato. Recorde = andar alcançado, salvo em `Profile.data.endless` (campo novo com padrão: saves antigos carregam com recorde 0) e mostrado na tela inicial, no topo da partida e no fim. Eventos e monstros usam o andar dentro da volta de 30 (todos os eventos valem para os andares 1–30); a cada volta entram monstros de 3 torres acima e outro trio de chefes. Sem maldição, sem multiplicador de pó de torre, não mexe no progresso das torres.
  - **Por que os chefes do Infinito são mais leves (70% vida, 90% ataque):** sem isso a simulação mostrou 75–90% das partidas terminando exatamente num chefe (recordes sempre 10, 20, 30…) e um muro no andar 60. Testado também crescimento extra depois do andar 30 (1,08/1,06 e 1,10/1,07 por andar): todos paravam perto do andar 50, e a evolução do jogador quase não mudava o recorde. Ficou só o crescimento normal.
  - **1ª vitória dos chefes protegida:** no Infinito aparecem chefes das torres 4–20 antes de o jogador chegar lá. Vencer um deles no Infinito não conta como vitória no perfil e o osso cai com a chance de repetição (10%), sem diamantes de 1ª vitória nem curiosidade — senão o Infinito daria lendários das torres altas cedo e o jogador perderia o prêmio garantido quando chegasse à torre.
  - **Simulação** (`-- mode=endless players=12 runs=120`, 3 partidas no Infinito em cada ponto): após 3 partidas andar médio 17,7; após 10, 33,6; após 30 (torre ~4,5), 42,0; após 60 (torre ~7), 50,3; após 120 (torre ~9), 56,1, máximo 84. Torres sem mudança (Rei Rato 90%, Golem 69%).
  - **Pó:** por andar igual à Torre 1, então por minuto o Infinito paga menos que a torre mais alta do jogador: não vira atalho para juntar pó.
  - Dica única na tela inicial quando o modo abre (`tip_endless`), para quem já tinha vencido o Rei Rato descobrir o modo na atualização.
  - Ferramenta: `BT_ENDLESS=1` começa a partida no Infinito (com `BT_FLOOR=n`, no andar n).
- **Infinito mais duro (pedido depois do 1º teste):** o modo não pode ser mais fácil que a torre normal, o jogador tem que perder em algum momento e a partida não pode ser longa.
  - Saiu o desconto dos chefes (agora 100%) e entrou um salto a cada dezena: +30% de vida e +20% de ataque nos andares 11–20, de novo nos 21–30, e assim por diante (`decade_hp_mult` 1,3 e `decade_atk_mult` 1,2), além dos ~5% por andar de sempre. Teste garante que em todo andar de 1 a 60 monstros e chefes são pelo menos tão fortes quanto na Torre 1.
  - Ossos e monstros vêm da torre mais alta liberada (`endless_tier`, gravada no começo e no Continuar). Sem isso, o jogador da torre 10 só via ossos da Torre 1 e não conseguia mostrar a força que tem.
  - Testado também 1,5/1,35 por dezena (recorde parava em ~25–30 para todo mundo) e crescimento extra por andar desde o 1º (1,06/1,045: quase todos paravam no andar 10–20).
  - Simulação final: após 3 partidas recorde médio 15,9; após 10, 22,9; após 30 (torre ~4), 25,9; após 60 (torre ~6,5), 32,1; após 120 (torre ~9), 35,6, máximo 60. A partida típica tem 15–40 andares (até ~1,3 partida de torre).
  - Anúncios iguais aos da partida normal, conferido na partida real: reviver com anúncio e "Dobrar pó (anúncio)" no fim.
- **Cartão do Coveiro 1.4:** sem anúncios (sem intersticial; os recompensados entregam o prêmio na hora e continuam com os mesmos limites por partida/dia), 1.500 de pó (era 300), 50 diamantes (era 30), 1 ficha de osso raro (começar a partida com um osso raro já descoberto) e 2 reviver grátis (era 1) por dia; o baú raro semanal continua. Preço igual. Contador novo `free_revives_used` com padrão: quem já usou o reviver hoje numa versão antiga ainda tem mais 1. Atualizar a descrição do produto na Play Console (texto em `iap_gravedigger_card_desc`).
- **Letreiro atrás da janela (bug):** um letreiro ainda na tela (nome do modo, "Novo recorde!", nome do chefe) aparecia por trás da janela de fim de partida, através do painel. Agora toda janela (`_dialog_frame`, Desistir, x2) apaga o letreiro e os avisos do topo antes de abrir. O aviso "Seu recorde: andar N" e o HUD usam o recorde de quando a partida começou (antes podiam mostrar o novo recorde já gravado).

## Versão 1.4.1: comparação de ossos
- Pedido de jogadores: sempre poder comparar o osso oferecido com o equipado. Decisão do dono do jogo: **só a comparação osso a osso** (sem somar família, forma ou força total — a build é escolha do jogador) e **trocas automáticas continuam automáticas**, com aviso.
- Janela "Osso encontrado" (queda de monstro/chefe, eventos, Ossudo, Caçador, Altar, depois de comprar no Mercador): cartão **Equipado** à esquerda, **Novo** à direita e quadro **O que muda** com cada atributo (atual → novo e a diferença, verde se melhora, vermelho se piora) e "Ganha/Perde o efeito especial".
- **Braços:** um bloco por braço ("Braço esquerdo · Garra de Urso") com a diferença em uma linha e o botão "Trocar este". Antes só aparecia o osso novo.
- **Mercador:** embaixo de cada osso, "Melhor que o seu / Pior que o seu / Troca atributos / Igual / Encaixe vazio" e a diferença, comparando com o osso do encaixe (nos braços, com o braço mais fraco) — antes de pagar.
- **Trocas automáticas** (encaixe vazio, mesmo osso melhor, mesmo osso igual/pior) seguem sem perguntar, com aviso no topo por ~2,4 s dizendo o que mudou. Avisos ao mesmo tempo ficam um embaixo do outro.
- Só tela: contas do jogo e save não mudam. Funções em `Body.compare_rows/compare_verdict/compare_short` e `Widgets.bone_compare`. Teste `test_27`.
- **Revisão em telas pequenas (1.4.1):** a tela lógica nunca é menor que 720x1280 (`stretch aspect = expand`), então o risco é a janela passar da altura. Medidas de todas as combinações de ossos no pior caso (espanhol, nível máximo, 3 braços com a Coluna de Hidra): a troca de braço ocupava 1177 de 1280 e cobria o HUD. Agora o osso novo dos braços usa cartão deitado (`Widgets.bone_card_row`) e cada braço é uma linha com o botão ao lado: pior caso cai para ~940 e o maior passa a ser a troca de pernas (~1030). Teste garante < 1100. O título "O que muda" mostra o veredito (Melhor/Pior/Troca atributos) e os textos do mercador subiram de 16 para 17–19.
- **Cartão do Coveiro como carro-chefe (1.4.1):** primeiro item da loja, com selo "Melhor valor da loja", prévia do Ossinho com a skin, 10 benefícios com ícone e "Vale mais de 5x o preço". Novidades: **skin exclusiva "Coveiro"** (chapéu de coveiro + brilho de lanterna fantasma; vale só com o Cartão ativo, não entra na lista de skins compradas; vencido, o visual volta ao normal e a escolha fica guardada para quando renovar), **300 diamantes na hora** de cada compra, **+50% de pó em toda partida** (`run_dust_bonus`, soma com os outros bônus). Continua: sem anúncios, x2 liberado, por dia 1.500 de pó / 50 diamantes / 1 osso raro / 2 reviver grátis, baú raro semanal. Preço igual.
  - **Conta do "mais de 5x"** (preços em US$ da própria loja; o melhor pacote é 2.600 diamantes por US$ 19,99 ≈ US$ 0,0077 por diamante): 300 + 30 × 50 = 1.800 diamantes ≈ US$ 13,8; 2 reviver/dia × 30 = 60 reviver × 30 diamantes = 1.800 diamantes ≈ US$ 13,8; "Sem anúncios" US$ 4,99; skin ≈ US$ 2,99 (preço das skins). Total ≈ US$ 35,6 por US$ 4,99 ≈ 7x, sem contar 45.000 de pó, +50% de pó nas partidas, ossos raros e baús. Dizemos "mais de 5x" para ficar abaixo da conta.
  - **Sem cobrança automática** é verdade: o produto é um passe de 30 dias (consumível), não uma assinatura recorrente da Play.
  - **Lembretes discretos** (sem janela que bloqueia): na morte, "Cartão do Coveiro: 2 reviver grátis por dia"; no fim da partida, "Com o Cartão do Coveiro: +N de pó nesta partida" (o valor real que o +50% daria). Assinante vê "Cartão do Coveiro: +N de pó nesta partida".
  - Na grade de skins, a do Coveiro aparece para todos com "Só com o Cartão do Coveiro".
  - Atualizar a descrição do produto na Play Console (texto em `iap_gravedigger_card_desc`).
- **Cartão do Coveiro, conversão (1.4.1, 2ª rodada):**
  - **Capa** (`tools/art_card_cover.py` → `art/ui/ui_card_cover.png`): cemitério à noite com lua, lápides, pá e lanternas fantasma; o Ossinho com a skin do Coveiro fica à esquerda, nome e valor à direita sobre um fundo escuro para leitura.
  - **Na hora, a cada compra:** 500 diamantes, 3.000 de pó, relíquia rara, baú de curiosidades raro e a skin. (Era só 300 diamantes.)
  - **Valor mostrado = conta da própria loja**, em diamantes (`Store.card_value()`): cada item vale o preço dele em diamantes na loja (1.000 de pó = 50, osso raro = 80, reviver = 30, baú raro = 150, relíquia rara = 200, skin = 500), "sem anúncios" vale o preço do produto convertido pelo melhor pacote de diamantes. Hoje dá ≈ 10.700 diamantes em itens, "vale até 16x o preço" — com "até" e a nota "pelos preços da própria loja, usando tudo nos 30 dias", porque depende de entrar todo dia e usar os revivers. Muda sozinho se os preços da loja mudarem. Não mostramos valor em dinheiro para não depender da moeda de cada país.
  - **"Você paga x Você recebe"** em barras, e para assinante **"Seu Cartão já rendeu"** (diamantes, pó — inclusive o +50% das partidas —, ossos raros, revivers grátis usados e anúncios pulados), contado em `subscription.earned` (campo novo com padrão).
  - **Oferta na tela inicial**, ao voltar de uma partida: só para quem não tem o Cartão, a partir da 5ª partida, no máximo 1 vez a cada 7 dias, nunca junto da oferta de "sem anúncios" nem do Kit 24h; botão "Ver o Cartão" abre a loja. Eventos `card_offer_shown` e `card_offer_open` para medir a conversão. Ajustável em `shop.json` (`offer_min_runs`, `offer_every_days`).
  - Aviso do fim da partida continua discreto (uma linha).
- **Abas do hub sem a tela inicial ao fundo + FPS (1.4.1):** as páginas (Loja, Ossuário, Coleção) tinham fundo 94% opaco e o cenário da cripta (velas, partículas, luzes) e o Ossinho continuavam sendo desenhados e atualizados por baixo. Agora o cenário fica invisível e parado fora da aba Início (`_set_world_active`) e o fundo das páginas é opaco. Na loja, cada prévia de skin era um Ossinho animado num SubViewport atualizado todo quadro (8 de uma vez, mesmo fora da tela); agora só anima e desenha enquanto aparece na tela. Medido em software (xvfb, só para comparar): loja 47 → 14 ms por quadro, Ossuário 24 → 8,5 ms. Teste `test_29`.
- **Preço do Cartão:** R$ 9,99 definido na Play Console para todos os países (a Play converte). `shop.json` passou a 9,99 e o "vale até Nx" agora é calculado em reais (Cartão x melhor pacote de diamantes em reais). O `price_usd` da tabela é 1,79 (o preço que a Play mostra em dólar depois de converter R$ 9,99); serve de reserva no computador e no evento `iap_revenue` (`usd`).

## Versão 1.4.2: ícone novo
- Ícone do app trocado pelo Ossinho de dragão (crânio, asas e cauda de dragão) sobre fundo de fogo com raios — opção escolhida entre 8 testadas (prévias na loja, na lista da Play e pequeno no celular). O personagem é um render do próprio jogo (`tools/icon_src/icon_dragon_render.png`) e o ícone sai de `tools/art_app_icon.py` (`gen_art.py icon` chama o mesmo script).
- Ícone adaptável: fundo cheio + personagem reduzido a 68% na camada da frente, para a cabeça inteira caber na área que o Android mostra (círculo ou quadrado arredondado).
- O crânio antigo continua dentro do jogo (aba Início e recompensa de skin) como `art/ui/ui_icon_skull.png`, para não mudar o visual do jogo.
- O ícone da página da loja (512x512) é enviado à mão na Play Console: `art/ui/ui_app_icon_512.png`.
