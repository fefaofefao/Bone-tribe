class_name StatusPopup
extends RefCounted
## Status do esqueleto durante a partida: atributos de agora, famílias, forma e
## ossos equipados. O jogo fica pausado enquanto a tela está aberta.

const MAIN_STATS := ["atk", "def", "crit", "crit_mult", "dodge", "speed"]
const EXTRA_STATS := ["lifesteal", "reflect", "regen", "poison_bonus", "fire_bonus", "dust_bonus", "drop_bonus", "trap_avoid", "rare_event_bonus"]


static func _t(key: String) -> String:
	return String(TranslationServer.translate(key))


static func open(parent: Node, state: RunState) -> Control:
	var tree := parent.get_tree()
	var was_paused := tree.paused
	tree.paused = true
	var bg := Widgets.dim_overlay(parent, 0.82)
	bg.process_mode = Node.PROCESS_MODE_ALWAYS
	var p := Style.panel(Style.C_PANEL)
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	p.offset_left = 24
	p.offset_right = -24
	p.offset_top = 90
	p.offset_bottom = -90
	bg.add_child(p)
	var outer := Style.vbox(10)
	p.add_child(outer)
	outer.add_child(Style.title(_t("status_title"), 44))
	var scroll := TouchScroll.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(scroll)
	var v := Style.vbox(8)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(v)
	fill(v, state)
	var close := Style.button(_t("btn_back"), "", 72)
	close.pressed.connect(func():
		tree.paused = was_paused
		bg.queue_free())
	outer.add_child(close)
	Widgets.pop_in(p)
	return bg


static func fill(v: VBoxContainer, state: RunState) -> void:
	var hero := state.make_hero()
	var c := state.compute()
	var s: Dictionary = c.stats
	v.add_child(Style.bold(Body.creature_name(state.equipped), 26, Style.C_BONE, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(_t("hud_level") % state.level + "  ·  " + _t("hud_tower_floor") % [state.tower, maxi(1, state.floor_n), state.total_floors], 19, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	for fid in c.forms:
		v.add_child(Style.bold(_t("status_form") % _t(String(GameData.forms[fid].get("name", fid + "_name"))), 22, Color("d7aaff"), HORIZONTAL_ALIGNMENT_CENTER))

	_head(v, "status_stats")
	_row(v, _t("stat_hp"), "%d / %d" % [int(ceil(state.hp)), int(hero.max_hp)])
	var vals := {"atk": hero.atk, "def": hero.def, "crit": hero.crit, "crit_mult": hero.crit_mult, "dodge": hero.dodge, "speed": hero.speed}
	for k in MAIN_STATS:
		var val := float(vals[k])
		var txt := ""
		match k:
			"crit", "dodge":
				txt = "%d%%" % roundi(val * 100.0)
			"crit_mult":
				txt = "×" + String.num(val, 2).trim_suffix("0").trim_suffix(".")
			_:
				txt = str(roundi(val))
		_row(v, _t("stat_" + k), txt)
	for k in EXTRA_STATS:
		var x := float(s.get(k, 0.0))
		if absf(x) > 0.0001:
			_row(v, _t("stat_" + k), Body.stat_value_text(k, x))

	var fams: Dictionary = c.families
	if not fams.is_empty():
		_head(v, "status_families")
		for fam in fams:
			var fd: Dictionary = GameData.families.get(fam, {})
			var n := int(fams[fam])
			var txt := "%d %s" % [n, _t("status_pieces")]
			_row(v, _t(String(fd.get("name", fam))), txt, Style.C_CANDLE if n >= 2 else Style.C_BONE)

	_head(v, "status_bones")
	for slot_def in GameData.slots():
		var slot := String(slot_def.id)
		if not state.equipped.has(slot):
			continue
		var inst: Dictionary = state.equipped[slot]
		var b := GameData.bone(String(inst.get("id", "")))
		if b.is_empty():
			continue
		var row := Style.hbox(10)
		row.add_child(Widgets.icon(GameData.bone_texture_path(String(b.id)), 44))
		var name := _t(String(b.name))
		var lv := int(inst.get("level", 1))
		if lv > 1:
			name += "  " + _t("hud_level") % lv
		var nl := Style.nowrap(Style.label(name, 20, Style.rarity_color(String(b.get("rarity", "basic")))))
		nl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		nl.clip_text = true
		nl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		row.add_child(nl)
		row.add_child(Style.nowrap(Style.label(_t(slot), 17, Style.C_MUTED)))
		v.add_child(row)


static func _head(v: VBoxContainer, key: String) -> void:
	v.add_child(Style.bold(_t(key), 26, Style.C_CANDLE))


static func _row(v: VBoxContainer, label: String, value: String, color: Color = Style.C_BONE) -> void:
	var box := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(1, 1, 1, 0.045 if v.get_child_count() % 2 == 0 else 0.0)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 5
	sb.content_margin_bottom = 5
	box.add_theme_stylebox_override("panel", sb)
	var row := Style.hbox(12)
	box.add_child(row)
	var l := Style.nowrap(Style.label(label, 21, Style.C_TEXT))
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.clip_text = true
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	row.add_child(l)
	var r := Style.nowrap(Style.bold(value, 21, color))
	r.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(r)
	v.add_child(box)
