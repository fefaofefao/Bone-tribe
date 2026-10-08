extends HubPage
## Ossuário: melhorias permanentes, companheiros, relíquias, baú de ossos e a
## estante do Gabinete de Curiosidades.

const STAT_ICONS := {"hp": "ui_icon_heart", "atk": "ui_icon_attack", "def": "ui_icon_shield", "drop": "ui_icon_dust"}
var rng := RandomNumberGenerator.new()


func build() -> void:
	rng.randomize()
	_upgrades()
	_companions()
	_relics()
	_cabinet()


# ----------------------------------------------------------------- melhorias

func _upgrades() -> void:
	var box := section("ossuary_upgrades", tr("ossuary_upgrades_sub"))
	for stat in Meta.OSSUARY_STATS:
		var c := card()
		var h := Style.hbox(14)
		c.add_child(h)
		h.add_child(Widgets.icon("res://art/ui/%s.png" % STAT_ICONS[stat], 64))
		var tv := Style.vbox(2)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(Style.bold(tr("ossuary_" + stat) + "  " + tr("hud_level") % Meta.ossuary_level(stat), 26, Style.C_BONE))
		tv.add_child(Style.label(tr("ossuary_" + stat + "_desc") % _stat_value(stat), 20, Style.C_MUTED))
		h.add_child(tv)
		if Meta.ossuary_level(stat) >= Meta.ossuary_max():
			h.add_child(Style.nowrap(Style.bold(tr("max_level"), 22, Style.C_CANDLE)))
		else:
			var cost := Meta.ossuary_cost(stat)
			var b := price_button(cost, "dust", Profile.dust() >= cost)
			var s: String = stat
			b.pressed.connect(func():
				if Meta.ossuary_upgrade(s):
					Haptics.medium()
					toast(tr("upgraded"), Style.C_CANDLE)
					rebuild())
			h.add_child(b)
		box.add_child(c)


func _stat_value(stat: String) -> String:
	var st := Meta.ossuary_stats()
	match stat:
		"hp":
			return "+%d%%" % int(roundf(float(st.hp_pct) * 100))
		"atk":
			return "+%d%%" % int(roundf(float(st.atk_pct) * 100))
		"def":
			return "+%d" % int(st.def)
		_:
			return "+%d%%" % int(roundf(float(st.drop_bonus) * 100))


# -------------------------------------------------------------- companheiros

func _companions() -> void:
	var box := section("companions_title", tr("companions_sub"))
	for id in ["companion_ossudo", "companion_lumi", "companion_bigorna"]:
		var c_data: Dictionary = GameData.companions.get(id, {})
		var unlocked := Meta.companion_unlocked(id)
		var selected: bool = String(Profile.data.get("selected_companion", "")) == id
		var c := card(Color(Style.C_PANEL_2, 0.96), Style.C_CANDLE if selected else Style.C_EDGE)
		var h := Style.hbox(14)
		c.add_child(h)
		var portrait := Widgets.icon("res://art/ui/%s.png" % id, 110)
		if not unlocked:
			portrait.modulate = Color(0, 0, 0, 0.75)
		h.add_child(portrait)
		var tv := Style.vbox(4)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var title := tr(String(c_data.name))
		if unlocked:
			title += "  " + tr("hud_level") % Meta.companion_level(id)
		tv.add_child(Style.bold(title, 26, Style.C_BONE))
		tv.add_child(Style.label(tr(String(c_data.role)), 19, Style.C_CANDLE))
		tv.add_child(Style.label(tr(String(c_data.desc)), 20, Style.C_MUTED))
		if not unlocked:
			tv.add_child(Style.label(tr("companion_lock_" + id), 19, Color("e07a8a")))
		else:
			var row := Style.hbox(10)
			if not selected:
				var sel := Style.button(tr("btn_take_along"), "DarkButton", 56)
				var cid: String = id
				sel.pressed.connect(func():
					Profile.data.selected_companion = cid
					Profile.save()
					Haptics.light()
					rebuild())
				row.add_child(sel)
			else:
				row.add_child(Style.nowrap(Style.bold(tr("companion_selected"), 20, Style.C_CANDLE)))
			if Meta.companion_level(id) < Meta.companion_max(id):
				var cost := Meta.companion_upgrade_cost(id)
				var up := price_button(cost, "dust", Profile.dust() >= cost)
				var cid2: String = id
				up.pressed.connect(func():
					if Meta.companion_upgrade(cid2):
						Haptics.medium()
						toast(tr("upgraded"), Style.C_CANDLE)
						rebuild())
				row.add_child(up)
			tv.add_child(row)
		h.add_child(tv)
		box.add_child(c)


# ----------------------------------------------------------------- relíquias

func _relics() -> void:
	var box := section("relics_title", tr("relics_sub"))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	box.add_child(grid)
	for slot in Meta.RELIC_SLOTS:
		var r := Meta.relic_equipped(slot)
		var c := card()
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var v := Style.vbox(6)
		c.add_child(v)
		v.add_child(Style.bold(tr(slot), 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		if r.is_empty():
			var ic := Widgets.icon("res://art/ui/ui_%s.png" % slot, 72)
			ic.modulate = Color(0, 0, 0, 0.6)
			v.add_child(ic)
			v.add_child(Style.label(tr("relic_empty"), 19, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
		else:
			var rd: Dictionary = GameData.relics[r.id]
			v.add_child(Widgets.icon("res://art/ui/%s.png" % r.id, 72))
			v.add_child(Style.bold(tr(String(rd.name)) + " +" + str(int(r.level) - 1), 21, Style.rarity_color(String(rd.rarity)), HORIZONTAL_ALIGNMENT_CENTER))
			v.add_child(Style.label(tr(String(rd.desc)), 18, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
			if int(r.level) < int(GameData.bal("relics/max_level", 10)):
				var cost := Meta.relic_upgrade_cost(r)
				var up := price_button(cost, "dust", Profile.dust() >= cost)
				var uid := int(r.uid)
				up.pressed.connect(func():
					if Meta.relic_upgrade(uid):
						Haptics.medium()
						rebuild())
				v.add_child(up)
			var others := Meta.relics_owned().filter(func(x): return String(GameData.relics[x.id].slot) == slot and int(x.uid) != int(r.uid))
			if not others.is_empty():
				var sw := Style.button(tr("btn_switch"), "DarkButton", 52)
				var sl: String = slot
				sw.pressed.connect(func(): _switch_relic(sl))
				v.add_child(sw)
		grid.add_child(c)
	# baú de ossos
	var chest := card(Color(0.16, 0.1, 0.2, 0.96), Color("8a5cc0"))
	var h := Style.hbox(14)
	chest.add_child(h)
	h.add_child(Widgets.icon("res://art/ui/ui_bone_chest.png", 110))
	var tv := Style.vbox(6)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(Style.bold(tr("bone_chest_title"), 26, Style.C_BONE))
	tv.add_child(Style.label(_odds_text(), 18, Style.C_MUTED))
	var row := Style.hbox(10)
	var cost2 := int(GameData.bal("relics/chest/dust_cost", 300))
	var buy := price_button(cost2, "dust", Profile.dust() >= cost2)
	buy.pressed.connect(func():
		if Profile.spend_dust(cost2, "bone_chest"):
			_open_chest())
	row.add_child(buy)
	var left := _chest_ads_left()
	var ad := Style.button(tr("btn_chest_ad") % left, "DarkButton", 60)
	ad.disabled = left <= 0
	ad.pressed.connect(func():
		ad.disabled = true
		if await Ads.show_rewarded("extra_chest"):
			var shop: Dictionary = Profile.data.shop
			var day := Backend.server_day()
			if int(shop.chest_ad_day) != day:
				shop.chest_ad_day = day
				shop.chest_ad_count = 0
			shop.chest_ad_count = int(shop.chest_ad_count) + 1
			Profile.save()
			_open_chest())
	row.add_child(ad)
	tv.add_child(row)
	h.add_child(tv)
	box.add_child(chest)


func _chest_ads_left() -> int:
	var shop: Dictionary = Profile.data.shop
	var lim := int(GameData.bal("relics/chest/ad_per_day", 3))
	if int(shop.get("chest_ad_day", -1)) != Backend.server_day():
		return lim
	return maxi(0, lim - int(shop.get("chest_ad_count", 0)))


func _odds_text() -> String:
	var odds := Meta.chest_odds()
	var total := 0.0
	for k in odds:
		total += float(odds[k])
	var parts := []
	for k in odds:
		parts.append("%s %d%%" % [tr("odds_" + k), int(roundf(float(odds[k]) / total * 100))])
	return tr("odds_title") + " " + ", ".join(parts)


func _open_chest() -> void:
	var res := Meta.open_bone_chest(rng)
	Haptics.heavy()
	var bg := Widgets.dim_overlay(self, 0.8)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(560, 0)
	center.add_child(p)
	var v := Style.vbox(14)
	p.add_child(v)
	v.add_child(Style.title(tr("bone_chest_opened"), 46, Style.C_CANDLE))
	var icon := Widgets.icon("res://art/ui/%s.png" % res.id, 150)
	v.add_child(icon)
	var name_key := ""
	var color := Style.C_BONE
	if res.type == "relic":
		name_key = String(GameData.relics[res.id].name)
		color = Style.rarity_color(String(GameData.relics[res.id].rarity))
		v.add_child(Style.bold(tr(name_key), 30, color, HORIZONTAL_ALIGNMENT_CENTER))
		v.add_child(Style.label(tr(String(GameData.relics[res.id].desc)), 22, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	else:
		name_key = String(GameData.curiosities[res.id].name)
		v.add_child(Style.bold(tr(name_key), 30, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
		v.add_child(Style.label(tr("stars_n") % int(res.stars), 22, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
	var ok := Style.button(tr("btn_continue"), "", 72)
	ok.pressed.connect(func():
		bg.queue_free()
		rebuild())
	v.add_child(ok)
	Widgets.pop_in(p)
	icon.pivot_offset = Vector2(75, 75)
	icon.scale = Vector2(0.2, 0.2)
	var tw := icon.create_tween()
	tw.tween_property(icon, "scale", Vector2.ONE, 0.5).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)


func _switch_relic(slot: String) -> void:
	var bg := Widgets.dim_overlay(self, 0.8)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(560, 0)
	center.add_child(p)
	var v := Style.vbox(12)
	p.add_child(v)
	v.add_child(Style.title(tr(slot), 42))
	for r in Meta.relics_owned():
		if String(GameData.relics[r.id].slot) != slot:
			continue
		var rd: Dictionary = GameData.relics[r.id]
		var b := Style.button(tr(String(rd.name)) + " +" + str(int(r.level) - 1), "DarkButton", 70)
		b.icon = load("res://art/ui/%s.png" % r.id)
		b.expand_icon = true
		b.add_theme_constant_override("icon_max_width", 50)
		var uid := int(r.uid)
		b.pressed.connect(func():
			Meta.equip_relic(uid)
			bg.queue_free()
			rebuild())
		v.add_child(b)
	var close := Style.button(tr("btn_back"), "", 64)
	close.pressed.connect(bg.queue_free)
	v.add_child(close)
	Widgets.pop_in(p)


# ------------------------------------------------------------------ gabinete

func _cabinet() -> void:
	var owned := 0
	for id in GameData.curiosities:
		if Meta.curiosity_stars(id) > 0:
			owned += 1
	var box := section("cabinet_title", tr("cabinet_sub") % [owned, GameData.curiosities.size()])
	for sid in GameData.curiosity_sets:
		var sd: Dictionary = GameData.curiosity_sets[sid]
		var complete := Meta.set_complete(sid)
		var shelf := card(Color(0.17, 0.12, 0.1, 0.96), Style.C_CANDLE if complete else Color("5a4030"))
		var v := Style.vbox(8)
		shelf.add_child(v)
		v.add_child(Style.bold(tr(String(sd.name)) + ("  · " + tr("set_complete") if complete else ""), 22, Style.C_CANDLE if complete else Style.C_BONE))
		v.add_child(Style.label(tr(String(sd.desc)), 18, Style.C_MUTED))
		var row := Style.hbox(10)
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		for it in sd.items:
			var cell := Style.vbox(2)
			cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var stars := Meta.curiosity_stars(it)
			var ic := Widgets.icon("res://art/ui/%s.png" % it, 76)
			if stars <= 0:
				ic.modulate = Color(0, 0, 0, 0.7)
			cell.add_child(ic)
			var nm := tr(String(GameData.curiosities[it].name)) if stars > 0 else tr("unknown_item")
			cell.add_child(Style.label(nm, 17, Style.C_TEXT if stars > 0 else Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
			if stars > 0:
				cell.add_child(Widgets.stars(stars, 5, 18))
				cell.add_child(Style.label(tr(String(GameData.curiosities[it].desc)), 15, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
			row.add_child(cell)
		v.add_child(row)
		# prateleira
		var plank := ColorRect.new()
		plank.color = Color("5a3a24")
		plank.custom_minimum_size = Vector2(0, 8)
		v.add_child(plank)
		box.add_child(shelf)
