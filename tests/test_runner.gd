extends Node
## Testes automáticos (rodados no CI antes do build do AAB):
##   godot --headless --path . res://tests/TestRunner.tscn
## Sai com código 0 se tudo passar, 1 se algo falhar.

var failures: Array = []
var checks := 0


func _ready() -> void:
	for f in _suites():
		call(f)
	print("")
	print("Testes: %d verificações, %d falhas" % [checks, failures.size()])
	for msg in failures:
		print("  FALHA: ", msg)
	get_tree().quit(1 if failures.size() > 0 else 0)


func _suites() -> Array:
	var out := []
	for m in get_method_list():
		if String(m.name).begins_with("test_"):
			out.append(m.name)
	out.sort()
	return out


func check(cond: bool, msg: String) -> void:
	checks += 1
	if not cond:
		failures.append(msg)


func tr_all(key: String) -> bool:
	for loc in ["pt_BR", "en_US", "es"]:
		TranslationServer.set_locale(loc)
		if TranslationServer.translate(key) == key:
			Profile.apply_locale()
			return false
	Profile.apply_locale()
	return true


func test_00_data_loaded() -> void:
	check(GameData.load_errors.is_empty(), "erros ao ler JSON: %s" % [GameData.load_errors])
	check(not GameData.skeleton.is_empty(), "skeleton.json carregado")


func test_01_i18n_basics() -> void:
	for key in ["hero_name", "game_title"]:
		check(tr_all(key), "tradução em 3 idiomas: " + key)
	TranslationServer.set_locale("pt_BR")
	check(TranslationServer.translate("hero_name") == "Ossinho", "hero_name pt_BR = Ossinho")
	TranslationServer.set_locale("en_US")
	check(TranslationServer.translate("hero_name") == "Bonesy", "hero_name en_US = Bonesy")
	TranslationServer.set_locale("es")
	check(TranslationServer.translate("hero_name") == "Huesito", "hero_name es_419 = Huesito")
	Profile.apply_locale()


func test_02_data_integrity() -> void:
	for id in GameData.bones:
		var b: Dictionary = GameData.bones[id]
		for f in ["name", "desc", "name_part", "adjective"]:
			check(b.has(f) and tr_all(String(b[f])), "osso %s campo %s traduzido" % [id, f])
		for s in GameData.bone_slots(id):
			check(not GameData.slot_def(s).is_empty(), "osso %s encaixe %s existe" % [id, s])
		if String(b.get("monster", "")) != "":
			check(GameData.monsters.has(b.monster), "osso %s monstro %s existe" % [id, b.monster])
		check(ResourceLoader.exists(GameData.bone_texture_path(id)), "arte do osso " + id)
	for id in GameData.monsters:
		var m: Dictionary = GameData.monsters[id]
		check(tr_all(String(m.get("name", ""))), "nome do monstro " + id)
		for d in m.get("drops", []):
			check(GameData.bones.has(d), "monstro %s solta %s" % [id, d])
		check(ResourceLoader.exists(GameData.monster_texture_path(id)), "arte do monstro " + id)
	for id in GameData.levelups:
		check(tr_all(GameData.levelups[id].name) and tr_all(GameData.levelups[id].desc), "textos do bônus " + id)
	for id in GameData.forms:
		check(tr_all(GameData.forms[id].name) and tr_all(GameData.forms[id].desc), "textos da forma " + id)
	for id in GameData.events:
		_check_event(GameData.events[id])


func _check_event(ev: Dictionary) -> void:
	check(tr_all(String(ev.get("text", ""))), "texto do evento " + String(ev.id))
	for o in ev.get("options", []):
		check(tr_all(String(o.get("label", ""))), "opção %s de %s" % [o.get("label", ""), ev.id])
		_check_actions(ev.id, o.get("actions", []))


func _check_actions(eid: String, actions: Array) -> void:
	for a in actions:
		match String(a.get("do", "")):
			"result":
				check(tr_all(String(a.get("text", ""))), "resultado %s em %s" % [a.get("text", ""), eid])
			"combat":
				for m in a.get("monsters", []):
					check(GameData.monsters.has(m), "monstro %s em %s" % [m, eid])
			"bone":
				if a.has("id"):
					check(GameData.bones.has(a.id), "osso %s em %s" % [a.id, eid])
			"chance":
				_check_actions(eid, a.get("then", []))
				_check_actions(eid, a.get("else", []))
			"roll":
				for row in a.get("table", []):
					_check_actions(eid, row.get("actions", []))


func test_03_body_and_forms() -> void:
	var eq := {"slot_skull": {"id": "bone_skull_wolf", "level": 1}, "slot_back": {"id": "bone_wings_bat", "level": 1}, "slot_tail": {"id": "bone_tail_scorpion", "level": 1}, "slot_legs": {"id": "bone_legs_spider", "level": 1}}
	var forms := Body.active_forms(eq)
	check(forms.has("form_night_manticore"), "Manticora Noturna ativa com lobo+morcego+escorpião")
	var hero := Body.make_hero(eq)
	check(absf(hero.crit - 0.20) < 0.001, "crítico 5% + 15% do Crânio de Lobo")
	check(absf(hero.dodge - 0.25) < 0.001, "esquiva das Patas de Aranha")
	check(hero.has_effect("crit_status"), "efeito da Manticora no lutador")
	TranslationServer.set_locale("pt_BR")
	check(Body.creature_name(eq) == "Lobo-Aranha Venenoso", "nome pt_BR: " + Body.creature_name(eq))
	TranslationServer.set_locale("en_US")
	check(Body.creature_name(eq) == "Venomous Wolf-Spider", "nome en_US: " + Body.creature_name(eq))
	TranslationServer.set_locale("es")
	check(Body.creature_name(eq) == "Lobo-Araña Venenoso", "nome es_419: " + Body.creature_name(eq))
	TranslationServer.set_locale("pt_BR")
	check(Body.creature_name({}) == "Osso-Osso Ossudo", "nome com encaixes vazios: " + Body.creature_name({}))
	Profile.apply_locale()


func test_04_combat() -> void:
	var e := MonsterFactory.make("monster_crypt_wolf", 1)
	check(absf(MonsterFactory.enemy_hp(1) - 33.6) < 0.01, "vida do inimigo no andar 1 = 33,6")
	check(absf(MonsterFactory.enemy_atk(1) - 5.5) < 0.01, "ataque do inimigo no andar 1 = 5,5")
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var wins := 0
	for i in 20:
		var hero := Body.make_hero({})
		var c := Combat.new(hero, [MonsterFactory.make("monster_crypt_wolf", 1)], {"rng": rng})
		if c.run_to_end() == "win":
			wins += 1
	check(wins >= 15, "Ossinho básico vence o lobo do andar 1 na maioria das vezes (%d/20)" % wins)
	var boss := MonsterFactory.make("boss_rat_king", 10)
	check(boss.is_boss and boss.max_hp > e.max_hp * 5, "Rei Rato é chefe e tem vida de chefe")
	var hero2 := Body.make_hero({})
	hero2.max_hp = 99999
	hero2.hp = 99999
	var c2 := Combat.new(hero2, [boss], {"rng": rng, "max_turns": 99})
	var summoned := false
	for t in 6:
		for ev in c2.step():
			if ev.t == "summon":
				summoned = true
	check(summoned, "Rei Rato invoca ratos a cada 3 turnos")


func test_05_all_scripts_compile() -> void:
	var files := []
	_collect("res://scripts", files)
	for f in files:
		var s: Script = load(f)
		check(s != null and s.can_instantiate(), "script compila: " + f)
	for scene in ["res://scenes/TitleScreen.tscn", "res://scenes/Run.tscn", "res://scenes/Ossinho.tscn", "res://scenes/CreatureCard.tscn"]:
		var ps: PackedScene = load(scene)
		check(ps != null and ps.can_instantiate(), "cena carrega: " + scene)


func _collect(dir: String, out: Array) -> void:
	var d := DirAccess.open(dir)
	if d == null:
		return
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir + "/" + f)
	for sub in d.get_directories():
		_collect(dir + "/" + sub, out)
