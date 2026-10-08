class_name LoginPopup
extends Control
## Calendário de login: 7 dias de boas-vindas e depois o ciclo de 28 dias.
## Conta dias com login (não dias seguidos) pelo horário do servidor.

signal closed

var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := Widgets.dim_overlay(self, 0.82)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(660, 0)
	center.add_child(p)
	var v := Style.vbox(12)
	p.add_child(v)
	var first := Store.calendar_id() == "first7"
	v.add_child(Style.title(tr("login_first7_title" if first else "login_cycle_title"), 46, Style.C_CANDLE))
	v.add_child(Style.label(tr("login_first7_sub" if first else "login_cycle_sub"), 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var days := Store.calendar_days()
	var idx := Store.calendar_index()
	var can := Store.can_claim_login()
	var grid := GridContainer.new()
	grid.columns = 4 if first else 7
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	v.add_child(grid)
	for i in days.size():
		var d: Dictionary = days[i]
		var claimed := i < idx
		var current := i == idx
		var big := first and i == 6
		var cell := PanelContainer.new()
		var edge := Style.C_CANDLE if current and can else (Color(1, 1, 1, 0.08) if not claimed else Color(Style.C_HEAL, 0.6))
		if big and not claimed and not current:
			edge = Color(Style.C_CANDLE, 0.6)
		var fill := Color(0.2, 0.14, 0.1, 0.95) if current else Color(0.12, 0.09, 0.13, 0.95)
		cell.add_theme_stylebox_override("panel", Style.flat_box(fill, edge, 12, 2 if not current else 3, 6))
		var size := Vector2(140 if first else 80, 128 if first else 86)
		cell.custom_minimum_size = size
		var cv := Style.vbox(2)
		cv.alignment = BoxContainer.ALIGNMENT_CENTER
		cell.add_child(cv)
		cv.add_child(Style.bold(tr("login_day") % int(d.day), 16 if not first else 19, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		var icons := Style.hbox(2)
		icons.alignment = BoxContainer.ALIGNMENT_CENTER
		for r in d.rewards:
			var ic := Widgets.icon(_reward_icon(r), 54 if first else 36)
			ic.modulate = RewardPopup.result_color(r)
			if claimed:
				ic.modulate.a = 0.35
			icons.add_child(ic)
		cv.add_child(icons)
		if first:
			cv.add_child(Style.label(_reward_label(d.rewards), 15, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
		grid.add_child(cell)
	var btn := Style.button(tr("login_claim") if can else tr("login_come_back") % Store.format_time(Backend.seconds_to_next_day()), "CandleButton" if can else "DarkButton", 80)
	btn.disabled = not can
	btn.pressed.connect(func():
		var res := Store.claim_login(_rng)
		var pop := RewardPopup.show_on(self, "rewards_title", res)
		await pop.closed
		closed.emit()
		queue_free())
	v.add_child(btn)
	var close := Style.button(tr("btn_back"), "", 64)
	close.pressed.connect(func():
		closed.emit()
		queue_free())
	v.add_child(close)
	Widgets.pop_in(p)


func _reward_icon(r: Dictionary) -> String:
	match String(r.type):
		"relic":
			return "res://art/ui/relic_moon_amulet.png"
		"curiosity", "curiosity_chest_rare":
			return "res://art/ui/cur_torn_map.png"
		"bone_chest", "bone_chest_rare":
			return "res://art/ui/ui_bone_chest.png"
		_:
			return RewardPopup.result_icon(r)


func _reward_label(rewards: Array) -> String:
	var parts := []
	for r in rewards:
		match String(r.type):
			"dust":
				parts.append(tr("reward_dust") % Style.num(int(r.amount)))
			"diamonds":
				parts.append(tr("reward_diamonds") % int(r.amount))
			"companion":
				parts.append(tr(String(GameData.companions[r.id].name)).split(",")[0])
			"skin":
				parts.append(tr(String(GameData.skins[r.id].name)))
			_:
				parts.append(tr("reward_" + String(r.type)))
	return " + ".join(parts)
