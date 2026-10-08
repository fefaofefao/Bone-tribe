class_name CombatPanel
extends VBoxContainer
## Painel de combate: cartões dos inimigos (retrato, vida, estados e próxima
## habilidade), o corpo do Ossinho (atributos, sinergias, habilidades com contagem
## de turnos) e um registro das últimas ações. Tocar num cartão foca o inimigo.

signal focus_requested(f: Fighter)

const LOG_LINES := 4

var combat: Combat
var state: RunState
var _turn_badge: Label
var _cards_box: HFlowContainer
var _cards: Dictionary = {}   # Fighter -> {panel, bar, hp, status, next}
var _hero_abilities: VBoxContainer
var _log_box: VBoxContainer
var _log: Array = []


func setup(p_combat: Combat, p_state: RunState, is_boss: bool) -> void:
	combat = p_combat
	state = p_state
	add_theme_constant_override("separation", 10)
	# cabeçalho
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 10)
	head.add_child(Widgets.icon("res://art/ui/ui_event_%s.png" % ("boss" if is_boss else "combat"), 40))
	var t := Style.nowrap(Style.bold(tr("event_type_boss" if is_boss else "event_type_combat"), 24, Style.C_CANDLE))
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head.add_child(t)
	var badge := PanelContainer.new()
	badge.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0.4), Color(1, 1, 1, 0.12), 14, 1, 6))
	_turn_badge = Style.nowrap(Style.bold("", 20, Style.C_BONE))
	badge.add_child(_turn_badge)
	head.add_child(badge)
	add_child(head)
	# inimigos
	_cards_box = HFlowContainer.new()
	_cards_box.add_theme_constant_override("h_separation", 8)
	_cards_box.add_theme_constant_override("v_separation", 8)
	add_child(_cards_box)
	# Ossinho
	add_child(_hero_section())
	# registro
	var log_panel := PanelContainer.new()
	log_panel.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0.32), Color(1, 1, 1, 0.05), 12, 1, 8))
	log_panel.custom_minimum_size = Vector2(0, 4 * 22 + 16)
	_log_box = VBoxContainer.new()
	_log_box.add_theme_constant_override("separation", 2)
	log_panel.add_child(_log_box)
	add_child(log_panel)
	refresh()


# ------------------------------------------------------------ inimigos

func _ensure_cards() -> void:
	var alive := combat.alive_enemies()
	for f in _cards.keys():
		if not alive.has(f):
			var c: Dictionary = _cards[f]
			if is_instance_valid(c.panel):
				var tw: Tween = c.panel.create_tween()
				tw.tween_property(c.panel, "modulate:a", 0.0, 0.2)
				tw.tween_callback(c.panel.queue_free)
			_cards.erase(f)
	for f in alive:
		if not _cards.has(f):
			_cards[f] = _enemy_card(f)


func _enemy_card(f: Fighter) -> Dictionary:
	var panel := Button.new()
	panel.theme_type_variation = "DarkButton"
	var w := 210.0 if combat.enemies.size() > 2 else 300.0
	panel.custom_minimum_size = Vector2(w, 118)
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.add_theme_stylebox_override("normal", Style.flat_box(Color(0.13, 0.09, 0.12, 0.96), Color(1, 1, 1, 0.1), 14, 2, 8))
	panel.add_theme_stylebox_override("hover", Style.flat_box(Color(0.16, 0.11, 0.14, 0.96), Color(1, 1, 1, 0.2), 14, 2, 8))
	panel.add_theme_stylebox_override("pressed", Style.flat_box(Color(0.2, 0.14, 0.1, 0.96), Style.C_CANDLE, 14, 2, 8))
	panel.pressed.connect(func(): focus_requested.emit(f))
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 8)
	h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	h.offset_left = 8
	h.offset_right = -8
	h.offset_top = 6
	h.offset_bottom = -6
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(h)
	var portrait := Widgets.icon(GameData.monster_texture_path(f.id) if f.id != "boss_bone_hunter" else "res://art/monsters/boss_bone_hunter_hood.png", 72)
	h.add_child(portrait)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 3)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(v)
	var name_l := Style.nowrap(Style.bold(tr(f.name_key), 18, Style.C_DANGER.lightened(0.3) if f.is_boss else Style.C_TEXT))
	name_l.clip_text = true
	name_l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	name_l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(name_l)
	var bar: Control = preload("res://scripts/ui/hud_bar.gd").new()
	bar.custom_minimum_size = Vector2(0, 20)
	bar.fill_color = Color("b23a8f") if f.is_boss else Style.C_DANGER
	bar.font_size = 15
	v.add_child(bar)
	var status := HBoxContainer.new()
	status.add_theme_constant_override("separation", 4)
	status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(status)
	var next := Style.label("", 15, Style.C_MUTED)
	next.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(next)
	_cards_box.add_child(panel)
	Widgets.pop_in(panel)
	return {"panel": panel, "bar": bar, "status": status, "next": next}


func _ability_text(f: Fighter) -> String:
	var parts := []
	for a in f.effects:
		var every := int(a.get("every", 0))
		var tail := ""
		if every > 0:
			tail = " " + tr("next_in") % _turns_until(every)
		match String(a.get("type", "")):
			"summon":
				parts.append(tr("ability_summon") + tail)
			"breath":
				parts.append(tr("ability_breath") + tail)
			"special":
				parts.append(tr("special_" + String(a.get("name", ""))).trim_suffix("!") + tail)
			"multi_attack":
				parts.append(tr("ability_multi") % int(a.get("hits", 2)))
			"guard":
				parts.append(tr("ability_guard") % int(a.get("hits", 3)))
			"on_hit_status":
				parts.append(tr("ability_" + String(a.get("status", ""))))
	if f.regen > 0.0:
		parts.append(tr("ability_regen"))
	if f.lifesteal > 0.0:
		parts.append(tr("ability_lifesteal"))
	if f.def > 0.0:
		parts.append(tr("ability_def") % int(f.def))
	return " · ".join(parts)


func _turns_until(every: int) -> int:
	var t := combat.turn
	var r := every - (t % every)
	return r if r > 0 else every


# --------------------------------------------------------------- Ossinho

func _hero_section() -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(0.1, 0.09, 0.12, 0.9), Color(Style.C_BONE, 0.18), 14, 2, 10))
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	p.add_child(v)
	var hero := combat.hero
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	var who := Style.nowrap(Style.bold(tr("hero_name"), 20, Style.C_BONE))
	row.add_child(who)
	for item in [["ui_icon_attack", str(int(roundf(hero.atk)))], ["ui_icon_shield", str(int(roundf(hero.def)))],
			["ui_levelup_empty_eye", "%d%%" % int(roundf(hero.crit * 100))], ["ui_levelup_quick_knees", "%d%%" % int(roundf(hero.dodge * 100))]]:
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 3)
		h.size_flags_horizontal = Control.SIZE_EXPAND | Control.SIZE_SHRINK_END
		h.add_child(Widgets.icon("res://art/ui/%s.png" % item[0], 28))
		h.add_child(Style.nowrap(Style.bold(item[1], 19, Style.C_TEXT)))
		row.add_child(h)
	v.add_child(row)
	var chips := HFlowContainer.new()
	chips.add_theme_constant_override("h_separation", 6)
	chips.add_theme_constant_override("v_separation", 6)
	var c := state.compute()
	for fid in c.forms:
		chips.add_child(_chip(tr(String(GameData.forms[fid].name)), Color(String(GameData.forms[fid].get("aura", "#ffffff")))))
	for fam in c.families:
		if int(c.families[fam]) >= 2:
			chips.add_child(_chip("%s ×%d" % [tr(String(GameData.families[fam].name)), int(c.families[fam])], GameData.family_color(fam)))
	if c.rejection:
		chips.add_child(_chip(tr("rejection_chip"), Style.C_DANGER))
	for al in combat.allies:
		chips.add_child(_chip(tr(al.name_key), Style.C_HEAL))
	if chips.get_child_count() > 0:
		v.add_child(chips)
	_hero_abilities = VBoxContainer.new()
	_hero_abilities.add_theme_constant_override("separation", 1)
	v.add_child(_hero_abilities)
	return p


func _chip(text: String, color: Color) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(color, 0.15), Color(color, 0.7), 12, 2, 5))
	p.add_child(Style.nowrap(Style.bold(text, 16, color)))
	return p


func _refresh_hero_abilities() -> void:
	for ch in _hero_abilities.get_children():
		ch.queue_free()
	var lines := []
	for e in combat.hero.effects_of("periodic"):
		lines.append(tr("special_" + String(e.get("action", ""))).trim_suffix("!") + " " + tr("next_in") % _turns_until(int(e.get("every", 3))))
	if int(combat.companion.get("heal_every", 0)) > 0:
		lines.append(tr("ability_companion_heal") + " " + tr("next_in") % _turns_until(int(combat.companion.heal_every)))
	if combat.hero.shield > 0.0:
		lines.append(tr("ability_shield") % int(combat.hero.shield))
	for l in lines:
		_hero_abilities.add_child(Style.label(l, 16, Style.C_CANDLE))


# ------------------------------------------------------------- atualizar

func refresh() -> void:
	if combat == null:
		return
	_turn_badge.text = tr("combat_turn") % maxi(1, combat.turn)
	_ensure_cards()
	for f in _cards:
		var c: Dictionary = _cards[f]
		c.bar.set_value(f.hp, f.max_hp, "%d / %d" % [int(ceil(maxf(f.hp, 0))), int(f.max_hp)])
		var st: HBoxContainer = c.status
		for ch in st.get_children():
			ch.queue_free()
		if f.guard_max > 0:
			st.add_child(_pip(tr("guard_up") if f.guard_broken_turns <= 0 else tr("guard_down"), Color(0.5, 0.7, 1.0)))
		if f.statuses.has("bleed"):
			st.add_child(_pip(tr("status_bleed"), Color("d8343f")))
		if f.statuses.has("poison") or f.statuses.has("stack_poison"):
			var n := int(f.statuses.get("stack_poison", {}).get("stacks", 0))
			st.add_child(_pip(tr("status_poison") + (" ×%d" % n if n > 1 else ""), Color("8fe04a")))
		if f.stunned():
			st.add_child(_pip(tr("status_stun"), Color("ffd84a")))
		c.next.text = _ability_text(f)
		var focused: bool = combat.focus == f
		(c.panel as Button).add_theme_stylebox_override("normal", Style.flat_box(Color(0.13, 0.09, 0.12, 0.96), Style.C_CANDLE if focused else Color(1, 1, 1, 0.1), 14, 3 if focused else 2, 8))
	_refresh_hero_abilities()


func _pip(text: String, color: Color) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(color, 0.2), Color(color, 0.8), 8, 1, 3))
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var l := Style.nowrap(Style.bold(text, 13, color.lightened(0.3)))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_child(l)
	return p


## Acrescenta uma linha ao registro (as mais novas em cima).
func log_line(text: String, color: Color = Style.C_TEXT) -> void:
	if _log_box == null:
		return
	var l := Style.label(text, 17, color)
	l.autowrap_mode = TextServer.AUTOWRAP_OFF
	l.clip_text = true
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_log_box.add_child(l)
	_log_box.move_child(l, 0)
	_log.push_front(l)
	while _log.size() > LOG_LINES:
		var old: Label = _log.pop_back()
		old.queue_free()
	for i in _log.size():
		(_log[i] as Label).modulate.a = 1.0 - i * 0.2
