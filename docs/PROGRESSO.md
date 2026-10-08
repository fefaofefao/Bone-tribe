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

## Em andamento
- Passo 3 — catálogo completo.

## Problemas
- O ambiente de desenvolvimento não acessa `dl.google.com`, então o AAB só é gerado e validado no GitHub Actions.
