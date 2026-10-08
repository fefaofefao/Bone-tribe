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
