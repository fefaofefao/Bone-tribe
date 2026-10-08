extends Control
## Barra grande da interface (vida, experiência) com rastro animado e texto.

var ratio := 1.0
var lag := 1.0
var fill_color := Color("e2554b")
var text := ""
var font_size := 20
var _pulse := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_value(value: float, max_value: float, label := "") -> void:
	var r := clampf(value / max_value, 0.0, 1.0) if max_value > 0 else 0.0
	if r > ratio:
		_pulse = 1.0
	ratio = r
	text = label
	queue_redraw()


func _process(delta: float) -> void:
	var dirty := false
	if lag > ratio:
		lag = maxf(ratio, lag - delta * 0.6)
		dirty = true
	elif lag < ratio:
		lag = minf(ratio, lag + delta * 2.0)
		dirty = true
	if _pulse > 0.0:
		_pulse = maxf(0.0, _pulse - delta * 2.5)
		dirty = true
	if dirty:
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var rad := size.y * 0.5
	draw_style_box(Style.flat_box(Color(0.05, 0.03, 0.06, 0.9), Color(0, 0, 0, 0.9), int(rad), 3, 0), r.grow(2))
	var inner := r.grow(-3)
	if lag > ratio:
		draw_style_box(Style.flat_box(Color(1, 0.92, 0.78, 0.85), Color(0, 0, 0, 0), int(rad), 0, 0), Rect2(inner.position, Vector2(maxf(inner.size.y, inner.size.x * lag), inner.size.y)))
	if ratio > 0.0:
		var c := fill_color.lerp(Color.WHITE, _pulse * 0.5)
		draw_style_box(Style.flat_box(c, Color(0, 0, 0, 0), int(rad), 0, 0), Rect2(inner.position, Vector2(maxf(inner.size.y, inner.size.x * ratio), inner.size.y)))
		draw_style_box(Style.flat_box(Color(1, 1, 1, 0.16), Color(0, 0, 0, 0), int(rad * 0.6), 0, 0), Rect2(inner.position + Vector2(4, 2), Vector2(maxf(0, inner.size.x * ratio - 8), inner.size.y * 0.35)))
	if text != "":
		var f: Font = Style.font_bold
		var ts := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
		var p := Vector2((size.x - ts.x) * 0.5, (size.y + font_size * 0.72) * 0.5)
		draw_string_outline(f, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, 6, Color(0, 0, 0, 0.9))
		draw_string(f, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color.WHITE)
