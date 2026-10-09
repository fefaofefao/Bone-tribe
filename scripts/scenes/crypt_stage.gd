class_name CryptStage
extends Node2D
## Cenário da Cripta Esquecida: fundo pintado, velas com luz 2D dinâmica,
## brasas e poeira no ar, e um escurecedor para momentos cinematográficos.
## Na qualidade baixa, a luz dinâmica e as partículas extras são desligadas.

const CANDLES := [
	{"pos": Vector2(84, 760), "scale": 0.6},
	{"pos": Vector2(690, 768), "scale": 0.64},
	{"pos": Vector2(150, 630), "scale": 0.3},
	{"pos": Vector2(560, 630), "scale": 0.3},
]

var modulate_node: CanvasModulate
var dimmer: ColorRect
var lights: Array = []
var _t := 0.0
var _flames: Array = []
var low := false
## Cor do ambiente (cada torre tem a sua); transparente = cor padrão.
var tint := Color(0, 0, 0, 0)


func _ready() -> void:
	low = Profile.setting("quality") == "low"
	var bg := Sprite2D.new()
	bg.texture = load("res://art/env/env_forgotten_crypt.png")
	bg.centered = false
	bg.position = Vector2(0, 0)
	bg.z_index = -100
	add_child(bg)
	# extensão para telas mais altas que 16:9
	var ext := ColorRect.new()
	ext.color = Color(0.04, 0.03, 0.05)
	ext.position = Vector2(-400, 1280)
	ext.size = Vector2(1520, 800)
	ext.z_index = -101
	add_child(ext)
	var ext2 := ColorRect.new()
	ext2.color = Color(0.04, 0.03, 0.05)
	ext2.position = Vector2(-400, -800)
	ext2.size = Vector2(1520, 800)
	ext2.z_index = -101
	add_child(ext2)

	modulate_node = CanvasModulate.new()
	modulate_node.color = (tint if tint.a > 0.0 else Color(0.58, 0.53, 0.64)) if not low else Color(0.92, 0.9, 0.96)
	add_child(modulate_node)

	for prop in [["env_tombstone", Vector2(40, 770), 0.6], ["env_bone_pile", Vector2(600, 790), 0.55], ["env_tombstone", Vector2(700, 780), 0.5]]:
		var s := Sprite2D.new()
		s.texture = load("res://art/env/%s.png" % prop[0])
		s.centered = true
		s.offset = Vector2(0, -s.texture.get_height() * 0.5)
		s.position = prop[1]
		s.scale = Vector2.ONE * float(prop[2])
		s.z_index = -40
		add_child(s)

	for c in CANDLES:
		_add_candle(c.pos, c.scale)

	if not low:
		_add_ambient()

	dimmer = ColorRect.new()
	dimmer.color = Color(0.02, 0.01, 0.03, 0.0)
	dimmer.position = Vector2(-400, -800)
	dimmer.size = Vector2(1520, 2880)
	dimmer.z_index = -2
	dimmer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dimmer)


func _add_candle(pos: Vector2, k: float) -> void:
	var candle := Sprite2D.new()
	candle.texture = load("res://art/env/env_candle.png")
	candle.centered = true
	candle.offset = Vector2(0, -75)
	candle.position = pos
	candle.scale = Vector2.ONE * k
	candle.z_index = -30
	add_child(candle)
	var flame := Sprite2D.new()
	flame.texture = load("res://art/fx/fx_flame.png")
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	flame.material = add
	flame.position = pos + Vector2(0, -132 * k)
	flame.scale = Vector2.ONE * k * 1.2
	flame.offset = Vector2(0, -20)
	flame.z_index = -29
	add_child(flame)
	_flames.append({"n": flame, "k": k, "phase": randf() * TAU})
	if low:
		return
	var light := PointLight2D.new()
	light.texture = load("res://art/fx/fx_light.png")
	light.position = flame.position + Vector2(0, -10)
	light.texture_scale = 1.6 + k * 2.4
	light.color = Color(1.0, 0.72, 0.42)
	light.energy = 0.9
	light.range_item_cull_mask = 1 | 2
	add_child(light)
	lights.append({"n": light, "base": 0.45 + k * 0.5, "phase": randf() * TAU})
	var emb := GPUParticles2D.new()
	emb.amount = 6
	emb.lifetime = 2.2
	emb.position = flame.position
	emb.texture = load("res://art/fx/fx_ember.png")
	emb.material = add
	emb.z_index = -28
	var pm := ParticleProcessMaterial.new()
	pm.direction = Vector3(0, -1, 0)
	pm.spread = 20.0
	pm.initial_velocity_min = 18.0
	pm.initial_velocity_max = 40.0
	pm.gravity = Vector3(0, -6, 0)
	pm.scale_min = 0.2
	pm.scale_max = 0.5
	pm.color = Color(1, 0.6, 0.25)
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1, 1, 1, 1))
	ramp.set_color(1, Color(1, 1, 1, 0))
	var rt := GradientTexture1D.new()
	rt.gradient = ramp
	pm.color_ramp = rt
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 2.0
	emb.process_material = pm
	add_child(emb)


func _add_ambient() -> void:
	var dust := GPUParticles2D.new()
	dust.amount = 40
	dust.lifetime = 9.0
	dust.preprocess = 9.0
	dust.position = Vector2(360, 500)
	dust.texture = load("res://art/fx/fx_soft.png")
	dust.z_index = -20
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(380, 360, 1)
	pm.direction = Vector3(1, -0.2, 0)
	pm.spread = 60.0
	pm.initial_velocity_min = 4.0
	pm.initial_velocity_max = 14.0
	pm.gravity = Vector3(0, 0, 0)
	pm.scale_min = 0.05
	pm.scale_max = 0.14
	pm.color = Color(1, 0.9, 0.75, 0.35)
	var ramp := Gradient.new()
	ramp.offsets = PackedFloat32Array([0.0, 0.3, 0.7, 1.0])
	ramp.colors = PackedColorArray([Color(1, 1, 1, 0), Color(1, 1, 1, 1), Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
	var rt := GradientTexture1D.new()
	rt.gradient = ramp
	pm.color_ramp = rt
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 1.5
	pm.turbulence_noise_scale = 3.0
	dust.process_material = pm
	add_child(dust)
	# brasas subindo pelo ar
	var emb := GPUParticles2D.new()
	emb.amount = 18
	emb.lifetime = 7.0
	emb.preprocess = 7.0
	emb.position = Vector2(360, 900)
	emb.texture = load("res://art/fx/fx_ember.png")
	emb.z_index = -15
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	emb.material = add
	var em := ParticleProcessMaterial.new()
	em.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	em.emission_box_extents = Vector3(380, 40, 1)
	em.direction = Vector3(0.2, -1, 0)
	em.spread = 25.0
	em.initial_velocity_min = 25.0
	em.initial_velocity_max = 60.0
	em.gravity = Vector3(0, -4, 0)
	em.scale_min = 0.25
	em.scale_max = 0.6
	em.color = Color(1, 0.55, 0.2, 0.9)
	em.color_ramp = rt
	em.turbulence_enabled = true
	em.turbulence_noise_strength = 3.0
	em.turbulence_noise_scale = 2.0
	emb.process_material = em
	add_child(emb)
	# névoa rasteira
	var fog := GPUParticles2D.new()
	fog.amount = 10
	fog.lifetime = 12.0
	fog.preprocess = 12.0
	fog.position = Vector2(360, 780)
	fog.texture = load("res://art/fx/fx_smoke.png")
	fog.z_index = -25
	var fm := ParticleProcessMaterial.new()
	fm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	fm.emission_box_extents = Vector3(420, 20, 1)
	fm.direction = Vector3(1, 0, 0)
	fm.spread = 10.0
	fm.initial_velocity_min = 6.0
	fm.initial_velocity_max = 14.0
	fm.gravity = Vector3.ZERO
	fm.scale_min = 2.0
	fm.scale_max = 3.5
	fm.color = Color(0.7, 0.62, 0.8, 0.1)
	fm.color_ramp = rt
	fog.process_material = fm
	add_child(fog)


func _process(delta: float) -> void:
	_t += delta
	for f in _flames:
		var n: Sprite2D = f.n
		var k: float = f.k
		var flick := 1.0 + sin(_t * 9.0 + f.phase) * 0.06 + sin(_t * 23.0 + f.phase * 2.0) * 0.04
		n.scale = Vector2(k * 1.2 * (2.0 - flick), k * 1.2 * flick)
	for l in lights:
		var n2: PointLight2D = l.n
		n2.energy = float(l.base) * (1.0 + sin(_t * 7.0 + l.phase) * 0.08 + sin(_t * 17.0 + l.phase) * 0.05)


## Escurece o cenário (0 = normal, 1 = escuro).
func dim(amount: float, time := 0.4) -> Tween:
	var tw := create_tween()
	tw.tween_property(dimmer, "color:a", amount * 0.82, time)
	return tw
