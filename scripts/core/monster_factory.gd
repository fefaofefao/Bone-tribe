class_name MonsterFactory
extends RefCounted
## Cria lutadores de monstros/chefes a partir de data/monsters.json,
## aplicando as fórmulas de equilíbrio do GDD (n = andar).


static func enemy_hp(floor_n: int) -> float:
	return float(GameData.bal("enemy/hp_base", 30)) * pow(float(GameData.bal("enemy/hp_growth", 1.12)), floor_n)


static func enemy_atk(floor_n: int) -> float:
	return float(GameData.bal("enemy/atk_base", 5)) * pow(float(GameData.bal("enemy/atk_growth", 1.10)), floor_n)


static func make(monster_id: String, floor_n: int) -> Fighter:
	var m := GameData.monster(monster_id)
	if m.is_empty():
		push_error("monstro desconhecido: " + monster_id)
		return null
	var f := Fighter.new()
	f.id = monster_id
	f.name_key = String(m.get("name", monster_id + "_name"))
	f.family = String(m.get("family", ""))
	f.is_boss = String(m.get("kind", "")) == "boss"
	var hp := enemy_hp(floor_n) * float(m.get("hp_mult", 1.0))
	var atk := enemy_atk(floor_n) * float(m.get("atk_mult", 1.0))
	if f.is_boss:
		hp *= float(GameData.bal("boss/hp_mult", 8))
		atk *= float(GameData.bal("boss/atk_mult", 1.5))
	f.max_hp = roundf(hp)
	f.hp = f.max_hp
	f.atk = atk
	f.def = float(m.get("def", 0))
	f.crit = float(m.get("crit", 0.05))
	f.dodge = float(m.get("dodge", 0.0))
	f.speed = float(m.get("speed", 10))
	f.lifesteal = float(m.get("lifesteal", 0.0))
	f.reflect = float(m.get("reflect", 0.0))
	f.regen = float(m.get("regen", 0.0))
	f.effects = (m.get("abilities", []) as Array).duplicate(true)
	f.flags["floor"] = floor_n
	return f


## Monstro aleatório adequado ao andar (comuns e raros; nunca chefes/lacaios).
static func random_for_floor(floor_n: int, rng: RandomNumberGenerator) -> String:
	var pool := []
	var weights := []
	for id in GameData.monster_order:
		var m: Dictionary = GameData.monsters[id]
		var kind := String(m.get("kind", ""))
		if kind != "common" and kind != "rare":
			continue
		var fl: Array = m.get("floors", [1, 99])
		if floor_n < int(fl[0]) or floor_n > int(fl[1]):
			continue
		pool.append(id)
		weights.append(0.35 if kind == "rare" else 1.0)
	if pool.is_empty():
		return ""
	var total := 0.0
	for w in weights:
		total += w
	var r := rng.randf() * total
	for i in pool.size():
		r -= weights[i]
		if r <= 0.0:
			return pool[i]
	return pool[-1]


static func xp_for(monster_id: String, floor_n: int) -> int:
	var m := GameData.monster(monster_id)
	var base := float(GameData.bal("xp/per_kill_base", 6)) + float(GameData.bal("xp/per_kill_per_floor", 1.0)) * floor_n
	if String(m.get("kind", "")) == "boss":
		base *= float(GameData.bal("xp/boss_mult", 4))
	return int(roundf(base * float(m.get("xp_mult", 1.0))))


## Osso de um monstro comum: sorteia uma das partes que ele tem e testa a chance
## pela raridade dela. No máximo um osso por monstro, então ter mais variações
## não aumenta a quantidade de ossos por partida.
static func roll_bone_drop(monster_id: String, rng: RandomNumberGenerator, drop_bonus := 0.0) -> String:
	var drops: Array = GameData.monster(monster_id).get("drops", [])
	if drops.is_empty():
		return ""
	var bid := String(drops[rng.randi() % drops.size()])
	var b := GameData.bone(bid)
	var chance := float(GameData.bal("drops/" + String(b.get("rarity", "common")), 0.25)) + drop_bonus
	return bid if rng.randf() < chance else ""


## Ossos que o chefe solta: garantido na 1ª vitória, 10% nas seguintes; um só,
## sorteado entre os ossos do chefe (ex.: Gaiola ou Punho de Golem).
static func boss_drop(monster_id: String, wins_before: int, rng: RandomNumberGenerator) -> String:
	var drops: Array = GameData.monster(monster_id).get("drops", [])
	if drops.is_empty():
		return ""
	var chance := float(GameData.bal("drops/legendary_first", 1.0)) if wins_before == 0 else float(GameData.bal("drops/legendary_repeat", 0.1))
	if rng.randf() >= chance:
		return ""
	return String(drops[rng.randi() % drops.size()])


## Aliado que luta ao lado do Ossinho (não pode ser alvo dos inimigos).
static func make_ally(ally_id: String, floor_n: int) -> Fighter:
	var f := make(ally_id, floor_n)
	if f == null:
		return null
	f.is_ally = true
	f.max_hp = 1
	f.hp = 1
	f.crit = 0.05
	return f


## Estoque do mercador: ossos comuns e raros (nunca de chefe) e, às vezes,
## um lendário já descoberto na Coleção (ver docs/DECISOES.md).
static func merchant_stock(count: int, rarities: Array, rng: RandomNumberGenerator) -> Array:
	var out := []
	var cfg: Dictionary = GameData.bal("merchant", {})
	var rare_w := float(cfg.get("rare_weight", 0.3))
	var tries := 0
	while out.size() < count and tries < 50:
		tries += 1
		var want := "rare" if rng.randf() < rare_w else "common"
		if rarities.has("legendary") and rng.randf() < float(cfg.get("legendary_chance", 0.15)):
			want = "legendary"
		if not rarities.is_empty() and not rarities.has(want):
			want = rarities[0]
		var pool := GameData.bones_by({"rarity": want})
		if want == "legendary":
			pool = pool.filter(func(x): return Profile.is_bone_discovered(x))
		else:
			pool = pool.filter(func(x): return not GameData.bone(x).get("boss_drop", false))
		if pool.is_empty():
			continue
		var bid: String = pool[rng.randi() % pool.size()]
		var dup := false
		for o in out:
			if o.id == bid:
				dup = true
		if not dup:
			var disc := 0.0
			for k in ["merchant_discount"]:
				disc += float(Meta.cabinet_stats().get(k, 0.0))
			out.append({"id": bid, "price": int(roundf(int(cfg.get("prices", {}).get(want, 50)) * (1.0 - disc)))})
	return out


## Altar de troca: um osso de outra família, do mesmo encaixe quando possível.
static func altar_bone(old_id: String, rng: RandomNumberGenerator) -> String:
	var old := GameData.bone(old_id)
	var fam := String(old.get("family", ""))
	var slot := String(GameData.bone_slots(old_id)[0])
	var pool := []
	for id in GameData.catalog_bones():
		var b := GameData.bone(id)
		if String(b.family) == fam or b.get("boss_drop", false):
			continue
		if GameData.bone_slots(id).has(slot):
			pool.append(id)
	if pool.is_empty():
		for id in GameData.catalog_bones():
			var b2 := GameData.bone(id)
			if String(b2.family) != fam and not b2.get("boss_drop", false):
				pool.append(id)
	return pool[rng.randi() % pool.size()] if not pool.is_empty() else ""


## O Caçador de Ossos: um esqueleto rival vestindo os ossos que roubou.
static func make_hunter(floor_n: int) -> Fighter:
	var f := make("boss_bone_hunter", floor_n)
	if f == null:
		return null
	var c := Body.compute(Meta.hunter_body())
	var st: Dictionary = c.stats
	f.is_boss = true
	f.max_hp = roundf(enemy_hp(floor_n) * float(GameData.bal("hunter/hp_mult", 3.5)) * (1.0 + float(st.get("hp_pct", 0.0))) + float(st.get("hp", 0.0)))
	f.hp = f.max_hp
	f.atk = (enemy_atk(floor_n) * float(GameData.bal("hunter/atk_mult", 1.25)) + float(st.get("atk", 0.0))) * (1.0 + float(st.get("atk_pct", 0.0)))
	f.def = float(st.get("def", 0.0))
	f.crit = clampf(0.05 + float(st.get("crit", 0.0)), 0.0, 0.6)
	f.dodge = clampf(float(st.get("dodge", 0.0)), 0.0, 0.4)
	f.lifesteal = float(st.get("lifesteal", 0.0))
	f.reflect = float(st.get("reflect", 0.0))
	f.regen = float(st.get("regen", 0.0))
	f.poison_bonus = float(st.get("poison_bonus", 0.0))
	f.effects = []
	for e in c.effects:
		var t := String(e.get("type", ""))
		if t in ["on_hit_status", "crit_status"]:
			f.effects.append(e)
		elif t == "multi_hit":
			f.effects.append({"type": "multi_attack", "hits": int(e.get("hits", 2)), "mult": float(e.get("mult", 0.6))})
	return f
