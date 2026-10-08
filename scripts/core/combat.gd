class_name Combat
extends RefCounted
## Combate automático por turnos. Não desenha nada: cada chamada de step()
## devolve a lista de acontecimentos do turno, que a cena Run anima.
## A mesma lógica roda nos testes e na simulação de equilíbrio.

var hero: Fighter
var enemies: Array = []
var allies: Array = []
var turn := 0
var max_turns := 15
var is_boss := false
var rng: RandomNumberGenerator
var result := ""  # "", "win", "lose", "flee"
var focus: Fighter = null
## Simulação: foca sempre o inimigo com menos vida (jogador que prioriza alvos).
var auto_focus_weakest := false
var companion: Dictionary = {}
var spawned_count := 0
var _log: Array = []
var _hero_hit_count := 0


func _init(p_hero: Fighter, p_enemies: Array, opts: Dictionary = {}) -> void:
	hero = p_hero
	enemies = p_enemies.duplicate()
	allies = opts.get("allies", []).duplicate()
	max_turns = int(opts.get("max_turns", GameData.bal("combat/max_turns", 15)))
	is_boss = bool(opts.get("is_boss", false))
	rng = opts.get("rng", RandomNumberGenerator.new())
	companion = opts.get("companion", {})
	auto_focus_weakest = bool(opts.get("auto_focus", false))
	_start_of_combat()


func finished() -> bool:
	return result != ""


func alive_enemies() -> Array:
	return enemies.filter(func(e): return e.alive())


# --------------------------------------------------------------- início

func _start_of_combat() -> void:
	var shield_pct := float(hero.flags.get("shield_start", 0.0))
	if shield_pct > 0.0:
		hero.shield = hero.max_hp * shield_pct
	hero.flags["immune_ready"] = hero.has_effect("immune_first_hit")
	for e in hero.effects_of("summon_allies"):
		for i in int(e.get("count", 2)):
			allies.append(make_summon_ally(hero, String(e.get("ally", "ally_bone_insect"))))
	for en in enemies:
		_init_enemy(en)


func _init_enemy(en: Fighter) -> void:
	for a in en.effects_of("guard"):
		en.guard_max = int(a.get("hits", 3))
		en.guard_hits = en.guard_max


static func make_summon_ally(owner: Fighter, ally_id: String) -> Fighter:
	var f := Fighter.new()
	f.id = ally_id
	f.name_key = ally_id + "_name"
	f.is_ally = true
	f.max_hp = 1
	f.hp = 1
	f.atk = owner.atk * 0.35
	f.crit = 0.0
	f.effects = [{"type": "on_hit_status", "status": "poison", "chance": 1.0}]
	f.poison_bonus = owner.poison_bonus
	return f


# ----------------------------------------------------------------- turno

func step() -> Array:
	_log = []
	if finished():
		return _log
	turn += 1
	_hero_hit_count = 0
	_emit({"t": "turn", "n": turn})
	# 1) Efeitos de início de turno.
	_tick_statuses(hero)
	for en in enemies:
		if en.alive():
			_tick_statuses(en)
	if _check_end():
		return _log
	for f: Fighter in [hero] + alive_enemies():
		if f.regen > 0.0 and f.alive() and f.hp < f.max_hp:
			var h := f.heal(f.max_hp * f.regen)
			if h > 0.5:
				_emit({"t": "heal", "dst": f, "amount": h, "source": "regen"})
	_companion_turn()
	for en in enemies:
		if en.alive() and en.guard_max > 0 and en.guard_broken_turns > 0:
			en.guard_broken_turns -= 1
			if en.guard_broken_turns == 0:
				en.guard_hits = en.guard_max
				_emit({"t": "guard", "dst": en, "state": "up"})

	# 2) Ordem de ação.
	var order := _turn_order()
	for f in order:
		if not f.alive():
			continue
		if f == hero:
			_hero_act()
			for al in allies:
				if al.alive():
					_ally_act(al)
		else:
			_enemy_act(f)
		if _check_end():
			return _log
		if not hero.alive():
			break
	if _check_end():
		return _log
	# 3) Limite de turnos: o inimigo foge.
	if turn >= max_turns:
		result = "flee"
		_emit({"t": "flee"})
		_emit({"t": "end", "result": result})
	return _log


func _turn_order() -> Array:
	var hero_first := hero.has_effect("first_strike") or (turn == 1 and hero.has_effect("first_strike_turn1"))
	var list := alive_enemies()
	list.sort_custom(func(a, b): return a.speed > b.speed)
	var order := []
	if hero_first:
		order.append(hero)
		order.append_array(list)
		return order
	var placed := false
	for en in list:
		if not placed and hero.speed >= en.speed:
			order.append(hero)
			placed = true
		order.append(en)
	if not placed:
		order.append(hero)
	return order


func _companion_turn() -> void:
	if companion.is_empty() or not hero.alive():
		return
	var every := int(companion.get("heal_every", 0))
	if every > 0 and turn % every == 0:
		var h := hero.heal(hero.max_hp * float(companion.get("heal_pct", 0.0)))
		if h > 0.5:
			_emit({"t": "heal", "dst": hero, "amount": h, "source": "companion"})


# ------------------------------------------------------------ Ossinho

func _hero_act() -> void:
	if hero.stunned():
		hero.statuses.stun.turns = int(hero.statuses.stun.turns) - 1
		_emit({"t": "stunned", "dst": hero})
		return
	# Habilidades periódicas (crânio, punho, asas, formas).
	var extra_actions := 0
	for e in hero.effects_of("periodic"):
		var every := int(e.get("every", 3))
		if every <= 0 or turn % every != 0:
			continue
		var action := String(e.get("action", ""))
		if action == "extra_action":
			extra_actions += 1
			continue
		_hero_special(e)
		if alive_enemies().is_empty():
			return
	_hero_basic_attack()
	for i in extra_actions:
		if alive_enemies().is_empty():
			return
		_emit({"t": "special", "src": hero, "name": "extra_action"})
		_hero_basic_attack()


func _hero_target() -> Fighter:
	if focus != null and focus.alive():
		return focus
	var list := alive_enemies()
	if auto_focus_weakest and list.size() > 1:
		list.sort_custom(func(a, b): return a.hp < b.hp)
	return list[0] if not list.is_empty() else null


func _hero_basic_attack() -> void:
	var hits := 1
	var mult := 1.0
	# cada osso de golpe múltiplo soma golpes (duas Lâminas = 3 golpes)
	for e in hero.effects_of("multi_hit"):
		hits += int(e.get("hits", 2)) - 1
		mult = minf(mult, float(e.get("mult", 0.6)))
	for i in hits:
		var target := _hero_target()
		if target == null:
			return
		_attack(hero, target, mult, "normal")


func _hero_special(e: Dictionary) -> void:
	var action := String(e.get("action", ""))
	var mult := float(e.get("mult", 1.0))
	var element := String(e.get("element", ""))
	_emit({"t": "special", "src": hero, "name": action})
	match String(e.get("target", "single")):
		"all":
			for en in alive_enemies():
				_attack(hero, en, mult, action, element, true)
				if action == "wave" and en.alive():
					_apply_status(en, "stun", hero)
		_:
			var target := _hero_target()
			if target != null:
				_attack(hero, target, mult, action, element, true)


func _ally_act(al: Fighter) -> void:
	var list := alive_enemies()
	if list.is_empty():
		return
	var target: Fighter = focus if focus != null and focus.alive() else list[rng.randi() % list.size()]
	_attack(al, target, 1.0, "ally")


# ------------------------------------------------------------- inimigos

func _enemy_act(en: Fighter) -> void:
	if en.stunned():
		en.statuses.stun.turns = int(en.statuses.stun.turns) - 1
		_emit({"t": "stunned", "dst": en})
		return
	if en.guard_max > 0 and en.guard_broken_turns <= 0 and en.guard_hits < en.guard_max:
		en.guard_hits = en.guard_max
	var acted_special := false
	for a in en.effects:
		var every := int(a.get("every", 0))
		if every <= 0 or turn % every != 0:
			continue
		match String(a.get("type", "")):
			"summon":
				acted_special = _summon(en, a) or acted_special
			"breath":
				_emit({"t": "special", "src": en, "name": "fire_breath"})
				var mult := float(a.get("mult", 1.2))
				if not hero.fire_resist:
					mult *= float(a.get("no_resist_mult", 2.0))
				_attack(en, hero, mult, "fire_breath", "fire", true)
				acted_special = true
			"special":
				var sname := String(a.get("name", "special"))
				_emit({"t": "special", "src": en, "name": sname})
				_attack(en, hero, float(a.get("mult", 1.3)), sname, String(a.get("element", "")), true)
				acted_special = true
	if acted_special or not hero.alive():
		return
	var hits := 1
	for a in en.effects_of("multi_attack"):
		hits = int(a.get("hits", 2))
	for i in hits:
		if not hero.alive():
			return
		_attack(en, hero, 1.0 if hits == 1 else float(en.effects_of("multi_attack")[0].get("mult", 0.6)), "normal")


func _summon(en: Fighter, a: Dictionary) -> bool:
	var max_enemies := int(GameData.bal("combat/max_enemies", 3)) + 1
	var spawned := []
	for i in int(a.get("count", 2)):
		if alive_enemies().size() >= max_enemies:
			break
		var m := MonsterFactory.make(String(a.get("monster", "")), int(en.flags.get("floor", 1)))
		if m == null:
			continue
		enemies.append(m)
		_init_enemy(m)
		spawned.append(m)
		spawned_count += 1
	if spawned.is_empty():
		return false
	_emit({"t": "summon", "src": en, "spawned": spawned})
	return true


# ---------------------------------------------------------------- golpe

func _attack(src: Fighter, dst: Fighter, mult: float, kind: String, element: String = "", special: bool = false) -> void:
	if not dst.alive() or not src.alive():
		return
	var ev := {"t": "attack", "src": src, "dst": dst, "kind": kind, "dmg": 0.0, "crit": false, "dodged": false, "blocked": false, "element": element}
	# Esquiva (golpes especiais em área não podem ser esquivados).
	if not special and dst.dodge > 0.0 and rng.randf() < dst.dodge:
		ev.dodged = true
		_emit(ev)
		_on_blocked(dst, src)
		return
	# Imune ao primeiro golpe (Colosso).
	if dst == hero and hero.flags.get("immune_ready", false):
		hero.flags["immune_ready"] = false
		ev.blocked = true
		_emit(ev)
		_on_blocked(dst, src)
		return
	var raw := src.atk * mult * src.damage_mult
	if src == hero:
		for e in hero.effects_of("low_hp_atk"):
			if hero.hp_ratio() < float(e.get("threshold", 0.3)):
				raw *= float(e.get("mult", 2.0))
		if element == "fire":
			raw *= 1.0 + hero.fire_bonus
	if rng.randf() < src.crit:
		ev.crit = true
		raw *= src.crit_mult
	var k := float(GameData.bal("defense_k", 50))
	var dmg := raw * (1.0 - dst.def / (dst.def + k)) if dst.def > 0 else raw
	# Escudo do Golem.
	if dst.guard_max > 0 and dst.guard_broken_turns <= 0:
		dmg *= 0.25
		dst.guard_hits -= 1
		if dst.guard_hits <= 0:
			dst.guard_broken_turns = 2
			_emit({"t": "guard", "dst": dst, "state": "broken"})
	# Escudo absorve.
	if dst.shield > 0.0:
		var absorbed := minf(dst.shield, dmg)
		dst.shield -= absorbed
		dmg -= absorbed
		ev["absorbed"] = absorbed
		if dmg <= 0.0:
			ev.blocked = true
	dmg = maxf(0.0, dmg)
	if dmg > 0.0:
		dmg = maxf(1.0, roundf(dmg))
	dst.hp -= dmg
	ev.dmg = dmg
	_emit(ev)
	if src == hero:
		_hero_hit_count += 1
	# Estados ao acertar.
	if dmg > 0.0 and dst.alive():
		for e in src.effects_of("on_hit_status"):
			if rng.randf() < float(e.get("chance", 1.0)):
				_apply_status(dst, String(e.get("status", "")), src)
		if ev.crit:
			for e in src.effects_of("crit_status"):
				_apply_status(dst, String(e.get("status", "poison")), src)
	# Roubo de vida.
	if src.lifesteal > 0.0 and dmg > 0.0 and src.alive():
		var h := src.heal(dmg * src.lifesteal)
		if h >= 1.0:
			_emit({"t": "heal", "dst": src, "amount": h, "source": "lifesteal"})
	# Reflexo.
	if dst.reflect > 0.0 and dmg > 0.0 and src.alive() and kind != "reflect":
		var r := maxf(1.0, roundf(dmg * dst.reflect))
		src.hp -= r
		_emit({"t": "attack", "src": dst, "dst": src, "kind": "reflect", "dmg": r, "crit": false, "dodged": false, "blocked": false, "element": ""})
		if not src.alive():
			_on_death(src)
	if ev.blocked:
		_on_blocked(dst, src)
	if not dst.alive():
		_on_death(dst)


func _on_blocked(dst: Fighter, src: Fighter) -> void:
	if dst == hero and hero.has_effect("counter_on_block") and src.alive():
		_attack(hero, src, 1.0, "counter")


func _apply_status(dst: Fighter, status: String, src: Fighter) -> void:
	if status == "" or not dst.alive():
		return
	var b: Dictionary = GameData.balance.get("status", {})
	match status:
		"bleed":
			dst.statuses["bleed"] = {"power": src.atk * float(b.get("bleed_power", 0.25)), "turns": int(b.get("bleed_turns", 3))}
		"poison":
			var p := src.atk * float(b.get("poison_power", 0.18)) * (1.0 + src.poison_bonus)
			var cur: Dictionary = dst.statuses.get("poison", {"power": 0.0, "turns": 0})
			dst.statuses["poison"] = {"power": maxf(p, float(cur.power)), "turns": int(b.get("poison_turns", 3))}
		"stack_poison":
			var cur2: Dictionary = dst.statuses.get("stack_poison", {"stacks": 0, "power": 0.0})
			dst.statuses["stack_poison"] = {"stacks": int(cur2.stacks) + 1, "power": src.atk * float(b.get("stack_poison_power", 0.06)) * (1.0 + src.poison_bonus)}
		"stun":
			if dst.is_boss and dst.flags.get("stun_immune_turn", -1) == turn:
				return
			dst.statuses["stun"] = {"turns": int(b.get("stun_turns", 1))}
		_:
			return
	_emit({"t": "apply_status", "dst": dst, "status": status})


func _tick_statuses(f: Fighter) -> void:
	for s in ["bleed", "poison", "stack_poison"]:
		if not f.statuses.has(s) or not f.alive():
			continue
		var st: Dictionary = f.statuses[s]
		var dmg := 0.0
		if s == "stack_poison":
			dmg = float(st.power) * int(st.stacks)
		else:
			dmg = float(st.power)
			st.turns = int(st.turns) - 1
			if int(st.turns) <= 0:
				f.statuses.erase(s)
		dmg = maxf(1.0, roundf(dmg))
		f.hp -= dmg
		_emit({"t": "status", "dst": f, "status": s, "dmg": dmg})
		if not f.alive():
			_on_death(f)


func _on_death(f: Fighter) -> void:
	if f.flags.get("dead_emitted", false):
		return
	if f == hero:
		var pct := float(hero.flags.get("revive_available", 0.0))
		if pct > 0.0 and not hero.flags.get("revive_used", false):
			hero.flags["revive_used"] = true
			hero.hp = hero.max_hp * pct
			hero.statuses.clear()
			_emit({"t": "revive", "dst": hero, "source": "lich"})
			return
	f.flags["dead_emitted"] = true
	_emit({"t": "death", "dst": f})


func _check_end() -> bool:
	if finished():
		return true
	if not hero.alive():
		result = "lose"
	elif alive_enemies().is_empty():
		result = "win"
	else:
		return false
	_emit({"t": "end", "result": result})
	return true


func _emit(ev: Dictionary) -> void:
	_log.append(ev)


## Roda o combate inteiro sem animação (testes e simulação).
func run_to_end() -> String:
	var guard := 0
	while not finished() and guard < 500:
		step()
		guard += 1
	return result
