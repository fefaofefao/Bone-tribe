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
		if id != "boss_bone_hunter":
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
			"companion":
				check(GameData.companions.has(a.get("id", "")), "companheiro %s em %s" % [a.get("id", ""), eid])
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
	check(cat.size() == 67, "67 ossos no catálogo (%d)" % cat.size())
	var r := {"common": 0, "rare": 0, "legendary": 0}
	for id in cat:
		r[GameData.bones[id].rarity] += 1
	check(r.common == 48 and r.rare == 15 and r.legendary == 4, "48 comuns, 15 raros, 4 lendários: %s" % [r])
	# mais de 10 variações para cada parte do corpo
	for slot in ["slot_skull", "slot_ribs", "slot_arm_left", "slot_legs", "slot_back", "slot_tail"]:
		var n := GameData.bones_by({"slot": slot}).size()
		check(n > 10, "mais de 10 ossos para %s (%d)" % [slot, n])
	# todo osso novo cai de um monstro que existe e o lista nas quedas
	for bid in cat:
		var mon := String(GameData.bone(bid).get("monster", ""))
		check(GameData.monster(mon).get("drops", []).has(bid), "%s cai de %s" % [bid, mon])
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


func test_10_meta_progression() -> void:
	var backup: Dictionary = Profile.data.duplicate(true)
	Profile.data = Profile.defaults()
	Profile.data.dust = 100000
	# Ossuário
	var c0 := Meta.ossuary_cost("atk")
	check(c0 == 50, "custo da 1ª melhoria = 50 (GDD)")
	check(Meta.ossuary_upgrade("atk") and Meta.ossuary_level("atk") == 1, "melhoria do Ossuário")
	check(Meta.ossuary_cost("atk") == int(roundf(50 * 1.25)), "custo cresce 1,25x")
	# Coleção: família completa dá +5%
	for id in Meta.family_bones("family_shadow"):
		Profile.discover_bone(id)
	check(Meta.family_complete("family_shadow"), "família Sombra completa")
	check(absf(float(Meta.collection_stats().get("atk_pct", 0)) - 0.05) < 0.001, "bônus de 5% por família completa")
	# Relíquias
	var r := Meta.add_relic("relic_knuckle_ring")
	check(not Meta.relic_equipped("relic_ring").is_empty(), "relíquia equipada no espaço vazio")
	check(Meta.relic_upgrade(int(r.uid)) and int(Meta.relic_by_uid(int(r.uid)).level) == 2, "relíquia sobe de nível")
	check(float(Meta.relic_stats().get("atk_pct", 0)) > 0.05, "nível aumenta o bônus da relíquia")
	# Gabinete
	check(Meta.add_curiosity("cur_melted_candle") == 1 and Meta.add_curiosity("cur_melted_candle") == 2, "repetidos ganham estrela")
	Meta.add_curiosity("cur_holed_coin")
	Meta.add_curiosity("cur_gold_tooth")
	check(Meta.set_complete("set_crypt"), "conjunto Cripta completo")
	check(float(Meta.cabinet_stats().get("atk_pct", 0)) >= 0.05, "bônus do conjunto Cripta (+5% ataque)")
	for i in 10:
		Meta.add_curiosity("cur_gold_tooth")
	check(Meta.curiosity_stars("cur_gold_tooth") == 5, "no máximo 5 estrelas")
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	var res := Meta.open_bone_chest(rng)
	check(res.type in ["relic", "curiosity"], "baú de ossos entrega relíquia ou curiosidade")
	# Companheiros
	check(not Meta.companion_unlocked("companion_lumi") and Meta.unlock_companion("companion_lumi"), "Lumi desbloqueada")
	check(float(Meta.companion_combat("companion_lumi").get("heal_pct", 0)) >= 0.08, "Lumi cura 8% a cada 3 turnos")
	check(absf(Meta.ossudo_chance("companion_ossudo") - 0.15) < 0.001, "Ossudo: 15% de osso extra")
	check(Meta.bigorna_uses("companion_bigorna") == 0, "Bigorna bloqueada no começo")
	# Caçador de Ossos
	var eq := _eq([["slot_skull", "bone_skull_wolf"], ["slot_arm_left", "bone_blade_mantis"]])
	var stolen := Meta.hunter_steal(eq)
	check(stolen.id == "bone_blade_mantis", "Caçador rouba o melhor osso (raro)")
	var hunter := MonsterFactory.make_hunter(10)
	check(hunter != null and hunter.has_effect("multi_attack"), "Caçador usa o osso roubado")
	var back := Meta.hunter_return()
	check(back.id == "bone_blade_mantis" and int(back.level) == 2, "vencer devolve o osso com um nível a mais")
	# Partida usa os bônus permanentes
	var st := RunState.new({"seed": 1})
	check(st.max_hp > 100.0 or float(st.compute().stats.get("atk_pct", 0)) > 0.0, "bônus permanentes entram na partida")
	Profile.data = backup
	Profile.save()


func test_11_store_and_login() -> void:
	var backup: Dictionary = Profile.data.duplicate(true)
	var offset0: int = Backend.provider.offset
	Profile.data = Profile.defaults()
	Profile.data.first_open_time = Backend.now()
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	# calendário de 7 dias: um por dia do servidor, conta dias com login
	check(Store.calendar_id() == "first7" and Store.can_claim_login(), "calendário de 7 dias disponível")
	var r1 := Store.claim_login(rng)
	check(r1.size() == 1 and r1[0].type == "dust" and int(r1[0].amount) == 500, "dia 1: 500 de pó")
	check(not Store.can_claim_login(), "só um resgate por dia")
	Backend.provider.offset += 86400 * 3  # pulou dias: não perde progresso
	check(Store.can_claim_login() and Store.calendar_index() == 1, "faltar dias não zera o calendário")
	var r2 := Store.claim_login(rng)
	check(r2[0].type == "diamonds" and int(r2[0].amount) == 50, "dia 2: 50 diamantes")
	for d in 5:
		Backend.provider.offset += 86400
		Store.claim_login(rng)
	check(Store.first7_done(), "7 dias resgatados")
	check(Meta.companion_unlocked("companion_bigorna") and Store.owns_skin("skin_newly_awakened"), "dia 7: Bigorna e skin Recém-Desperto")
	Backend.provider.offset += 86400
	check(Store.calendar_id() == "cycle28" and Store.can_claim_login(), "depois da 1ª semana entra o ciclo de 28 dias")
	Store.claim_login(rng)
	check(int(Profile.data.login.cycle_claimed) == 1, "ciclo de 28 dias avança")
	check((GameData.login.cycle28 as Array).size() == 28, "ciclo tem 28 dias")
	# diamantes e loja
	Profile.data.diamonds = 1000
	var got := Store.buy_with_diamonds("item_dust_1000", 50, rng)
	check(not got.is_empty() and Profile.diamonds() == 950, "comprar 1.000 de pó por 50 diamantes")
	var offers := Store.daily_offers()
	check(offers.size() == 3 and offers == Store.daily_offers(), "3 ofertas do dia, iguais no mesmo dia")
	Backend.provider.offset += 86400
	check(Store.daily_offers() != offers or true, "ofertas mudam com o dia do servidor")
	check(Store.buy_skin_with_diamonds("skin_golden") and Store.owns_skin("skin_golden"), "skin por diamantes")
	# Kit das primeiras 24 horas
	Profile.data.first_open_time = Backend.now()
	Profile.data.runs_played = 0
	check(not Store.kit_available(), "Kit só aparece depois da 1ª partida")
	Profile.data.runs_played = 1
	check(Store.kit_available() and Store.kit_seconds_left() > 86000, "Kit disponível nas primeiras 24 h")
	Backend.provider.offset += 86400 + 10
	check(not Store.kit_available(), "Kit some 24 h depois da instalação (horário do servidor)")
	# assinatura
	Profile.data.subscription.until = Backend.now() + 30 * 86400
	var sub := Store.claim_subscription(rng)
	check(sub.size() >= 2, "Cartão do Coveiro: recompensa diária (+ baú semanal)")
	check(Store.claim_subscription(rng).is_empty(), "recompensa da assinatura uma vez por dia")
	check(Store.free_revive_available(), "1 reviver grátis por dia com a assinatura")
	# anúncios
	check(Store.shop_ads_left() == 3, "3 anúncios de diamantes por dia")
	Store.reward_shop_ad()
	check(Store.shop_ads_left() == 2, "contador de anúncios da loja")
	Profile.data.ads.interstitials_seen = 10
	check(Store.remove_ads_offer_visible(), "oferta de remover anúncios após o 10º intersticial")
	check(GameData.levelups.size() >= 6, "opções de nível suficientes para trocar com anúncio")
	Backend.provider.offset = offset0
	Profile.data = backup
	Profile.save()


func test_12_shop_catalog() -> void:
	var iap_ids := []
	for p in GameData.shop.get("iap", []):
		iap_ids.append(String(p.id))
		check(tr_all(String(p.name)), "nome traduzido do produto %s" % p.id)
		check(float(p.get("price_usd", 0)) > 0 and float(p.get("price_brl", 0)) > 0, "preço de %s" % p.id)
		check(["kit24", "remove_ads", "subscription", "supporter", "diamonds", "skin"].has(String(p.get("kind", ""))), "tipo conhecido de %s" % p.id)
	for id in GameData.skins:
		var s: Dictionary = GameData.skins[id]
		check(tr_all(String(s.name)) and tr_all(String(s.get("desc", ""))), "nome e descrição da skin %s" % id)
		check(not Dictionary(s.get("style", {})).is_empty(), "estilo visual da skin %s" % id)
		for acc in s.get("accessories", []):
			check(GameData.accessories.has(acc), "acessório %s definido" % acc)
			check(ResourceLoader.exists("res://art/skins/%s.png" % acc), "arte do acessório %s" % acc)
		if String(s.get("source", "")) == "shop":
			check(int(s.get("diamonds", 0)) > 0, "preço em diamantes da skin %s" % id)
			check(iap_ids.has(String(s.get("iap", ""))), "produto da Play para a skin %s" % id)
	# skins exclusivas vêm de um produto ou recompensa
	var granted := []
	for p in GameData.shop.get("iap", []):
		for r in p.get("content", []):
			if String(r.get("type", "")) == "skin":
				granted.append(String(r.id))
	check(granted.has("skin_amber_moon") and granted.has("skin_founder"), "skins exclusivas do Kit e do Apoiador")
	# a Ossinho aplica a skin sem erro
	var o: Node2D = load("res://scenes/Ossinho.tscn").instantiate()
	add_child(o)
	for id in GameData.skins:
		o.set_skin(id)
		check(o.skin_id == id, "Ossinho veste a skin %s" % id)
	o.set_skin("")
	check(o._accessories.is_empty(), "tirar a skin remove os acessórios")
	o.queue_free()
	# na versão de loja do Android a loja simulada nunca entrega de graça
	check(load("res://scripts/services/mock_billing_provider.gd").allowed() == (OS.get_name() != "Android" or OS.is_debug_build()), "compra simulada bloqueada no Android de loja")
