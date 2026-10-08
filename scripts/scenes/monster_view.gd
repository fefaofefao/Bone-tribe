class_name MonsterView
extends Node2D
## Monstro na tela: sprite com pivot nos pés, barra de vida, animações de ataque,
## dano e morte (o monstro se desmonta em ossos).

const FLASH_SHADER := preload("res://art/shaders/flash.gdshader")

var fighter: Fighter
var sprite: Sprite2D
var hp_bar: Control
var _mat: ShaderMaterial
var _t := 0.0
var _phase := 0.0
var _focus_ring: Sprite2D
var _shadow: Sprite2D
var _guard: Sprite2D
var flying := false
var dead := false
var art_size := Vector2(300, 300)
var display_scale := 0.5


func setup(f: Fighter) -> void:
	fighter = f
	var m := GameData.monster(f.id)
	flying = bool(m.get("flying", false))
	var art: Dictionary = m.get("art", {"size": [300, 300], "pivot": [150, 290]})
	art_size = Vector2(art.size[0], art.size[1])
	display_scale = float(m.get("display_scale", 0.6))
	if f.is_boss:
		display_scale = float(m.get("display_scale", 0.62))
	_phase = randf() * TAU

	_shadow = Sprite2D.new()
	_shadow.texture = load("res://art/fx/fx_soft.png")
	_shadow.modulate = Color(0, 0, 0, 0.5)
	_shadow.scale = Vector2(art_size.x / 64.0 * display_scale * 0.9, 0.7)
	add_child(_shadow)

	_focus_ring = Sprite2D.new()
	_focus_ring.texture = load("res://art/fx/fx_ring.png")
	_focus_ring.scale = Vector2(art_size.x / 160.0 * display_scale * 1.1, 0.32)
	_focus_ring.modulate = Color(1, 0.75, 0.3, 0.0)
	add_child(_focus_ring)

	sprite = Sprite2D.new()
	var path := GameData.monster_texture_path(f.id)
	sprite.texture = load(path) if ResourceLoader.exists(path) else null
	sprite.centered = false
	sprite.offset = -Vector2(art.pivot[0], art.pivot[1])
	sprite.scale = Vector2.ONE * display_scale
	_mat = ShaderMaterial.new()
	_mat.shader = FLASH_SHADER
	sprite.material = _mat
	add_child(sprite)
	if f.is_ally:
		sprite.flip_h = true
		sprite.offset.x = -(art_size.x - float(art.pivot[0]))

	_guard = Sprite2D.new()
	_guard.texture = load("res://art/fx/fx_ring.png")
	_guard.position = Vector2(0, -art_size.y * display_scale * 0.5)
	_guard.scale = Vector2.ONE * art_size.y * display_scale / 140.0
	_guard.modulate = Color(0.45, 0.65, 1.0, 0.0)
	add_child(_guard)

	hp_bar = preload("res://scripts/ui/mini_bar.gd").new()
	hp_bar.position = Vector2(-60, -art_size.y * display_scale - 30 - (40 if flying else 0))
	hp_bar.size = Vector2(120, 14)
	hp_bar.boss = f.is_boss
	hp_bar.visible = not f.is_ally
	add_child(hp_bar)
	refresh()


func top_global() -> Vector2:
	return to_global(Vector2(0, -art_size.y * display_scale - (40 if flying else 0)))


func center_global() -> Vector2:
	return to_global(sprite.position + Vector2(0, -art_size.y * display_scale * 0.5))


func hit_rect() -> Rect2:
	var w := art_size.x * display_scale
	var h := art_size.y * display_scale
	return Rect2(global_position + Vector2(-w * 0.5, -h - (40 if flying else 0)), Vector2(w, h))


func refresh() -> void:
	if fighter == null:
		return
	hp_bar.ratio = fighter.hp_ratio()
	hp_bar.queue_redraw()
	var st := []
	if fighter.statuses.has("bleed"):
		st.append({"color": Color("d8343f")})
	if fighter.statuses.has("poison") or fighter.statuses.has("stack_poison"):
		st.append({"color": Color("8fe04a"), "count": int(fighter.statuses.get("stack_poison", {}).get("stacks", 0))})
	if fighter.stunned():
		st.append({"color": Color("ffd84a")})
	hp_bar.statuses = st
	var guard_up := fighter.guard_max > 0 and fighter.guard_broken_turns <= 0
	_guard.modulate.a = 0.55 if guard_up else 0.0


func set_focused(on: bool) -> void:
	var tw := create_tween()
	tw.tween_property(_focus_ring, "modulate:a", 0.9 if on else 0.0, 0.15)


func _process(delta: float) -> void:
	if dead:
		return
	_t += delta
	var bob := sin(_t * 2.6 + _phase)
	if flying:
		sprite.position.y = -40.0 + bob * 10.0
		sprite.scale = Vector2.ONE * display_scale
	else:
		sprite.scale = Vector2(display_scale * (1.0 + bob * 0.025), display_scale * (1.0 - bob * 0.025))
	_focus_ring.rotation = 0.0


func flash(color: Color = Color.WHITE, strength := 1.0, time := 0.16) -> void:
	_mat.set_shader_parameter("flash_color", color)
	_mat.set_shader_parameter("flash", strength)
	var tw := create_tween()
	tw.tween_method(func(v): _mat.set_shader_parameter("flash", v), strength, 0.0, time)


func attack_anim(direction: float = -1.0, heavy := false) -> void:
	var tw := create_tween()
	var base := sprite.position.x
	tw.tween_property(sprite, "position:x", base + 12.0 * -direction, 0.08)
	tw.tween_property(sprite, "position:x", base + (60.0 if heavy else 40.0) * direction, 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(sprite, "position:x", base, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func hit_anim(crit := false) -> void:
	flash(Color.WHITE, 1.0, 0.2 if crit else 0.14)
	var tw := create_tween()
	tw.tween_property(sprite, "position:x", 18.0 if not crit else 30.0, 0.05)
	tw.tween_property(sprite, "position:x", 0.0, 0.25).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	refresh()


func dodge_anim() -> void:
	var tw := create_tween()
	tw.tween_property(sprite, "position", Vector2(30, -20 + (-40.0 if flying else 0.0)), 0.1)
	tw.tween_property(sprite, "position", Vector2(0, -40.0 if flying else 0.0), 0.18).set_trans(Tween.TRANS_BOUNCE)


## Morte: o monstro pisca, se desfaz em lascas de osso e some.
func die_anim(fx_parent: Node) -> void:
	dead = true
	hp_bar.visible = false
	_focus_ring.visible = false
	flash(Color.WHITE, 1.0, 0.3)
	var center := center_global()
	if fx_parent and fx_parent.has_method("bone_burst"):
		fx_parent.bone_burst(center, 12 if not fighter.is_boss else 30, fighter.is_boss)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(sprite, "scale", Vector2(display_scale * 1.25, display_scale * 0.2), 0.28).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_property(sprite, "modulate:a", 0.0, 0.3)
	tw.tween_property(_shadow, "modulate:a", 0.0, 0.3)
	tw.chain().tween_callback(queue_free)


func appear_anim() -> void:
	sprite.modulate.a = 0.0
	var base_y := -40.0 if flying else 0.0
	sprite.position.y = base_y - 30.0
	var tw := create_tween().set_parallel(true)
	tw.tween_property(sprite, "modulate:a", 1.0, 0.25)
	tw.tween_property(sprite, "position:y", base_y, 0.35).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
