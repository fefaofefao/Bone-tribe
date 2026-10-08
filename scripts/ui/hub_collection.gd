extends HubPage
## Coleção: álbum dos ossos encontrados (completar uma família dá +5%),
## escolha do osso inicial, Bestiário de Formas e o Caçador de Ossos.


func build() -> void:
	_album()
	_bestiary()
	_hunter()


func _album() -> void:
	var box := section("collection_title", tr("collection_sub") % [Meta.discovered_count(), GameData.catalog_bones().size()])
	var start := String(Profile.data.get("starting_bone", ""))
	var tokens := int(Profile.data.get("rare_start_tokens", 0))
	var info := tr("start_bone_current") % (tr(String(GameData.bone(start).name)) if start != "" else tr("start_bone_none"))
	if tokens > 0:
		info += "  ·  " + tr("start_tokens") % tokens
	box.add_child(Style.label(info, 21, Style.C_CANDLE))
	for fam in GameData.families:
		var fd: Dictionary = GameData.families[fam]
		var complete := Meta.family_complete(fam)
		var fc := GameData.family_color(fam)
		var c := card(Color(Style.C_PANEL_2, 0.96), fc if complete else Style.C_EDGE)
		var v := Style.vbox(8)
		c.add_child(v)
		var head := Style.hbox(10)
		var dot := ColorRect.new()
		dot.color = fc
		dot.custom_minimum_size = Vector2(16, 16)
		dot.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		head.add_child(dot)
		head.add_child(Style.nowrap(Style.bold(tr(String(fd.name)), 24, fc)))
		var bonus := Style.label(tr("family_bonus_done") if complete else tr("family_bonus_todo"), 18, Style.C_CANDLE if complete else Style.C_MUTED)
		bonus.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		bonus.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		head.add_child(bonus)
		v.add_child(head)
		var grid := GridContainer.new()
		grid.columns = 3
		grid.add_theme_constant_override("h_separation", 8)
		grid.add_theme_constant_override("v_separation", 8)
		v.add_child(grid)
		for id in Meta.family_bones(fam):
			grid.add_child(_bone_cell(id, start == id))
		box.add_child(c)


func _bone_cell(id: String, is_start: bool) -> Control:
	var b: Dictionary = GameData.bone(id)
	var found := Profile.is_bone_discovered(id)
	var btn := Button.new()
	btn.theme_type_variation = "DarkButton"
	btn.custom_minimum_size = Vector2(200, 168)
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if is_start:
		btn.add_theme_stylebox_override("normal", Style.flat_box(Color(0.3, 0.2, 0.08), Style.C_CANDLE, 16, 3, 8))
	Style.juice(btn)
	var v := Style.vbox(2)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_top = 8
	v.offset_bottom = -6
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	btn.add_child(v)
	var ic := Widgets.icon(GameData.bone_texture_path(id), 92)
	if not found:
		ic.modulate = Color(0, 0, 0, 0.75)
	v.add_child(ic)
	var nm := Style.label(tr(String(b.name)) if found else tr("unknown_item"), 17, Style.rarity_color(String(b.rarity)) if found else Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	nm.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(nm)
	if found:
		btn.pressed.connect(func(): _bone_detail(id))
	else:
		btn.disabled = true
	return btn


func _bone_detail(id: String) -> void:
	var bg := Widgets.dim_overlay(self, 0.8)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var v := Style.vbox(12)
	v.custom_minimum_size = Vector2(520, 0)
	center.add_child(v)
	var bc := Widgets.bone_card({"id": id, "level": 1})
	v.add_child(bc)
	var src := String(GameData.bone(id).get("monster", ""))
	if src != "":
		v.add_child(Style.label(tr("bone_source") % tr(String(GameData.monster(src).name)), 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var start := String(Profile.data.get("starting_bone", ""))
	if start == id:
		var clear := Style.button(tr("start_bone_clear"), "DarkButton", 70)
		clear.pressed.connect(func():
			Profile.data.starting_bone = ""
			Profile.save()
			bg.queue_free()
			rebuild())
		v.add_child(clear)
	elif Meta.can_start_with(id):
		var set_b := Style.button(tr("start_bone_set"), "CandleButton", 76)
		set_b.pressed.connect(func():
			Profile.data.starting_bone = id
			Profile.save()
			Haptics.medium()
			bg.queue_free()
			rebuild())
		v.add_child(set_b)
	else:
		v.add_child(Style.label(tr("start_bone_need_token"), 20, Color("e07a8a"), HORIZONTAL_ALIGNMENT_CENTER))
	var close := Style.button(tr("btn_back"), "", 66)
	close.pressed.connect(bg.queue_free)
	v.add_child(close)
	Widgets.pop_in(v)


func _bestiary() -> void:
	var found := 0
	for id in GameData.form_order:
		if Profile.is_form_discovered(id):
			found += 1
	var box := section("bestiary_title", tr("bestiary_sub") % [found, GameData.form_order.size()])
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	box.add_child(grid)
	for id in GameData.form_order:
		var f: Dictionary = GameData.forms[id]
		var known := Profile.is_form_discovered(id)
		var secret := bool(f.get("secret", false))
		var col := Color(String(f.get("aura", "#ffffff")))
		var c := card(Color(col.darkened(0.82), 0.96) if known else Color(0.08, 0.06, 0.1, 0.96), col if known else Style.C_EDGE)
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		c.custom_minimum_size = Vector2(0, 230)
		var v := Style.vbox(4)
		c.add_child(v)
		var sil := FormSilhouette.new()
		sil.custom_minimum_size = Vector2(0, 110)
		sil.form_id = id
		sil.known = known
		v.add_child(sil)
		var name := tr(String(f.name)) if (known or not secret) else tr("unknown_form")
		v.add_child(Style.bold(name, 19, col if known else Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		if known:
			v.add_child(Style.label(tr(String(f.desc)), 15, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
		elif not secret:
			v.add_child(Style.label(tr("form_hint_family") % tr(String(GameData.families[f.family].name)), 15, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		else:
			v.add_child(Style.label(tr("form_hint_secret"), 15, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		grid.add_child(c)


func _hunter() -> void:
	var stolen := Meta.hunter_stolen()
	var box := section("hunter_title", tr("hunter_sub"))
	var c := card(Color(0.16, 0.06, 0.09, 0.96), Color("80303f"))
	var v := Style.vbox(8)
	c.add_child(v)
	if stolen.is_empty():
		v.add_child(Style.label(tr("hunter_none"), 21, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	else:
		v.add_child(Style.label(tr("hunter_has"), 21, Color("e07a8a")))
		var row := HFlowContainer.new()
		row.add_theme_constant_override("h_separation", 8)
		for inst in stolen:
			var cell := Style.vbox(0)
			cell.add_child(Widgets.icon(GameData.bone_texture_path(String(inst.id)), 72))
			cell.add_child(Style.label(tr(String(GameData.bone(String(inst.id)).name)), 15, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
			cell.custom_minimum_size = Vector2(110, 0)
			row.add_child(cell)
		v.add_child(row)
	box.add_child(c)
