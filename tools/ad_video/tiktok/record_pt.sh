#!/bin/bash
# grava as cenas em português em 1080x1920 (override.cfg temporário)
cd /home/user/Bone-tribe
OUT=$1
printf '[display]\n\nwindow/size/window_width_override=1080\nwindow/size/window_height_override=1920\n' > override.cfg
rec() { # nome quadros env...
  local name=$1 frames=$2; shift 2
  env LANG=pt_BR.UTF-8 "$@" timeout 2400 xvfb-run -a -s "-screen 0 1200x2000x24" godot --path . --write-movie $OUT/$name.avi --fixed-fps 30 --quit-after $frames > $OUT/$name.log 2>&1
  rm -f ~/.local/share/godot/app_userdata/BoneTribe/run_save.json
}
rec demo 2100 BT_START=run BT_DEMO=1
rec elite 720 BT_START=run BT_AUTO=1 BT_EVENT=event_elite_nest
rec frost 420 BT_START=run BT_AUTO=1 BT_TOWER=4
rec cursed 420 BT_START=run BT_AUTO=1 BT_TOWER=23
rm -f override.cfg
for f in demo elite frost cursed; do ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of compact $OUT/$f.avi; done
echo FIM
