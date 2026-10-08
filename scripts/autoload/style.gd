extends Node
## Identidade visual: paleta, fontes, tema da interface e fábricas de controles.
## Os textos sempre chegam como chaves de tradução (res://i18n/).

const C_BG := Color("0e0b10")
const C_PANEL := Color("1f1822")
const C_PANEL_2 := Color("2b2130")
const C_EDGE := Color("4d3b46")
const C_BONE := Color("eadfc6")
const C_BONE_DARK := Color("b9a787")
const C_INK := Color("2a1d1a")
const C_TEXT := Color("f4ead6")
const C_MUTED := Color("a99c8c")
const C_CANDLE := Color("ffb347")
const C_DANGER := Color("e2554b")
const C_HEAL := Color("74d68f")
const C_DUST := Color("dcc9a0")
const C_DIAMOND := Color("72d6ff")
const C_XP := Color("b38cff")

const RARITY_COLORS := {
	"basic": Color("bfb3a0"),
	"common": Color("d9ccb0"),
	"rare": Color("5fb4ff"),
	"legendary": Color("ffb43a"),
}

var font_body: Font
var font_bold: Font
var font_title: Font
var theme: Theme


func _ready() -> void:
	var base: FontFile = load("res://art/fonts/Fredoka-Variable.ttf")
	var body := FontVariation.new()
	body.base_font = base
	body.variation_opentype = {TextServerManager.get_primary_interface().name_to_tag("wght"): 500}
	font_body = body
	var bold := FontVariation.new()
	bold.base_font = base
	bold.variation_opentype = {TextServerManager.get_primary_interface().name_to_tag("wght"): 650}
	font_bold = bold
	font_title = load("res://art/fonts/PirataOne-Regular.ttf")
	theme = _build_theme()
	get_tree().root.theme = theme


func _box(fill: Color, edge: Color, radius: int = 18, border: int = 3, pad: int = 16) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fill
	s.border_color = edge
	s.set_border_width_all(border)
	s.set_corner_radius_all(radius)
	s.set_content_margin_all(pad)
	s.anti_aliasing = true
	return s


func _build_theme() -> Theme:
	var t := Theme.new()
	t.default_font = font_body
	t.default_font_size = 26
	t.set_color("font_color", "Label", C_TEXT)
	t.set_color("font_outline_color", "Label", Color(0, 0, 0, 0.7))
	t.set_color("default_color", "RichTextLabel", C_TEXT)
	t.set_font("bold_font", "RichTextLabel", font_bold)
	t.set_font_size("normal_font_size", "RichTextLabel", 26)
	t.set_font_size("bold_font_size", "RichTextLabel", 26)

	var panel := _box(Color(C_PANEL, 0.96), C_EDGE, 22, 3, 20)
	panel.shadow_color = Color(0, 0, 0, 0.45)
	panel.shadow_size = 14
	panel.shadow_offset = Vector2(0, 6)
	t.set_stylebox("panel", "PanelContainer", panel)
	t.set_stylebox("panel", "Panel", panel)

	var normal := _box(C_BONE, C_BONE_DARK.darkened(0.35), 18, 3, 14)
	normal.shadow_color = Color(0, 0, 0, 0.35)
	normal.shadow_size = 6
	normal.shadow_offset = Vector2(0, 4)
	normal.content_margin_left = 22
	normal.content_margin_right = 22
	var hover := normal.duplicate()
	hover.bg_color = C_BONE.lightened(0.12)
	var pressed := normal.duplicate()
	pressed.bg_color = C_BONE_DARK
	pressed.shadow_size = 2
	pressed.shadow_offset = Vector2(0, 1)
	var disabled := normal.duplicate()
	disabled.bg_color = Color(C_BONE, 0.35)
	disabled.shadow_size = 0
	t.set_stylebox("normal", "Button", normal)
	t.set_stylebox("hover", "Button", hover)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_stylebox("disabled", "Button", disabled)
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	t.set_color("font_color", "Button", C_INK)
	t.set_color("font_hover_color", "Button", C_INK)
	t.set_color("font_pressed_color", "Button", C_INK)
	t.set_color("font_focus_color", "Button", C_INK)
	t.set_color("font_disabled_color", "Button", Color(C_INK, 0.5))
	t.set_font("font", "Button", font_bold)
	t.set_font_size("font_size", "Button", 28)

	# Variação escura de botão.
	t.add_type("DarkButton")
	t.set_type_variation("DarkButton", "Button")
	var dn := _box(C_PANEL_2, C_EDGE.lightened(0.15), 18, 3, 14)
	var dh := dn.duplicate()
	dh.bg_color = C_PANEL_2.lightened(0.08)
	var dp := dn.duplicate()
	dp.bg_color = C_PANEL_2.darkened(0.2)
	t.set_stylebox("normal", "DarkButton", dn)
	t.set_stylebox("hover", "DarkButton", dh)
	t.set_stylebox("pressed", "DarkButton", dp)
	t.set_stylebox("disabled", "DarkButton", _box(Color(C_PANEL_2, 0.5), C_EDGE, 18, 3, 14))
	for k in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		t.set_color(k, "DarkButton", C_TEXT)
	t.set_color("font_disabled_color", "DarkButton", Color(C_TEXT, 0.4))

	# Variação de destaque (vela).
	t.add_type("CandleButton")
	t.set_type_variation("CandleButton", "Button")
	var cn := _box(C_CANDLE, C_CANDLE.darkened(0.45), 18, 3, 14)
	cn.shadow_color = Color(C_CANDLE, 0.35)
	cn.shadow_size = 12
	var ch := cn.duplicate()
	ch.bg_color = C_CANDLE.lightened(0.15)
	var cp := cn.duplicate()
	cp.bg_color = C_CANDLE.darkened(0.15)
	t.set_stylebox("normal", "CandleButton", cn)
	t.set_stylebox("hover", "CandleButton", ch)
	t.set_stylebox("pressed", "CandleButton", cp)

	var bar_bg := _box(Color(0, 0, 0, 0.55), Color(0, 0, 0, 0.8), 10, 2, 0)
	var bar_fill := _box(C_DANGER, Color(0, 0, 0, 0), 10, 0, 0)
	t.set_stylebox("background", "ProgressBar", bar_bg)
	t.set_stylebox("fill", "ProgressBar", bar_fill)
	t.set_color("font_color", "ProgressBar", C_TEXT)
	t.set_font_size("font_size", "ProgressBar", 20)

	var scroll := StyleBoxFlat.new()
	scroll.bg_color = Color(1, 1, 1, 0.08)
	scroll.set_corner_radius_all(6)
	t.set_stylebox("scroll", "VScrollBar", scroll)
	var grab := StyleBoxFlat.new()
	grab.bg_color = Color(C_BONE, 0.5)
	grab.set_corner_radius_all(6)
	t.set_stylebox("grabber", "VScrollBar", grab)
	t.set_stylebox("grabber_highlight", "VScrollBar", grab)
	t.set_stylebox("grabber_pressed", "VScrollBar", grab)
	return t


# ------------------------------------------------------------- fábricas

func label(text: String, size: int = 26, color: Color = C_TEXT, align: int = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = align
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


func title(text: String, size: int = 56, color: Color = C_BONE) -> Label:
	var l := label(text, size, color, HORIZONTAL_ALIGNMENT_CENTER)
	l.add_theme_font_override("font", font_title)
	l.add_theme_constant_override("outline_size", 10)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	return l


func bold(text: String, size: int = 26, color: Color = C_TEXT, align: int = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := label(text, size, color, align)
	l.add_theme_font_override("font", font_bold)
	return l


func button(text: String, variation: String = "", min_h: int = 84) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", 28)
	b.custom_minimum_size = Vector2(0, min_h)
	if variation != "":
		b.theme_type_variation = variation
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	juice(b)
	return b


func panel(fill: Color = Color(C_PANEL, 0.96), edge: Color = C_EDGE, radius: int = 22) -> PanelContainer:
	var p := PanelContainer.new()
	var s := _box(fill, edge, radius, 3, 20)
	s.shadow_color = Color(0, 0, 0, 0.45)
	s.shadow_size = 14
	s.shadow_offset = Vector2(0, 6)
	p.add_theme_stylebox_override("panel", s)
	return p


func flat_box(fill: Color, edge: Color, radius: int = 14, border: int = 2, pad: int = 10) -> StyleBoxFlat:
	return _box(fill, edge, radius, border, pad)


func vbox(sep: int = 16) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", sep)
	return v


func hbox(sep: int = 16) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	return h


func rarity_color(rarity: String) -> Color:
	return RARITY_COLORS.get(rarity, C_BONE)


## Animação de toque: o botão encolhe ao pressionar e salta ao soltar.
func juice(c: Control) -> void:
	c.resized.connect(func(): c.pivot_offset = c.size * 0.5)
	if c is BaseButton:
		var b := c as BaseButton
		b.button_down.connect(func():
			Haptics.light()
			var tw := b.create_tween()
			tw.tween_property(b, "scale", Vector2(0.94, 0.94), 0.06))
		b.button_up.connect(func():
			var tw := b.create_tween()
			tw.tween_property(b, "scale", Vector2(1.05, 1.05), 0.08).set_trans(Tween.TRANS_BACK)
			tw.tween_property(b, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_SINE))


## Formata números grandes com separador de milhar conforme o idioma.
func num(n: int) -> String:
	var s := str(absi(n))
	var out := ""
	var sep := "," if Profile.current_locale() == "en_US" else "."
	while s.length() > 3:
		out = sep + s.substr(s.length() - 3) + out
		s = s.substr(0, s.length() - 3)
	return ("-" if n < 0 else "") + s + out
