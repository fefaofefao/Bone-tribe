# Bone Tribe — regras para o Claude Code

- Fonte da verdade: `docs/GDD.md`. Decisões em `docs/DECISOES.md`, andamento em `docs/PROGRESSO.md`, publicação em `docs/PUBLICACAO.md`.
- **APKs e AABs são sempre gerados pelo GitHub Actions** (`.github/workflows/android-aab.yml`), nunca localmente. Para testar: faça push e baixe o artefato `BoneTribe-apk` da execução. Para uma versão: crie a tag `vX.Y.Z` e os arquivos saem anexados no Release.
- Só nomes e IDs do GDD. Todo texto visível em `i18n/*.csv` (pt_BR, en_US, es_419) via `tools/i18n.py`; depois de mudar CSV, rode `godot --headless --import`.
- Dados do jogo em `data/*.json`, nada de conteúdo no código.
- Anúncios (plugin Poing AdMob em `addons/admob`) e compras (plugin oficial em `addons/GodotGooglePlayBilling`) são reais no Android e simulados no computador/testes (`scripts/services/`). Os binários Android dos plugins são baixados pelo workflow, não ficam no repositório. IDs do AdMob vêm das variáveis `ADMOB_*` do GitHub (`tools/admob_ids.py`); nunca commitar credenciais.
- Ganchos de teste (`BT_*`) passam por `Dev.env()` e só funcionam em build de depuração.
- Antes de cada commit: `godot --headless --path . tests/TestRunner.tscn` (0 falhas).
