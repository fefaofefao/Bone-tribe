#!/bin/bash
# 2ª leva de cenas (pt-BR, 1080x1920)
cd /home/user/Bone-tribe
OUT=$1
printf '[display]\n\nwindow/size/window_width_override=1080\nwindow/size/window_height_override=1920\n' > override.cfg
rec() {
  local name=$1 frames=$2; shift 2
  env LANG=pt_BR.UTF-8 "$@" timeout 2400 xvfb-run -a -s "-screen 0 1200x2000x24" godot --path . --write-movie $OUT/$name.avi --fixed-fps 30 --quit-after $frames > $OUT/$name.log 2>&1
  rm -f ~/.local/share/godot/app_userdata/BoneTribe/run_save.json
}
rec lose 1500 BT_START=run BT_AUTO=1 BT_FLOOR=10
rec riddle 420 BT_START=run BT_AUTO=1 BT_EVENT=event_riddle_teeth
rec cups 420 BT_START=run BT_AUTO=1 BT_EVENT=event_skull_cups
rec arena 1080 BT_START=run BT_AUTO=1 BT_EVENT=event_bone_arena
rec swamp 360 BT_START=run BT_AUTO=1 BT_TOWER=7
rec collection 150 BT_SAMPLE_PROFILE=1 BT_TAB=collection
rec ossuary 150 BT_SAMPLE_PROFILE=1 BT_TAB=ossuary
rm -f override.cfg
echo FIM2
