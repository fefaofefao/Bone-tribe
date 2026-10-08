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

**APK de teste**: o mesmo workflow também gera `BoneTribe.apk` (artefato `BoneTribe-apk`),
instalável direto no celular (ative "instalar apps de fontes desconhecidas").

**Versões**: crie a tag `vX.Y.Z` e o workflow anexa APK e AAB ao Release da tag.
Os APKs são sempre gerados pelo GitHub Actions, não localmente. O passo a passo da
publicação na Google Play está em [docs/PUBLICACAO.md](docs/PUBLICACAO.md).

## Modo demonstração

Na tela de título, segure o logo **Bone Tribe** por 3 segundos. O Ossinho joga sozinho,
preenche todos os encaixes e forma a Manticora Noturna (bom para gravar vídeos).

## Como adicionar um osso novo

1. Acrescente uma entrada em `data/bones.json`, por exemplo:

   ```json
   {"id": "bone_skull_owl", "slot": "slot_skull", "family": "family_shadow", "rarity": "common",
    "monster": "monster_crypt_wolf", "name": "bone_skull_owl_name", "desc": "bone_skull_owl_desc",
    "name_part": "bone_skull_owl_part", "adjective": "bone_skull_owl_adj",
    "stats": {"crit": 0.10}, "effects": []}
   ```

   - `slot` (ou `slots` para braços), `family` e `rarity` usam os IDs existentes.
   - `stats` soma atributos (`hp`, `atk`, `def`, `crit`, `dodge`, `speed`, `lifesteal`,
     `reflect`, `regen`, `dust_bonus`, `shield_start`...).
   - `effects` usa os efeitos de combate prontos (`on_hit_status`, `multi_hit`,
     `periodic`, `first_strike`, `extra_slot`...). Veja exemplos no próprio arquivo.
2. Os campos `name`, `desc`, `name_part` e `adjective` são chaves de tradução: acrescente
   as quatro linhas nos três arquivos de `i18n/` (ou use `python3 tools/i18n.py upsert`).
3. Para o monstro soltar o osso, coloque o ID em `drops` no `data/monsters.json`.
4. Rode `python3 tools/gen_art.py bones`: ossos sem desenho próprio ganham um placeholder
   automático `art/bones/<id>.png` no tamanho e no ponto de encaixe do slot
   (`data/skeleton.json`). A arte final substitui esse PNG sem mexer em código.
5. Rode os testes: eles conferem traduções, encaixes, monstros e arte de todos os ossos.

## Serviços simulados

Anúncios (`Ads`), compras (`Billing`) e Firebase (`Backend`: horário do servidor e analytics)
têm interface e lógica prontas com provedores simulados em `scripts/services/`. Para o
lançamento, escreva provedores reais com os mesmos métodos. Nenhum SDK ou credencial está no projeto.

## Ferramentas

| Comando | O que faz |
| --- | --- |
| `godot --headless --path . res://tests/TestRunner.tscn` | Testes automáticos (rodam no CI) |
| `godot --headless --path . res://tests/BalanceSim.tscn -- players=60 runs=4` | Simula jogadores novos para calibrar o equilíbrio |
| `python3 tools/gen_art.py all` | Regera todos os placeholders de arte |
| `python3 tools/preview_body.py saida.png slot_skull=bone_skull_wolf ...` | Prévia do Ossinho montado |
| `python3 tools/i18n.py check` | Valida os três arquivos de tradução |

Variáveis de depuração (só desenvolvimento): `BT_START=run` abre a partida, `BT_DEMO=1` modo
demonstração, `BT_AUTO=1` escolhas automáticas, `BT_TAB=ossuary|collection|shop` abre uma aba,
`BT_SAMPLE_PROFILE=1` perfil de exemplo, `BT_SHOT=arquivo.png` captura a tela.

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
