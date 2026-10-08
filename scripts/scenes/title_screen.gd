extends Control
## Tela de título e hub: cripta animada, Ossinho com o companheiro escolhido,
## logo (toque longo de 3 s = modo demonstração), Jogar e abas
## Ossuário, Coleção e Loja.

const DEMO_HOLD := 3.0
const TABS := [
	{"id": "home", "label": "tab_home", "icon": "res://art/ui/ui_app_icon.png"},
	{"id": "ossuary", "label": "tab_ossuary", "icon": "res://art/ui/ui_bone_chest.png"},
	{"id": "collection", "label": "tab_collection", "icon": "res://art/ui/cur_endless_book.png"},
	{"id": "shop", "label": "tab_shop", "icon": "res://art/ui/ui_icon_diamond.png"},
]
const PAGES := {
	"ossuary": "res://scripts/ui/hub_ossuary.gd",
	"collection": "res://scripts/ui/hub_collection.gd",
	"shop": "res://scripts/ui/hub_shop.gd",
}

var _hold := -1.0
var _logo: TextureRect
var _hold_ring: Control
var _world: Node2D
var _hero: OssinhoView
var _ui: Control
var _home: Control
var _page_root: Control
var _page: Control
var _tab := "home"
var _tab_buttons := {}
var _dust_label: Label
var _dia_label: Label
var _companion: Sprite2D
var _chips: VBoxContainer


func _ready() -> void:
	_world = Node2D.new()
	add_child(_world)
	var stage := CryptStage.new()
	_world.add_child(stage)
	_hero = preload("res://scenes/Ossinho.tscn").instantiate()
	_hero.position = Vector2(360, 760)
	_hero.scale = Vector2.ONE * 1.1
	_world.add_child(_hero)
	_refresh_hero()

	var layer := CanvasLayer.new()
	add_child(layer)
	_ui = Control.new()
	_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_ui)

	_home = Control.new()
	_home.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_home.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_home)
	_build_home()

	_page_root = Control.new()
	_page_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_page_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_page_root)

	_build_top_bar()
	_build_nav()
	Profile.currency_changed.connect(_refresh_currency)
	_refresh_currency()
	Backend.log_event("hub_open", {"runs": Profile.data.runs_played})
	if Dev.env("BT_TAB") != "":
		_open_tab.call_deferred(Dev.env("BT_TAB"))
	_after_open()


## Ao abrir o hub: intersticial entre partidas, oferta de remover anúncios,
## Kit das primeiras 24 horas, recompensa diária do Cartão do Coveiro e calendário.
func _after_open() -> void:
	if Dev.env("BT_TAB") != "" or Dev.env("BT_SHOT") != "" and Dev.env("BT_POPUPS") == "":
		return
	await get_tree().create_timer(0.5).timeout
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	if bool(Router.params.get("after_run", false)):
		var before := int(Profile.data.ads.interstitials_seen)
		await Ads.maybe_show_interstitial()
		var p := Store.iap("iap_remove_ads")
		if before < int(p.get("show_after_interstitials", 10)) and Store.remove_ads_offer_visible():
			await _offer_popup("iap_remove_ads", "iap_remove_ads_desc")
		if Store.kit_available() and not bool(Profile.data.kit24.offered):
			Profile.data.kit24.offered = true
			Profile.save()
			_open_tab("shop")
			return
	var sub := Store.claim_subscription(rng)
	if not sub.is_empty():
		await RewardPopup.show_on(_ui, "subscription_daily", sub).closed
	if Store.can_claim_login():
		await _open_calendar()
	_refresh_currency()


func _open_calendar() -> void:
	var pop := LoginPopup.new()
	_ui.add_child(pop)
	await pop.closed
	_refresh_currency()
	_refresh_hero()
	_refresh_chips()


func _offer_popup(pid: String, desc_key: String) -> void:
	var bg := Widgets.dim_overlay(_ui, 0.8)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(560, 0)
	center.add_child(p)
	var v := Style.vbox(14)
	p.add_child(v)
	v.add_child(Style.title(tr(String(Store.iap(pid).name)), 44, Style.C_CANDLE))
	v.add_child(Style.label(tr(desc_key), 22, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	var done := [false]
	var buy := Style.button(Billing.price_text(pid), "CandleButton", 80)
	buy.pressed.connect(func():
		var rng := RandomNumberGenerator.new()
		await Store.buy_iap(pid, rng)
		bg.queue_free()
		done[0] = true)
	v.add_child(buy)
	var no := Style.button(tr("btn_not_now"), "DarkButton", 66)
	no.pressed.connect(func():
		bg.queue_free()
		done[0] = true)
	v.add_child(no)
	Widgets.pop_in(p)
	while not done[0]:
		await get_tree().process_frame


func _refresh_hero() -> void:
	var eq: Dictionary = GameData.skeleton.get("starting_bones", {}).duplicate()
	var sb := String(Profile.data.get("starting_bone", ""))
	if sb != "" and Meta.can_start_with(sb):
		eq[GameData.bone_slots(sb)[0]] = sb
	_hero.set_equipped(eq)
	_hero.set_skin_tint(Store.skin_tint())
	if _companion:
		_companion.queue_free()
		_companion = null
	var cid := String(Profile.data.get("selected_companion", ""))
	if cid != "" and Meta.companion_unlocked(cid):
		_companion = Sprite2D.new()
		_companion.texture = load("res://art/ui/%s.png" % cid)
		_companion.centered = false
		_companion.offset = Vector2(-130, -270)
		_companion.scale = Vector2.ONE * 0.5
		_companion.position = Vector2(200, 772) if cid != "companion_lumi" else Vector2(210, 620)
		_world.add_child(_companion)


# ------------------------------------------------------------------- home

func _build_home() -> void:
	_logo = TextureRect.new()
	_logo.texture = load("res://art/ui/ui_logo.png")
	_logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_logo.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_logo.offset_left = -300
	_logo.offset_right = 300
	_logo.offset_top = 120
	_logo.offset_bottom = 360
	_logo.mouse_filter = Control.MOUSE_FILTER_STOP
	_logo.gui_input.connect(_on_logo_input)
	_logo.pivot_offset = Vector2(300, 120)
	_home.add_child(_logo)

	_hold_ring = preload("res://scripts/ui/hold_ring.gd").new()
	_hold_ring.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_hold_ring.offset_left = -40
	_hold_ring.offset_right = 40
	_hold_ring.offset_top = 370
	_hold_ring.offset_bottom = 450
	_home.add_child(_hold_ring)

	var tag := Style.label(tr("title_tagline"), 26, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	tag.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	tag.offset_top = 360
	tag.offset_bottom = 410
	tag.offset_left = 40
	tag.offset_right = -40
	_home.add_child(tag)

	var bottom := Style.vbox(14)
	bottom.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_left = 50
	bottom.offset_right = -50
	bottom.offset_top = -400
	bottom.offset_bottom = -132
	bottom.alignment = BoxContainer.ALIGNMENT_END
	_home.add_child(bottom)
	_chips = Style.vbox(6)
	bottom.add_child(_chips)
	_refresh_chips()
	var play := Style.button(tr("btn_play"), "CandleButton", 108)
	play.add_theme_font_size_override("font_size", 42)
	play.pressed.connect(func(): Router.go("run", {}))
	bottom.add_child(play)
	var tw := create_tween().set_loops()
	tw.tween_property(play, "scale", Vector2(1.03, 1.03), 0.8).set_trans(Tween.TRANS_SINE)
	tw.tween_property(play, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_SINE)


func _refresh_chips() -> void:
	for c in _chips.get_children():
		c.queue_free()
	var cid := String(Profile.data.get("selected_companion", ""))
	if cid != "" and Meta.companion_unlocked(cid):
		_chips.add_child(_chip("res://art/ui/%s.png" % cid, tr("chip_companion") % tr(String(GameData.companions[cid].name))))
	var sb := String(Profile.data.get("starting_bone", ""))
	if sb != "" and Meta.can_start_with(sb):
		_chips.add_child(_chip(GameData.bone_texture_path(sb), tr("chip_start_bone") % tr(String(GameData.bone(sb).name))))
	var stolen := Meta.hunter_stolen()
	if not stolen.is_empty():
		_chips.add_child(_chip(GameData.bone_texture_path(String(stolen[-1].id)), tr("chip_hunter") % stolen.size(), Color("e07a8a")))
	var cal := Style.button(tr("login_open") + ("  •" if Store.can_claim_login() else ""), "DarkButton", 56)
	cal.icon = load("res://art/ui/ui_bone_chest.png")
	cal.expand_icon = true
	cal.add_theme_constant_override("icon_max_width", 36)
	cal.add_theme_font_size_override("font_size", 20)
	cal.pressed.connect(_open_calendar)
	_chips.add_child(cal)


func _chip(icon_path: String, text: String, color := Style.C_TEXT) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0.55), Color(1, 1, 1, 0.08), 22, 1, 6))
	var h := Style.hbox(10)
	p.add_child(h)
	h.add_child(Widgets.icon(icon_path, 36))
	var l := Style.label(text, 20, color)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	h.add_child(l)
	return p


# ------------------------------------------------------------ barra/abas

func _build_top_bar() -> void:
	var bar := PanelContainer.new()
	bar.add_theme_stylebox_override("panel", Style.flat_box(Color(0.05, 0.035, 0.06, 0.85), Color(0, 0, 0, 0.6), 0, 0, 12))
	bar.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	bar.offset_bottom = 88
	_ui.add_child(bar)
	var h := Style.hbox(12)
	bar.add_child(h)
	h.alignment = BoxContainer.ALIGNMENT_BEGIN
	h.add_child(_currency_pill("res://art/ui/ui_icon_dust.png", Style.C_DUST, true))
	h.add_child(_currency_pill("res://art/ui/ui_icon_diamond.png", Style.C_DIAMOND, false))
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(spacer)
	var lang := Style.button(tr("menu_language"), "DarkButton", 60)
	lang.add_theme_font_size_override("font_size", 20)
	lang.pressed.connect(_language_menu)
	h.add_child(lang)
	var opts := Style.button(tr("menu_settings"), "DarkButton", 60)
	opts.add_theme_font_size_override("font_size", 20)
	opts.pressed.connect(_settings_menu)
	h.add_child(opts)


func _currency_pill(icon_path: String, color: Color, dust: bool) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0.5), Color(color, 0.4), 22, 2, 6))
	p.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var h := Style.hbox(6)
	p.add_child(h)
	h.add_child(Widgets.icon(icon_path, 40))
	var l := Style.bold("0", 26, color)
	l.autowrap_mode = TextServer.AUTOWRAP_OFF
	l.custom_minimum_size = Vector2(72, 0)
	h.add_child(l)
	if dust:
		_dust_label = l
	else:
		_dia_label = l
	return p


func _refresh_currency() -> void:
	if _dust_label:
		_dust_label.text = Style.num(Profile.dust())
	if _dia_label:
		_dia_label.text = Style.num(Profile.diamonds())


func _build_nav() -> void:
	var nav := PanelContainer.new()
	nav.add_theme_stylebox_override("panel", Style.flat_box(Color(0.06, 0.045, 0.07, 0.96), Color(1, 1, 1, 0.06), 0, 1, 8))
	nav.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	nav.offset_top = -112
	_ui.add_child(nav)
	var h := Style.hbox(6)
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	nav.add_child(h)
	for t in TABS:
		var b := Button.new()
		b.theme_type_variation = "DarkButton"
		b.toggle_mode = true
		b.custom_minimum_size = Vector2(164, 92)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.icon = load(String(t.icon))
		b.expand_icon = true
		b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		b.add_theme_constant_override("icon_max_width", 44)
		b.text = tr(String(t.label))
		b.add_theme_font_size_override("font_size", 19)
		var id := String(t.id)
		b.pressed.connect(func(): _open_tab(id))
		Style.juice(b)
		h.add_child(b)
		_tab_buttons[id] = b
	_update_tab_buttons()


func _update_tab_buttons() -> void:
	for id in _tab_buttons:
		var b: Button = _tab_buttons[id]
		b.button_pressed = id == _tab
		b.modulate = Color.WHITE if id == _tab else Color(1, 1, 1, 0.7)


func _open_tab(id: String) -> void:
	Haptics.light()
	_tab = id
	_update_tab_buttons()
	if _page:
		_page.queue_free()
		_page = null
	_home.visible = id == "home"
	if id == "home":
		_refresh_hero()
		_refresh_chips()
		return
	_page = load(PAGES[id]).new()
	_page_root.add_child(_page)
	_page.modulate.a = 0.0
	var tw := _page.create_tween()
	tw.tween_property(_page, "modulate:a", 1.0, 0.18)


# ------------------------------------------------------------------ demo

func _on_logo_input(event: InputEvent) -> void:
	var down: bool = (event is InputEventScreenTouch and event.pressed) or (event is InputEventMouseButton and event.pressed)
	var up: bool = (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed)
	if down:
		_hold = 0.0
	elif up:
		_hold = -1.0
		_hold_ring.progress = 0.0


var _timer_acc := 0.0


func _process(delta: float) -> void:
	_logo.rotation = sin(Time.get_ticks_msec() / 900.0) * 0.015
	_timer_acc += delta
	if _timer_acc >= 1.0:
		_timer_acc = 0.0
		var shop_btn: Button = _tab_buttons.get("shop")
		if shop_btn:
			shop_btn.text = tr("tab_shop") + ("\n" + Store.format_time(Store.kit_seconds_left()) if Store.kit_available() else "")
	if _hold >= 0.0:
		_hold += delta
		_hold_ring.progress = _hold / DEMO_HOLD
		if _hold >= DEMO_HOLD:
			_hold = -1.0
			Haptics.heavy()
			Router.go("run", {"demo": true})


# ---------------------------------------------------------------- menus

func _menu(title_key: String, items: Array) -> void:
	var bg := Widgets.dim_overlay(_ui)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(560, 0)
	center.add_child(p)
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
	var items := [
		[tr("menu_vibration") + ": " + tr("on" if vib else "off"), func(): Profile.set_setting("vibration", not vib)],
		[tr("menu_quality") + ": " + tr("quality_" + q), func():
			Profile.set_setting("quality", "low" if q == "high" else "high")
			Router.go("title", {})],
	]
	# a política só aparece quando o endereço estiver preenchido em data/app.json
	if String(GameData.app.get("privacy_url", "")) != "":
		items.append([tr("menu_privacy"), _open_privacy])
	if Ads.privacy_options_required():
		items.append([tr("menu_ad_privacy"), Ads.show_privacy_options])
	items.append([tr("menu_credits"), _credits])
	_menu("menu_settings", items)


func _open_privacy() -> void:
	var url := String(GameData.app.get("privacy_url", ""))
	if url != "":
		OS.shell_open(url)


## Créditos: autor, licenças (fontes SIL OFL, Godot MIT) e apoiadores.
func _credits() -> void:
	var bg := Widgets.dim_overlay(_ui)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(600, 0)
	center.add_child(p)
	var v := Style.vbox(12)
	p.add_child(v)
	v.add_child(Style.title(tr("menu_credits"), 48))
	v.add_child(Style.label(tr("credits_author") % String(GameData.app.get("author", "")), 24, Style.C_BONE, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(tr("credits_engine"), 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(tr("credits_fonts"), 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var sup: Array = GameData.app.get("supporters", [])
	if bool(Profile.data.get("supporter", false)) or not sup.is_empty():
		v.add_child(Style.bold(tr("credits_supporters"), 24, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
		v.add_child(Style.label(", ".join(sup) if not sup.is_empty() else tr("credits_thanks"), 20, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.label(tr("credits_version") % String(ProjectSettings.get_setting("application/config/version", "")), 18, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var close := Style.button(tr("btn_back"), "", 70)
	close.pressed.connect(bg.queue_free)
	v.add_child(close)
	Widgets.pop_in(p)
