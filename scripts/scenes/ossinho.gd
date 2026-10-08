class_name OssinhoView
extends Node2D
## O Ossinho: Skeleton2D com um sprite por encaixe.
## Trocar um osso = trocar a textura do encaixe; as animações continuam valendo.
## Animação procedural (respiração, balanço, asas, cauda) e efeitos de golpe.

signal bone_attached(slot: String)

const FLASH_SHADER := preload("res://art/shaders/flash.gdshader")

var equipped: Dictionary = {}
var slot_nodes: Dictionary = {}   # slot_id -> Bone2D
var base_nodes: Dictionary = {}   # base part id -> Bone2D
var slot_defs: Dictionary = {}
var aura_color := Color(1, 0.75, 0.4)
var aura_strength := 0.0
var form_id := ""
var skin_tint := Color.WHITE
var skin_id := ""
var _accessories: Array = []
var idle_enabled := true
var lowered := 0.0          # quanto o corpo desce sem pernas
var _target_lowered := 0.0
var _t := 0.0
var _material: ShaderMaterial
var _aura: Sprite2D
var _aura_light: PointLight2D
var _aura_particles: GPUParticles2D
var _shadow: Sprite2D
var _root: Bone2D
var _busy_parts: Dictionary = {}
var _form_scale := 1.0


func _ready() -> void:
	_root = $Body/Skeleton2D/Root
	_material = ShaderMaterial.new()
	_material.shader = FLASH_SHADER
	$Body.material = _material
	_set_light_mask($Body, 2)
	_build_fx()
	var tex_scale := float(GameData.skeleton.get("texture_scale", 0.5))
	for p in GameData.skeleton.get("base_parts", []):
		var n: Bone2D = _root.get_node(String(p.id))
		base_nodes[p.id] = n
		_config_sprite(n.get_node("Sprite"), p, "res://art/bones/%s.png" % p.id, tex_scale)
	for s in GameData.slots():
		slot_defs[s.id] = s
		var n2: Bone2D = _root.get_node_or_null(String(s.id))
		if n2 == null:
			continue
		slot_nodes[s.id] = n2
		n2.position = Vector2(s.attach[0], s.attach[1])
		n2.rotation_degrees = float(s.get("rest_rot", 0))
		var spr: Sprite2D = n2.get_node("Sprite")
		spr.centered = false
		spr.offset = -Vector2(s.pivot[0], s.pivot[1])
		spr.z_index = int(s.z)
		spr.material = _material
		spr.visible = false
	set_equipped(GameData.skeleton.get("starting_bones", {}).duplicate())


func _set_light_mask(n: Node, mask: int) -> void:
	if n is CanvasItem:
		(n as CanvasItem).light_mask = mask
	for c in n.get_children():
		_set_light_mask(c, mask)


func _config_sprite(spr: Sprite2D, def: Dictionary, path: String, scale_k: float) -> void:
	spr.texture = load(path) if ResourceLoader.exists(path) else null
	spr.centered = false
	spr.offset = -Vector2(def.pivot[0], def.pivot[1])
	spr.scale = Vector2.ONE * scale_k
	spr.z_index = int(def.get("z", 0))
	spr.material = _material


func _build_fx() -> void:
	_shadow = Sprite2D.new()
	_shadow.texture = load("res://art/fx/fx_soft.png")
	_shadow.modulate = Color(0, 0, 0, 0.55)
	_shadow.scale = Vector2(3.2, 0.7)
	_shadow.z_index = -10
	add_child(_shadow)
	move_child(_shadow, 0)
	_aura = Sprite2D.new()
	_aura.texture = load("res://art/fx/fx_soft.png")
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_aura.material = add
	_aura.position = Vector2(0, -170)
	_aura.scale = Vector2(6.5, 7.5)
	_aura.z_index = -5
	_aura.modulate = Color(aura_color, 0.0)
	add_child(_aura)
	move_child(_aura, 1)
	_aura_light = PointLight2D.new()
	_aura_light.texture = load("res://art/fx/fx_light.png")
	_aura_light.position = Vector2(0, -170)
	_aura_light.texture_scale = 2.4
	_aura_light.energy = 0.0
	# a aura ilumina o cenário, não o próprio Ossinho
	_aura_light.range_item_cull_mask = 1
	_aura_light.color = aura_color
	add_child(_aura_light)
	_aura_particles = GPUParticles2D.new()
	_aura_particles.amount = 24
	_aura_particles.lifetime = 1.8
	_aura_particles.position = Vector2(0, -150)
	_aura_particles.texture = load("res://art/fx/fx_ember.png")
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.emission_sphere_radius = 90.0
	pm.direction = Vector3(0, -1, 0)
	pm.spread = 25.0
	pm.initial_velocity_min = 20.0
	pm.initial_velocity_max = 50.0
	pm.gravity = Vector3(0, -10, 0)
	pm.scale_min = 0.4
	pm.scale_max = 1.0
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1, 1, 1, 0.9))
	ramp.set_color(1, Color(1, 1, 1, 0))
	var rt := GradientTexture1D.new()
	rt.gradient = ramp
	pm.color_ramp = rt
	_aura_particles.process_material = pm
	_aura_particles.material = add
	_aura_particles.emitting = false
	add_child(_aura_particles)


# ---------------------------------------------------------------- ossos

func set_equipped(eq: Dictionary) -> void:
	equipped = {}
	for s in eq:
		var v: Variant = eq[s]
		equipped[s] = v if typeof(v) == TYPE_DICTIONARY else {"id": v, "level": 1}
	for s in slot_nodes:
		_apply_slot(s)
	_update_lowered(true)
	refresh_aura()


func set_slot(slot: String, inst: Dictionary) -> void:
	if inst.is_empty():
		equipped.erase(slot)
	else:
		equipped[slot] = inst
	_apply_slot(slot)
	_update_lowered(false)
	refresh_aura()


func _apply_slot(slot: String) -> void:
	var n: Bone2D = slot_nodes.get(slot)
	if n == null:
		return
	var spr: Sprite2D = n.get_node("Sprite")
	var inst: Dictionary = equipped.get(slot, {})
	if inst.is_empty():
		spr.visible = false
		return
	var bone_id := String(inst.get("id", ""))
	var path := GameData.bone_texture_path(bone_id)
	spr.texture = load(path) if ResourceLoader.exists(path) else null
	var rs: Dictionary = GameData.skeleton.get("rarity_scale", {})
	var k := float(GameData.skeleton.get("texture_scale", 0.5)) * float(rs.get(Body.instance_rarity(inst), 1.0))
	spr.scale = Vector2.ONE * k
	spr.visible = true


func _update_lowered(instant: bool) -> void:
	_target_lowered = 0.0 if equipped.has("slot_legs") else 96.0
	if instant:
		lowered = _target_lowered


func slot_global_position(slot: String) -> Vector2:
	var n: Node2D = slot_nodes.get(slot)
	if n == null:
		return global_position + Vector2(0, -170)
	var d: Dictionary = slot_defs.get(slot, {})
	var c := Vector2(d.canvas[0], d.canvas[1]) * 0.5 - Vector2(d.pivot[0], d.pivot[1])
	return n.to_global(c * float(GameData.skeleton.get("texture_scale", 0.5)))


func body_center_global() -> Vector2:
	return to_global(Vector2(0, -170 + lowered))


func slot_sprite(slot: String) -> Sprite2D:
	var n: Node2D = slot_nodes.get(slot)
	return n.get_node("Sprite") if n else null


# ----------------------------------------------------------- aura e forma

func refresh_aura() -> void:
	var counts := Body.family_counts(equipped)
	var best := ""
	var best_n := 0
	for f in counts:
		if int(counts[f]) > best_n:
			best_n = int(counts[f])
			best = f
	var forms := Body.active_forms(equipped)
	var new_form: String = forms[0] if not forms.is_empty() else ""
	if new_form != "":
		aura_color = Color(String(GameData.forms[new_form].get("aura", "#ffffff")))
		aura_strength = 1.0
	elif best != "":
		aura_color = GameData.family_color(best)
		aura_strength = clampf(0.25 + 0.2 * best_n, 0.0, 0.85)
	else:
		aura_color = Color(1.0, 0.72, 0.35)
		aura_strength = 0.15
	form_id = new_form
	var tint := Color.WHITE
	_form_scale = 1.0
	if form_id != "":
		var fd: Dictionary = GameData.forms[form_id]
		tint = Color(String(fd.get("tint", "#ffffff")))
		_form_scale = float(fd.get("scale", 1.0))
	_material.set_shader_parameter("tint", tint * skin_tint)
	var on: bool = Profile.setting("quality") != "low"
	_aura_particles.emitting = on and aura_strength >= 0.45
	var pm: ParticleProcessMaterial = _aura_particles.process_material
	pm.color = aura_color
	_aura_light.color = aura_color
	_aura_light.enabled = on


func set_skin_tint(c: Color) -> void:
	skin_tint = c
	refresh_aura()


## Aplica uma skin de data/skins.json: paleta, contorno, brilho e faíscas no
## shader de todos os ossos, mais os acessórios (chapéu, tapa-olho, coroa).
## id vazio = Ossinho normal.
func set_skin(id: String) -> void:
	skin_id = id
	var s: Dictionary = GameData.skins.get(id, {})
	var st: Dictionary = s.get("style", {})
	var tint := Color(String(s.get("tint", "#ffffff")))
	tint.a = 1.0
	skin_tint = tint
	_material.set_shader_parameter("remap", float(st.get("remap", 0.0)))
	_material.set_shader_parameter("pal_dark", Color(String(st.get("pal_dark", "#000000"))))
	_material.set_shader_parameter("pal_light", Color(String(st.get("pal_light", "#ffffff"))))
	_material.set_shader_parameter("rim", float(st.get("rim", 0.0)))
	_material.set_shader_parameter("rim_color", Color(String(st.get("rim_color", "#ffffff"))))
	_material.set_shader_parameter("rim_width", float(st.get("rim_width", 3.0)))
	_material.set_shader_parameter("pulse", float(st.get("pulse", 0.0)))
	_material.set_shader_parameter("sheen", float(st.get("sheen", 0.0)))
	_material.set_shader_parameter("sheen_color", Color(String(st.get("sheen_color", "#ffffff"))))
	var low: bool = Profile.setting("quality") == "low"
	_material.set_shader_parameter("sparkle", 0.0 if low else float(st.get("sparkle", 0.0)))
	_material.set_shader_parameter("skin_alpha", float(st.get("alpha", 1.0)))
	for a in _accessories:
		if is_instance_valid(a):
			a.queue_free()
	_accessories.clear()
	for acc_id in s.get("accessories", []):
		var def: Dictionary = GameData.accessories.get(acc_id, {})
		var bone: Node2D = slot_nodes.get(String(def.get("slot", "slot_skull")))
		if def.is_empty() or bone == null:
			continue
		var spr := Sprite2D.new()
		spr.texture = load("res://art/skins/%s.png" % acc_id)
		spr.position = Vector2(def.pos[0], def.pos[1])
		spr.scale = Vector2.ONE * float(def.get("scale", 0.5))
		spr.rotation_degrees = float(def.get("rot", 0.0))
		spr.z_index = int(def.get("z", 9))
		spr.light_mask = 2
		bone.add_child(spr)
		_accessories.append(spr)
	refresh_aura()


func flash(color: Color = Color.WHITE, strength: float = 1.0, time: float = 0.18) -> void:
	_material.set_shader_parameter("flash_color", color)
	_material.set_shader_parameter("flash", strength)
	var tw := create_tween()
	tw.tween_method(func(v): _material.set_shader_parameter("flash", v), strength, 0.0, time)


# ----------------------------------------------------------------- loop

func _process(delta: float) -> void:
	_t += delta
	lowered = lerpf(lowered, _target_lowered, clampf(delta * 8.0, 0.0, 1.0))
	var target_scale := _form_scale
	$Body.scale = $Body.scale.lerp(Vector2.ONE * target_scale, clampf(delta * 4.0, 0.0, 1.0))
	_aura.modulate = Color(aura_color, aura_strength * (0.32 + 0.08 * sin(_t * 2.4)))
	_aura.position = Vector2(0, -170 + lowered) * $Body.scale.y
	_aura_light.energy = aura_strength * (0.55 + 0.1 * sin(_t * 3.1))
	_aura_light.position = _aura.position
	_aura_particles.position = Vector2(0, -150 + lowered) * $Body.scale.y
	_shadow.scale = Vector2(3.2, 0.7) * $Body.scale.x
	if not idle_enabled:
		return
	var breath := sin(_t * 2.2)
	var upper := Vector2(0, breath * 2.5 + lowered)
	for p in base_nodes:
		var def := _base_def(p)
		var off := upper if p == "ossinho_spine" else Vector2(0, lowered)
		if not _busy_parts.has(p):
			base_nodes[p].position = Vector2(def.attach[0], def.attach[1]) + off
	for s in slot_nodes:
		if _busy_parts.has(s):
			continue
		var d: Dictionary = slot_defs[s]
		var n: Bone2D = slot_nodes[s]
		var pos := Vector2(d.attach[0], d.attach[1])
		var rot := float(d.get("rest_rot", 0))
		match String(d.get("tag", "")):
			"legs":
				pos.y += 0.0
			"tail":
				pos.y += lowered
				rot += sin(_t * 1.7) * 6.0
			"extra":
				pos.y += lowered
			"skull":
				pos += upper + Vector2(0, sin(_t * 2.2 - 0.6) * 1.5)
				rot += sin(_t * 1.1) * 2.0
			"arm":
				pos += upper
				rot += sin(_t * 2.2 + (0.8 if s == "slot_arm_left" else 0.0)) * 4.0
			"back":
				pos += upper
				n.scale.x = 1.0 + sin(_t * 3.0) * 0.06
			_:
				pos += upper
		n.position = pos
		n.rotation_degrees = rot
	if not equipped.has("slot_legs"):
		# sem pernas, o Ossinho dá pulinhos
		$Body.position.y = -absf(sin(_t * 3.2)) * 10.0
	else:
		$Body.position.y = lerpf($Body.position.y, 0.0, clampf(delta * 10.0, 0.0, 1.0))


func _base_def(id: String) -> Dictionary:
	for p in GameData.skeleton.get("base_parts", []):
		if p.id == id:
			return p
	return {}


# -------------------------------------------------------------- ações

func attack_anim(direction: float = 1.0, heavy: bool = false) -> void:
	var body: Node2D = $Body
	var tw := create_tween()
	var dist := 70.0 if heavy else 46.0
	tw.tween_property(body, "position:x", -10.0 * direction, 0.08).set_trans(Tween.TRANS_SINE)
	tw.tween_property(body, "position:x", dist * direction, 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(body, "position:x", 0.0, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	for arm in ["slot_arm_right", "slot_arm_left", "slot_arm_third"]:
		if not equipped.has(arm):
			continue
		var n: Bone2D = slot_nodes[arm]
		_busy_parts[arm] = true
		var base_rot := float(slot_defs[arm].get("rest_rot", 0))
		var tw2 := create_tween()
		tw2.tween_property(n, "rotation_degrees", base_rot + 60.0, 0.08)
		tw2.tween_property(n, "rotation_degrees", base_rot - 95.0, 0.09).set_trans(Tween.TRANS_QUAD)
		tw2.tween_property(n, "rotation_degrees", base_rot, 0.22).set_trans(Tween.TRANS_BACK)
		tw2.finished.connect(func(): _busy_parts.erase(arm))


func hit_anim(direction: float = -1.0) -> void:
	flash(Color(1, 0.35, 0.3), 0.85, 0.22)
	var body: Node2D = $Body
	var tw := create_tween()
	tw.tween_property(body, "position:x", 22.0 * direction, 0.06)
	tw.tween_property(body, "position:x", 0.0, 0.2).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	var tw2 := create_tween()
	tw2.tween_property(body, "rotation_degrees", 6.0 * direction, 0.06)
	tw2.tween_property(body, "rotation_degrees", 0.0, 0.25).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)


func dodge_anim() -> void:
	var body: Node2D = $Body
	var tw := create_tween()
	tw.tween_property(body, "position", Vector2(-40, -30), 0.1).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(body, "position", Vector2.ZERO, 0.2).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	var tw2 := create_tween()
	modulate.a = 1.0
	tw2.tween_property(self, "modulate:a", 0.45, 0.06)
	tw2.tween_property(self, "modulate:a", 1.0, 0.2)


func victory_anim() -> void:
	var body: Node2D = $Body
	var tw := create_tween()
	tw.tween_property(body, "position:y", -50.0, 0.18).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(body, "position:y", 0.0, 0.3).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)


## Desmonta o Ossinho: cada peça cai e quica (morte).
func collapse_anim() -> void:
	idle_enabled = false
	var i := 0
	for s in slot_nodes:
		var n: Node2D = slot_nodes[s]
		if not n.get_node("Sprite").visible:
			continue
		var tw := create_tween().set_parallel(true)
		var fall := -n.position.y - 10.0
		tw.tween_property(n, "position:y", n.position.y + fall, 0.45 + i * 0.04).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
		tw.tween_property(n, "position:x", n.position.x + randf_range(-60, 60), 0.5)
		tw.tween_property(n, "rotation_degrees", randf_range(-120, 120), 0.5)
		i += 1
	for p in base_nodes:
		var n2: Node2D = base_nodes[p]
		var tw2 := create_tween().set_parallel(true)
		tw2.tween_property(n2, "position:y", -10.0, 0.5).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
		tw2.tween_property(n2, "rotation_degrees", 90.0 if p == "ossinho_spine" else 0.0, 0.5)


## Remonta depois de reviver.
func reassemble() -> void:
	idle_enabled = true
	modulate = Color.WHITE
	flash(Color(1, 0.9, 0.6), 1.0, 0.6)


## Flutua (transformação em câmera lenta).
func float_up(height: float = 60.0, time: float = 0.8) -> Tween:
	var body: Node2D = $Body
	var tw := create_tween()
	tw.tween_property(body, "position:y", -height, time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	return tw


func land(time: float = 0.35) -> void:
	var tw := create_tween()
	tw.tween_property($Body, "position:y", 0.0, time).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)


## Brilho no encaixe recém-preenchido.
func pop_slot(slot: String) -> void:
	var n: Node2D = slot_nodes.get(slot)
	if n == null:
		return
	_busy_parts[slot] = true
	var spr: Sprite2D = n.get_node("Sprite")
	var base := spr.scale
	spr.scale = base * 1.6
	var tw := create_tween()
	tw.tween_property(spr, "scale", base, 0.35).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	tw.finished.connect(func(): _busy_parts.erase(slot))
	flash(Color(1, 0.95, 0.75), 0.9, 0.4)
	bone_attached.emit(slot)
