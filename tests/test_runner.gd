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
			"ally":
				check(GameData.monsters.has(a.get("id", "")) and GameData.monsters[a.id].kind == "ally", "aliado %s em %s" % [a.get("id", ""), eid])
			"dust", "dust_mult", "pay", "lose_current_pct", "heal_pct", "max_hp_pct", "stat", "trap", "skip", "merchant", "sell_bone", "altar", "upgrade_bone", "xp":
				pass

			"chance":
				_check_actions(eid, a.get("then", []))
				_check_actions(eid, a.get("else", []))
			"roll":
				for row in a.get("table", []):
					_check_actions(eid, row.get("actions", []))
			_:
				check(false, "ação desconhecida %s em %s" % [a.get("do", ""), eid])


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


func _eq(pairs: Array) -> Dictionary:
	var out := {}
	for p in pairs:
		out[p[0]] = {"id": p[1], "level": int(p[2]) if p.size() > 2 else 1}
	return out


func test_06_catalog_counts() -> void:
	var cat := GameData.catalog_bones()
	check(cat.size() == 20, "20 ossos no catálogo (%d)" % cat.size())
	var r := {"common": 0, "rare": 0, "legendary": 0}
	for id in cat:
		r[GameData.bones[id].rarity] += 1
	check(r.common == 12 and r.rare == 5 and r.legendary == 3, "12 comuns, 5 raros, 3 lendários: %s" % [r])
	var fams := {}
	for id in cat:
		fams[GameData.bones[id].family] = true
	check(fams.size() == 6, "6 famílias cobertas")
	var commons := 0
	var bosses := []
	for id in GameData.monsters:
		var k: String = GameData.monsters[id].kind
		if k == "common" or k == "rare":
			commons += 1
		elif k == "boss":
			bosses.append(id)
	check(commons == 14, "14 monstros comuns/raros (%d)" % commons)
	check(bosses.size() == 4 and bosses.has("boss_hydra"), "3 chefes + Hidra")
	var family_forms := 0
	var secrets := 0
	for id in GameData.forms:
		if GameData.forms[id].get("secret", false):
			secrets += 1
		else:
			family_forms += 1
	check(family_forms == 6 and secrets == 3, "6 formas de família e 3 secretas")
	for id in cat:
		var b: Dictionary = GameData.bones[id]
		if b.rarity == "legendary":
			check(String(GameData.monsters[b.monster].kind) == "boss", "lendário só cai de chefe: " + id)


func test_07_every_form_reachable() -> void:
	var cases := {
		"form_werewolf": _eq([["slot_skull", "bone_skull_wolf"], ["slot_arm_left", "bone_claw_bear"], ["slot_arm_right", "bone_claw_bear"], ["slot_legs", "bone_legs_centaur"]]),
		"form_swarm_queen": _eq([["slot_legs", "bone_legs_spider"], ["slot_arm_left", "bone_stinger_wasp"], ["slot_back", "bone_shell_beetle"], ["slot_tail", "bone_tail_scorpion"]]),
		"form_leviathan": _eq([["slot_ribs", "bone_ribs_turtle"], ["slot_arm_left", "bone_pincer_crab"], ["slot_arm_right", "bone_pincer_crab", 2]]),
		"form_bone_wyrm": _eq([["slot_skull", "bone_skull_dragon"], ["slot_back", "bone_wings_dragon"]]),
		"form_colossus": _eq([["slot_skull", "bone_skull_cyclops"], ["slot_ribs", "bone_ribs_golem"], ["slot_arm_left", "bone_fist_golem"], ["slot_arm_right", "bone_fist_golem"]]),
		"form_lich": _eq([["slot_back", "bone_wings_bat", 2], ["slot_tail", "bone_tail_rat", 2]]),
		"form_night_manticore": _eq([["slot_skull", "bone_skull_wolf"], ["slot_back", "bone_wings_bat"], ["slot_tail", "bone_tail_scorpion"]]),
		"form_chimera": _eq([["slot_skull", "bone_skull_wolf"], ["slot_ribs", "bone_ribs_turtle"], ["slot_legs", "bone_legs_spider"], ["slot_back", "bone_wings_bat"], ["slot_tail", "bone_tail_lizard"]]),
		"form_abyssal_knight": _eq([["slot_arm_left", "bone_pincer_crab"], ["slot_back", "bone_shell_beetle"], ["slot_legs", "bone_legs_centaur"]]),
	}
	for fid in cases:
		check(Body.active_forms(cases[fid]).has(fid), "forma alcançável: " + fid)
	check(not Body.active_forms(_eq([["slot_back", "bone_wings_bat"], ["slot_tail", "bone_tail_rat"]])).has("form_lich"), "Lich não ativa com 2 peças")
	var rej := _eq([["slot_tail", "bone_tail_lizard"], ["slot_ribs", "bone_ribs_turtle"]])
	check(Body.rejection_active(rej), "rejeição Dragão + Marinho")
	var h1 := Body.make_hero(_eq([["slot_tail", "bone_tail_lizard"]]))
	var h2 := Body.make_hero(rej)
	check(h2.damage_mult > h1.damage_mult, "rejeição dá +25% de dano")


func test_08_bosses() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	var golem := MonsterFactory.make("boss_forgotten_golem", 20)
	var hero := Body.make_hero({})
	hero.max_hp = 99999
	hero.hp = 99999
	var c := Combat.new(hero, [golem], {"rng": rng, "max_turns": 2})
	check(golem.guard_max == 3, "Golem tem escudo de 3 golpes")
	var before := golem.hp
	c.step()
	var single_hit_dmg := before - golem.hp
	check(single_hit_dmg < hero.atk * 0.6, "escudo do Golem reduz golpe único (%.1f)" % single_hit_dmg)
	var hero2 := Body.make_hero(_eq([["slot_arm_left", "bone_blade_mantis"], ["slot_arm_right", "bone_blade_mantis"]]))
	hero2.max_hp = 99999
	hero2.hp = 99999
	var golem2 := MonsterFactory.make("boss_forgotten_golem", 20)
	var c2 := Combat.new(hero2, [golem2], {"rng": rng, "max_turns": 3})
	var broke := false
	for i in 3:
		for ev in c2.step():
			if ev.t == "guard" and ev.state == "broken":
				broke = true
	check(broke, "ataques múltiplos quebram o escudo do Golem")
	# Dragão: sopro dobra sem defesa contra fogo
	var dmg_plain := _breath_damage({})
	var dmg_resist := _breath_damage(_eq([["slot_tail", "bone_tail_lizard"]]))
	check(dmg_plain > dmg_resist * 1.5, "sopro do Dragão dobra sem defesa contra fogo (%.0f vs %.0f)" % [dmg_plain, dmg_resist])
	var drops := {}
	for i in 40:
		drops[MonsterFactory.boss_drop("boss_forgotten_golem", 0, rng)] = true
	check(drops.has("bone_ribs_golem") and drops.has("bone_fist_golem"), "Golem solta Gaiola ou Punho")
	var st := RunState.new({"seed": 1})
	check(st.boss_for_floor(10) == "boss_rat_king" and st.boss_for_floor(20) == "boss_forgotten_golem" and st.boss_for_floor(30) == "boss_ancient_dragon", "chefes nos andares 10, 20 e 30")
	check(st.boss_for_floor(31) == "boss_hydra", "Hidra no andar secreto")


func _breath_damage(eq: Dictionary) -> float:
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	var hero := Body.make_hero(eq)
	hero.max_hp = 99999
	hero.hp = 99999
	hero.dodge = 0
	var dragon := MonsterFactory.make("boss_ancient_dragon", 30)
	dragon.crit = 0
	var c := Combat.new(hero, [dragon], {"rng": rng, "max_turns": 99})
	for t in 3:
		for ev in c.step():
			if ev.t == "attack" and ev.kind == "fire_breath":
				return float(ev.dmg)
	return 0.0


func test_09_events() -> void:
	check(GameData.events.size() == 60, "60 eventos (%d)" % GameData.events.size())
	var body := 0
	var types := {}
	for id in GameData.events:
		var ev: Dictionary = GameData.events[id]
		types[ev.type] = int(types.get(ev.type, 0)) + 1
		var is_body := false
		for o in ev.options:
			var req: Dictionary = o.get("requires", {})
			if req.has("bone") or req.has("tag") or req.has("any_bone") or req.has("family"):
				is_body = true
				if req.has("bone"):
					check(GameData.bones.has(req.bone), "requisito de osso válido em " + id)
		if is_body:
			body += 1
		if ev.has("prop"):
			check(ResourceLoader.exists("res://art/props/%s.png" % ev.prop), "arte do cenário %s" % ev.prop)
	check(body == 15, "15 eventos ligados ao corpo (%d)" % body)
	for t in ["combat", "choice", "chest", "merchant", "ally", "altar", "rest", "rare"]:
		check(int(types.get(t, 0)) > 0, "há eventos do tipo " + t)
	# toda partida automática termina sem travar
	for seed in 12:
		var ar := AutoRunner.new({"seed": 500 + seed})
		var st := ar.play()
		check(st.floor_n >= 1 and st.floor_n <= 31, "partida automática termina (semente %d, andar %d)" % [seed, st.floor_n])
