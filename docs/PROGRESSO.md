# Progresso

## Feito

### Passo 1 — Estrutura, i18n e build
- Projeto Godot `BoneTribe` (4.7.2, GDScript), pacote `com.bonetribe.game`, retrato.
- Pastas: `data/`, `i18n/`, `scenes/`, `scripts/` (autoload, core, services, scenes, ui), `art/` (bones, monsters, ui, fx, env, fonts), `tools/`, `tests/`, `docs/`.
- Autoloads: `GameData` (JSON), `Backend` (Firebase simulado: horário do servidor e analytics), `Profile` (salvamento), `Ads` e `Billing` (simulados), `Haptics`, `Style` (tema), `Router` (transições).
- i18n em pt_BR, en_US e es_419 com validador `tools/i18n.py`.
- Gerador de placeholders `tools/gen_art.py` (ícone do app).
- Testes automáticos `tests/TestRunner.tscn`, rodados no CI.
- Workflow `.github/workflows/android-aab.yml` que gera o AAB.

### Passo 2 — Protótipo
- `Ossinho.tscn`: Skeleton2D com os 7 encaixes na ordem do GDD (`slot_skull` ... `slot_tail`) + `slot_extra` e `slot_arm_third`; um Sprite2D por encaixe; animação procedural (respiração, braços, asas, cauda), aura da família, flash de dano, desmontar ao morrer.
- `Run.tscn`: A Cripta Esquecida com 10 eventos (combate 60%, escolha 20%, baú 20%), 3 eventos do GDD + 8 novos, combate automático animado, foco por toque, velocidade x1/x2, Trocar/Triturar, encaixe cinematográfico (câmera, voo do osso, brilho, tremor, vibração), subida de nível (Medula Forte, Fêmur Afiado, Olho Vazio), Rei Rato invocando ratos, Manticora Noturna com tela escura e câmera lenta, morte com reviver por anúncio simulado, fim de partida com dobrar pó.
- `CreatureCard.tscn`: criatura girando, logo, nome automático (ex.: "Lobo-Aranha Venenoso"), desafio, Compartilhar exporta PNG 1080x1920.
- `TitleScreen.tscn`: cripta animada com velas e luz 2D, Jogar, idioma, opções (vibração, qualidade), toque longo de 3 s no logo = modo demonstração.
- Placeholders gerados: 8 ossos, 8 monstros/chefe, cenário, ícones, logo e texturas de efeitos.
- Simulador de equilíbrio `tests/BalanceSim.tscn` e jogador automático `AutoRunner`.

### Passo 3 — Catálogo completo
- 20 ossos (12 comuns, 5 raros, 3 lendários) cobrindo os 7 encaixes + Extra e as 6 famílias, com placeholders desenhados para cada um.
- 6 formas de família (Lobisomem de Osso, Rainha Enxame, Leviatã, Wyrm Ósseo, Colosso, Lich) e 3 secretas (Manticora Noturna, Quimera, Cavaleiro Abissal).
- 14 monstros comuns/raros, 2 lacaios (Rato-Esqueleto, Mímico Faminto), 3 chefes (Rei Rato, Golem Esquecido com escudo de 3 golpes, Dragão Ancião com sopro que dobra sem defesa contra fogo) e a Hidra secreta (andar 31, só para quem vence o Dragão como Wyrm Ósseo).
- Partida completa de 30 andares; drops de chefe (1ª vitória garantida, depois 10%); diamantes por chefe.
- Testes: contagem do catálogo, toda forma alcançável, rejeição, escudo do Golem, sopro do Dragão, drops.
- Modo de depuração `BT_AUTO=1` (escolhas automáticas sem os reforços do modo demonstração).

### Passo 4 — 60 eventos
- 60 eventos em `data/events.json` com textos nos 3 idiomas (pt_BR, en_US, es_419), 15 deles com opção extra ligada ao corpo.
- Ações novas: mercador (comprar ossos), vender osso, altar de troca, melhorar osso (+1 nível), aliado, armadilha, voo sobre o abismo, pagar pó, bônus de atributo.
- 14 cenários de evento e 4 aliados desenhados.
- Testes: 60 eventos, 15 do corpo, todas as ações e textos válidos, 12 partidas automáticas completas sem travar.

### Passo 5 — Meta-progressão
- Hub na tela de título com abas: Início (Jogar, companheiro, osso inicial, aviso do Caçador), Ossuário, Coleção e Loja.
- Ossuário: 4 melhorias permanentes, 3 companheiros (subir de nível, escolher), 4 espaços de relíquias (melhorar, trocar), Baú de ossos (pó ou anúncio, com as chances visíveis) e a estante do Gabinete de Curiosidades (30 itens, 10 conjuntos, estrelas, silhuetas).
- Coleção: álbum dos 20 ossos por família com bônus de família completa, escolha do osso inicial, Bestiário de Formas com silhuetas e os ossos roubados pelo Caçador.
- Na partida: Caçador de Ossos (rouba ao morrer, reaparece como chefe opcional vestindo os ossos roubados), Ossudo traz ossos, Lumi cura, Bigorna forja, curiosidades caem de baús/eventos/chefes, Mapa Rasgado revela o próximo evento.
- Arte: retratos dos 3 companheiros, ícones das 12 relíquias e dos 30 itens, capuz do Caçador, Baú de ossos.
- Correção importante: o tema visual não chegava aos controles dentro de CanvasLayer; agora é mesclado no tema padrão do motor.

### Passo 6 — Calendários, diamantes, loja e Kit 24h
- Calendário de boas-vindas de 7 dias e ciclo diário de 28 dias (pop-up ao abrir o hub e botão no Início), pelo horário do servidor simulado.
- Diamantes: chefes, calendários, anúncio na loja (5, até 3 por dia), compras simuladas (Punhado, Saco, Baú, Cofre).
- Aba Loja: Kit das primeiras 24 horas com cronômetro, ofertas do dia (3 itens com desconto, trocam à meia-noite do servidor), itens por diamantes com chances visíveis, skins com prévia do Ossinho, pacotes de diamantes, Cartão do Coveiro (assinatura de 30 dias), remover anúncios e pacote apoiador.
- Na partida: reviver por anúncio, Reviver extra, reviver grátis da assinatura ou por diamantes; trocar as opções de nível por anúncio (3 por partida, 10 bônus de nível no total).
- Intersticiais limitados entre partidas e oferta de remover anúncios após o 10º.
- Correção: diálogos criados por código agora usam âncoras e margens completas (ficavam desalinhados).

### Passo 7 — Acabamento visual
- Luz 2D dinâmica: velas tremulando, aura da família/forma iluminando o cenário, e flashes de luz em críticos, faíscas fortes, ondas de choque, raios, sopros de fogo e encaixes.
- Partículas: pó de osso, faíscas, poeira a cada passo, brasas subindo no ar, névoa rasteira, lascas de osso quando inimigos se desmontam, brasas no voo do osso até o corpo.
- Câmera: tremor proporcional ao golpe, aproximação no encaixe e na transformação, câmera lenta na transformação e na derrota de chefes, pausa curta (hit-stop) nos críticos.
- Vibração em toques, golpes, encaixes, formas e chefes (desligável nas opções).
- Interface: vinheta cinematográfica, pulso vermelho com vida baixa, resumo do corpo no combate (atributos, sinergias, forma, rejeição), nomes de inimigos agrupados (×2), botões com animação ao toque, transições suaves.
- Qualidade reduzida (opções) desliga a luz dinâmica e as partículas extras para aparelhos fracos.

### Preparação para publicação
- Painel de combate refeito (`scripts/ui/combat_panel.gd`): cartões de inimigo com retrato, vida, estados e contagem da próxima habilidade; atributos, formas e sinergias do Ossinho; registro dos últimos golpes; altura que se ajusta ao conteúdo.
- Workflow gera APK e AAB com versão automática; tag `v*` publica um Release com os dois.
- Ganchos de teste só em build de depuração; créditos e política de privacidade no menu.
- `store/`: textos da ficha (3 idiomas), ícone 512, gráfico de destaque, 24 capturas 1080x1920 (8 por idioma); rascunho de `docs/privacy.html`.
- Checklist completo em `docs/PUBLICACAO.md`.

## Concluído
Todos os 7 passos foram concluídos. Ver "Problemas" e "Próximos passos" abaixo.

## Próximos passos sugeridos
- Substituir os placeholders pela arte final (mesmo nome, tamanho e ponto de encaixe).
- Trocar os provedores simulados por AdMob, Google Play Billing e Firebase reais.
- Plugin Android de compartilhamento e gravação do vídeo de 8 s do Cartão da Criatura.
- Seguir o checklist de `docs/PUBLICACAO.md`.
- Revisão humana dos textos dos 60 eventos nos 3 idiomas (o GDD pede revisão antes de entrar no jogo).
- Teste de equilíbrio com 5 pessoas reais (meta do GDD).

## Problemas
- O ambiente de desenvolvimento não acessa `dl.google.com`, então o AAB só é gerado e validado no GitHub Actions (todos os builds passaram).
- O vídeo de 8 segundos do Cartão da Criatura não foi feito: exige um codificador nativo (plugin Android); o cartão exporta a imagem 1080x1920.
- O compartilhamento nativo também exige plugin; a imagem é salva em `user://cards/`.
- Áudio não foi pedido nos passos e não foi incluído.
