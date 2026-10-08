extends Node
## Uma partida: andares de eventos, combate automático animado, ossos que
## voam até o corpo, subidas de nível, formas, morte e fim de partida.

signal option_chosen(index: int)
signal dialog_closed(value: Variant)

const HERO_POS := Vector2(200, 742)
const ENEMY_BASE_Y := 742.0

var state: RunState
var world: Node2D
var stage: CryptStage
var hero_view: OssinhoView
var fx: FxLayer
var cam: ShakeCamera
var ui: CanvasLayer
var hud: Control
var panel: PanelContainer
var panel_box: VBoxContainer
var overlay_root: Control
var enemy_views: Dictionary = {}   # Fighter -> MonsterView
var combat: Combat
var speed := 1.0
var demo := false
## Escolhas automáticas (modo demonstração ou depuração com BT_AUTO=1).
var autoplay := false
var _demo_plan: Array = []
var _banner: Label
var _turn_label: Label
var _next_icon: TextureRect

# HUD
var hp_bar: Control
var xp_bar: Control
var dust_label: Label
var level_label: Label
var floor_label: Label
var floor_dots: HBoxContainer
var speed_btn: Button


func _ready() -> void:
	var p := Router.params
	demo = bool(p.get("demo", false))
	autoplay = demo or Dev.env("BT_AUTO") == "1"
	var start_bone := "" if demo else Meta.take_start_bone()
	state = RunState.new({"demo": demo, "companion": "" if demo else String(Profile.data.get("selected_companion", "")), "start_bone": start_bone})
	if start_bone != "":
		Profile.discover_bone(start_bone)
	speed = 2.0 if Profile.setting("fast_combat") else 1.0
	if demo:
		speed = 1.6
		_demo_plan = GameData.bal("demo/plan", []).duplicate()
	_build_world()
	_build_ui()
	_refresh_hud()
	Backend.log_event("run_start", {"demo": demo, "runs": Profile.data.runs_played})
	_run_loop()


# ================================================================ construção

func _build_world() -> void:
	world = Node2D.new()
	add_child(world)
	stage = CryptStage.new()
	world.add_child(stage)
	hero_view = preload("res://scenes/Ossinho.tscn").instantiate()
	hero_view.position = HERO_POS
	world.add_child(hero_view)
	hero_view.set_equipped(state.equipped)
	if not demo:
		hero_view.set_skin(Store.equipped_skin())
	_build_companion_view()
	fx = FxLayer.new()
	world.add_child(fx)
	cam = ShakeCamera.new()
	world.add_child(cam)


var companion_view: Sprite2D


func _build_companion_view() -> void:
	if state.companion_id == "":
		return
	var path := "res://art/ui/%s.png" % state.companion_id
	if not ResourceLoader.exists(path):
		return
	companion_view = Sprite2D.new()
	companion_view.texture = load(path)
	companion_view.centered = false
	companion_view.offset = Vector2(-130, -270)
	companion_view.scale = Vector2.ONE * 0.42
	companion_view.position = Vector2(70, 772) if state.companion_id != "companion_lumi" else Vector2(92, 640)
	world.add_child(companion_view)
	var tw := companion_view.create_tween().set_loops()
	var dy := 10.0 if state.companion_id == "companion_lumi" else 3.0
	tw.tween_property(companion_view, "position:y", companion_view.position.y - dy, 0.9).set_trans(Tween.TRANS_SINE)
	tw.tween_property(companion_view, "position:y", companion_view.position.y, 0.9).set_trans(Tween.TRANS_SINE)


func _companion_pop(text: String) -> void:
	var pos := companion_view.global_position + Vector2(0, -120) if companion_view else hero_view.body_center_global()
	fx.float_text(pos, text, Style.C_HEAL, 24)
	if companion_view:
		var tw := create_tween()
		tw.tween_property(companion_view, "scale", Vector2.ONE * 0.5, 0.1)
		tw.tween_property(companion_view, "scale", Vector2.ONE * 0.42, 0.2).set_trans(Tween.TRANS_BACK)


var _vignette: TextureRect
var _danger: TextureRect


## O painel inferior cresce e encolhe conforme o conteúdo (sem sobras vazias).
func _fit_panel() -> void:
	if panel == null or panel_box == null:
		return
	var want := clampf(panel_box.get_combined_minimum_size().y + 48.0, PANEL_MIN_H, PANEL_MAX_H)
	var cur := -panel.offset_top - 14.0
	if absf(cur - want) > 0.5:
		panel.offset_top = -(lerpf(cur, want, 0.25) + 14.0)


## Vinheta cinematográfica e pulso vermelho quando a vida está baixa.
func _build_vignette() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 5
	add_child(layer)
	for i in 2:
		var g := Gradient.new()
		g.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
		var edge := Color(0.02, 0.0, 0.03, 0.85) if i == 0 else Color(0.75, 0.05, 0.08, 0.9)
		g.colors = PackedColorArray([Color(edge, 0.0), Color(edge, 0.0), edge])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.45)
		t.fill_to = Vector2(1.05, 1.05)
		t.width = 256
		t.height = 456
		var r := TextureRect.new()
		r.texture = t
		r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		r.stretch_mode = TextureRect.STRETCH_SCALE
		r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.add_child(r)
		if i == 0:
			_vignette = r
		else:
			_danger = r
			r.modulate.a = 0.0


const PANEL_MIN_H := 250.0
const PANEL_MAX_H := 560.0


func _process(_delta: float) -> void:
	_fit_panel()
	if _danger == null or state == null:
		return
	var low := state.max_hp > 0.0 and state.hp / state.max_hp < 0.3 and not state.dead
	var target := (0.45 + 0.35 * sin(Time.get_ticks_msec() / 220.0)) if low else 0.0
	_danger.modulate.a = lerpf(_danger.modulate.a, target, 0.15)


func _build_ui() -> void:
	_build_vignette()
	ui = CanvasLayer.new()
	ui.layer = 10
	add_child(ui)
	hud = Control.new()
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(hud)

	# --- barra superior
	var top := Style.panel(Color(0.07, 0.05, 0.08, 0.82), Color(0, 0, 0, 0.6), 0)
	top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top.offset_bottom = 118
	hud.add_child(top)
	var tv := Style.vbox(8)
	top.add_child(tv)
	var row1 := Style.hbox(10)
	tv.add_child(row1)
	row1.add_child(Widgets.icon("res://art/ui/ui_icon_heart.png", 40))
	hp_bar = preload("res://scripts/ui/hud_bar.gd").new()
	hp_bar.custom_minimum_size = Vector2(0, 34)
	hp_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hp_bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row1.add_child(hp_bar)
	row1.add_child(Widgets.icon("res://art/ui/ui_icon_dust.png", 40))
	dust_label = Style.bold("0", 28, Style.C_DUST)
	dust_label.custom_minimum_size = Vector2(70, 0)
	dust_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	row1.add_child(dust_label)
	var row2 := Style.hbox(10)
	tv.add_child(row2)
	level_label = Style.bold("", 22, Style.C_XP)
	level_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	row2.add_child(level_label)
	xp_bar = preload("res://scripts/ui/hud_bar.gd").new()
	xp_bar.fill_color = Style.C_XP
	xp_bar.custom_minimum_size = Vector2(120, 16)
	xp_bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row2.add_child(xp_bar)
	floor_label = Style.bold("", 22, Style.C_BONE)
	floor_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	floor_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	floor_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row2.add_child(floor_label)
	floor_dots = Style.hbox(4)
	row2.add_child(floor_dots)
	_next_icon = Widgets.icon("res://art/ui/ui_event_combat.png", 26)
	_next_icon.visible = false
	row2.add_child(_next_icon)

	if demo and Dev.env("BT_STORE") != "1":
		var dl := Style.bold(tr("demo_mode"), 18, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER)
		dl.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
		dl.offset_top = 124
		dl.offset_bottom = 150
		hud.add_child(dl)

	# --- painel inferior de eventos
	panel = Style.panel(Color(Style.C_PANEL, 0.95), Style.C_EDGE, 26)
	panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_top = -(PANEL_MIN_H + 14.0)
	panel.offset_left = 14
	panel.offset_right = -14
	panel.offset_bottom = -14
	hud.add_child(panel)
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(scroll)
	panel_box = Style.vbox(14)
	panel_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(panel_box)

	speed_btn = Style.button("", "DarkButton", 56)
	speed_btn.custom_minimum_size = Vector2(96, 56)
	speed_btn.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	speed_btn.position = Vector2(720 - 112, 132)
	speed_btn.pressed.connect(_toggle_speed)
	hud.add_child(speed_btn)
	_update_speed_btn()

	overlay_root = Control.new()
	overlay_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(overlay_root)

	_banner = Style.title("", 64, Style.C_CANDLE)
	_banner.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_banner.offset_left = -340
	_banner.offset_right = 340
	_banner.offset_top = -240
	_banner.offset_bottom = -100
	_banner.modulate.a = 0.0
	_banner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(_banner)


func _toggle_speed() -> void:
	speed = 1.0 if speed > 1.0 else 2.0
	Profile.set_setting("fast_combat", speed > 1.0)
	_update_speed_btn()


func _update_speed_btn() -> void:
	speed_btn.text = "x%d" % int(round(speed)) if speed >= 1.5 else "x1"


func _refresh_hud() -> void:
	hp_bar.set_value(state.hp, state.max_hp, "%d / %d" % [int(ceil(state.hp)), int(state.max_hp)])
	xp_bar.set_value(state.xp, RunState.xp_needed(state.level))
	level_label.text = tr("hud_level") % state.level
	dust_label.text = Style.num(state.dust)
	floor_label.text = tr("hud_floor") % [maxi(1, state.floor_n), state.total_floors]
	for c in floor_dots.get_children():
		c.queue_free()
	var seg_start := int((maxi(1, state.floor_n) - 1) / 10) * 10
	for i in 10:
		var n := seg_start + i + 1
		var dot := ColorRect.new()
		dot.custom_minimum_size = Vector2(12, 12) if not state.is_boss_floor(n) else Vector2(16, 16)
		dot.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		if n < state.floor_n:
			dot.color = Style.C_BONE
		elif n == state.floor_n:
			dot.color = Style.C_CANDLE
		else:
			dot.color = Color(1, 1, 1, 0.18)
		if state.is_boss_floor(n) and n >= state.floor_n:
			dot.color = Color(Style.C_DANGER, 0.9 if n == state.floor_n else 0.5)
		floor_dots.add_child(dot)


func _wait(t: float) -> void:
	await get_tree().create_timer(t / speed).timeout


# ================================================================ loop

func _run_loop() -> void:
	await _intro()
	while not state.dead and state.floor_n < state.total_floors:
		state.floor_n += 1
		if state.pending_skip > 0:
			# voo sobre o abismo: pula andares, mas nunca um chefe
			var target := state.floor_n + state.pending_skip
			var n := state.floor_n
			while n < target and not state.is_boss_floor(n + 1):
				n += 1
			state.floor_n = n
			state.pending_skip = 0
		_refresh_hud()
		await _walk()
		var boss := state.boss_for_floor(state.floor_n)
		if boss != "":
			await _boss_floor(boss)
		elif state.should_meet_hunter():
			await _hunter_floor()
		else:
			var ev := _demo_event() if demo else state.take_event()
			if ev.is_empty():
				continue
			await _play_event(ev)
			if not state.dead:
				await _curiosity_roll(String(ev.get("type", "")))
		_reveal_next()
	state.victory = not state.dead
	await _end_run()


## Mapa Rasgado (Gabinete): revela o tipo do próximo evento.
func _reveal_next() -> void:
	if demo or state.stat("reveal_next") <= 0.0 or state.dead:
		_next_icon.visible = false
		return
	var n := state.floor_n + 1
	if n > state.total_floors or state.is_boss_floor(n):
		_next_icon.visible = false
		return
	var saved := state.floor_n
	state.floor_n = n
	state.next_event = state.pick_event()
	state.floor_n = saved
	_next_icon.texture = load("res://art/ui/ui_event_%s.png" % String(state.next_event.get("type", "combat")))
	_next_icon.visible = true


## Itens do Gabinete de Curiosidades caem de baús, eventos raros, mercadores...
func _curiosity_roll(event_type: String) -> void:
	if demo:
		return
	var chance := float(GameData.bal("curiosity_drop/" + event_type, 0.0))
	if chance <= 0.0 or state.rng.randf() >= chance:
		return
	var cid := Meta.random_curiosity(event_type, state.rng)
	if cid != "":
		await _gain_curiosity(cid)


func _gain_curiosity(cid: String) -> void:
	var stars := Meta.add_curiosity(cid)
	state.flags["curiosities"] = int(state.flags.get("curiosities", 0)) + 1
	var icon := Sprite2D.new()
	icon.texture = load("res://art/ui/%s.png" % cid)
	icon.position = Vector2(540, 560)
	icon.scale = Vector2.ONE * 0.2
	icon.z_index = 45
	world.add_child(icon)
	var tw := create_tween()
	tw.tween_property(icon, "scale", Vector2.ONE * 1.3, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	fx.spark_burst(icon.position, Style.C_CANDLE, 16, 320)
	Haptics.medium()
	var key := "curiosity_found" if stars <= 1 else "curiosity_star"
	await _show_result(tr(key) % [tr(String(GameData.curiosities[cid].name)), stars])
	var tw2 := create_tween()
	tw2.tween_property(icon, "modulate:a", 0.0, 0.25)
	tw2.tween_callback(icon.queue_free)


func _hydra_unlocked() -> bool:
	return bool(state.flags.get("hydra_unlocked", false))


func _intro() -> void:
	hero_view.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(hero_view, "modulate:a", 1.0, 0.5)
	cam.zoom = Vector2.ONE * 1.25
	cam.position = HERO_POS + Vector2(60, -160)
	await cam.reset(0.9).finished
	_show_banner(tr("floor_forgotten_crypt"), Style.C_BONE, 1.6)
	await get_tree().create_timer(0.6).timeout


func _walk() -> void:
	# O Ossinho avança: poeira nos passos e um leve escurecer entre salas.
	for i in 3:
		fx.dust_puff(HERO_POS + Vector2(randf_range(-20, 20), 0), Color(0.8, 0.75, 0.7, 0.45), 3)
		hero_view.get_node("Body").position.y = -8.0
		var tw := create_tween()
		tw.tween_property(hero_view.get_node("Body"), "position:y", 0.0, 0.12)
		await _wait(0.14)
	await stage.dim(0.35, 0.12).finished
	await stage.dim(0.0, 0.2).finished


func _show_banner(text: String, color: Color, hold := 1.2) -> void:
	_banner.text = text
	_banner.add_theme_color_override("font_color", color)
	_banner.pivot_offset = _banner.size * 0.5
	_banner.scale = Vector2(0.6, 0.6)
	var tw := create_tween()
	tw.tween_property(_banner, "modulate:a", 1.0, 0.18)
	tw.parallel().tween_property(_banner, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_interval(hold)
	tw.tween_property(_banner, "modulate:a", 0.0, 0.3)


# ================================================================ eventos

func _clear_panel() -> void:
	for c in panel_box.get_children():
		c.queue_free()


func _panel_header(icon_name: String, title_key: String) -> void:
	var h := Style.hbox(12)
	h.add_child(Widgets.icon("res://art/ui/ui_event_%s.png" % icon_name, 44))
	var l := Style.bold(tr(title_key), 24, Style.C_CANDLE)
	l.autowrap_mode = TextServer.AUTOWRAP_OFF
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(l)
	panel_box.add_child(h)


func _panel_text(text: String) -> RichTextLabel:
	var r := RichTextLabel.new()
	r.bbcode_enabled = true
	r.fit_content = true
	r.scroll_active = false
	r.text = text
	r.add_theme_font_size_override("normal_font_size", 27)
	r.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	r.visible_ratio = 0.0
	panel_box.add_child(r)
	var tw := r.create_tween()
	tw.tween_property(r, "visible_ratio", 1.0, clampf(text.length() / 90.0, 0.25, 1.2) / speed)
	return r


var _prop: Sprite2D


func _show_prop(prop_id: String) -> void:
	_hide_prop()
	var path := "res://art/props/%s.png" % prop_id
	if prop_id == "" or not ResourceLoader.exists(path):
		return
	_prop = Sprite2D.new()
	_prop.texture = load(path)
	_prop.centered = false
	_prop.offset = Vector2(-_prop.texture.get_width() * 0.5, -_prop.texture.get_height() + 10)
	_prop.position = Vector2(540, ENEMY_BASE_Y)
	_prop.scale = Vector2.ONE * 0.6
	world.add_child(_prop)
	world.move_child(_prop, hero_view.get_index())
	_prop.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_prop, "modulate:a", 1.0, 0.3)
	fx.dust_puff(_prop.position, Color(0.8, 0.75, 0.7, 0.4), 4)


func _hide_prop() -> void:
	if _prop and is_instance_valid(_prop):
		var p := _prop
		var tw := create_tween()
		tw.tween_property(p, "modulate:a", 0.0, 0.25)
		tw.tween_callback(p.queue_free)
	_prop = null


func _play_event(ev: Dictionary) -> void:
	_clear_panel()
	_show_prop(String(ev.get("prop", "")))
	var type := String(ev.get("type", "combat"))
	_panel_header(type, "event_type_" + type)
	_panel_text(tr(String(ev.text)))
	var options: Array = []
	for o in ev.get("options", []):
		var req: Dictionary = o.get("requires", {})
		if not req.is_empty() and not state.requirement_met(req):
			if req.has("bone") or req.has("tag") or req.has("any_bone") or req.has("family"):
				continue  # opções do corpo só aparecem com o osso certo
		options.append(o)
	var buttons := []
	for i in options.size():
		var o: Dictionary = options[i]
		var req2: Dictionary = o.get("requires", {})
		var body_opt := req2.has("bone") or req2.has("tag") or req2.has("any_bone") or req2.has("family")
		var b := Style.button(tr(String(o.label)), "CandleButton" if body_opt else "", 78)
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		if not req2.is_empty() and not state.requirement_met(req2):
			b.disabled = true
		if body_opt:
			var bid := String(req2.get("bone", ""))
			if bid != "":
				b.icon = load(GameData.bone_texture_path(bid))
				b.expand_icon = true
				b.add_theme_constant_override("icon_max_width", 52)
		b.pressed.connect(func(): option_chosen.emit(i))
		panel_box.add_child(b)
		Widgets.pop_in(b, 0.12 + i * 0.06)
		buttons.append(b)
	if state.bigorna_left > 0 and not _common_bones().is_empty():
		var forge := Style.button(tr("bigorna_forge") % state.bigorna_left, "DarkButton", 64)
		forge.icon = load("res://art/ui/companion_bigorna.png")
		forge.expand_icon = true
		forge.add_theme_constant_override("icon_max_width", 48)
		forge.pressed.connect(func(): option_chosen.emit(-2))
		panel_box.add_child(forge)
		buttons.append(forge)
	var choice := -1
	if autoplay:
		await _wait(1.2)
		choice = 0
		for i in options.size():
			var rq: Dictionary = options[i].get("requires", {})
			if rq.has("bone") and state.requirement_met(rq):
				choice = i
	else:
		choice = await option_chosen
	if choice == -2:
		await _bigorna_forge()
		await _play_event(ev)
		return
	for b in buttons:
		b.disabled = true
	Backend.log_event("event_choice", {"event": ev.id, "option": options[choice].get("label", "")})
	var acts: Array = options[choice].get("actions", [])
	if _has_combat(acts):
		_hide_prop()
	await _exec(acts)
	_hide_prop()


func _has_combat(actions: Array) -> bool:
	for a in actions:
		if String(a.get("do", "")) == "combat":
			return true
	return false


func _exec(actions: Array) -> void:
	for a in actions:
		if state.dead:
			return
		await _do(a)


func _do(a: Dictionary) -> void:
	match String(a.get("do", "")):
		"combat":
			var ids: Array = []
			if a.has("monsters"):
				ids = a.monsters
			else:
				for i in int(a.get("count", 1)):
					ids.append(MonsterFactory.random_for_floor(state.floor_n, state.rng))
			await _combat(ids)
		"result":
			await _show_result(tr(String(a.text)))
		"dust":
			var n := int(a.get("amount", state.rng.randi_range(int(a.get("min", 10)), int(a.get("max", 20)))))
			_gain_dust(n, hero_view.body_center_global())
			await _wait(0.4)
		"dust_mult":
			var before := state.dust
			state.dust = int(round(state.dust * float(a.value)))
			var diff := state.dust - before
			fx.float_text(hero_view.body_center_global() + Vector2(0, -120), ("+" if diff >= 0 else "") + Style.num(diff) + " " + tr("dust_short"), Style.C_DUST)
			_refresh_hud()
			await _wait(0.5)
		"lose_current_pct":
			var d := maxf(1.0, round(state.hp * float(a.value)))
			state.hp = maxf(1.0, state.hp - d)
			hero_view.hit_anim()
			cam.shake(0.3)
			Haptics.medium()
			fx.damage_number(hero_view.body_center_global() + Vector2(0, -60), "-%d" % int(d), Style.C_DANGER)
			_refresh_hud()
			await _wait(0.6)
		"heal_pct":
			var h := state.heal_pct(float(a.value))
			if h > 0.5:
				fx.damage_number(hero_view.body_center_global() + Vector2(0, -60), "+%d" % int(h), Style.C_HEAL)
				fx.spark_burst(hero_view.body_center_global(), Style.C_HEAL, 8, 200)
			_refresh_hud()
			await _wait(0.5)
		"max_hp_pct":
			state.bonus_stats["hp_pct"] = float(state.bonus_stats.get("hp_pct", 0.0)) + float(a.value)
			var before_max := state.max_hp
			state.recalc()
			fx.float_text(hero_view.body_center_global() + Vector2(0, -100), tr("result_max_hp") % int(state.max_hp - before_max), Style.C_HEAL)
			_refresh_hud()
			await _wait(0.5)
		"bone":
			var bid := String(a.get("id", ""))
			if bid == "":
				var pool: Array = GameData.bones_by(a.get("pool", {}))
				pool = pool.filter(func(x): return not GameData.bone(x).get("boss_drop", false))
				if pool.is_empty():
					return
				bid = pool[state.rng.randi() % pool.size()]
			await _offer_bone({"id": bid, "level": int(a.get("level", 1))}, hero_view.body_center_global() + Vector2(160, -200))
		"chance":
			if state.rng.randf() < float(a.get("p", 0.5)):
				await _exec(a.get("then", []))
			else:
				await _exec(a.get("else", []))
		"roll":
			var table: Array = a.get("table", [])
			var total := 0.0
			for row in table:
				total += float(row.get("w", 1))
			var r := state.rng.randf() * total
			for row in table:
				r -= float(row.get("w", 1))
				if r <= 0.0:
					await _exec(row.get("actions", []))
					break
		"xp":
			await _gain_xp(int(a.get("amount", 10)))
		"pay":
			var cost := int(a.get("dust", 0))
			state.add_dust(-cost)
			fx.float_text(hero_view.body_center_global() + Vector2(0, -120), "-" + Style.num(cost) + " " + tr("dust_short"), Style.C_DUST)
			_refresh_hud()
			await _wait(0.3)
		"stat":
			var st: Dictionary = a.get("stats", {})
			for k in st:
				state.bonus_stats[k] = float(state.bonus_stats.get(k, 0.0)) + float(st[k])
			state.recalc()
			hero_view.flash(Style.C_CANDLE, 0.8, 0.4)
			fx.spark_burst(hero_view.body_center_global(), Style.C_CANDLE, 14, 300)
			fx.float_text(hero_view.body_center_global() + Vector2(0, -140), tr("result_power_up"), Style.C_CANDLE)
			_refresh_hud()
			await _wait(0.6)
		"trap":
			if state.rng.randf() < state.stat("trap_avoid"):
				await _show_result(tr("trap_avoided"))
			else:
				var d2 := maxf(1.0, roundf(state.max_hp * float(a.get("value", GameData.bal("trap/default", 0.15)))))
				state.hp = maxf(1.0, state.hp - d2)
				hero_view.hit_anim()
				cam.shake(0.45)
				Haptics.medium()
				fx.damage_number(hero_view.body_center_global() + Vector2(0, -60), "-%d" % int(d2), Style.C_DANGER)
				_refresh_hud()
				await _show_result(tr("trap_hit"))
		"skip":
			state.pending_skip = int(a.get("n", 3))
			await _fly_over()
		"ally":
			var aid := String(a.get("id", ""))
			state.allies.append(aid)
			var tmp := MonsterFactory.make_ally(aid, state.floor_n)
			if tmp:
				var v := MonsterView.new()
				v.position = ALLY_SPOTS[(state.allies.size() - 1) % ALLY_SPOTS.size()]
				world.add_child(v)
				v.setup(tmp)
				v.display_scale *= 0.85
				v.appear_anim()
				fx.spark_burst(v.center_global(), Style.C_HEAL, 12, 260)
				fx.float_text(v.top_global(), tr("ally_joined") % tr(tmp.name_key), Style.C_HEAL, 26)
				await _wait(0.9)
				v.queue_free()
		"merchant":
			await _merchant(int(a.get("stock", 3)), a.get("rarities", []))
		"sell_bone":
			var slot := await _choose_bone_dialog("choose_bone_sell", true)
			if slot != "":
				var inst := state.unequip(slot)
				var value := int(state.crush_value(inst) * float(GameData.bal("merchant/sell_mult", 2.0)))
				hero_view.set_slot(slot, {})
				fx.bone_burst(hero_view.slot_global_position(slot), 8)
				_gain_dust(value, hero_view.body_center_global())
				await _wait(0.5)
		"altar":
			var slot2 := await _choose_bone_dialog("choose_bone_altar", false)
			if slot2 != "":
				var old := state.unequip(slot2)
				hero_view.set_slot(slot2, {})
				fx.smoke(hero_view.slot_global_position(slot2), Color(0.6, 0.4, 0.9, 0.7), 6)
				cam.shake(0.3)
				await _wait(0.5)
				var nb := MonsterFactory.altar_bone(String(old.id), state.rng)
				if nb != "":
					await _offer_bone({"id": nb, "level": int(old.get("level", 1))}, Vector2(540, 600))
		"companion":
			var cid := String(a.get("id", ""))
			if not demo and Meta.unlock_companion(cid):
				Haptics.heavy()
				fx.spark_burst(hero_view.body_center_global() + Vector2(-80, -60), Color(0.5, 0.8, 1.0), 24, 380)
				_show_banner(tr(String(GameData.companions[cid].name)), Color(0.6, 0.85, 1.0), 1.2)
				await _show_result(tr("companion_unlocked") % tr(String(GameData.companions[cid].name)))
		"upgrade_bone":
			var slot3 := await _choose_bone_dialog("choose_bone_upgrade", false)
			if slot3 != "":
				var inst3: Dictionary = state.equipped[slot3]
				var max_lvl := int(GameData.bal("bone_max_level", 5))
				inst3["level"] = mini(max_lvl, int(inst3.get("level", 1)) + 1)
				state.recalc()
				hero_view.set_slot(slot3, inst3)
				hero_view.pop_slot(slot3)
				fx.spark_burst(hero_view.slot_global_position(slot3), Style.C_CANDLE, 18, 360)
				fx.float_text(hero_view.slot_global_position(slot3) + Vector2(0, -50), tr("bone_upgraded") % [tr(String(GameData.bone(String(inst3.id)).name)), int(inst3.level) - 1], Style.C_CANDLE, 26)
				Haptics.medium()
				_refresh_hud()
				await _wait(0.7)
				await _check_forms()
		_:
			push_warning("ação desconhecida: " + str(a))


func _common_bones() -> Array:
	return state.non_basic_bones().filter(func(sl): return Body.instance_rarity(state.equipped[sl]) == "common")


## Bigorna, o ferreiro: uma vez por partida sobe um osso de comum para raro.
func _bigorna_forge() -> void:
	var commons := _common_bones()
	if commons.is_empty():
		return
	var parts := _dialog_frame("bigorna_title")
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	v.add_child(Style.label(tr("bigorna_desc"), 22, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var picked := [""]
	for sl in commons:
		var inst: Dictionary = state.equipped[sl]
		var btn := Style.button(tr(String(GameData.bone(String(inst.id)).name)), "DarkButton", 74)
		btn.icon = load(GameData.bone_texture_path(String(inst.id)))
		btn.expand_icon = true
		btn.add_theme_constant_override("icon_max_width", 56)
		var slot_id: String = sl
		btn.pressed.connect(func():
			picked[0] = slot_id
			dialog_closed.emit(slot_id))
		v.add_child(btn)
	var cancel := Style.button(tr("btn_back"), "", 70)
	cancel.pressed.connect(func(): dialog_closed.emit(""))
	v.add_child(cancel)
	await dialog_closed
	_close_dialog(bg)
	if picked[0] == "":
		return
	var slot: String = picked[0]
	var inst2: Dictionary = state.equipped[slot]
	inst2["rarity"] = "rare"
	state.bigorna_left -= 1
	state.recalc()
	hero_view.set_slot(slot, inst2)
	hero_view.pop_slot(slot)
	fx.spark_burst(hero_view.slot_global_position(slot), Color(1, 0.6, 0.2), 26, 460)
	fx.embers(hero_view.slot_global_position(slot), Color(1, 0.5, 0.2), 14, 30)
	cam.shake(0.5)
	Haptics.heavy()
	_companion_pop(tr("bigorna_done"))
	_refresh_hud()
	await _wait(0.8)


## Voo sobre o abismo: o Ossinho levanta voo e a câmera acompanha.
func _fly_over() -> void:
	Haptics.medium()
	stage.dim(0.6, 0.3)
	var tw: Tween = hero_view.float_up(140.0, 0.5)
	fx.dust_puff(HERO_POS, Color(0.8, 0.75, 0.7, 0.5), 8)
	await tw.finished
	for i in 3:
		fx.embers(hero_view.body_center_global(), Color(0.8, 0.7, 1.0), 6, 40)
		await _wait(0.25)
	hero_view.land(0.4)
	stage.dim(0.0, 0.4)
	await _wait(0.4)


func _choose_bone_dialog(title_key: String, show_value: bool) -> String:
	var slots := state.non_basic_bones()
	if slots.is_empty():
		return ""
	if autoplay:
		return slots[state.rng.randi() % slots.size()]
	var parts := _dialog_frame(title_key)
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	var picked := [""]
	for s in slots:
		var inst: Dictionary = state.equipped[s]
		var b := GameData.bone(String(inst.id))
		var label := tr(String(b.name))
		if int(inst.get("level", 1)) > 1:
			label += " +%d" % (int(inst.level) - 1)
		if show_value:
			label += "  (+%d)" % int(state.crush_value(inst) * float(GameData.bal("merchant/sell_mult", 2.0)))
		var btn := Style.button(label, "DarkButton", 74)
		btn.icon = load(GameData.bone_texture_path(String(inst.id)))
		btn.expand_icon = true
		btn.add_theme_constant_override("icon_max_width", 56)
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var slot_id: String = s
		btn.pressed.connect(func():
			picked[0] = slot_id
			dialog_closed.emit(slot_id))
		v.add_child(btn)
	var cancel := Style.button(tr("btn_back"), "", 70)
	cancel.pressed.connect(func(): dialog_closed.emit(""))
	v.add_child(cancel)
	await dialog_closed
	_close_dialog(bg)
	return picked[0]


func _merchant(count: int, rarities: Array) -> void:
	var stock := MonsterFactory.merchant_stock(count, rarities, state.rng)
	while true:
		if autoplay:
			for o in stock:
				if state.dust >= int(o.price) and state.free_slot_for(String(o.id)) != "":
					state.add_dust(-int(o.price))
					stock.erase(o)
					await _offer_bone({"id": o.id, "level": 1}, Vector2(540, 620))
					break
			return
		var parts := _dialog_frame("merchant_title")
		var bg: Control = parts[0]
		var v: VBoxContainer = parts[1]
		v.add_child(Style.bold(tr("merchant_dust") % Style.num(state.dust), 24, Style.C_DUST, HORIZONTAL_ALIGNMENT_CENTER))
		var row := Style.hbox(10)
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		v.add_child(row)
		var bought := [-1]
		for i in stock.size():
			var o: Dictionary = stock[i]
			var col := Style.vbox(8)
			col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var card := Widgets.bone_card({"id": o.id, "level": 1}, "", true)
			card.size_flags_vertical = Control.SIZE_EXPAND_FILL
			col.add_child(card)
			var buy := Style.button(str(o.price), "CandleButton", 64)
			buy.icon = load("res://art/ui/ui_icon_dust.png")
			buy.expand_icon = true
			buy.add_theme_constant_override("icon_max_width", 34)
			buy.disabled = state.dust < int(o.price)
			var idx := i
			buy.pressed.connect(func():
				bought[0] = idx
				dialog_closed.emit(idx))
			col.add_child(buy)
			row.add_child(col)
		var leave := Style.button(tr("btn_leave_shop"), "DarkButton", 70)
		leave.pressed.connect(func(): dialog_closed.emit(-1))
		v.add_child(leave)
		await dialog_closed
		_close_dialog(bg)
		if bought[0] < 0:
			return
		var o2: Dictionary = stock[bought[0]]
		stock.remove_at(bought[0])
		state.add_dust(-int(o2.price))
		_refresh_hud()
		Haptics.light()
		await _offer_bone({"id": o2.id, "level": 1}, Vector2(540, 620))
		if stock.is_empty():
			return


func _show_result(text: String) -> void:
	_clear_panel()
	_panel_text(text)
	var b := Style.button(tr("btn_continue"), "", 74)
	panel_box.add_child(b)
	Widgets.pop_in(b, 0.2)
	if autoplay:
		await _wait(1.4)
	else:
		await b.pressed


func _gain_dust(n: int, from: Vector2) -> void:
	state.add_dust(n)
	fx.float_text(from + Vector2(0, -120), "+" + Style.num(n) + " " + tr("dust_short"), Style.C_DUST)
	fx.spark_burst(from, Style.C_DUST, 6, 160)
	_refresh_hud()


# ================================================================ combate

func _enemy_positions(list: Array) -> Array:
	var out := []
	var boss_idx := -1
	for i in list.size():
		if list[i].is_boss:
			boss_idx = i
	if boss_idx >= 0:
		var minion_spots := [Vector2(415, 780), Vector2(685, 780), Vector2(455, 705), Vector2(660, 705)]
		var k := 0
		for i in list.size():
			if i == boss_idx:
				out.append(Vector2(565, ENEMY_BASE_Y))
			else:
				out.append(minion_spots[k % minion_spots.size()])
				k += 1
		return out
	var n := list.size()
	for i in n:
		var x := 520.0 if n == 1 else lerpf(430.0, 660.0, float(i) / float(n - 1))
		var y := ENEMY_BASE_Y + (20.0 if i % 2 == 1 else 0.0)
		out.append(Vector2(x, y))
	return out


func _spawn_view(f: Fighter, pos: Vector2) -> Node2D:
	var v: Node2D = preload("res://scripts/scenes/monster_view.gd").new()
	v.position = pos
	world.add_child(v)
	world.move_child(v, hero_view.get_index())
	v.setup(f)
	v.appear_anim()
	enemy_views[f] = v
	return v


func _relayout_enemies() -> void:
	var alive := []
	for f in enemy_views:
		if is_instance_valid(enemy_views[f]) and not enemy_views[f].dead:
			alive.append(f)
	var pos := _enemy_positions(alive)
	for i in alive.size():
		var v: Node2D = enemy_views[alive[i]]
		var tw := create_tween()
		tw.tween_property(v, "position", pos[i], 0.25)


func _combat(ids: Array, is_boss := false) -> void:
	var enemies := []
	for id in ids:
		var f := MonsterFactory.make_hunter(state.floor_n) if String(id) == "boss_bone_hunter" else MonsterFactory.make(String(id), state.floor_n)
		if f != null:
			enemies.append(f)
	if enemies.is_empty():
		return
	enemy_views.clear()
	var pos := _enemy_positions(enemies)
	for i in enemies.size():
		_spawn_view(enemies[i], pos[i])
	var hero := state.make_hero()
	var comp: Dictionary = _companion_combat()
	var allies := []
	for aid in state.allies:
		var af := MonsterFactory.make_ally(String(aid), state.floor_n)
		if af:
			allies.append(af)
	combat = Combat.new(hero, enemies, {"rng": state.rng, "is_boss": is_boss, "allies": allies,
		"max_turns": int(GameData.bal("combat/boss_max_turns" if is_boss else "combat/max_turns", 15)), "companion": comp})
	_spawn_ally_views()
	_combat_panel(enemies)
	await _wait(0.5)
	var killed: Array = []
	while true:
		while not combat.finished():
			var evs := combat.step()
			await _animate(evs, killed)
			if combat_panel and is_instance_valid(combat_panel):
				combat_panel.refresh()
			_refresh_hud_from(hero)
		if combat.result == "lose":
			state.absorb_hero(hero)
			var revived: bool = await _death_dialog()
			if revived:
				hero.hp = hero.max_hp * float(GameData.bal("revive_pct", 0.5))
				hero.statuses.clear()
				hero.flags.erase("dead_emitted")
				combat.result = ""
				hero_view.reassemble()
				hero_view.set_equipped(state.equipped)
				fx.spark_burst(hero_view.body_center_global(), Style.C_CANDLE, 20, 400)
				_refresh_hud_from(hero)
				await _wait(0.6)
				continue
			state.dead = true
			return
		break
	state.absorb_hero(hero)
	_refresh_hud()
	if combat.result == "flee":
		for f in enemy_views:
			var v: Node2D = enemy_views[f]
			if is_instance_valid(v) and not v.dead:
				fx.float_text(v.top_global(), tr("combat_flee") % tr(f.name_key), Style.C_MUTED, 26)
				var tw := create_tween()
				tw.tween_property(v, "position:x", 900.0, 0.5)
				tw.tween_callback(v.queue_free)
		await _wait(0.8)
		return
	hero_view.victory_anim()
	await _wait(0.5)
	await _combat_rewards(killed, is_boss)


var ally_views: Dictionary = {}
const ALLY_SPOTS := [Vector2(118, 700), Vector2(40, 730), Vector2(150, 640), Vector2(30, 660)]


func _spawn_ally_views() -> void:
	for f in ally_views:
		if is_instance_valid(ally_views[f]):
			ally_views[f].queue_free()
	ally_views.clear()
	var i := 0
	for al in combat.allies:
		var v: MonsterView = MonsterView.new()
		v.position = ALLY_SPOTS[i % ALLY_SPOTS.size()]
		world.add_child(v)
		world.move_child(v, hero_view.get_index())
		v.setup(al)
		v.display_scale *= 0.85
		v.appear_anim()
		ally_views[al] = v
		i += 1


## Companheiro escolhido (Lumi cura em combate; os outros agem fora dele).
func _companion_combat() -> Dictionary:
	return Meta.companion_combat(state.companion_id) if state.companion_id != "" else {}


func _refresh_hud_from(hero: Fighter) -> void:
	state.hp = clampf(hero.hp, 0.0, state.max_hp)
	_refresh_hud()


var combat_panel: CombatPanel


func _combat_panel(enemies: Array) -> void:
	_clear_panel()
	combat_panel = CombatPanel.new()
	combat_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel_box.add_child(combat_panel)
	combat_panel.setup(combat, state, enemies[0].is_boss)
	combat_panel.focus_requested.connect(_set_focus)
	if enemies.size() > 1 or enemies[0].is_boss:
		combat_panel.log_line(tr("combat_tap_focus"), Style.C_MUTED)


func _set_focus(f: Fighter) -> void:
	if combat == null or not f.alive():
		return
	combat.focus = f
	for g in enemy_views:
		if is_instance_valid(enemy_views[g]):
			enemy_views[g].set_focused(g == f)
	if combat_panel:
		combat_panel.refresh()
	Haptics.light()


func _who(f: Fighter) -> String:
	return tr("hero_name") if f.is_hero else tr(f.name_key)


func _cp_log(text: String, color: Color = Style.C_TEXT) -> void:
	if combat_panel and is_instance_valid(combat_panel):
		combat_panel.log_line(text, color)


## Resumo do corpo no painel de combate: atributos, sinergias e forma ativa.
func _build_summary() -> void:
	var hero := state.make_hero()
	var row := Style.hbox(14)
	for item in [["ui_icon_attack", str(int(roundf(hero.atk)))], ["ui_icon_shield", str(int(roundf(hero.def)))],
			["ui_levelup_empty_eye", "%d%%" % int(roundf(hero.crit * 100))], ["ui_levelup_quick_knees", "%d%%" % int(roundf(hero.dodge * 100))]]:
		var h := Style.hbox(4)
		h.add_child(Widgets.icon("res://art/ui/%s.png" % item[0], 34))
		h.add_child(Style.nowrap(Style.bold(item[1], 22, Style.C_BONE)))
		row.add_child(h)
	panel_box.add_child(row)
	var chips := HFlowContainer.new()
	chips.add_theme_constant_override("h_separation", 8)
	chips.add_theme_constant_override("v_separation", 6)
	var c := state.compute()
	for fid in c.forms:
		chips.add_child(_summary_chip(tr(String(GameData.forms[fid].name)), Color(String(GameData.forms[fid].get("aura", "#ffffff")))))
	for fam in c.families:
		var n := int(c.families[fam])
		if n >= 2:
			chips.add_child(_summary_chip("%s ×%d" % [tr(String(GameData.families[fam].name)), n], GameData.family_color(fam)))
	if c.rejection:
		chips.add_child(_summary_chip(tr("rejection_chip"), Style.C_DANGER))
	if chips.get_child_count() > 0:
		panel_box.add_child(chips)


func _summary_chip(text: String, color: Color) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(color, 0.16), Color(color, 0.7), 14, 2, 6))
	var l := Style.nowrap(Style.bold(text, 19, color))
	p.add_child(l)
	return p


func _view_of(f: Fighter) -> Node2D:
	if f == null or f.is_hero:
		return hero_view
	if f.is_ally:
		var av: Variant = ally_views.get(f)
		return av if av != null and is_instance_valid(av) else null
	var v: Variant = enemy_views.get(f)
	if v != null and is_instance_valid(v):
		return v
	return null


func _pos_of(f: Fighter) -> Vector2:
	if f.is_hero:
		return hero_view.body_center_global()
	if f.is_ally:
		var av := _view_of(f)
		return av.center_global() if av else hero_view.body_center_global()
	var v := _view_of(f)
	return v.center_global() if v else Vector2(520, 640)


func _animate(evs: Array, killed: Array) -> void:
	for ev in evs:
		_log_event(ev)
		match String(ev.t):
			"attack":
				await _anim_attack(ev)
			"status":
				var f: Fighter = ev.dst
				var col := Color("d8343f") if ev.status == "bleed" else Color("8fe04a")
				fx.damage_number(_pos_of(f) + Vector2(0, -40), "-%d" % int(ev.dmg), col, false, 26)
				var v := _view_of(f)
				if v and v != hero_view:
					v.refresh()
				elif f.is_hero:
					hero_view.flash(col, 0.5, 0.15)
				await _wait(0.16)
			"apply_status":
				var v2 := _view_of(ev.dst)
				if v2 and v2 != hero_view:
					v2.refresh()
				if ev.status == "stun":
					fx.float_text(_pos_of(ev.dst) + Vector2(0, -90), tr("combat_stun"), Color("ffd84a"), 22)
			"heal":
				fx.damage_number(_pos_of(ev.dst) + Vector2(0, -70), "+%d" % int(ev.amount), Style.C_HEAL, false, 24)
				if ev.dst.is_hero:
					hero_view.flash(Style.C_HEAL, 0.35, 0.2)
			"summon":
				fx.float_text(_pos_of(ev.src) + Vector2(0, -150), tr("combat_summon"), Color("c58cff"), 30)
				ev.src.flags["floor"] = state.floor_n
				var view_src := _view_of(ev.src)
				if view_src:
					view_src.attack_anim(-1.0, false)
				for s in ev.spawned:
					var v3 := _spawn_view(s, Vector2(640, ENEMY_BASE_Y))
					fx.smoke(v3.center_global(), Color(0.5, 0.35, 0.6, 0.6), 4)
				_relayout_enemies()
				cam.shake(0.25)
				await _wait(0.5)
			"special":
				await _anim_special(ev)
			"death":
				var f2: Fighter = ev.dst
				if f2.is_hero:
					hero_view.collapse_anim()
					cam.shake(0.6)
					Haptics.heavy()
					fx.bone_burst(hero_view.body_center_global(), 10)
					await _wait(1.0)
				else:
					killed.append(f2)
					var v4 := _view_of(f2)
					if v4:
						_last_positions[f2] = v4.center_global()
						v4.die_anim(fx)
					cam.shake(0.35 if not f2.is_boss else 0.9)
					Haptics.medium()
					if f2.is_boss:
						Haptics.heavy()
						fx.shockwave(_last_positions.get(f2, Vector2(540, 600)), Style.C_CANDLE, 5.0, 0.9)
						fx.spark_burst(_last_positions.get(f2, Vector2(540, 600)), Style.C_CANDLE, 30, 700)
						stage.dim(0.5, 0.1)
						Engine.time_scale = 0.25
						await get_tree().create_timer(0.9, true, false, true).timeout
						Engine.time_scale = 1.0
						stage.dim(0.0, 0.5)
					if f2 == combat.focus:
						combat.focus = null
					await _wait(0.35)
					_relayout_enemies()
			"revive":
				hero_view.reassemble()
				fx.smoke(hero_view.body_center_global(), Color(0.6, 0.35, 0.9, 0.8), 10)
				fx.float_text(hero_view.body_center_global() + Vector2(0, -150), tr("form_lich_name"), Color("c58cff"), 34)
				await _wait(0.8)
			"guard":
				var v5 := _view_of(ev.dst)
				if v5:
					v5.refresh()
					if ev.state == "broken":
						fx.spark_burst(v5.center_global(), Color(0.5, 0.7, 1.0), 18, 420)
						fx.float_text(v5.top_global(), tr("combat_guard_broken"), Color(0.6, 0.8, 1.0), 28)
						cam.shake(0.4)
			"stunned":
				fx.float_text(_pos_of(ev.dst) + Vector2(0, -110), tr("combat_stun"), Color("ffd84a"), 22)
				await _wait(0.2)
			"turn":
				if is_instance_valid(_turn_label):
					_turn_label.text = tr("combat_turn") % int(ev.n)
			"flee", "end":
				pass


## Uma linha no registro do painel de combate para cada acontecimento.
func _log_event(ev: Dictionary) -> void:
	match String(ev.t):
		"attack":
			var src: Fighter = ev.src
			var dst: Fighter = ev.dst
			if ev.dodged:
				_cp_log(tr("log_dodge") % _who(dst), Color(0.75, 0.85, 1.0))
			elif ev.blocked:
				_cp_log(tr("log_blocked") % _who(dst), Color(0.6, 0.8, 1.0))
			elif ev.crit:
				_cp_log(tr("log_crit") % [_who(src), _who(dst), int(ev.dmg)], Color("ffd23f"))
			else:
				_cp_log(tr("log_attack") % [_who(src), _who(dst), int(ev.dmg)], Color("ff8a7a") if dst.is_hero else Style.C_TEXT)
		"status":
			_cp_log(tr("log_status") % [_who(ev.dst), int(ev.dmg), tr("status_" + String(ev.status))], Color("d8343f") if ev.status == "bleed" else Color("8fe04a"))
		"heal":
			_cp_log(tr("log_heal") % [_who(ev.dst), int(ev.amount)], Style.C_HEAL)
		"summon":
			_cp_log(tr("log_summon") % _who(ev.src), Color("c58cff"))
		"special":
			_cp_log(tr("log_special") % [_who(ev.src), tr("special_" + String(ev.name)).trim_suffix("!")], Style.C_CANDLE)
		"death":
			_cp_log(tr("log_death") % _who(ev.dst), Style.C_BONE)
		"stunned":
			_cp_log(tr("log_stunned") % _who(ev.dst), Color("ffd84a"))
	if combat_panel and is_instance_valid(combat_panel) and String(ev.t) in ["attack", "status", "summon", "death", "guard", "turn", "apply_status", "heal"]:
		combat_panel.refresh()


func _anim_attack(ev: Dictionary) -> void:
	var src: Fighter = ev.src
	var dst: Fighter = ev.dst
	var kind := String(ev.kind)
	var src_view := _view_of(src)
	var dst_view := _view_of(dst)
	var dir := 1.0 if src.is_hero or src.is_ally else -1.0
	if kind in ["normal", "counter"] and src_view:
		src_view.attack_anim(dir, false)
		await _wait(0.12)
	elif kind == "ally":
		if src_view:
			src_view.attack_anim(1.0, false)
		fx.beam(_pos_of(src), _pos_of(dst), Color(0.75, 1.0, 0.6, 0.7), 5, 0.15)
	var hit_pos := _pos_of(dst)
	if ev.dodged:
		if dst_view:
			dst_view.dodge_anim()
		fx.float_text(hit_pos + Vector2(0, -90), tr("combat_miss"), Color(0.8, 0.9, 1.0), 26)
		await _wait(0.22)
		return
	if ev.blocked:
		fx.shockwave(hit_pos, Color(0.5, 0.75, 1.0), 1.4, 0.3)
		fx.float_text(hit_pos + Vector2(0, -90), tr("combat_blocked"), Color(0.6, 0.8, 1.0), 26)
		await _wait(0.22)
		return
	var crit: bool = ev.crit
	if dst_view:
		if dst.is_hero:
			dst_view.hit_anim(-1.0)
		else:
			dst_view.hit_anim(crit)
	var color := Color.WHITE
	if crit:
		color = Color("ffd23f")
	if dst.is_hero:
		color = Color("ff6b5e")
	if kind == "reflect":
		color = Color(0.7, 0.8, 1.0)
	fx.damage_number(hit_pos + Vector2(0, -50), str(int(ev.dmg)), color, crit, 32 if kind != "reflect" else 24)
	if kind in ["normal", "counter", "ally"]:
		fx.slash(hit_pos, Color(1, 0.95, 0.85) if not crit else Color(1, 0.85, 0.3), dir < 0)
	fx.spark_burst(hit_pos, Color(1, 0.85, 0.6) if not dst.is_hero else Color(1, 0.4, 0.3), 6 if not crit else 14, 300 if not crit else 460)
	cam.shake(0.18 if not crit else 0.45)
	if crit:
		Haptics.medium()
		fx.light_flash(hit_pos, Color(1, 0.8, 0.4), 1.4, 2.2, 0.25)
		_hitstop(0.06)
	elif dst.is_hero:
		Haptics.light()
	await _wait(0.26 if kind != "ally" else 0.14)


func _hitstop(t: float) -> void:
	Engine.time_scale = 0.05
	await get_tree().create_timer(t, true, false, true).timeout
	Engine.time_scale = 1.0


func _anim_special(ev: Dictionary) -> void:
	var name := String(ev.name)
	var src: Fighter = ev.src
	fx.float_text(_pos_of(src) + Vector2(0, -170), tr("special_" + name), Style.C_CANDLE, 30)
	match name:
		"eye_beam":
			var t := combat._hero_target()
			if t:
				fx.beam(hero_view.slot_global_position("slot_skull"), _pos_of(t), Color(0.5, 0.75, 1.0), 22, 0.35)
		"fire_breath":
			if src.is_hero:
				fx.fire_breath(hero_view.slot_global_position("slot_skull"), Vector2(560, 650))
			else:
				fx.fire_breath(_pos_of(src) + Vector2(-40, -60), hero_view.body_center_global())
			cam.shake(0.5)
			Haptics.medium()
		"golem_punch":
			hero_view.attack_anim(1.0, true)
		"wave":
			fx.shockwave(Vector2(540, 700), Color(0.3, 0.9, 0.9), 4.0, 0.6)
			cam.shake(0.4)
		"extra_action":
			fx.embers(hero_view.body_center_global(), Color(1, 0.5, 0.2), 8)
	await _wait(0.35)


func _unhandled_input(event: InputEvent) -> void:
	if combat == null or combat.finished():
		return
	var pressed: bool = (event is InputEventScreenTouch and event.pressed) or (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT)
	if not pressed:
		return
	var p: Vector2 = event.position
	var wp := world.get_global_transform_with_canvas().affine_inverse() * p
	for f in enemy_views:
		var v: Node2D = enemy_views[f]
		if is_instance_valid(v) and not v.dead and v.hit_rect().has_point(wp):
			_set_focus(f)
			return


# ================================================================ recompensas

func _combat_rewards(killed: Array, is_boss: bool) -> void:
	var xp := 0
	var drops: Array = []
	for f in killed:
		state.kills += 1
		xp += MonsterFactory.xp_for(f.id, state.floor_n)
		var m := GameData.monster(f.id)
		if m.has("dust_drop"):
			_gain_dust(state.rng.randi_range(int(m.dust_drop[0]), int(m.dust_drop[1])), _last_pos(f))
		else:
			state.add_dust(int(GameData.bal("dust/per_kill", 3)))
		for bid in _roll_drops(f):
			drops.append({"id": bid, "from": _last_pos(f)})
	_refresh_hud()
	if demo:
		drops = _demo_drops(killed)
	await _gain_xp(xp)
	for d in drops:
		await _offer_bone({"id": d.id, "level": 1}, d.from)
		if state.dead:
			return
	# Ossudo, o cão esqueleto: chance de trazer um osso extra
	if not demo and not killed.is_empty() and state.rng.randf() < Meta.ossudo_chance(state.companion_id):
		var pool := []
		for f in killed:
			pool.append_array(GameData.monster(f.id).get("drops", []))
		pool = pool.filter(func(x): return not GameData.bone(x).get("boss_drop", false))
		if pool.is_empty():
			pool = GameData.bones_by({"rarity": "common"}).filter(func(x): return not GameData.bone(x).get("boss_drop", false))
		_companion_pop(tr("ossudo_fetch"))
		await _wait(0.5)
		await _offer_bone({"id": pool[state.rng.randi() % pool.size()], "level": 1}, companion_view.global_position + Vector2(0, -60) if companion_view else hero_view.body_center_global())
	await _rejection_check()


var _last_positions: Dictionary = {}


func _last_pos(f: Fighter) -> Vector2:
	if _last_positions.has(f):
		return _last_positions[f]
	var v := _view_of(f)
	if v:
		return v.center_global()
	return Vector2(540, 640)


func _roll_drops(f: Fighter) -> Array:
	var out := []
	var m := GameData.monster(f.id)
	if String(m.get("kind", "")) == "boss":
		var bid := MonsterFactory.boss_drop(f.id, Profile.boss_wins(f.id), state.rng)
		if bid != "":
			out.append(bid)
		return out
	var bid := MonsterFactory.roll_bone_drop(f.id, state.rng, state.stat("drop_bonus"))
	if bid != "":
		out.append(bid)
	return out


func _gain_xp(amount: int) -> void:
	if amount <= 0:
		return
	var ups := state.add_xp(amount)
	fx.float_text(hero_view.body_center_global() + Vector2(0, -200), tr("xp_gain") % amount, Style.C_XP, 24)
	_refresh_hud()
	for i in ups:
		await _levelup_dialog()


func _rejection_check() -> void:
	if not Body.rejection_active(state.equipped):
		return
	if state.rng.randf() >= float(GameData.bal("rejection/drop_chance", 0.1)):
		return
	var slots := state.non_basic_bones()
	if slots.is_empty():
		return
	var slot: String = slots[state.rng.randi() % slots.size()]
	var inst := state.unequip(slot)
	hero_view.set_slot(slot, {})
	fx.bone_burst(hero_view.slot_global_position(slot), 10)
	cam.shake(0.4)
	Haptics.medium()
	await _show_result(tr("rejection_drop") % tr(String(GameData.bone(String(inst.id)).get("name", ""))))


# ================================================================ ossos

func _offer_bone(inst: Dictionary, from: Vector2) -> void:
	var bid := String(inst.id)
	if Profile.discover_bone(bid):
		fx.float_text(hero_view.body_center_global() + Vector2(0, -240), tr("collection_new"), Style.C_CANDLE, 24)
	var free := state.free_slot_for(bid)
	if demo:
		var target := _demo_slot_for(bid)
		if target == "crush":
			await _crush(inst, from)
			return
		if target != "":
			if state.equipped.has(target):
				await _swap(target, inst, from)
			else:
				await _attach(target, inst, from)
			return
	if free != "":
		await _attach(free, inst, from)
		return
	if autoplay:
		var rank := {"basic": 0, "common": 1, "rare": 2, "legendary": 3}
		for s2 in state.slots_for(bid):
			if int(rank.get(Body.instance_rarity(state.equipped.get(s2, {})), 1)) < int(rank.get(Body.instance_rarity(inst), 1)):
				await _swap(s2, inst, from)
				return
		await _crush(inst, from)
		return
	var choice: Dictionary = await _bone_choice_dialog(inst)
	if choice.get("action", "") == "swap":
		await _swap(String(choice.slot), inst, from)
	else:
		await _crush(inst, from)


func _swap(slot: String, inst: Dictionary, from: Vector2) -> void:
	var old: Dictionary = state.equipped.get(slot, {})
	if not old.is_empty():
		var v := state.crush_value(old)
		fx.bone_burst(hero_view.slot_global_position(slot), 8)
		state.add_dust(v)
		fx.float_text(hero_view.slot_global_position(slot) + Vector2(0, -40), tr("bone_crushed") % v, Style.C_DUST, 24)
		hero_view.set_slot(slot, {})
		state.equipped.erase(slot)
		await _wait(0.3)
	await _attach(slot, inst, from)


func _crush(inst: Dictionary, from: Vector2) -> void:
	var v := state.crush_value(inst)
	state.add_dust(v)
	fx.bone_burst(from, 10)
	fx.dust_puff(from, Color(0.9, 0.85, 0.75, 0.7), 8)
	fx.float_text(from + Vector2(0, -60), tr("bone_crushed") % v, Style.C_DUST, 28)
	Haptics.light()
	_refresh_hud()
	await _wait(0.6)


## Encaixe cinematográfico: a câmera aproxima, o osso voa até o corpo,
## brilha, a tela treme e o celular vibra.
func _attach(slot: String, inst: Dictionary, from: Vector2) -> void:
	var bid := String(inst.id)
	var fam := String(GameData.bone(bid).get("family", ""))
	var fcol := GameData.family_color(fam) if fam != "" else Style.C_BONE
	await cam.focus(hero_view.body_center_global() + Vector2(70, -10), 1.35, 0.3 / sqrt(speed)).finished
	var flying := Sprite2D.new()
	flying.texture = load(GameData.bone_texture_path(bid))
	flying.global_position = from
	flying.scale = Vector2.ONE * 0.2
	flying.z_index = 40
	world.add_child(flying)
	var glow_s := Sprite2D.new()
	glow_s.texture = load("res://art/fx/fx_soft.png")
	glow_s.modulate = Color(fcol, 0.8)
	glow_s.scale = Vector2.ONE * 3.0
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	glow_s.material = add
	glow_s.show_behind_parent = true
	flying.add_child(glow_s)
	var target := hero_view.slot_global_position(slot)
	var ctrl := (from + target) * 0.5 + Vector2(0, -180)
	var tw := create_tween()
	tw.tween_property(flying, "scale", Vector2.ONE * 0.75, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_method(func(t: float):
		var p := from.lerp(ctrl, t).lerp(ctrl.lerp(target, t), t)
		flying.global_position = p
		flying.rotation = t * TAU * 1.5
		if randf() < 0.5:
			fx.embers(p, fcol, 1, 6)
	, 0.0, 1.0, 0.5 / sqrt(speed)).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(flying, "scale", Vector2.ONE * 0.5, 0.5 / sqrt(speed))
	await tw.finished
	flying.queue_free()
	state.equip(slot, inst)
	hero_view.set_slot(slot, inst)
	hero_view.pop_slot(slot)
	fx.spark_burst(target, fcol, 18, 420)
	fx.shockwave(target, fcol, 1.8, 0.4)
	cam.shake(0.35)
	Haptics.medium()
	_refresh_hud()
	fx.float_text(target + Vector2(0, -70), tr("bone_equipped") % tr(String(GameData.bone(bid).get("name", ""))), Style.C_BONE, 26)
	await _wait(0.55)
	await cam.reset(0.3).finished
	await _check_forms()


func _check_forms() -> void:
	for fid in Body.active_forms(state.equipped):
		if state.forms_announced.has(fid):
			continue
		state.forms_announced[fid] = true
		await _transformation(fid)


## Transformação em câmera lenta: a tela escurece, o Ossinho flutua e o nome aparece.
func _transformation(fid: String) -> void:
	var f: Dictionary = GameData.forms[fid]
	var secret := bool(f.get("secret", false))
	var newly := Profile.discover_form(fid)
	Backend.log_event("form", {"form": fid, "new": newly})
	var col := Color(String(f.get("aura", "#ffffff")))
	Haptics.heavy()
	stage.dim(1.0, 0.4)
	cam.focus(hero_view.body_center_global() + Vector2(0, -20), 1.55, 0.6)
	Engine.time_scale = 0.4
	var tw: Tween = hero_view.float_up(70.0, 0.9)
	fx.shockwave(hero_view.body_center_global(), col, 3.5, 0.9)
	fx.embers(hero_view.body_center_global(), col, 30, 120)
	await tw.finished
	hero_view.refresh_aura()
	hero_view.flash(col, 1.0, 0.9)
	fx.spark_burst(hero_view.body_center_global(), col, 30, 600)
	cam.shake(0.6)
	var key := "form_discovered" if secret else "form_activated"
	_show_banner(tr(key) % tr(String(f.name)), col, 1.6)
	await get_tree().create_timer(1.1, true, false, true).timeout
	Engine.time_scale = 1.0
	_clear_panel()
	_panel_text("[b]%s[/b]\n%s" % [tr(String(f.name)), tr(String(f.desc))])
	hero_view.land()
	stage.dim(0.0, 0.5)
	await cam.reset(0.5).finished
	await _wait(1.2)


# ================================================================ diálogos

func _dialog_frame(title_key: String, title_color := Style.C_CANDLE) -> Array:
	var bg := Widgets.dim_overlay(overlay_root)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel(Color(Style.C_PANEL, 0.98), Style.C_EDGE, 26)
	p.custom_minimum_size = Vector2(650, 0)
	center.add_child(p)
	var v := Style.vbox(16)
	p.add_child(v)
	v.add_child(Style.title(tr(title_key), 50, title_color))
	Widgets.pop_in(p)
	return [bg, v, p]


func _close_dialog(bg: Control) -> void:
	var tw := bg.create_tween()
	tw.tween_property(bg, "modulate:a", 0.0, 0.15)
	tw.tween_callback(bg.queue_free)


func _bone_choice_dialog(inst: Dictionary) -> Dictionary:
	var parts := _dialog_frame("bone_found_title")
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	var slots: Array = state.slots_for(String(inst.id))
	var row := Style.hbox(12)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(row)
	var nc := Widgets.bone_card(inst, tr("bone_new"), true)
	nc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(nc)
	if slots.size() == 1:
		var cur: Dictionary = state.equipped.get(slots[0], {})
		var cc := Widgets.bone_card(cur, tr("bone_current"), true)
		cc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(cc)
		v.add_child(Style.label(tr("bone_found_occupied") % tr(String(slots[0])), 22, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	else:
		v.add_child(Style.label(tr("choose_arm"), 22, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var result := {}
	var done := func(r: Dictionary):
		result.merge(r)
		dialog_closed.emit(r)
	for s in slots:
		var cur2: Dictionary = state.equipped.get(s, {})
		var label := tr("btn_swap")
		if slots.size() > 1:
			label += " · " + tr(String(s)) + " (" + tr(String(GameData.bone(String(cur2.get("id", ""))).get("name", ""))) + ")"
		var b := Style.button(label, "", 78)
		b.pressed.connect(func(): done.call({"action": "swap", "slot": s}))
		v.add_child(b)
	var cb := Style.button(tr("btn_crush") + "  (+" + str(state.crush_value(inst)) + ")", "DarkButton", 78)
	cb.icon = load("res://art/ui/ui_icon_dust.png")
	cb.expand_icon = true
	cb.add_theme_constant_override("icon_max_width", 40)
	cb.pressed.connect(func(): done.call({"action": "crush"}))
	v.add_child(cb)
	await dialog_closed
	_close_dialog(bg)
	return result


func _levelup_dialog() -> void:
	Haptics.medium()
	fx.spark_burst(hero_view.body_center_global(), Style.C_XP, 20, 420)
	fx.shockwave(hero_view.body_center_global(), Style.C_XP, 2.4, 0.5)
	var parts := _dialog_frame("levelup_title", Style.C_XP)
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	v.add_child(Style.label(tr("levelup_subtitle"), 24, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var choices := state.levelup_choices(3)
	var picked := [""]
	var reroll_used := int(state.flags.get("rerolls", 0))
	var reroll_lim := Ads.limit("reroll_levelup")
	if not autoplay and reroll_used < reroll_lim:
		var rb := Style.button(tr("btn_reroll_ad") % (reroll_lim - reroll_used), "DarkButton", 62)
		rb.add_theme_font_size_override("font_size", 22)
		rb.pressed.connect(func():
			rb.disabled = true
			if await Ads.show_rewarded("reroll_levelup"):
				state.flags["rerolls"] = int(state.flags.get("rerolls", 0)) + 1
				picked[0] = "__reroll__"
				dialog_closed.emit("__reroll__"))
		v.add_child(rb)
	for i in choices.size():
		var id: String = choices[i]
		var lu: Dictionary = GameData.levelups[id]
		var b := Style.button("", "DarkButton", 110)
		var h := Style.hbox(16)
		h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		h.offset_left = 16
		h.offset_right = -16
		h.mouse_filter = Control.MOUSE_FILTER_IGNORE
		h.add_child(Widgets.icon("res://art/ui/%s.png" % String(lu.get("icon", "ui_icon_attack")), 72))
		var tv := Style.vbox(2)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.alignment = BoxContainer.ALIGNMENT_CENTER
		tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var n := Style.bold(tr(String(lu.name)), 28, Style.C_BONE)
		n.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tv.add_child(n)
		var d := Style.label(tr(String(lu.desc)), 22, Style.C_MUTED)
		d.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tv.add_child(d)
		h.add_child(tv)
		b.add_child(h)
		b.pressed.connect(func():
			picked[0] = id
			dialog_closed.emit(id))
		v.add_child(b)
		Widgets.pop_in(b, 0.1 + i * 0.08)
	if autoplay:
		await _wait(1.0)
		picked[0] = choices[0]
	else:
		await dialog_closed
	if picked[0] == "__reroll__":
		_close_dialog(bg)
		await _levelup_dialog()
		return
	state.apply_levelup(picked[0])
	_refresh_hud()
	_close_dialog(bg)
	await _wait(0.2)


func _death_dialog() -> bool:
	await _wait(0.4)
	var can_ad := not bool(state.flags.get("revive_ad_used", false))
	if demo:
		return true
	if autoplay:
		if can_ad and await Ads.show_rewarded("revive"):
			state.flags["revive_ad_used"] = true
			return true
		return false
	var parts := _dialog_frame("death_title", Style.C_DANGER)
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	var res := [false]
	v.add_child(Style.label(tr("death_sub"), 24, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	if Store.free_revive_available():
		var fb := Style.button(tr("btn_revive_free"), "CandleButton", 80)
		fb.pressed.connect(func():
			Store.use_free_revive()
			res[0] = true
			dialog_closed.emit(true))
		v.add_child(fb)
	if int(Profile.data.extra_revives) > 0:
		var eb := Style.button(tr("btn_revive_extra") % int(Profile.data.extra_revives), "CandleButton", 80)
		eb.pressed.connect(func():
			Profile.data.extra_revives = int(Profile.data.extra_revives) - 1
			Profile.save()
			res[0] = true
			dialog_closed.emit(true))
		v.add_child(eb)
	if can_ad:
		var b := Style.button(tr("btn_revive_ad"), "CandleButton", 84)
		b.pressed.connect(func():
			var ok: bool = await Ads.show_rewarded("revive")
			if ok:
				state.flags["revive_ad_used"] = true
				res[0] = true
				dialog_closed.emit(true))
		v.add_child(b)
	var price := int(Store.diamond_item("item_extra_revive").get("price", 30))
	var db := Style.button(tr("btn_revive_diamonds") % price, "DarkButton", 74)
	db.icon = load("res://art/ui/ui_icon_diamond.png")
	db.expand_icon = true
	db.add_theme_constant_override("icon_max_width", 34)
	db.disabled = Profile.diamonds() < price
	db.pressed.connect(func():
		if Profile.spend_diamonds(price, "revive"):
			res[0] = true
			dialog_closed.emit(true))
	v.add_child(db)
	var g := Style.button(tr("btn_give_up"), "DarkButton", 74)
	g.pressed.connect(func(): dialog_closed.emit(false))
	v.add_child(g)
	await dialog_closed
	_close_dialog(bg)
	return res[0]


# ================================================================ chefes

func _boss_floor(boss_id: String) -> void:
	_clear_panel()
	_panel_header("boss", "event_type_boss")
	_panel_text(tr("event_" + boss_id + "_text"))
	stage.dim(0.4, 0.5)
	await cam.focus(Vector2(520, 560), 1.12, 0.6).finished
	_show_banner(tr(String(GameData.monster(boss_id).get("name", ""))), Style.C_DANGER, 1.2)
	Haptics.heavy()
	cam.shake(0.5)
	var b := Style.button(tr("opt_fight"), "CandleButton", 80)
	panel_box.add_child(b)
	Widgets.pop_in(b, 0.3)
	if autoplay:
		await _wait(1.5)
	else:
		await b.pressed
	stage.dim(0.0, 0.4)
	await cam.reset(0.4).finished
	await _combat([boss_id], true)
	if state.dead:
		return
	var first := Profile.boss_wins(boss_id) == 0
	state.bosses_beaten.append(boss_id)
	Profile.register_boss_win(boss_id)
	Backend.log_event("boss_win", {"boss": boss_id, "floor": state.floor_n, "first": first})
	var m := GameData.monster(boss_id)
	var dia := int(m.get("diamonds_first", 0)) if first else int(m.get("diamonds_repeat", 0))
	if dia > 0 and not demo:
		Profile.add_diamonds(dia, "boss_" + boss_id)
		fx.float_text(hero_view.body_center_global() + Vector2(0, -230), tr("reward_diamonds") % dia, Style.C_DIAMOND, 30)
		await _wait(0.6)
	if first and not demo:
		var cid := Meta.random_curiosity(boss_id, state.rng)
		if cid != "":
			await _gain_curiosity(cid)
	# Hidra: só aparece para quem vence o Dragão Ancião na forma Wyrm Ósseo.
	if boss_id == "boss_ancient_dragon" and Body.active_forms(state.equipped).has(String(GameData.bal("run/secret_requires_form", "form_bone_wyrm"))):
		state.flags["hydra_unlocked"] = true
		state.total_floors = int(GameData.bal("run/secret_floor", 31))
		_refresh_hud()
		cam.shake(0.8)
		Haptics.heavy()
		_show_banner(tr("hydra_awakens"), Color("ff5032"), 1.6)
		await _show_result(tr("event_hydra_unlock_text"))


# ================================================================ caçador

func _hunter_floor() -> void:
	state.hunter_met = true
	_clear_panel()
	_panel_header("boss", "hunter_title")
	var stolen := Meta.hunter_stolen()
	var names := []
	for inst in stolen:
		names.append(tr(String(GameData.bone(String(inst.id)).name)))
	_panel_text(tr("event_hunter_text") % ", ".join(names))
	stage.dim(0.35, 0.4)
	var hunter := MonsterFactory.make_hunter(state.floor_n)
	var preview: MonsterView = MonsterView.new()
	preview.position = Vector2(560, ENEMY_BASE_Y)
	world.add_child(preview)
	world.move_child(preview, hero_view.get_index())
	preview.setup(hunter)
	preview.appear_anim()
	_show_banner(tr("boss_bone_hunter_name"), Color("c0405a"), 1.2)
	cam.shake(0.4)
	Haptics.heavy()
	var fight := Style.button(tr("hunter_fight"), "CandleButton", 78)
	fight.pressed.connect(func(): option_chosen.emit(0))
	panel_box.add_child(fight)
	var flee := Style.button(tr("hunter_flee"), "DarkButton", 72)
	flee.pressed.connect(func(): option_chosen.emit(1))
	panel_box.add_child(flee)
	var choice := 0
	if autoplay:
		await _wait(1.0)
	else:
		choice = await option_chosen
	preview.queue_free()
	stage.dim(0.0, 0.3)
	if choice == 1:
		await _show_result(tr("hunter_fled"))
		return
	Backend.log_event("hunter_fight", {"floor": state.floor_n})
	await _combat(["boss_bone_hunter"], true)
	if state.dead:
		return
	var back := Meta.hunter_return()
	_gain_dust(state.rng.randi_range(int(GameData.bal("hunter/dust_reward", [40, 70])[0]), int(GameData.bal("hunter/dust_reward", [40, 70])[1])), Vector2(560, 620))
	if not back.is_empty():
		await _show_result(tr("hunter_defeated") % [tr(String(GameData.bone(String(back.id)).name)), int(back.level) - 1])
		await _offer_bone(back, Vector2(560, 620))


# ================================================================ fim

func _end_run() -> void:
	var rewards := state.end_rewards()
	if not demo:
		Profile.add_dust(int(rewards.total), "run_end")
		Profile.data.runs_played = int(Profile.data.runs_played) + 1
		Profile.data.best_index = maxi(int(Profile.data.best_index), state.floor_n)
		Profile.save()
	var stolen := {}
	if state.dead and not demo:
		stolen = Meta.hunter_steal(state.equipped)
	Backend.log_event("run_end", {"floor": state.floor_n, "dead": state.dead, "dust": rewards.total})
	await _wait(0.6)
	var parts := _dialog_frame("victory_title" if state.victory else "run_end_title", Style.C_CANDLE if state.victory else Style.C_BONE)
	var bg: Control = parts[0]
	var v: VBoxContainer = parts[1]
	v.add_child(Style.bold(Body.creature_name(state.equipped), 32, Style.C_BONE, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(tr("run_end_floor") % state.floor_n, 24, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(tr("run_end_bosses") % state.bosses_beaten.size(), 24, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	if not stolen.is_empty():
		var hrow := Style.hbox(10)
		hrow.alignment = BoxContainer.ALIGNMENT_CENTER
		hrow.add_child(Widgets.icon(GameData.bone_texture_path(String(stolen.id)), 56))
		var hl := Style.label(tr("hunter_stole") % tr(String(GameData.bone(String(stolen.id)).name)), 22, Color("e07a8a"))
		hl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hrow.add_child(hl)
		v.add_child(hrow)
	var dust_l := Style.bold(tr("run_end_dust") % Style.num(int(rewards.total)), 30, Style.C_DUST, HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(dust_l)
	var total := [int(rewards.total)]
	if not demo:
		var dbl := Style.button(tr("btn_double_dust_ad"), "CandleButton", 80)
		dbl.pressed.connect(func():
			dbl.disabled = true
			var ok: bool = await Ads.show_rewarded("double_dust")
			if ok:
				Profile.add_dust(total[0], "double_dust_ad")
				total[0] *= 2
				dust_l.text = tr("run_end_dust") % Style.num(total[0])
				fx.spark_burst(Vector2(360, 600), Style.C_DUST, 20, 400))
		v.add_child(dbl)
	var card := Style.button(tr("btn_view_card"), "", 84)
	card.pressed.connect(func(): dialog_closed.emit(true))
	v.add_child(card)
	if autoplay:
		await _wait(2.5)
	else:
		await dialog_closed
	_close_dialog(bg)
	Router.go("card", {"equipped": state.equipped.duplicate(true), "floor": state.floor_n, "victory": state.victory, "demo": demo})


# ================================================================ demonstração

## Modo demonstração: sequência fixa que preenche todos os encaixes e força a
## Manticora Noturna (para gravar vídeos). Plano em data/balance.json -> demo.
func _demo_event() -> Dictionary:
	if _demo_plan.is_empty():
		return {"id": "demo_ambush", "type": "combat", "text": "event_crypt_ambush_text", "options": [{"label": "opt_fight", "actions": [{"do": "combat", "pool": "floor", "count": 1}]}]}
	var step: Dictionary = _demo_plan.pop_front()
	if step.has("event"):
		var ev: Dictionary = GameData.events.get(String(step.event), {})
		return ev
	return {"id": "demo_" + String(step.monster), "type": "combat", "text": String(step.get("text", "event_crypt_ambush_text")),
		"options": [{"label": "opt_fight", "actions": [{"do": "combat", "monsters": [step.monster]}]}]}


func _demo_drops(killed: Array) -> Array:
	var out := []
	for f in killed:
		for bid in GameData.monster(f.id).get("drops", []):
			out.append({"id": bid, "from": _last_pos(f)})
	return out


func _demo_slot_for(bid: String) -> String:
	var target: Dictionary = GameData.bal("demo/target", {})
	for slot in target:
		if String(target[slot]) == bid and not (state.equipped.has(slot) and String(state.equipped[slot].id) == bid):
			return slot
	return "crush"
