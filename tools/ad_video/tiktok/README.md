# Vídeos do TikTok (pt-BR)

1. Grave as cenas (cria e apaga um `override.cfg` temporário para 1080x1920; nunca commitar o `override.cfg`):
   `bash record_pt.sh <pasta>/rec` e `bash record_pt2.sh <pasta>/rec`
2. Música: `ffmpeg -i musica.mp4 -ac 2 -ar 44100 <pasta>/song.wav` (a música não fica no repositório). `python3 beats.py <pasta>/song.wav` mostra o ritmo; os cortes seguem a grade 0,44 + 0,906·k s.
3. Textos: `python3 overlays_tt.py <pasta>/ov`
4. Montagem: `python3 build_tt.py <pasta> plans/<video>.json saida.mp4`
   - `crop`: world (cenário), boss (luta com chefe), panel (cenário + painel de opções), ui (telas do menu)
   - `freeze`: congela o quadro (perguntas para o público)
