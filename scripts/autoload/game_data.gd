extends Node
## Carrega todos os dados do jogo de res://data/*.json.
## Nada de conteúdo fica no código: ossos, monstros, eventos, formas, bônus,
## companheiros, relíquias, curiosidades, loja e calendários vivem nos JSON.

const DATA_DIR := "res://data/"

var balance: Dictionary = {}
var skeleton: Dictionary = {}
var families: Dictionary = {}
var bones: Dictionary = {}
var monsters: Dictionary = {}
var events: Dictionary = {}
var forms: Dictionary = {}
var levelups: Dictionary = {}
var companions: Dictionary = {}
var relics: Dictionary = {}
var curiosities: Dictionary = {}
var curiosity_sets: Dictionary = {}
var shop: Dictionary = {}
var login: Dictionary = {}
var skins: Dictionary = {}
var app: Dictionary = {}
var admob: Dictionary = {}

var bone_order: Array = []
var monster_order: Array = []
var event_order: Array = []
var form_order: Array = []
var load_errors: Array = []


func _ready() -> void:
	reload()


func reload() -> void:
	load_errors.clear()
	balance = _read("balance.json", {})
	skeleton = _read("skeleton.json", {})
	families = _index(_read("families.json", []), [])
	bone_order = []
	bones = _index(_read("bones.json", []), bone_order)
	monster_order = []
	monsters = _index(_read("monsters.json", []), monster_order)
	event_order = []
	events = _index(_read("events.json", []), event_order)
	form_order = []
	forms = _index(_read("forms.json", []), form_order)
	levelups = _index(_read("levelup.json", []), [])
	companions = _index(_read("companions.json", []), [])
	relics = _index(_read("relics.json", []), [])
	var cab: Dictionary = _read("curiosities.json", {})
	curiosities = _index(cab.get("items", []), [])
	curiosity_sets = _index(cab.get("sets", []), [])
	shop = _read("shop.json", {})
	login = _read("login.json", {})
	skins = _index(_read("skins.json", []), [])
	app = _read("app.json", {})
	admob = _read("admob.json", {})
	for e in load_errors:
		push_error(e)


func _read(file: String, fallback: Variant) -> Variant:
	var path := DATA_DIR + file
	if not FileAccess.file_exists(path):
		return fallback
	var text := FileAccess.get_file_as_string(path)
	var json := JSON.new()
	var err := json.parse(text)
	if err != OK:
		load_errors.append("%s:%d %s" % [path, json.get_error_line(), json.get_error_message()])
		return fallback
	return json.data


func _index(list: Array, order: Array) -> Dictionary:
	var out := {}
	for item in list:
		if typeof(item) != TYPE_DICTIONARY or not item.has("id"):
			continue
		out[item.id] = item
		order.append(item.id)
	return out


# ---------------------------------------------------------------- consultas

func bal(path: String, fallback: Variant = null) -> Variant:
	var node: Variant = balance
	for part in path.split("/"):
		if typeof(node) != TYPE_DICTIONARY or not node.has(part):
			return fallback
		node = node[part]
	return node


func bone(id: String) -> Dictionary:
	return bones.get(id, {})


func monster(id: String) -> Dictionary:
	return monsters.get(id, {})


func slots() -> Array:
	return skeleton.get("slots", [])


func slot_def(slot_id: String) -> Dictionary:
	for s in slots():
		if s.id == slot_id:
			return s
	return {}


func bone_slots(bone_id: String) -> Array:
	var b := bone(bone_id)
	if b.has("slots"):
		return b.slots
	return [b.get("slot", "")]


func family_color(family_id: String) -> Color:
	var f: Dictionary = families.get(family_id, {})
	return Color(f.get("aura", "#e8dcc0"))


func bones_by(filter: Dictionary) -> Array:
	var out := []
	for id in bone_order:
		var b: Dictionary = bones[id]
		if b.get("rarity", "") == "basic":
			continue
		var ok := true
		for k in filter:
			var v: Variant = filter[k]
			if k == "slot":
				if not bone_slots(id).has(v):
					ok = false
			elif k == "rarities":
				if not (v as Array).has(b.get("rarity", "")):
					ok = false
			elif b.get(k) != v:
				ok = false
		if ok:
			out.append(id)
	return out


func bone_texture_path(bone_id: String) -> String:
	return "res://art/bones/%s.png" % bone_id


func monster_texture_path(monster_id: String) -> String:
	return "res://art/monsters/%s.png" % monster_id


func catalog_bones() -> Array:
	## Os 20 ossos do catálogo (sem os básicos).
	return bones_by({})
