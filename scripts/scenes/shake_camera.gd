class_name ShakeCamera
extends Camera2D
## Câmera com tremor (trauma) e aproximação suave para momentos cinematográficos.

var trauma := 0.0
var base_offset := Vector2.ZERO
var home := Vector2(360, 640)


func _ready() -> void:
	position = home
	make_current()


func shake(amount: float) -> void:
	trauma = clampf(trauma + amount, 0.0, 1.0)


func _process(delta: float) -> void:
	if trauma > 0.0:
		trauma = maxf(0.0, trauma - delta * 1.8)
		var s := trauma * trauma
		offset = base_offset + Vector2(randf_range(-1, 1), randf_range(-1, 1)) * 22.0 * s
		rotation = randf_range(-1, 1) * 0.03 * s
	else:
		offset = base_offset
		rotation = 0.0


## Aproxima a câmera de um ponto. Use com await no tween devolvido.
func focus(target: Vector2, z: float, time := 0.35) -> Tween:
	var tw := create_tween().set_parallel(true)
	tw.tween_property(self, "position", target, time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(self, "zoom", Vector2.ONE * z, time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	return tw


func reset(time := 0.35) -> Tween:
	return focus(home, 1.0, time)
