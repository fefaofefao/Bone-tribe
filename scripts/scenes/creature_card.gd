extends Control
## Cartão da Criatura: a criatura montada girando, logo Bone Tribe, nome automático
## e desafio. Compartilhar exporta a imagem em 1080x1920.

const CARD_SIZE := Vector2i(1080, 1920)
const NativeShare := preload("res://scripts/core/native_share.gd")

var viewport: SubViewport
var creature: Node2D
var equipped: Dictionary = {}
var _t := 0.0
var _toast: Label


func _ready() -> void:
	var p := Router.params
	equipped = p.get("equipped", GameData.skeleton.get("starting_bones", {}).duplicate())
	var bg := ColorRect.new()
	bg.color = Style.C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	viewport = SubViewport.new()
	viewport.size = CARD_SIZE
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.transparent_bg = false
	add_child(viewport)
	_build_card(p)

	var root := Style.vbox(14)
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.offset_left = 24
	root.offset_right = -24
	root.offset_top = 24
	root.offset_bottom = -24
	add_child(root)
	var view := TextureRect.new()
	view.texture = viewport.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(view)
	var share := Style.button(tr("btn_share"), "CandleButton", 86)
	share.pressed.connect(_share)
	root.add_child(share)
	var row := Style.hbox(14)
	root.add_child(row)
	var again := Style.button(tr("btn_play_again"), "", 80)
	again.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	again.pressed.connect(func(): Router.go("run", {}))
	row.add_child(again)
	var menu := Style.button(tr("btn_menu"), "DarkButton", 80)
	menu.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	menu.pressed.connect(func(): Router.go("title", {"after_run": not bool(p.get("demo", false))}))
	row.add_child(menu)
	_toast = Style.label("", 22, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	_toast.modulate.a = 0.0
	root.add_child(_toast)


func _build_card(p: Dictionary) -> void:
	var W := float(CARD_SIZE.x)
	var H := float(CARD_SIZE.y)
	var world := Node2D.new()
	viewport.add_child(world)
	var bg := Sprite2D.new()
	bg.texture = load("res://art/env/env_forgotten_crypt.png")
	bg.centered = false
	bg.scale = Vector2(W / 720.0, H / 1280.0)
	bg.modulate = Color(0.55, 0.5, 0.6)
	world.add_child(bg)
	# vinheta superior/inferior para o texto
	for top in [true, false]:
		var g := TextureRect.new()
		var grad := Gradient.new()
		grad.set_color(0, Color(0.03, 0.02, 0.04, 0.95))
		grad.set_color(1, Color(0.03, 0.02, 0.04, 0.0))
		var gt := GradientTexture2D.new()
		gt.gradient = grad
		gt.fill_from = Vector2(0, 0) if top else Vector2(0, 1)
		gt.fill_to = Vector2(0, 1) if top else Vector2(0, 0)
		g.texture = gt
		g.position = Vector2(0, 0 if top else H - 620)
		g.size = Vector2(W, 620)
		world.add_child(g)

	var forms := Body.active_forms(equipped)
	var aura := Color(1, 0.7, 0.35)
	if not forms.is_empty():
		aura = Color(String(GameData.forms[forms[0]].get("aura", "#ffffff")))
	var halo := Sprite2D.new()
	halo.texture = load("res://art/fx/fx_light.png")
	halo.position = Vector2(W * 0.5, H * 0.56)
	halo.scale = Vector2.ONE * 4.2
	halo.modulate = Color(aura, 0.55)
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	halo.material = add
	world.add_child(halo)

	creature = preload("res://scenes/Ossinho.tscn").instantiate()
	creature.position = Vector2(W * 0.5, H * 0.72)
	creature.scale = Vector2.ONE * 2.5
	world.add_child(creature)
	creature.set_equipped(equipped)
	if not bool(p.get("demo", false)):
		creature.set_skin_tint(Store.skin_tint())

	var logo := Sprite2D.new()
	logo.texture = load("res://art/ui/ui_logo.png")
	logo.position = Vector2(W * 0.5, 190)
	logo.scale = Vector2.ONE * 1.25
	world.add_child(logo)

	var ui := Control.new()
	ui.size = Vector2(W, H)
	ui.theme = Style.theme
	world.add_child(ui)
	var box := Style.vbox(10)
	box.position = Vector2(60, H - 520)
	box.size = Vector2(W - 120, 470)
	ui.add_child(box)
	var name_l := Style.title(Body.creature_name(equipped), 104, Style.C_BONE)
	box.add_child(name_l)
	if not forms.is_empty():
		box.add_child(Style.bold(tr("card_forms") % tr(String(GameData.forms[forms[0]].name)), 46, aura, HORIZONTAL_ALIGNMENT_CENTER))
	var sub := tr("card_floor") % int(p.get("floor", 1))
	if p.get("victory", false):
		sub += "  ·  " + tr("card_victory")
	box.add_child(Style.label(sub, 40, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var ch := Style.bold(tr("card_challenge"), 52, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER)
	box.add_child(ch)
	var footer := Style.label(tr("store_title"), 32, Color(1, 1, 1, 0.55), HORIZONTAL_ALIGNMENT_CENTER)
	box.add_child(footer)


func _process(delta: float) -> void:
	_t += delta
	if creature:
		# giro "3D" falso: a escala horizontal segue o cosseno
		var c := cos(_t * 1.1)
		creature.scale.x = 2.5 * (c if absf(c) > 0.08 else 0.08 * signf(c + 0.0001))


func _share() -> void:
	Haptics.medium()
	var img := viewport.get_texture().get_image()
	DirAccess.make_dir_recursive_absolute("user://cards")
	var path := "user://cards/bonetribe_%d.png" % Backend.now()
	img.save_png(path)
	var creature_name := Body.creature_name(equipped)
	Backend.log_event("card_share", {"name": creature_name})
	var text := tr("card_share_text") % creature_name
	var link := String(GameData.app.get("store_url", ""))
	if link != "":
		text += " " + link
	if NativeShare.share_image(path, text, tr("btn_share")):
		return
	# sem Android (ou se o menu falhar), o arquivo fica salvo no aparelho
	_toast.text = tr("card_saved") % ProjectSettings.globalize_path(path).get_file()
	var tw := create_tween()
	tw.tween_property(_toast, "modulate:a", 1.0, 0.2)
	tw.tween_interval(2.0)
	tw.tween_property(_toast, "modulate:a", 0.0, 0.4)
