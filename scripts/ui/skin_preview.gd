class_name SkinPreview
extends TextureRect
## Prévia de uma skin: um Ossinho de verdade, com a skin aplicada, num halo da cor dela.

var skin_id := ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var vp := SubViewport.new()
	vp.transparent_bg = true
	vp.size = Vector2i(260, 300)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var s: Dictionary = GameData.skins.get(skin_id, {})
	var halo := Sprite2D.new()
	halo.texture = load("res://art/fx/fx_light.png")
	halo.position = Vector2(130, 170)
	halo.scale = Vector2.ONE * 1.1
	halo.modulate = Color(Color(String(s.get("glow", "#ffffff"))), 0.55)
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	halo.material = add
	vp.add_child(halo)
	var o: OssinhoView = load("res://scenes/Ossinho.tscn").instantiate()
	o.position = Vector2(130, 292)
	o.scale = Vector2.ONE * 0.82
	vp.add_child(o)
	var tint := Color(String(s.get("tint", "#ffffff")))
	tint.a = float(s.get("alpha", 1.0))
	o.set_skin_tint(tint)
	texture = vp.get_texture()
