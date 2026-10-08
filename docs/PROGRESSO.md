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

## Em andamento
- Passo 2 — protótipo.

## Problemas
- O ambiente de desenvolvimento não acessa `dl.google.com`, então o AAB só é gerado e validado no GitHub Actions.
