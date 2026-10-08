class_name FormSilhouette
extends Control
## Ilustração de uma forma no Bestiário: halo na cor da aura e o osso-símbolo.
## Formas não descobertas aparecem como silhuetas escuras.

var form_id := ""
var known := false
var _tex: Texture2D
var _halo: Texture2D = preload("res://art/fx/fx_soft.png")


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var f: Dictionary = GameData.forms.get(form_id, {})
	var bone_id := ""
	if f.has("family"):
		var list := GameData.bones_by({"family": String(f.family)})
		bone_id = list[list.size() - 1] if not list.is_empty() else ""
	elif f.get("recipe", {}).has("bones"):
		bone_id = String(f.recipe.bones[0])
	else:
		bone_id = "bone_skull_basic"
	_tex = load(GameData.bone_texture_path(bone_id))


func _draw() -> void:
	var f: Dictionary = GameData.forms.get(form_id, {})
	var col := Color(String(f.get("aura", "#ffffff")))
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.62
	if known:
		draw_texture_rect(_halo, Rect2(c - Vector2(r, r), Vector2(r, r) * 2), false, Color(col, 0.75))
	if _tex:
		var ts := _tex.get_size()
		var k := minf(size.y * 0.95 / ts.y, size.x * 0.8 / ts.x)
		var sz := ts * k
		draw_texture_rect(_tex, Rect2(c - sz * 0.5, sz), false, Color.WHITE if known else Color(0, 0, 0, 0.8))
