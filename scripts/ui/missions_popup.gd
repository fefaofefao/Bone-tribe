class_name MissionsPopup
extends RefCounted
## Missões diárias e semanais: progresso, tempo até trocar e botão de resgate.


static func open(parent: Node, on_close: Callable = Callable()) -> void:
	Audio.play("ui_open")
	var bg := Widgets.dim_overlay(parent, 0.85)
	var p := Style.panel()
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	p.offset_left = 24
	p.offset_right = -24
	p.offset_top = 90
	p.offset_bottom = -90
	bg.add_child(p)
	var outer := Style.vbox(12)
	p.add_child(outer)
	outer.add_child(Style.title(_t("missions_title"), 46))
	var scroll := TouchScroll.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(scroll)
	var v := Style.vbox(12)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(v)
	var rebuild := [Callable()]
	rebuild[0] = func():
		for c in v.get_children():
			c.queue_free()
		_section(v, "daily", _t("missions_daily") % _time(Backend.seconds_to_next_day()), rebuild[0])
		_section(v, "weekly", _t("missions_weekly") % _time(Missions.seconds_to_next_week()), rebuild[0])
	rebuild[0].call()
	var close := Style.button(_t("btn_back"), "", 72)
	close.pressed.connect(func():
		bg.queue_free()
		if on_close.is_valid():
			on_close.call())
	outer.add_child(close)
	Widgets.pop_in(p)


static func _t(key: String) -> String:
	return String(TranslationServer.translate(key))


static func _time(s: int) -> String:
	var h := int(s / 3600.0)
	if h >= 24:
		return _t("missions_days") % int(h / 24.0)
	return "%dh %02dmin" % [h, int(s / 60.0) % 60]


static func _section(v: VBoxContainer, kind: String, subtitle: String, rebuild: Callable) -> void:
	v.add_child(Style.bold(subtitle, 26, Style.C_CANDLE))
	var arr := Missions.list(kind)
	for i in arr.size():
		var m: Dictionary = arr[i]
		var d := Missions.def(String(m.id))
		var target := int(d.get("target", 1))
		var card := PanelContainer.new()
		var done := Missions.is_done(m)
		card.add_theme_stylebox_override("panel", Style.flat_box(Color(Style.C_PANEL_2, 0.96), Style.C_CANDLE if done and not bool(m.claimed) else Style.C_EDGE, 16, 2, 12))
		var row := Style.hbox(10)
		card.add_child(row)
		var col := Style.vbox(6)
		col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(col)
		col.add_child(Style.label(_t("mission_" + String(m.id)) % target, 22, Style.C_TEXT))
		var bar := ProgressBar.new()
		bar.max_value = target
		bar.value = int(m.progress)
		bar.show_percentage = false
		bar.custom_minimum_size = Vector2(0, 14)
		col.add_child(bar)
		var r := Missions.reward(String(m.id))
		col.add_child(Style.label("%d / %d  ·  +%s %s  +%d %s" % [int(m.progress), target, Style.num(int(r.dust)), _t("dust_short"), int(r.diamonds), _t("diamonds_short")], 18, Style.C_MUTED))
		if bool(m.claimed):
			row.add_child(Style.nowrap(Style.bold(_t("missions_claimed"), 20, Style.C_HEAL)))
		else:
			var b := Style.button(_t("missions_claim"), "CandleButton" if done else "DarkButton", 64)
			b.custom_minimum_size.x = 150
			b.disabled = not done
			var k := kind
			var idx := i
			b.pressed.connect(func():
				var got := Missions.claim(k, idx)
				if not got.is_empty():
					Audio.play("ui_claim")
					Haptics.medium()
					rebuild.call())
			row.add_child(b)
		v.add_child(card)
