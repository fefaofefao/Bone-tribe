class_name StatsPopup
extends RefCounted
## Tela de Estatísticas: partidas, torres, chefes, monstros, pó, coleção e tempo.
## Os contadores marcados com * começaram a contar na versão que os criou.


static func open(parent: Node) -> void:
	var bg := Widgets.dim_overlay(parent, 0.85)
	var p := Style.panel()
	p.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	p.offset_left = 24
	p.offset_right = -24
	p.offset_top = 70
	p.offset_bottom = -70
	bg.add_child(p)
	var outer := Style.vbox(12)
	p.add_child(outer)
	outer.add_child(Style.title(TranslationServer.translate("stats_title"), 46))
	var scroll := TouchScroll.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(scroll)
	var v := Style.vbox(10)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(v)
	_fill(v)
	var close := Style.button(TranslationServer.translate("btn_back"), "", 72)
	close.pressed.connect(bg.queue_free)
	outer.add_child(close)
	Widgets.pop_in(p)


static func _t(key: String) -> String:
	return String(TranslationServer.translate(key))


static func _fill(v: VBoxContainer) -> void:
	var d: Dictionary = Profile.data
	_head(v, "stats_general")
	_row(v, "stats_runs", Style.num(int(d.get("runs_played", 0))))
	_row(v, "stats_kills", Style.num(int(Profile.stat("kills"))) + " *")
	_row(v, "stats_floors", Style.num(int(Profile.stat("floors"))) + " *")
	_row(v, "stats_deaths", Style.num(int(Profile.stat("deaths"))) + " *")
	_row(v, "stats_dust", Style.num(int(Profile.stat("dust_total"))) + " *")
	_row(v, "stats_crushed", Style.num(int(Profile.stat("bones_crushed"))) + " *")
	_row(v, "stats_time", time_text(Profile.stat("play_time")) + " *")

	_head(v, "stats_towers")
	var cleared := 0
	for n in range(1, Meta.tower_count() + 1):
		if Meta.tower_cleared(n):
			cleared += 1
	_row(v, "stats_towers_cleared", "%d / %d" % [cleared, Meta.tower_count()])
	for n in range(1, Meta.tower_unlocked() + 1):
		var wins := int(d.towers.get("wins", {}).get(str(n), 0))
		var txt := _t("stats_tower_best") % Meta.tower_best(n)
		if wins > 0:
			txt += "  ·  " + _t("stats_tower_wins") % wins
		_row_text(v, _t("tower_label") % [n, _t(String(GameData.tower(n).get("name", "")))], txt)

	_head(v, "stats_bosses")
	var total := 0
	for id in GameData.monster_order:
		if String(GameData.monster(id).get("kind", "")) != "boss":
			continue
		var wins := Profile.boss_wins(id)
		total += wins
		var row := Style.hbox(10)
		var ic := Widgets.icon(GameData.monster_texture_path(id), 56)
		if wins == 0:
			ic.modulate = Color(0, 0, 0, 0.7)
		row.add_child(ic)
		var nm := Style.label(_t(String(GameData.monster(id).name)) if wins > 0 else _t("unknown_item"), 22, Style.C_TEXT if wins > 0 else Style.C_MUTED)
		nm.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(nm)
		row.add_child(Style.nowrap(Style.bold("×%d" % wins, 24, Style.C_CANDLE if wins > 0 else Style.C_MUTED)))
		v.add_child(row)
	_row(v, "stats_bosses_total", Style.num(total))

	_head(v, "stats_collection")
	_row(v, "stats_bones", "%d / %d" % [Meta.discovered_count(), GameData.catalog_bones().size()])
	var forms := 0
	for id in GameData.forms:
		if Profile.is_form_discovered(id):
			forms += 1
	_row(v, "stats_forms", "%d / %d" % [forms, GameData.forms.size()])
	var fams := 0
	for fam in GameData.families:
		if Meta.family_complete(fam):
			fams += 1
	_row(v, "stats_families", "%d / %d" % [fams, GameData.families.size()])
	v.add_child(Style.label(_t("stats_since_note"), 17, Style.C_MUTED))


static func time_text(seconds: float) -> String:
	var m := int(seconds / 60.0)
	return _t("stats_time_fmt") % [m / 60, m % 60]


static func _head(v: VBoxContainer, key: String) -> void:
	var l := Style.bold(_t(key), 28, Style.C_CANDLE)
	v.add_child(l)


static func _row(v: VBoxContainer, key: String, value: String) -> void:
	_row_text(v, _t(key), value)


static func _row_text(v: VBoxContainer, label: String, value: String) -> void:
	var row := Style.hbox(10)
	var l := Style.label(label, 22, Style.C_TEXT)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	var r := Style.bold(value, 22, Style.C_BONE)
	r.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(r)
	v.add_child(row)
