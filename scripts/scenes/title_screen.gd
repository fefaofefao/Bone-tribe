extends Control
## Tela de título: cripta animada, Ossinho, logo (toque longo de 3 s = modo
## demonstração), botão Jogar e opções.

const DEMO_HOLD := 3.0

var _hold := -1.0
var _logo: TextureRect
var _hold_ring: Control
var _world: Node2D
var _hero: Node2D
var _ui: Control


func _ready() -> void:
	_world = Node2D.new()
	add_child(_world)
	var stage: Node2D = preload("res://scripts/scenes/crypt_stage.gd").new()
	_world.add_child(stage)
	_hero = preload("res://scenes/Ossinho.tscn").instantiate()
	_hero.position = Vector2(360, 760)
	_hero.scale = Vector2.ONE * 1.15
	_world.add_child(_hero)

	var layer := CanvasLayer.new()
	add_child(layer)
	var ui := Control.new()
	ui.set_anchors_preset(Control.PRESET_FULL_RECT)
	ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(ui)
	_ui = ui

	_logo = TextureRect.new()
	_logo.texture = load("res://art/ui/ui_logo.png")
	_logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_logo.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_logo.offset_left = -300
	_logo.offset_right = 300
	_logo.offset_top = 110
	_logo.offset_bottom = 350
	_logo.mouse_filter = Control.MOUSE_FILTER_STOP
	_logo.gui_input.connect(_on_logo_input)
	ui.add_child(_logo)
	_logo.pivot_offset = Vector2(300, 120)

	_hold_ring = preload("res://scripts/ui/hold_ring.gd").new()
	_hold_ring.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_hold_ring.offset_left = -40
	_hold_ring.offset_right = 40
	_hold_ring.offset_top = 360
	_hold_ring.offset_bottom = 440
	ui.add_child(_hold_ring)

	var tag := Style.label(tr("title_tagline"), 26, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	tag.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	tag.offset_top = 352
	tag.offset_bottom = 400
	tag.offset_left = 40
	tag.offset_right = -40
	ui.add_child(tag)

	var bottom := Style.vbox(16)
	bottom.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_left = 60
	bottom.offset_right = -60
	bottom.offset_top = -330
	bottom.offset_bottom = -60
	ui.add_child(bottom)
	var play := Style.button(tr("btn_play"), "CandleButton", 104)
	play.add_theme_font_size_override("font_size", 40)
	play.pressed.connect(func(): Router.go("run", {}))
	bottom.add_child(play)
	var row := Style.hbox(14)
	bottom.add_child(row)
	var lang := Style.button(tr("menu_language"), "DarkButton", 76)
	lang.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lang.pressed.connect(_language_menu)
	row.add_child(lang)
	var opts := Style.button(tr("menu_settings"), "DarkButton", 76)
	opts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	opts.pressed.connect(_settings_menu)
	row.add_child(opts)

	var tw := create_tween().set_loops()
	tw.tween_property(play, "scale", Vector2(1.03, 1.03), 0.8).set_trans(Tween.TRANS_SINE)
	tw.tween_property(play, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_SINE)


func _on_logo_input(event: InputEvent) -> void:
	var down: bool = (event is InputEventScreenTouch and event.pressed) or (event is InputEventMouseButton and event.pressed)
	var up: bool = (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed)
	if down:
		_hold = 0.0
	elif up:
		_hold = -1.0
		_hold_ring.progress = 0.0


func _process(delta: float) -> void:
	_logo.rotation = sin(Time.get_ticks_msec() / 900.0) * 0.015
	if _hold >= 0.0:
		_hold += delta
		_hold_ring.progress = _hold / DEMO_HOLD
		if _hold >= DEMO_HOLD:
			_hold = -1.0
			Haptics.heavy()
			Router.go("run", {"demo": true})


func _menu(title_key: String, items: Array) -> void:
	var bg := Widgets.dim_overlay(_ui)
	var p := Style.panel()
	p.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	p.offset_left = -300
	p.offset_right = 300
	p.offset_top = -260
	p.offset_bottom = 260
	bg.add_child(p)
	var v := Style.vbox(14)
	p.add_child(v)
	v.add_child(Style.title(tr(title_key), 48))
	for it in items:
		var b := Style.button(it[0], it[2] if it.size() > 2 else "DarkButton", 76)
		b.pressed.connect(func():
			it[1].call()
			bg.queue_free())
		v.add_child(b)
	var close := Style.button(tr("btn_back"), "", 70)
	close.pressed.connect(bg.queue_free)
	v.add_child(close)
	Widgets.pop_in(p)


func _language_menu() -> void:
	var items := []
	for loc in ["pt_BR", "en_US", "es_419"]:
		var l: String = loc
		items.append([tr("lang_" + l), func():
			Profile.set_locale(l)
			Router.go("title", {})])
	_menu("menu_language", items)


func _settings_menu() -> void:
	var vib: bool = Profile.setting("vibration")
	var q: String = Profile.setting("quality")
	_menu("menu_settings", [
		[tr("menu_vibration") + ": " + tr("on" if vib else "off"), func(): Profile.set_setting("vibration", not vib)],
		[tr("menu_quality") + ": " + tr("quality_" + q), func():
			Profile.set_setting("quality", "low" if q == "high" else "high")
			Router.go("title", {})],
	])
