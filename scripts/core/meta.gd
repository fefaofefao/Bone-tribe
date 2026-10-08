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
