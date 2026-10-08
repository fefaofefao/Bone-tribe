class_name AutoRunner
extends RefCounted
## Joga partidas inteiras sem interface (testes e simulação de equilíbrio).
## Política simples: luta sempre, encaixa em vazio, troca se o osso for de
## raridade maior, escolhe bônus de nível ao acaso e revive uma vez com anúncio.

var state: RunState
var log_combats := 0
var revive_ad := true


func _init(opts: Dictionary = {}) -> void:
	state = RunState.new(opts)
	revive_ad = bool(opts.get("revive_ad", true))


func play() -> RunState:
	var guard := 0
	while not state.dead and guard < 100:
		guard += 1
		if state.floor_n >= state.total_floors:
			break
		state.floor_n += 1
		var boss := state.boss_for_floor(state.floor_n)
		if boss != "":
			_combat([boss], true)
			if not state.dead:
				state.bosses_beaten.append(boss)
				if boss == "boss_ancient_dragon" and Body.active_forms(state.equipped).has("form_bone_wyrm"):
					state.flags["hydra_unlocked"] = true
					state.total_floors = int(GameData.bal("run/secret_floor", 31))
			continue
		var ev := state.pick_event()
		if ev.is_empty():
			continue
		var opts: Array = ev.get("options", [])
		var pick: Dictionary = opts[0]
		for o in opts:
			var req: Dictionary = o.get("requires", {})
			if not req.is_empty() and state.requirement_met(req) and (req.has("bone") or req.has("tag")):
				pick = o
		_exec(pick.get("actions", []))
	if not state.dead and state.floor_n >= state.total_floors:
		state.victory = true
	return state


func _exec(actions: Array) -> void:
	for a in actions:
		if state.dead:
			return
		match String(a.get("do", "")):
			"combat":
				var ids: Array = a.get("monsters", [])
				if ids.is_empty():
					for i in int(a.get("count", 1)):
						ids.append(MonsterFactory.random_for_floor(state.floor_n, state.rng))
				_combat(ids, false)
			"dust":
				state.add_dust(int(a.get("amount", state.rng.randi_range(int(a.get("min", 10)), int(a.get("max", 20))))))
			"dust_mult":
				state.dust = int(roundf(state.dust * float(a.value)))
			"lose_current_pct":
				state.hp = maxf(1.0, state.hp - roundf(state.hp * float(a.value)))
			"heal_pct":
				state.heal_pct(float(a.value))
			"max_hp_pct":
				state.bonus_stats["hp_pct"] = float(state.bonus_stats.get("hp_pct", 0.0)) + float(a.value)
				state.recalc()
			"bone":
				var bid := String(a.get("id", ""))
				if bid == "":
					var pool: Array = GameData.bones_by(a.get("pool", {}))
					pool = pool.filter(func(x): return not GameData.bone(x).get("boss_drop", false))
					if pool.is_empty():
						continue
					bid = pool[state.rng.randi() % pool.size()]
				offer({"id": bid, "level": 1})
			"chance":
				_exec(a.get("then", []) if state.rng.randf() < float(a.get("p", 0.5)) else a.get("else", []))
			"roll":
				var table: Array = a.get("table", [])
				var total := 0.0
				for row in table:
					total += float(row.get("w", 1))
				var r := state.rng.randf() * total
				for row in table:
					r -= float(row.get("w", 1))
					if r <= 0.0:
						_exec(row.get("actions", []))
						break
			"xp":
				_levelups(state.add_xp(int(a.get("amount", 10))))
			"pay":
				state.add_dust(-int(a.get("dust", 0)))
			"stat":
				var st: Dictionary = a.get("stats", {})
				for k in st:
					state.bonus_stats[k] = float(state.bonus_stats.get(k, 0.0)) + float(st[k])
				state.recalc()
			"trap":
				if state.rng.randf() >= state.stat("trap_avoid"):
					state.hp = maxf(1.0, state.hp - roundf(state.max_hp * float(a.get("value", 0.15))))
			"skip":
				var target := state.floor_n + int(a.get("n", 3))
				while state.floor_n < target and not state.is_boss_floor(state.floor_n + 1):
					state.floor_n += 1
			"ally":
				state.allies.append(String(a.get("id", "")))
			"merchant":
				for o in MonsterFactory.merchant_stock(int(a.get("stock", 3)), a.get("rarities", []), state.rng):
					if state.dust >= int(o.price) and state.free_slot_for(String(o.id)) != "":
						state.add_dust(-int(o.price))
						offer({"id": o.id, "level": 1})
						break
			"upgrade_bone":
				var slots := state.non_basic_bones()
				if not slots.is_empty():
					var inst: Dictionary = state.equipped[slots[state.rng.randi() % slots.size()]]
					inst["level"] = mini(int(GameData.bal("bone_max_level", 5)), int(inst.get("level", 1)) + 1)
					state.recalc()
			"sell_bone", "altar":
				pass


func _combat(ids: Array, is_boss: bool) -> void:
	var enemies := []
	for id in ids:
		var f := MonsterFactory.make(String(id), state.floor_n)
		if f:
			enemies.append(f)
	var hero := state.make_hero()
	var allies := []
	for aid in state.allies:
		var af := MonsterFactory.make_ally(String(aid), state.floor_n)
		if af:
			allies.append(af)
	var c := Combat.new(hero, enemies, {"rng": state.rng, "is_boss": is_boss, "auto_focus": true, "allies": allies,
		"companion": Meta.companion_combat(state.companion_id) if state.companion_id != "" else {},
		"max_turns": int(GameData.bal("combat/boss_max_turns" if is_boss else "combat/max_turns", 15))})
	log_combats += 1
	var res := c.run_to_end()
	if res == "lose" and revive_ad and not state.flags.get("revive_ad_used", false):
		state.flags["revive_ad_used"] = true
		hero.hp = hero.max_hp * float(GameData.bal("revive_pct", 0.5))
		hero.flags.erase("dead_emitted")
		c.result = ""
		res = c.run_to_end()
	state.absorb_hero(hero)
	if res == "lose":
		state.dead = true
		return
	if res != "win":
		return
	var xp := 0
	for e in c.enemies:
		if e.alive():
			continue
		state.kills += 1
		xp += MonsterFactory.xp_for(e.id, state.floor_n)
		state.add_dust(int(GameData.bal("dust/per_kill", 3)))
		var m := GameData.monster(e.id)
		if String(m.get("kind", "")) == "boss":
			var bb := MonsterFactory.boss_drop(e.id, 0, state.rng)
			if bb != "":
				offer({"id": bb, "level": 1})
			continue
		var bid := MonsterFactory.roll_bone_drop(e.id, state.rng, state.stat("drop_bonus"))
		if bid != "":
			offer({"id": bid, "level": 1})
	_levelups(state.add_xp(xp))


func _levelups(n: int) -> void:
	for i in n:
		var ch := state.levelup_choices(3)
		state.apply_levelup(ch[state.rng.randi() % ch.size()])


const RANK := {"basic": 0, "common": 1, "rare": 2, "legendary": 3}


func offer(inst: Dictionary) -> void:
	var bid := String(inst.id)
	var free := state.free_slot_for(bid)
	if free != "":
		state.equip(free, inst)
		return
	var new_rank := int(RANK.get(Body.instance_rarity(inst), 1))
	for s in state.slots_for(bid):
		var cur: Dictionary = state.equipped.get(s, {})
		if int(RANK.get(Body.instance_rarity(cur), 1)) < new_rank:
			state.add_dust(state.crush_value(cur))
			state.equip(s, inst)
			return
	state.add_dust(state.crush_value(inst))
