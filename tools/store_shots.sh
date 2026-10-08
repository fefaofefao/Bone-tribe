#!/bin/bash
# Gera capturas de tela da loja (1080x1920) a partir do jogo real.
# Uso: tools/store_shots.sh  (precisa de xvfb-run e do Godot no PATH)
set -e
cd "$(dirname "$0")/.."
OUT=store/screenshots
mkdir -p $OUT
shot() { # lang nome atraso [VAR=valor...]
  local lang=$1 name=$2 delay=$3; shift 3
  env LANG=$lang.UTF-8 BT_SHOT=$PWD/$OUT/${lang}_$name.png BT_SHOT_DELAY=$delay "$@" \
    timeout 120 xvfb-run -a -s "-screen 0 1200x2000x24" godot --path . --resolution 1080x1920 >/dev/null 2>&1 || true
}
LANGS=${*:-pt_BR en_US es_ES}
for L in $LANGS; do
  shot $L 1_hub 2.5 BT_SAMPLE_PROFILE=1
  shot $L 2_ossuary 2.5 BT_SAMPLE_PROFILE=1 BT_TAB=ossuary
  shot $L 3_collection 2.5 BT_SAMPLE_PROFILE=1 BT_TAB=collection
  shot $L 4_shop 2.5 BT_SAMPLE_PROFILE=1 BT_TAB=shop
  shot $L 8_card 150 BT_START=run BT_DEMO=1 BT_STORE=1
  # combate, chefe e forma: o tempo de cada momento varia; captura uma sequência
  # (um quadro a cada 2,5 s) em /tmp/bt_seq e copie à mão os melhores como
  # ${L}_5_combat.png, ${L}_6_boss.png e ${L}_7_form.png.
  mkdir -p /tmp/bt_seq
  env LANG=$L.UTF-8 BT_SHOT=/tmp/bt_seq/$L.png BT_SHOT_DELAY=2.5 BT_SHOTS=60 BT_START=run BT_DEMO=1 BT_STORE=1 \
    timeout 200 xvfb-run -a -s "-screen 0 1200x2000x24" godot --path . --resolution 1080x1920 >/dev/null 2>&1 || true
done
