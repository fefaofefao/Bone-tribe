class_name FxLayer
extends Node2D
## Efeitos visuais leves feitos à mão: números de dano, lascas de osso,
## faíscas, ondas de choque e cortes. Partículas simples simuladas em _process.

const TEX := {
	"chip": preload("res://art/fx/fx_bone_chip.png"),
	"spark": preload("res://art/fx/fx_spark.png"),
	"soft": preload("res://art/fx/fx_soft.png"),
	"dust": preload("res://art/fx/fx_dust.png"),
	"ring": preload("res://art/fx/fx_ring.png"),
	"slash": preload("res://art/fx/fx_slash.png"),
	"ember": preload("res://art/fx/fx_ember.png"),
	"smoke": preload("res://art/fx/fx_smoke.png"),
}

var _parts: Array = []
var _add_mat: CanvasItemMaterial


func _ready() -> void:
	_add_mat = CanvasItemMaterial.new()
	_add_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	z_index = 50


func low_quality() -> bool:
	return Profile.setting("quality") == "low"


func _spawn(tex: String, pos: Vector2, vel: Vector2, life: float, opts: Dictionary = {}) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = TEX[tex]
	s.global_position = pos
	s.modulate = opts.get("color", Color.WHITE)
	var sc: float = opts.get("scale", 1.0)
	s.scale = Vector2.ONE * sc
	s.rotation = opts.get("rot", randf() * TAU)
	if opts.get("add", false):
		s.material = _add_mat
	add_child(s)
	_parts.append({"n": s, "v": vel, "life": life, "max": life, "g": opts.get("gravity", 0.0),
		"spin": opts.get("spin", 0.0), "s0": sc, "s1": opts.get("end_scale", sc), "fade": opts.get("fade", true),
		"drag": opts.get("drag", 0.0), "bounce_y": opts.get("floor_y", INF), "a0": s.modulate.a})
	return s


func _process(delta: float) -> void:
	for i in range(_parts.size() - 1, -1, -1):
		var p: Dictionary = _parts[i]
		var n: Sprite2D = p.n
		p.life -= delta
		if p.life <= 0.0 or not is_instance_valid(n):
			if is_instance_valid(n):
				n.queue_free()
			_parts.remove_at(i)
			continue
		var v: Vector2 = p.v
		v.y += float(p.g) * delta
		v *= 1.0 - float(p.drag) * delta
		n.global_position += v * delta
		if n.global_position.y > float(p.bounce_y) and v.y > 0:
			n.global_position.y = float(p.bounce_y)
			v.y *= -0.35
			v.x *= 0.6
			p.spin = float(p.spin) * 0.5
		p.v = v
		n.rotation += float(p.spin) * delta
		var t := 1.0 - float(p.life) / float(p.max)
		var sc := lerpf(float(p.s0), float(p.s1), t)
		n.scale = Vector2.ONE * sc
		if p.fade:
			n.modulate.a = float(p.a0) * clampf(float(p.life) / (float(p.max) * 0.5), 0.0, 1.0)


# -------------------------------------------------------------- efeitos

func damage_number(pos: Vector2, text: String, color: Color, crit := false, size_px := 34) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Style.font_bold)
	var fs := size_px + (18 if crit else 0)
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", color)
	l.add_theme_constant_override("outline_size", 10)
	l.add_theme_color_override("font_outline_color", Color(0.08, 0.04, 0.06, 0.95))
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.size = Vector2(260, fs + 12)
	l.pivot_offset = l.size * 0.5
	l.position = pos - l.size * 0.5 + Vector2(randf_range(-18, 18), 0)
	l.z_index = 60
	add_child(l)
	l.scale = Vector2.ONE * (0.3 if crit else 0.6)
	var tw := l.create_tween()
	tw.tween_property(l, "scale", Vector2.ONE * (1.35 if crit else 1.0), 0.14).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(l, "position:y", l.position.y - 46, 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if crit:
		tw.tween_property(l, "scale", Vector2.ONE * 1.1, 0.1)
	tw.tween_property(l, "position:y", l.position.y - 76, 0.45)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 0.45)
	tw.tween_callback(l.queue_free)


func float_text(pos: Vector2, text: String, color: Color, size_px := 28) -> void:
	damage_number(pos, text, color, false, size_px)


func bone_burst(pos: Vector2, count := 12, big := false) -> void:
	var n := count if not low_quality() else count / 2
	for i in n:
		var a := randf_range(-PI * 0.95, -PI * 0.05)
		var sp := randf_range(180, 420) * (1.3 if big else 1.0)
		_spawn("chip", pos + Vector2(randf_range(-20, 20), randf_range(-20, 20)), Vector2(cos(a), sin(a)) * sp, randf_range(0.9, 1.4),
			{"gravity": 900.0, "spin": randf_range(-14, 14), "scale": randf_range(0.7, 1.3) * (1.4 if big else 1.0), "floor_y": pos.y + randf_range(60, 120), "fade": true})
	dust_puff(pos + Vector2(0, 40), Color(0.85, 0.8, 0.7, 0.6), 6)


func spark_burst(pos: Vector2, color: Color, count := 10, speed := 380.0) -> void:
	var n := count if not low_quality() else count / 2
	for i in n:
		var a := randf() * TAU
		_spawn("spark", pos, Vector2(cos(a), sin(a)) * randf_range(speed * 0.4, speed), randf_range(0.25, 0.5),
			{"color": color, "add": true, "scale": randf_range(0.4, 0.9), "end_scale": 0.05, "drag": 4.0})
	_spawn("soft", pos, Vector2.ZERO, 0.22, {"color": Color(color, 0.9), "add": true, "scale": 1.0, "end_scale": 3.0})


func dust_puff(pos: Vector2, color := Color(0.8, 0.75, 0.7, 0.5), count := 5) -> void:
	if low_quality():
		count = 2
	for i in count:
		_spawn("dust", pos + Vector2(randf_range(-20, 20), 0), Vector2(randf_range(-80, 80), randf_range(-60, -10)), randf_range(0.5, 0.9),
			{"color": color, "scale": randf_range(0.8, 1.4), "end_scale": 2.6, "drag": 2.0})


func shockwave(pos: Vector2, color: Color, size := 2.5, time := 0.45) -> void:
	_spawn("ring", pos, Vector2.ZERO, time, {"color": color, "add": true, "scale": 0.2, "end_scale": size, "rot": 0.0})


func slash(pos: Vector2, color: Color, flip := false) -> void:
	var s := _spawn("slash", pos, Vector2.ZERO, 0.22, {"color": color, "add": true, "scale": 0.7, "end_scale": 1.1, "rot": randf_range(-0.4, 0.4)})
	if flip:
		s.flip_h = true


func embers(pos: Vector2, color: Color, count := 12, radius := 60.0) -> void:
	if low_quality():
		count /= 2
	for i in count:
		_spawn("ember", pos + Vector2(randf_range(-radius, radius), randf_range(-radius * 0.5, radius * 0.5)), Vector2(randf_range(-30, 30), randf_range(-160, -60)),
			randf_range(0.6, 1.2), {"color": color, "add": true, "scale": randf_range(0.6, 1.2), "end_scale": 0.1})


func smoke(pos: Vector2, color: Color, count := 6) -> void:
	if low_quality():
		count = 2
	for i in count:
		_spawn("smoke", pos + Vector2(randf_range(-30, 30), randf_range(-20, 20)), Vector2(randf_range(-40, 40), randf_range(-70, -20)), randf_range(0.6, 1.1),
			{"color": color, "scale": randf_range(0.5, 0.9), "end_scale": 1.8, "drag": 1.0})


## Projétil simples (raio, sopro) de a até b.
func beam(a: Vector2, b: Vector2, color: Color, width := 18.0, time := 0.25) -> void:
	var l := Line2D.new()
	l.points = PackedVector2Array([a, b])
	l.width = width
	l.default_color = color
	l.material = _add_mat
	l.begin_cap_mode = Line2D.LINE_CAP_ROUND
	l.end_cap_mode = Line2D.LINE_CAP_ROUND
	add_child(l)
	var tw := l.create_tween()
	tw.tween_property(l, "width", 2.0, time)
	tw.parallel().tween_property(l, "modulate:a", 0.0, time)
	tw.tween_callback(l.queue_free)
	spark_burst(b, color, 8)


## Sopro de fogo em leque.
func fire_breath(from: Vector2, to: Vector2, color := Color(1, 0.45, 0.15)) -> void:
	var n := 26 if not low_quality() else 12
	for i in n:
		var dir := (to - from).normalized().rotated(randf_range(-0.25, 0.25))
		_spawn("soft", from, dir * randf_range(500, 800), randf_range(0.35, 0.6),
			{"color": Color(color.r, color.g * randf_range(0.6, 1.3), color.b, 0.9), "add": true, "scale": randf_range(0.5, 0.9), "end_scale": 2.2, "drag": 2.5})
	embers(to, color, 10, 50)
