#!/bin/bash
# grava as cenas em inglês em 1080x1920 (override.cfg temporário)
cd /home/user/Bone-tribe
OUT=$1
printf '[display]\n\nwindow/size/window_width_override=1080\nwindow/size/window_height_override=1920\n' > override.cfg
rec() { # nome quadros env...
  local name=$1 frames=$2; shift 2
  env LANG=en_US.UTF-8 "$@" timeout 2400 xvfb-run -a -s "-screen 0 1200x2000x24" godot --path . --write-movie $OUT/$name.avi --fixed-fps 30 --quit-after $frames > $OUT/$name.log 2>&1
}
rec demo 2100 BT_START=run BT_DEMO=1
rec lose 1500 BT_START=run BT_AUTO=1 BT_FLOOR=10
rec ossuary 180 BT_SAMPLE_PROFILE=1 BT_TAB=ossuary
rm -f override.cfg
for f in demo lose ossuary; do ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of compact $OUT/$f.avi; done
