extends Node
## Perfil persistente do jogador (user://profile.json).
## Guarda moedas, progressão permanente, coleções, calendários, loja e opções.

signal changed
signal currency_changed

const SAVE_PATH := "user://profile.json"
const SAVE_VERSION := 1

var data: Dictionary = {}


func _ready() -> void:
	load_profile()
	apply_locale()


func defaults() -> Dictionary:
	return {
		"version": SAVE_VERSION,
		"settings": {"locale": "", "vibration": true, "quality": "high", "fast_combat": false},
		"dust": 0,
		"diamonds": 0,
		"runs_played": 0,
		"best_index": 0,
		"first_open_time": 0,
		"ossuary": {"hp": 0, "atk": 0, "def": 0, "drop": 0},
		"discovered_bones": {},
		"discovered_forms": {},
		"bosses_defeated": {},
		"companions": {"companion_ossudo": {"unlocked": true, "level": 1}},
		"selected_companion": "companion_ossudo",
		"relics": {"owned": [], "equipped": {}, "next_uid": 1},
		"cabinet": {},
		"hunter": {"stolen": []},
		"starting_bone": "",
		"rare_start_tokens": 0,
		"extra_revives": 0,
		"login": {"first7_claimed": 0, "first7_last_day": -1, "cycle_claimed": 0, "cycle_last_day": -1},
		"shop": {"daily_day": -1, "daily_bought": [], "ad_day": -1, "ad_count": 0, "chest_ad_day": -1, "chest_ad_count": 0, "purchases": {}},
		"kit24": {"offered": false, "bought": false},
		"skins": {"owned": [], "equipped": ""},
		"ads": {"interstitials_seen": 0, "last_interstitial": 0, "removed": false},
		"subscription": {"until": 0, "last_daily_day": -1, "last_chest_week": -1, "free_revive_day": -1},
		"supporter": false,
		"bigorna_used_run": false,
	}


func load_profile() -> void:
	data = defaults()
	if FileAccess.file_exists(SAVE_PATH):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
		if typeof(parsed) == TYPE_DICTIONARY:
			_merge(data, parsed)
	if int(data.first_open_time) == 0:
		data.first_open_time = Backend.now()
		save()
	if OS.get_environment("BT_SAMPLE_PROFILE") == "1":
		_sample_profile()


## Ferramenta de desenvolvimento: perfil de exemplo para capturas de tela.
func _sample_profile() -> void:
	data.dust = 2480
	data.diamonds = 365
	for id in ["bone_skull_wolf", "bone_claw_bear", "bone_legs_spider", "bone_wings_bat", "bone_tail_scorpion", "bone_tail_rat", "bone_ribs_turtle", "bone_pincer_crab", "bone_stinger_wasp", "bone_legs_grasshopper", "bone_shell_beetle", "bone_blade_mantis", "bone_legs_centaur"]:
		data.discovered_bones[id] = true
	for id in ["form_night_manticore", "form_werewolf", "form_swarm_queen"]:
		data.discovered_forms[id] = true
	data.ossuary = {"hp": 4, "atk": 5, "def": 2, "drop": 1}
	data.companions["companion_lumi"] = {"unlocked": true, "level": 3}
	data.companions["companion_ossudo"] = {"unlocked": true, "level": 2}
	data.selected_companion = "companion_lumi"
	data.starting_bone = "bone_skull_wolf"
	data.relics = {"owned": [{"uid": 1, "id": "relic_moon_amulet", "level": 3}, {"uid": 2, "id": "relic_knuckle_ring", "level": 2}, {"uid": 3, "id": "relic_gravedigger_lantern", "level": 1}], "equipped": {"relic_amulet": 1, "relic_ring": 2, "relic_lantern": 3}, "next_uid": 4}
	data.cabinet = {"cur_melted_candle": 2, "cur_holed_coin": 1, "cur_gold_tooth": 3, "cur_rusty_shovel": 1, "cur_holed_hat": 1, "cur_loaded_die": 4, "cur_bone_goblet": 1}
	data.hunter = {"stolen": [{"id": "bone_blade_mantis", "level": 1}, {"id": "bone_wings_bat", "level": 2}]}


func _merge(base: Dictionary, incoming: Dictionary) -> void:
	for k in incoming:
		if base.has(k) and typeof(base[k]) == TYPE_DICTIONARY and typeof(incoming[k]) == TYPE_DICTIONARY:
			# Dicionários de configuração mesclam; coleções (ids livres) substituem.
			if base[k].is_empty():
				base[k] = incoming[k]
			else:
				_merge(base[k], incoming[k])
		else:
			base[k] = incoming[k]


func save() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data, "\t"))
	changed.emit()


func reset() -> void:
	data = defaults()
	data.first_open_time = Backend.now()
	save()
	currency_changed.emit()


# ------------------------------------------------------------------ idioma

func apply_locale() -> void:
	var loc: String = data.settings.get("locale", "")
	if loc == "":
		var os_loc := OS.get_locale()
		if os_loc.begins_with("pt"):
			loc = "pt_BR"
		elif os_loc.begins_with("es"):
			loc = "es_419"
		else:
			loc = "en_US"
	TranslationServer.set_locale(_engine_locale(loc))


func set_locale(loc: String) -> void:
	data.settings.locale = loc
	apply_locale()
	save()


func current_locale() -> String:
	var l := TranslationServer.get_locale()
	if l.begins_with("pt"):
		return "pt_BR"
	if l.begins_with("es"):
		return "es_419"
	return "en_US"


func _engine_locale(loc: String) -> String:
	# O Godot normaliza es_419 para "es" (ver docs/DECISOES.md).
	return "es" if loc == "es_419" else loc


func setting(key: String) -> Variant:
	return data.settings.get(key)


func set_setting(key: String, value: Variant) -> void:
	data.settings[key] = value
	save()


# ------------------------------------------------------------------ moedas

func dust() -> int:
	return int(data.dust)


func diamonds() -> int:
	return int(data.diamonds)


func add_dust(amount: int, source: String = "") -> void:
	data.dust = max(0, int(data.dust) + amount)
	Backend.log_event("currency_dust", {"amount": amount, "source": source})
	save()
	currency_changed.emit()


func spend_dust(amount: int, reason: String = "") -> bool:
	if int(data.dust) < amount:
		return false
	add_dust(-amount, reason)
	return true


func add_diamonds(amount: int, source: String = "") -> void:
	data.diamonds = max(0, int(data.diamonds) + amount)
	Backend.log_event("currency_diamonds", {"amount": amount, "source": source})
	save()
	currency_changed.emit()


func spend_diamonds(amount: int, reason: String = "") -> bool:
	if int(data.diamonds) < amount:
		return false
	add_diamonds(-amount, reason)
	return true


# ------------------------------------------------------------ descobertas

func discover_bone(id: String) -> bool:
	if data.discovered_bones.has(id):
		return false
	data.discovered_bones[id] = true
	save()
	return true


func is_bone_discovered(id: String) -> bool:
	return data.discovered_bones.has(id)


func discover_form(id: String) -> bool:
	if data.discovered_forms.has(id):
		return false
	data.discovered_forms[id] = true
	save()
	return true


func is_form_discovered(id: String) -> bool:
	return data.discovered_forms.has(id)


func boss_wins(boss_id: String) -> int:
	return int(data.bosses_defeated.get(boss_id, 0))


func register_boss_win(boss_id: String) -> void:
	data.bosses_defeated[boss_id] = boss_wins(boss_id) + 1
	save()
