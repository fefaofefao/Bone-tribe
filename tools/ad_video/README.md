# Vídeos de anúncio (10 s)

1. Gravar a demonstração em 1080x1920 com o Movie Maker do Godot (crie um `override.cfg` temporário com
   `window/size/window_width_override=1080` e `window_height_override=1920` na seção `[display]`, e apague depois):
   `BT_START=run BT_DEMO=1 xvfb-run -a godot --path . --write-movie raw.avi --fixed-fps 30 --quit-after 5400`
2. `python3 tools/ad_video/overlays.py . <pasta>/ov` (textos, faixa e tela final com as fontes do jogo)
3. `python3 tools/ad_video/build.py <pasta> audio/sfx` (gera o vertical 9:16 e o horizontal 16:9)

Os tempos dos trechos ficam em `SEGS` no build.py (a demonstração é determinística com --fixed-fps).

## Anúncios em inglês (A 10 s, B 15 s, C 20 s)

`tools/ad_video/en/record.sh <pasta>` grava em inglês a demonstração, a derrota para o Rei Rato (`BT_FLOOR=10`) e o Ossuário;
`overlays_en.py <pasta>/ov` gera os textos; `build_en.py <pasta> audio/sfx [ABC]` monta vertical e horizontal.
