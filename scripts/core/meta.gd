class_name Meta
extends RefCounted
## Progressão permanente entre partidas (Ossuário, Coleção, Relíquias,
## Gabinete de Curiosidades, Companheiros). Lê e grava em Profile.


## Bônus permanentes aplicados no início de cada partida.
static func permanent_extras() -> Array:
	var out := []
	out.append({"stats": ossuary_stats(), "effects": []})
	return out


# ---------------------------------------------------------------- Ossuário

static func ossuary_level(stat: String) -> int:
	return int(Profile.data.ossuary.get(stat, 0))


static func ossuary_cost(stat: String) -> int:
	var k := ossuary_level(stat)
	return int(roundf(float(GameData.bal("ossuary/cost_base", 50)) * pow(float(GameData.bal("ossuary/cost_growth", 1.25)), k)))


static func ossuary_stats() -> Dictionary:
	var per: Dictionary = GameData.bal("ossuary/per_level", {})
	return {
		"hp_pct": ossuary_level("hp") * float(per.get("hp", 0.05)),
		"atk_pct": ossuary_level("atk") * float(per.get("atk", 0.05)),
		"def": ossuary_level("def") * float(per.get("def", 1)),
		"drop_bonus": ossuary_level("drop") * float(per.get("drop", 0.01)),
	}


# ------------------------------------------------------------ Companheiros

static func companion_level(id: String) -> int:
	return int(Profile.data.companions.get(id, {}).get("level", 1))


## Efeito de combate do companheiro (Lumi cura a cada 3 turnos).
static func companion_combat(id: String) -> Dictionary:
	var c: Dictionary = GameData.companions.get(id, {})
	if c.is_empty() or not Profile.data.companions.has(id):
		return {}
	var e: Dictionary = c.get("combat", {})
	if e.is_empty():
		return {}
	var out := e.duplicate()
	var lvl := companion_level(id)
	if out.has("heal_pct"):
		out.heal_pct = float(out.heal_pct) * (1.0 + float(c.get("per_level", 0.1)) * (lvl - 1))
	return out
