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
