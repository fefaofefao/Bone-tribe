class_name Meta
extends RefCounted
## Progressão permanente entre partidas: Ossuário, Coleção de ossos, Relíquias,
## Gabinete de Curiosidades, Companheiros e Caçador de Ossos. Lê e grava em Profile.


## Bônus permanentes aplicados no início de cada partida.
static func permanent_extras() -> Array:
	return [
		{"stats": ossuary_stats(), "effects": []},
		{"stats": collection_stats(), "effects": []},
		{"stats": relic_stats(), "effects": []},
		{"stats": cabinet_stats(), "effects": []},
	]


static func _add(total: Dictionary, stats: Dictionary, mult: float = 1.0) -> void:
	for k in stats:
		total[k] = float(total.get(k, 0.0)) + float(stats[k]) * mult


static func cost(base: float, growth: float, level: int) -> int:
	return int(roundf(base * pow(growth, level)))


# ---------------------------------------------------------------- Ossuário

const OSSUARY_STATS := ["hp", "atk", "def", "drop"]


static func ossuary_level(stat: String) -> int:
	return int(Profile.data.ossuary.get(stat, 0))


static func ossuary_cost(stat: String) -> int:
	return cost(float(GameData.bal("ossuary/cost_base", 50)), float(GameData.bal("ossuary/cost_growth", 1.25)), ossuary_level(stat))


static func ossuary_max() -> int:
	return int(GameData.bal("ossuary/max_level", 30))


static func ossuary_stats() -> Dictionary:
	var per: Dictionary = GameData.bal("ossuary/per_level", {})
	return {
		"hp_pct": ossuary_level("hp") * float(per.get("hp", 0.05)),
		"atk_pct": ossuary_level("atk") * float(per.get("atk", 0.05)),
		"def": ossuary_level("def") * float(per.get("def", 1)),
		"drop_bonus": ossuary_level("drop") * float(per.get("drop", 0.01)),
	}


static func ossuary_upgrade(stat: String) -> bool:
	if ossuary_level(stat) >= ossuary_max():
		return false
	if not Profile.spend_dust(ossuary_cost(stat), "ossuary_" + stat):
		return false
	Profile.data.ossuary[stat] = ossuary_level(stat) + 1
	Profile.save()
	Backend.log_event("ossuary_upgrade", {"stat": stat, "level": ossuary_level(stat)})
	return true


# --------------------------------------------------------- Coleção de ossos

static func family_bones(fam: String) -> Array:
	return GameData.bones_by({"family": fam})


static func family_complete(fam: String) -> bool:
	for id in family_bones(fam):
		if not Profile.is_bone_discovered(id):
			return false
	return true


## Completar uma família dá +5% permanente em vida, ataque e defesa.
static func collection_stats() -> Dictionary:
	var out := {}
	var v := float(GameData.bal("collection/family_complete_bonus", 0.05))
	for fam in GameData.families:
		if family_complete(fam):
			_add(out, {"hp_pct": v, "atk_pct": v, "def_pct": v})
	return out


static func discovered_count() -> int:
	var n := 0
	for id in GameData.catalog_bones():
		if Profile.is_bone_discovered(id):
			n += 1
	return n


static func _free_start_rarity(r: String) -> bool:
	return (GameData.bal("collection/start_bone_rarities_free", ["common"]) as Array).has(r)


## Ossos que podem começar a partida encaixados: descobertos; raros e lendários
## exigem uma ficha "Osso inicial raro" da loja.
static func can_start_with(bone_id: String) -> bool:
	if not Profile.is_bone_discovered(bone_id):
		return false
	if _free_start_rarity(String(GameData.bone(bone_id).get("rarity", "common"))):
		return true
	return int(Profile.data.get("rare_start_tokens", 0)) > 0


## Consome o osso inicial escolhido (gasta a ficha se for raro).
static func take_start_bone() -> String:
	var id := String(Profile.data.get("starting_bone", ""))
	if id == "" or not can_start_with(id):
		return ""
	if not _free_start_rarity(String(GameData.bone(id).get("rarity", "common"))):
		Profile.data.rare_start_tokens = int(Profile.data.rare_start_tokens) - 1
		Profile.data.starting_bone = ""
		Profile.save()
	return id


# ---------------------------------------------------------------- Relíquias

const RELIC_SLOTS := ["relic_amulet", "relic_ring", "relic_cloak", "relic_lantern"]


static func relics_owned() -> Array:
	return Profile.data.relics.get("owned", [])


static func relic_by_uid(uid: int) -> Dictionary:
	for r in relics_owned():
		if int(r.uid) == uid:
			return r
	return {}


static func relic_equipped(slot: String) -> Dictionary:
	var uid := int(Profile.data.relics.equipped.get(slot, 0))
	return relic_by_uid(uid) if uid > 0 else {}


static func add_relic(relic_id: String) -> Dictionary:
	var rel: Dictionary = Profile.data.relics
	var uid := int(rel.get("next_uid", 1))
	var r := {"uid": uid, "id": relic_id, "level": 1}
	rel.owned.append(r)
	rel.next_uid = uid + 1
	var slot := String(GameData.relics.get(relic_id, {}).get("slot", ""))
	if slot != "":
		var cur := relic_equipped(slot)
		if cur.is_empty() or _relic_rank(relic_id) > _relic_rank(String(cur.id)):
			rel.equipped[slot] = uid
	Profile.save()
	Backend.log_event("relic_gain", {"relic": relic_id})
	return r


static func _relic_rank(id: String) -> int:
	return int(RANK.get(String(GameData.relics.get(id, {}).get("rarity", "common")), 1))


static func equip_relic(uid: int) -> void:
	var r := relic_by_uid(uid)
	if r.is_empty():
		return
	Profile.data.relics.equipped[String(GameData.relics[r.id].slot)] = uid
	Profile.save()


static func relic_power(r: Dictionary) -> float:
	return 1.0 + float(GameData.bal("relics/per_level", 0.15)) * (int(r.get("level", 1)) - 1)


static func relic_upgrade_cost(r: Dictionary) -> int:
	return cost(float(GameData.bal("relics/upgrade_cost_base", 80)), float(GameData.bal("relics/upgrade_cost_growth", 1.4)), int(r.get("level", 1)) - 1)


static func relic_upgrade(uid: int) -> bool:
	var r := relic_by_uid(uid)
	if r.is_empty() or int(r.level) >= int(GameData.bal("relics/max_level", 10)):
		return false
	if not Profile.spend_dust(relic_upgrade_cost(r), "relic_upgrade"):
		return false
	r.level = int(r.level) + 1
	Profile.save()
	return true


static func relic_stats() -> Dictionary:
	var out := {}
	for slot in RELIC_SLOTS:
		var r := relic_equipped(slot)
		if r.is_empty():
			continue
		_add(out, GameData.relics.get(r.id, {}).get("stats", {}), relic_power(r))
	return out


static func random_relic(rarity: String, rng: RandomNumberGenerator) -> String:
	var pool := []
	for id in GameData.relics:
		if String(GameData.relics[id].rarity) == rarity:
			pool.append(id)
	return pool[rng.randi() % pool.size()] if not pool.is_empty() else ""


## Baú de ossos do Ossuário: chances mostradas antes de abrir (exigência da Google Play).
static func chest_odds() -> Dictionary:
	return GameData.bal("relics/chest/odds", {})


static func open_bone_chest(rng: RandomNumberGenerator) -> Dictionary:
	var odds := chest_odds()
	var total := 0.0
	for k in odds:
		total += float(odds[k])
	var r := rng.randf() * total
	var pick := "curiosity"
	for k in odds:
		r -= float(odds[k])
		if r <= 0.0:
			pick = k
			break
	if pick == "curiosity":
		var ids: Array = GameData.curiosities.keys()
		var cid: String = ids[rng.randi() % ids.size()]
		var stars := add_curiosity(cid)
		return {"type": "curiosity", "id": cid, "stars": stars}
	var rel := random_relic(pick.replace("relic_", ""), rng)
	add_relic(rel)
	return {"type": "relic", "id": rel}


# ------------------------------------------------- Gabinete de Curiosidades

static func curiosity_stars(id: String) -> int:
	return int(Profile.data.cabinet.get(id, 0))


## Ganha um item; repetidos sobem uma estrela (até 5). Devolve as estrelas.
static func add_curiosity(id: String) -> int:
	if not GameData.curiosities.has(id):
		return 0
	var s := mini(int(GameData.bal("curiosity_max_stars", 5)), curiosity_stars(id) + 1)
	Profile.data.cabinet[id] = s
	Profile.save()
	Backend.log_event("curiosity", {"item": id, "stars": s})
	return s


static func set_complete(set_id: String) -> bool:
	for it in GameData.curiosity_sets.get(set_id, {}).get("items", []):
		if curiosity_stars(it) <= 0:
			return false
	return true


## Cada estrela acima da 1ª aumenta o bônus do item em 50%; conjuntos completos
## dão um bônus extra.
static func cabinet_stats() -> Dictionary:
	var out := {}
	for id in GameData.curiosities:
		var s := curiosity_stars(id)
		if s <= 0:
			continue
		_add(out, GameData.curiosities[id].get("stats", {}), 1.0 + 0.5 * (s - 1))
	for sid in GameData.curiosity_sets:
		if set_complete(sid):
			_add(out, GameData.curiosity_sets[sid].get("bonus", {}))
	return out


## Item aleatório de uma origem ("chest", "merchant", "boss_rat_king"...),
## preferindo os que ainda faltam.
static func random_curiosity(source: String, rng: RandomNumberGenerator) -> String:
	var pool := []
	for id in GameData.curiosities:
		if String(GameData.curiosities[id].source) == source:
			pool.append(id)
	if pool.is_empty():
		return ""
	var missing := pool.filter(func(x): return curiosity_stars(x) == 0)
	if not missing.is_empty() and rng.randf() < 0.7:
		pool = missing
	return pool[rng.randi() % pool.size()]


# ------------------------------------------------------------- Companheiros

static func companion_unlocked(id: String) -> bool:
	return Profile.data.companions.has(id)


static func unlock_companion(id: String) -> bool:
	if companion_unlocked(id) or not GameData.companions.has(id):
		return false
	Profile.data.companions[id] = {"unlocked": true, "level": 1}
	Profile.save()
	Backend.log_event("companion_unlock", {"companion": id})
	return true


static func companion_level(id: String) -> int:
	return int(Profile.data.companions.get(id, {}).get("level", 1))


static func companion_max(id: String) -> int:
	return int(GameData.companions.get(id, {}).get("max_level", 10))


static func companion_upgrade_cost(id: String) -> int:
	var c: Dictionary = GameData.companions.get(id, {})
	return cost(float(c.get("cost_base", 120)), float(c.get("cost_growth", 1.5)), companion_level(id) - 1)


static func companion_upgrade(id: String) -> bool:
	if not companion_unlocked(id) or companion_level(id) >= companion_max(id):
		return false
	if not Profile.spend_dust(companion_upgrade_cost(id), "companion_" + id):
		return false
	Profile.data.companions[id].level = companion_level(id) + 1
	Profile.save()
	return true


## Efeito de combate do companheiro (Lumi cura a cada 3 turnos).
static func companion_combat(id: String) -> Dictionary:
	var c: Dictionary = GameData.companions.get(id, {})
	if c.is_empty() or not companion_unlocked(id):
		return {}
	var e: Dictionary = c.get("combat", {})
	if e.is_empty():
		return {}
	var out := e.duplicate()
	if out.has("heal_pct"):
		out.heal_pct = float(out.heal_pct) * (1.0 + float(c.get("per_level", 0.1)) * (companion_level(id) - 1))
	return out


## Ossudo: chance de trazer um osso extra depois de cada combate.
static func ossudo_chance(id: String) -> float:
	if id != "companion_ossudo" or not companion_unlocked(id):
		return 0.0
	var c: Dictionary = GameData.companions[id]
	return float(c.get("extra_bone_chance", 0.15)) + float(c.get("per_level", 0.02)) * (companion_level(id) - 1)


## Bigorna: quantas forjas (comum -> raro) por partida.
static func bigorna_uses(id: String) -> int:
	if id != "companion_bigorna" or not companion_unlocked(id):
		return 0
	var c: Dictionary = GameData.companions[id]
	return int(c.get("forge_uses", 1)) + int((companion_level(id) - 1) / int(c.get("per_level_uses_every", 5)))


# --------------------------------------------------------- Caçador de Ossos

const RANK := {"basic": 0, "common": 1, "rare": 2, "legendary": 3}


static func hunter_stolen() -> Array:
	return Profile.data.hunter.get("stolen", [])


## Quando o Ossinho morre, o Caçador rouba o melhor osso que ele carregava.
static func hunter_steal(equipped: Dictionary) -> Dictionary:
	var best := {}
	var best_score := -1
	for slot in equipped:
		var inst: Dictionary = equipped[slot]
		var r := Body.instance_rarity(inst)
		if r == "basic":
			continue
		var score := int(RANK.get(r, 1)) * 10 + int(inst.get("level", 1))
		if score > best_score:
			best_score = score
			best = {"id": String(inst.id), "level": int(inst.get("level", 1))}
	if best.is_empty():
		return {}
	var stolen := hunter_stolen()
	stolen.append(best)
	var mx := int(GameData.bal("hunter/max_stolen", 7))
	while stolen.size() > mx:
		stolen.pop_front()
	Profile.data.hunter.stolen = stolen
	Profile.save()
	Backend.log_event("hunter_steal", {"bone": best.id})
	return best


## Corpo do Caçador: os ossos roubados, um por encaixe.
static func hunter_body() -> Dictionary:
	var eq := {}
	for inst in hunter_stolen():
		var slots := GameData.bone_slots(String(inst.id))
		var placed := false
		for s in slots:
			if s == "slot_arm_third":
				continue
			if not eq.has(s):
				eq[s] = inst.duplicate()
				placed = true
				break
		if not placed and not slots.is_empty():
			eq[slots[0]] = inst.duplicate()
	return eq


## Vencer o Caçador devolve o osso roubado mais recente com um nível a mais.
static func hunter_return() -> Dictionary:
	var stolen := hunter_stolen()
	if stolen.is_empty():
		return {}
	var inst: Dictionary = stolen.pop_back()
	Profile.data.hunter.stolen = stolen
	Profile.save()
	return {"id": inst.id, "level": mini(int(GameData.bal("bone_max_level", 5)), int(inst.get("level", 1)) + 1)}
