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
- Arte placeholder em `tools/art_extra_head.py`, `tools/art_extra_limbs.py` e `tools/art_extra_back.py`, chamada por `tools/gen_art.py bones`.
