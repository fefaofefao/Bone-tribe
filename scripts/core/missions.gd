class_name Missions
extends RefCounted
## Missões diárias e semanais (data/missions.json). Cada missão conta uma
## estatística do jogador; o progresso vem de Profile.stat_add. Trocam pela
## hora do servidor (Backend), então mudar o relógio do celular não adianta.


static func _cfg() -> Dictionary:
	return GameData.missions


static func day() -> int:
	return Backend.server_day()


## Semana começando na segunda (o dia 0 do Unix foi uma quinta).
static func week() -> int:
	return int(floor((day() + 3) / 7.0))


static func seconds_to_next_week() -> int:
	return ((week() + 1) * 7 - 3) * 86400 - Backend.now()


## Garante que as missões do dia e da semana atuais estão sorteadas.
static func refresh() -> void:
	var m: Dictionary = Profile.data.missions
	if int(m.get("day", -1)) != day():
		m.day = day()
		m.daily = _roll("daily", int(_cfg().get("daily_count", 3)), day())
	if int(m.get("week", -1)) != week():
		m.week = week()
		m.weekly = _roll("weekly", int(_cfg().get("weekly_count", 3)), week() * 31 + 7)


static func _roll(kind: String, count: int, seed: int) -> Array:
	var pool: Array = (_cfg().get(kind, []) as Array).duplicate()
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	var out := []
	var used_stats := {}
	while out.size() < count and not pool.is_empty():
		var i := rng.randi() % pool.size()
		var d: Dictionary = pool[i]
		pool.remove_at(i)
		if used_stats.has(d.stat):
			continue
		used_stats[d.stat] = true
		out.append({"id": d.id, "progress": 0, "claimed": false})
	return out


static func def(id: String) -> Dictionary:
	for kind in ["daily", "weekly"]:
		for d in _cfg().get(kind, []):
			if String(d.id) == id:
				return d
	return {}


static func list(kind: String) -> Array:
	refresh()
	return Profile.data.missions.get(kind, [])


static func is_done(m: Dictionary) -> bool:
	return int(m.progress) >= int(def(String(m.id)).get("target", 1))


## Soma progresso nas missões que contam esta estatística. Avisa (sinal
## Profile.mission_done) quando uma missão acaba de ser concluída.
static func track(stat: String, n: float) -> void:
	if not Profile.data.has("missions"):
		return
	refresh()
	for kind in ["daily", "weekly"]:
		for m in Profile.data.missions[kind]:
			var d := def(String(m.id))
			if String(d.get("stat", "")) != stat or bool(m.claimed):
				continue
			var was := is_done(m)
			m.progress = mini(int(d.target), int(m.progress) + int(n))
			if not was and is_done(m):
				Profile.mission_done.emit(String(m.id))


## Recompensa já ajustada à torre mais alta liberada.
static func reward(id: String) -> Dictionary:
	var r: Dictionary = def(id).get("reward", {})
	var mult := float(GameData.tower(Meta.tower_unlocked()).get("dust_mult", 1.0))
	return {"dust": int(roundf(int(r.get("dust", 0)) * mult)), "diamonds": int(r.get("diamonds", 0))}


static func claim(kind: String, index: int) -> Dictionary:
	var arr: Array = list(kind)
	if index < 0 or index >= arr.size():
		return {}
	var m: Dictionary = arr[index]
	if bool(m.claimed) or not is_done(m):
		return {}
	m.claimed = true
	var r := reward(String(m.id))
	if int(r.dust) > 0:
		Profile.add_dust(int(r.dust), "mission")
	if int(r.diamonds) > 0:
		Profile.add_diamonds(int(r.diamonds), "mission")
	Backend.log_event("mission_claim", {"id": String(m.id), "kind": kind})
	Profile.save()
	return r


static func claimable_count() -> int:
	var n := 0
	for kind in ["daily", "weekly"]:
		for m in list(kind):
			if is_done(m) and not bool(m.claimed):
				n += 1
	return n
