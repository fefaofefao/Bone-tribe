# Bone Tribe

Roguelite de eventos para Android em que o **Ossinho** (Bonesy / Huesito) monta o
próprio corpo com os ossos dos monstros que derrota. Documento de design: [docs/GDD.md](docs/GDD.md).

- Motor: Godot 4.7.2 (GDScript), projeto `BoneTribe`
- Pacote Android: `com.bonetribe.game`
- Idiomas: pt_BR, en_US, es_419 (`res://i18n/`)

## Rodar

1. Instale o Godot 4.7.2 estável.
2. Abra a pasta do repositório no Godot (ou `godot --path .`).
3. Pressione F5. A cena inicial é `res://scenes/TitleScreen.tscn`.

Testes automáticos:

```bash
godot --headless --import --path .
godot --headless --path . res://tests/TestRunner.tscn
```

## Gerar o AAB

**No GitHub Actions** (automático a cada push): o workflow `Android AAB` gera
`BoneTribe.aab` como artefato da execução. Para assinar com a chave de upload real,
cadastre os secrets `ANDROID_RELEASE_KEYSTORE_BASE64` (keystore em base64),
`ANDROID_RELEASE_KEYSTORE_USER` (alias) e `ANDROID_RELEASE_KEYSTORE_PASSWORD`.

**Localmente**: instale os templates de exportação 4.7.2, configure o Android SDK e o
JDK 17 em *Editor > Editor Settings > Export > Android*, depois:

```bash
godot --headless --path . --install-android-build-template --export-release "Android" build/BoneTribe.aab
```

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `data/` | Todo o conteúdo do jogo em JSON |
| `i18n/` | Textos visíveis (pt_BR.csv, en_US.csv, es_419.csv) |
| `scenes/` | Cenas Godot |
| `scripts/` | Código (autoload, core, services, scenes, ui) |
| `art/` | Arte (placeholders com o ID no nome do arquivo) |
| `tools/` | Gerador de placeholders e validador de i18n |
| `tests/` | Testes automáticos |
| `docs/` | GDD, decisões e progresso |
