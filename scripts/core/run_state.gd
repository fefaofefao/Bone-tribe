class_name RunState
extends RefCounted
## Estado de uma partida: andar atual, corpo montado, vida, pó de osso,
## experiência, escolhas e sorteio de eventos.

var rng := RandomNumberGenerator.new()
var floor_n := 0
var total_floors := 10
var prototype := false
var demo := false
var hp := 0.0
var max_hp := 0.0
var equipped: Dictionary = {}
var dust := 0
var xp := 0
var level := 1
var picks: Array = []
var bonus_stats: Dictionary = {}
var allies: Array = []
var companion_id := ""
var seen_events: Dictionary = {}
var bosses_beaten: Array = []
var kills := 0
var bones_found := 0
var forms_announced: Dictionary = {}
var flags: Dictionary = {}
var dead := false
var victory := false
var pending_skip := 0
var hunter_met := false
var bigorna_left := 0
var next_event: Dictionary = {}
var segment_chest: Dictionary = {}
var tower := 1


func _init(opts: Dictionary = {}) -> void:
	if opts.has("seed"):
		rng.seed = int(opts.seed)
	else:
		rng.randomize()
	demo = bool(opts.get("demo", false))
	tower = 1 if demo else clampi(int(opts.get("tower", 1)), 1, maxi(1, GameData.towers.size()))
	MonsterFactory.tower = tower
	prototype = bool(opts.get("prototype", GameData.bal("run/prototype_mode", false))) or demo
	total_floors = int(GameData.bal("run/prototype_floors", 10)) if prototype else int(GameData.bal("run/floors", 30))
	companion_id = String(opts.get("companion", ""))
	if not demo and companion_id != "" and not Meta.companion_unlocked(companion_id):
		companion_id = ""
	bigorna_left = Meta.bigorna_uses(companion_id)
	var start: Dictionary = GameData.skeleton.get("starting_bones", {})
	for slot in start:
		equipped[slot] = {"id": start[slot], "level": 1}
	var start_bone := String(opts.get("start_bone", ""))
	if start_bone != "":
		var slots := GameData.bone_slots(start_bone)
		if not slots.is_empty():
			equipped[slots[0]] = {"id": start_bone, "level": 1}
	recalc(true)


# ------------------------------------------------------------- atributos

func extras() -> Array:
	var out := Meta.permanent_extras() if not demo else []
	for id in picks:
		var lu: Dictionary = GameData.levelups.get(id, {})
		out.append({"stats": lu.get("stats", {}), "effects": lu.get("effects", [])})
	out.append({"stats": bonus_stats, "effects": []})
	if demo:
		out.append({"stats": {"hp_pct": 3.0, "atk_pct": 1.5, "def": 20}, "effects": []})
	return out


var _cache: Dictionary = {}


func compute() -> Dictionary:
	if _cache.is_empty():
		_cache = Body.compute(equipped, extras())
	return _cache


## Recalcula a vida máxima; se ela subiu, a vida atual sobe junto.
func recalc(full_heal: bool = false) -> void:
	_cache = {}
	var f := Body.make_hero(equipped, extras())
	var new_max := f.max_hp
	if full_heal or max_hp <= 0.0:
		hp = new_max
	elif new_max > max_hp:
		hp += new_max - max_hp
	max_hp = new_max
	hp = clampf(hp, 0.0, max_hp)


func make_hero() -> Fighter:
	var f := Body.make_hero(equipped, extras())
	f.hp = clampf(hp, 1.0, f.max_hp)
	if flags.get("lich_used", false):
		f.flags.erase("revive_available")
	return f


func absorb_hero(f: Fighter) -> void:
	hp = clampf(f.hp, 0.0, max_hp)
	if f.flags.get("revive_used", false):
		flags["lich_used"] = true


func stat(key: String) -> float:
	return float(compute().stats.get(key, 0.0))


func heal_pct(p: float) -> float:
	var before := hp
	hp = clampf(hp + max_hp * p * (1.0 + stat("heal_bonus")), 0.0, max_hp)
	return hp - before


func damage_pct(p: float) -> float:
	var d := roundf(max_hp * p)
	hp = maxf(1.0, hp - d)
	return d


# ----------------------------------------------------------- experiência

static func xp_needed(lvl: int) -> int:
	return int(roundf(float(GameData.bal("xp/base", 20)) * pow(lvl, float(GameData.bal("xp/exp", 1.5)))))


## Soma experiência e devolve quantos níveis subiram.
func add_xp(amount: int) -> int:
	xp += int(roundf(amount * (1.0 + stat("xp_bonus"))))
	var ups := 0
	while xp >= xp_needed(level):
		xp -= xp_needed(level)
		level += 1
		ups += 1
	return ups


func levelup_choices(count: int = 3) -> Array:
	var ids: Array = GameData.levelups.keys()
	var out := []
	var pool := ids.duplicate()
	while out.size() < count and not pool.is_empty():
		var i := rng.randi() % pool.size()
		out.append(pool[i])
		pool.remove_at(i)
	return out


func apply_levelup(id: String) -> void:
	picks.append(id)
	var lu: Dictionary = GameData.levelups.get(id, {})
	recalc()
	heal_pct(float(GameData.bal("levelup_heal_pct", 0.0)) + float(lu.get("heal_pct", 0.0)))


# ----------------------------------------------------------------- ossos

func equip(slot: String, inst: Dictionary) -> Dictionary:
	var old: Dictionary = equipped.get(slot, {})
	equipped[slot] = inst
	bones_found += 1
	recalc()
	return old


func unequip(slot: String) -> Dictionary:
	var old: Dictionary = equipped.get(slot, {})
	equipped.erase(slot)
	recalc()
	return old


func crush_value(inst: Dictionary) -> int:
	var r := Body.instance_rarity(inst)
	var base := int(GameData.bal("dust/crush/" + r, 10))
	return int(roundf(base * (1.0 + 0.5 * (int(inst.get("level", 1)) - 1))))


## Encaixes onde o osso pode entrar (o terceiro braço só existe com a Coluna de Hidra).
func slots_for(bone_id: String) -> Array:
	var out := []
	for s in GameData.bone_slots(bone_id):
		if s == "slot_arm_third" and not has_extra_arm():
			continue
		out.append(s)
	return out


func has_extra_arm() -> bool:
	for e in compute().effects:
		if e.get("type", "") == "extra_slot":
			return true
	return false


func free_slot_for(bone_id: String) -> String:
	for s in slots_for(bone_id):
		if not equipped.has(s):
			return s
	return ""


func add_dust(n: int) -> void:
	dust = maxi(0, dust + n)


# --------------------------------------------------------------- eventos

func is_boss_floor(n: int = -1) -> bool:
	if n < 0:
		n = floor_n
	return boss_for_floor(n) != ""


func boss_for_floor(n: int) -> String:
	if prototype:
		return "boss_rat_king" if n == total_floors else ""
	var bf: Dictionary = GameData.bal("run/boss_floors", {})
	if bf.has(str(n)):
		return String(bf[str(n)])
	if n == int(GameData.bal("run/secret_floor", 31)):
		return String(GameData.bal("run/secret_boss", "boss_hydra"))
	return ""


func segment_index() -> int:
	return int((floor_n - 1) / 10)


func pick_event_type() -> String:
	# Conjunto Coveiro completo: um baú garantido a cada bloco de 10 andares.
	var seg := segment_index()
	if stat("chest_per_floor") > 0.0 and not segment_chest.has(seg) and floor_n % 10 == 9:
		return "chest"
	var weights: Dictionary = GameData.bal("prototype_event_weights" if prototype else "event_weights", {})
	var w := weights.duplicate()
	if w.has("rare"):
		w.rare = float(w.rare) * (1.0 + stat("rare_event_bonus") * 10.0)
	var total := 0.0
	for k in w:
		total += float(w[k])
	var r := rng.randf() * total
	for k in w:
		r -= float(w[k])
		if r <= 0.0:
			return k
	return "combat"


func event_available(ev: Dictionary) -> bool:
	if prototype and not ev.get("prototype", false):
		return false
	if seen_events.has(ev.id) and not ev.get("repeatable", false):
		return false
	var fl: Array = ev.get("floors", [1, 99])
	if floor_n < int(fl[0]) or floor_n > int(fl[1]):
		return false
	var req: Dictionary = ev.get("requires", {})
	if not req.is_empty() and not requirement_met(req):
		return false
	return true


func pick_event() -> Dictionary:
	var type := pick_event_type()
	for attempt in 3:
		var pool := []
		var total := 0.0
		for id in GameData.event_order:
			var ev: Dictionary = GameData.events[id]
			if ev.get("type", "") != type or not event_available(ev):
				continue
			pool.append(ev)
			total += float(ev.get("weight", 1))
		if not pool.is_empty():
			var r := rng.randf() * total
			for ev in pool:
				r -= float(ev.get("weight", 1))
				if r <= 0.0:
					return _picked(ev)
			return _picked(pool[-1])
		type = "combat"
		# Se acabaram os eventos de combate, libera repetições.
		if attempt == 1:
			seen_events.clear()
	return {}


func _picked(ev: Dictionary) -> Dictionary:
	seen_events[ev.id] = true
	if String(ev.get("type", "")) == "chest":
		segment_chest[segment_index()] = true
	return ev


## Próximo evento (já sorteado quando o Mapa Rasgado revela o tipo).
func take_event() -> Dictionary:
	if not next_event.is_empty():
		var ev := next_event
		next_event = {}
		return ev
	return pick_event()


## Encontro com o Caçador de Ossos: no máximo um por partida.
func should_meet_hunter() -> bool:
	if hunter_met or demo or prototype or Meta.hunter_stolen().is_empty():
		return false
	var fl: Array = GameData.bal("hunter/floors", [4, 27])
	if floor_n < int(fl[0]) or floor_n > int(fl[1]) or is_boss_floor():
		return false
	# chance por andar calibrada para ~60% de encontros por partida
	return rng.randf() < float(GameData.bal("hunter/appear_chance", 0.6)) / 15.0


## Requisitos de opções ligadas ao corpo e a recursos.
func requirement_met(req: Dictionary) -> bool:
	if req.has("bone") and not Body.has_bone(equipped, String(req.bone)):
		return false
	if req.has("any_bone"):
		var ok := false
		for b in req.any_bone:
			if Body.has_bone(equipped, String(b)):
				ok = true
		if not ok:
			return false
	if req.has("tag") and not Body.has_tag(equipped, String(req.tag)):
		return false
	if req.has("dust") and dust < int(req.dust):
		return false
	if req.has("family"):
		var counts := Body.family_counts(equipped)
		if int(counts.get(String(req.family), 0)) < int(req.get("family_count", 1)):
			return false
	if req.has("has_bones") and non_basic_bones().is_empty():
		return false
	if req.has("hp_above") and hp / max_hp <= float(req.hp_above):
		return false
	return true


func non_basic_bones() -> Array:
	var out := []
	for slot in equipped:
		var b := GameData.bone(String(equipped[slot].id))
		if String(b.get("rarity", "")) != "basic":
			out.append(slot)
	return out


# --------------------------------------------------------------- recompensas

func end_rewards() -> Dictionary:
	var per_floor := int(GameData.bal("dust/per_floor", 10))
	var per_boss := int(GameData.bal("dust/per_boss", 50))
	var base := floor_n * per_floor + bosses_beaten.size() * per_boss + dust
	var bonus := stat("dust_bonus")
	var tower_mult := float(GameData.tower(tower).get("dust_mult", 1.0))
	var total := int(roundf(base * (1.0 + bonus) * tower_mult))
	return {"floors": floor_n * per_floor, "bosses": bosses_beaten.size() * per_boss, "collected": dust, "bonus_pct": bonus,
		"tower_mult": tower_mult, "total": total}
