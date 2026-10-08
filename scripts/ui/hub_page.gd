class_name HubPage
extends Control
## Base das páginas do hub: título, área rolável e utilitários de cartões.

signal changed

var scroll: ScrollContainer
var body: VBoxContainer


func _init() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color(0.04, 0.03, 0.05, 0.94)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	scroll = ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_top = 96
	scroll.offset_bottom = -112
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	add_child(scroll)
	var margin := MarginContainer.new()
	margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for side in ["left", "right"]:
		margin.add_theme_constant_override("margin_" + side, 20)
	margin.add_theme_constant_override("margin_bottom", 30)
	scroll.add_child(margin)
	body = Style.vbox(18)
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	margin.add_child(body)
	rebuild()
	Profile.changed.connect(_on_profile_changed)
	if Dev.env("BT_SCROLL") != "":
		await get_tree().create_timer(0.3).timeout
		scroll.scroll_vertical = int(Dev.env("BT_SCROLL"))


func _on_profile_changed() -> void:
	pass


## Reconstrói o conteúdo mantendo a posição de rolagem.
func rebuild() -> void:
	var sv := scroll.scroll_vertical
	for c in body.get_children():
		c.queue_free()
	build()
	await get_tree().process_frame
	scroll.scroll_vertical = sv


func build() -> void:
	pass


func section(title_key: String, subtitle: String = "") -> VBoxContainer:
	var box := Style.vbox(10)
	var t := Style.title(tr(title_key), 44, Style.C_BONE)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	box.add_child(t)
	if subtitle != "":
		box.add_child(Style.label(subtitle, 21, Style.C_MUTED))
	body.add_child(box)
	return box


func card(fill := Color(Style.C_PANEL_2, 0.96), edge := Style.C_EDGE) -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(fill, edge, 18, 2, 14))
	return p


## Botão com ícone de moeda e preço.
func price_button(amount: int, currency: String, enabled: bool, variation := "CandleButton") -> Button:
	var b := Style.button(Style.num(amount), variation, 60)
	b.icon = load("res://art/ui/ui_icon_%s.png" % currency)
	b.expand_icon = true
	b.add_theme_constant_override("icon_max_width", 32)
	b.custom_minimum_size = Vector2(150, 60)
	b.disabled = not enabled
	return b


func toast(text: String, color := Style.C_TEXT) -> void:
	var l := Style.bold(text, 26, color, HORIZONTAL_ALIGNMENT_CENTER)
	l.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	l.offset_left = -320
	l.offset_right = 320
	l.add_theme_constant_override("outline_size", 10)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	add_child(l)
	var tw := l.create_tween()
	tw.tween_property(l, "position:y", l.position.y - 60, 1.2)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 1.2).set_delay(0.6)
	tw.tween_callback(l.queue_free)
