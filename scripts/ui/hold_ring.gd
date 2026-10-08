extends Control
## Anel de progresso do toque longo (modo demonstração).

var progress := 0.0:
	set(v):
		progress = clampf(v, 0.0, 1.0)
		queue_redraw()


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	if progress <= 0.0:
		return
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.4
	draw_arc(c, r, 0, TAU, 48, Color(0, 0, 0, 0.5), 10, true)
	draw_arc(c, r, -PI / 2, -PI / 2 + TAU * progress, 48, Style.C_CANDLE, 8, true)
