class_name SkinPreview
extends TextureRect
## Prévia de uma skin: um Ossinho de verdade com o corpo montado (para mostrar
## que a skin vale para todos os ossos), a skin aplicada e um halo da cor dela.

const SAMPLE_BODY := {
	"slot_skull": "bone_skull_wolf",
	"slot_ribs": "bone_ribs_turtle",
	"slot_arm_left": "bone_claw_bear",
	"slot_arm_right": "bone_claw_bear",
	"slot_legs": "bone_legs_spider",
	"slot_back": "bone_wings_bat",
	"slot_tail": "bone_tail_scorpion",
}

var skin_id := ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var vp := SubViewport.new()
	vp.transparent_bg = true
	vp.size = Vector2i(320, 380)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var s: Dictionary = GameData.skins.get(skin_id, {})
	var halo := Sprite2D.new()
	halo.texture = load("res://art/fx/fx_light.png")
	halo.position = Vector2(160, 210)
	halo.scale = Vector2.ONE * 1.5
	halo.modulate = Color(Color(String(s.get("glow", "#ffffff"))), 0.7)
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	halo.material = add
	vp.add_child(halo)
	var o: OssinhoView = load("res://scenes/Ossinho.tscn").instantiate()
	o.position = Vector2(160, 352)
	o.scale = Vector2.ONE * 0.86
	vp.add_child(o)
	o.set_equipped(SAMPLE_BODY.duplicate())
	o.set_skin(skin_id)
	texture = vp.get_texture()
