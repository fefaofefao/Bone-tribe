extends Control
## Barra de vida pequena desenhada à mão (monstros), com rastro de dano
## e marcadores de estado (sangramento, veneno, atordoado).

var ratio := 1.0
var lag := 1.0
var boss := false
var statuses: Array = []   # [{color, count}]


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(delta: float) -> void:
	if lag > ratio:
		lag = maxf(ratio, lag - delta * 0.8)
		queue_redraw()
	elif lag < ratio:
		lag = ratio
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(r.grow(3), Color(0, 0, 0, 0.75), true)
	draw_rect(r, Color(0.16, 0.08, 0.1), true)
	draw_rect(Rect2(Vector2.ZERO, Vector2(size.x * lag, size.y)), Color(1, 0.93, 0.8, 0.9), true)
	var col := Color("b23a8f") if boss else Color("e2554b")
	draw_rect(Rect2(Vector2.ZERO, Vector2(size.x * ratio, size.y)), col, true)
	draw_rect(Rect2(Vector2(0, 0), Vector2(size.x * ratio, size.y * 0.35)), Color(1, 1, 1, 0.18), true)
	var x := 8.0
	for s in statuses:
		var c: Color = s.color
		var p := Vector2(x, -12)
		draw_circle(p, 8, Color(0, 0, 0, 0.8))
		draw_circle(p, 6, c)
		if int(s.get("count", 0)) > 1:
			draw_string(Style.font_bold, p + Vector2(8, 6), str(s.count), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
		x += 26.0 if int(s.get("count", 0)) > 1 else 18.0
