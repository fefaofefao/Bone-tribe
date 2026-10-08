class_name Body
extends RefCounted
## Regras do corpo montável: atributos dos ossos, sinergias de família,
## formas (de família e secretas), rejeição e nome automático da criatura.
## `equipped` é um dicionário slot_id -> {"id": bone_id, "level": int, "rarity": String opcional}.

const STAT_KEYS := ["hp", "atk", "def", "crit", "dodge", "speed", "lifesteal", "reflect", "regen",
	"dust_bonus", "shield_start", "atk_pct", "hp_pct", "def_pct", "poison_bonus", "fire_bonus",
	"trap_avoid", "drop_bonus", "rare_event_bonus", "crit_mult"]


static func instance_rarity(inst: Dictionary) -> String:
	if inst.has("rarity") and String(inst.rarity) != "":
		return String(inst.rarity)
	return String(GameData.bone(String(inst.get("id", ""))).get("rarity", "common"))


## Multiplicador do osso: nível (+25% por nível) e raridade melhorada pela Bigorna.
static func instance_power(inst: Dictionary) -> float:
	var lvl := int(inst.get("level", 1))
	var p := 1.0 + float(GameData.bal("bone_level_bonus", 0.25)) * (lvl - 1)
	var base_rarity := String(GameData.bone(String(inst.get("id", ""))).get("rarity", "common"))
	if base_rarity == "common" and instance_rarity(inst) == "rare":
		p *= 1.5
	return p


static func family_counts(equipped: Dictionary) -> Dictionary:
	var counts := {}
	for slot in equipped:
		var b := GameData.bone(String(equipped[slot].get("id", "")))
		var fam := String(b.get("family", ""))
		if fam == "":
			continue
		counts[fam] = int(counts.get(fam, 0)) + 1
	return counts


static func has_bone(equipped: Dictionary, bone_id: String) -> bool:
	for slot in equipped:
		if String(equipped[slot].get("id", "")) == bone_id:
			return true
	return false


static func has_tag(equipped: Dictionary, tag: String) -> bool:
	for slot in equipped:
		var b := GameData.bone(String(equipped[slot].get("id", "")))
		if (b.get("tags", []) as Array).has(tag):
			return true
	return false


## Formas ativas, da mais importante para a menos importante.
static func active_forms(equipped: Dictionary) -> Array:
	var counts := family_counts(equipped)
	var out := []
	for fid in GameData.form_order:
		var f: Dictionary = GameData.forms[fid]
		if f.has("family"):
			if int(counts.get(f.family, 0)) >= int(f.get("pieces", 4)):
				out.append(fid)
			continue
		var recipe: Dictionary = f.get("recipe", {})
		if recipe.has("bones"):
			var ok := true
			for bid in recipe.bones:
				if not has_bone(equipped, bid):
					ok = false
					break
			if ok:
				out.append(fid)
		elif recipe.has("distinct_families"):
			if counts.size() >= int(recipe.distinct_families):
				out.append(fid)
	out.sort_custom(func(a, b): return int(GameData.forms[a].get("priority", 0)) > int(GameData.forms[b].get("priority", 0)))
	return out


static func rejection_active(equipped: Dictionary) -> bool:
	var counts := family_counts(equipped)
	for pair in GameData.bal("rejection/pairs", []):
		if counts.has(pair[0]) and counts.has(pair[1]):
			return true
	return false


static func _add_stats(total: Dictionary, stats: Dictionary, mult: float = 1.0) -> void:
	for k in stats:
		total[k] = float(total.get(k, 0.0)) + float(stats[k]) * mult


static func _scaled_effects(effects: Array, power: float) -> Array:
	var out := []
	for e in effects:
		var c: Dictionary = e.duplicate(true)
		if c.has("mult") and power != 1.0:
			c["mult"] = float(c.mult) * power
		out.append(c)
	return out


## Soma de atributos e lista de efeitos do corpo atual.
## extra: lista de dicionários {stats, effects} (melhorias de nível, permanentes, etc.).
static func compute(equipped: Dictionary, extra: Array = []) -> Dictionary:
	var total := {}
	var effects := []
	for slot in equipped:
		var inst: Dictionary = equipped[slot]
		var b := GameData.bone(String(inst.get("id", "")))
		if b.is_empty():
			continue
		var p := instance_power(inst)
		_add_stats(total, b.get("stats", {}), p)
		effects.append_array(_scaled_effects(b.get("effects", []), p))
	var counts := family_counts(equipped)
	for fam in counts:
		if int(counts[fam]) >= 2:
			var fd: Dictionary = GameData.families.get(fam, {})
			_add_stats(total, fd.get("synergy2", {}).get("stats", {}))
	var forms := active_forms(equipped)
	for fid in forms:
		var f: Dictionary = GameData.forms[fid]
		_add_stats(total, f.get("stats", {}))
		effects.append_array((f.get("effects", []) as Array).duplicate(true))
		for e in f.get("effects", []):
			if e.get("type", "") == "all_stats_per_family":
				var v := float(e.get("value", 0.08)) * counts.size()
				_add_stats(total, {"atk_pct": v, "hp_pct": v, "def_pct": v, "crit": v * 0.25, "dodge": v * 0.25})
	for x in extra:
		_add_stats(total, x.get("stats", {}))
		effects.append_array((x.get("effects", []) as Array).duplicate(true))
	var rejection := rejection_active(equipped)
	return {"stats": total, "effects": effects, "forms": forms, "families": counts, "rejection": rejection}


## Cria o lutador do Ossinho a partir do corpo.
static func make_hero(equipped: Dictionary, extra: Array = []) -> Fighter:
	var c := compute(equipped, extra)
	var s: Dictionary = c.stats
	var h: Dictionary = GameData.balance.get("hero", {})
	var f := Fighter.new()
	f.id = "hero"
	f.name_key = "hero_name"
	f.is_hero = true
	f.max_hp = roundf((float(h.get("hp", 100)) + float(s.get("hp", 0))) * (1.0 + float(s.get("hp_pct", 0))))
	f.hp = f.max_hp
	f.atk = (float(h.get("atk", 10)) + float(s.get("atk", 0))) * (1.0 + float(s.get("atk_pct", 0)))
	f.def = (float(h.get("def", 0)) + float(s.get("def", 0))) * (1.0 + float(s.get("def_pct", 0)))
	f.crit = clampf(float(h.get("crit", 0.05)) + float(s.get("crit", 0)), 0.0, 0.95)
	f.crit_mult = float(h.get("crit_mult", 1.5)) + float(s.get("crit_mult", 0))
	f.dodge = clampf(float(s.get("dodge", 0)), 0.0, 0.6)
	f.speed = float(h.get("speed", 10)) + float(s.get("speed", 0))
	f.lifesteal = float(s.get("lifesteal", 0))
	f.reflect = float(s.get("reflect", 0))
	f.regen = float(s.get("regen", 0))
	f.poison_bonus = float(s.get("poison_bonus", 0))
	f.fire_bonus = float(s.get("fire_bonus", 0))
	f.effects = c.effects
	f.flags["shield_start"] = float(s.get("shield_start", 0))
	var fams: Dictionary = c.families
	f.fire_resist = fams.has("family_dragon") or fams.has("family_marine")
	if c.rejection:
		f.damage_mult += float(GameData.bal("rejection/damage_bonus", 0.25))
	for e in c.effects:
		if e.get("type", "") == "revive_once":
			f.flags["revive_available"] = float(e.get("pct", 0.5))
	return f


## Nome automático: palavra do crânio + hífen + palavra das pernas + adjetivo da cauda.
static func creature_name(equipped: Dictionary) -> String:
	var skull := _part(equipped, "slot_skull", "name_part")
	var legs := _part(equipped, "slot_legs", "name_part")
	var adj := _part(equipped, "slot_tail", "adjective")
	return TranslationServer.translate("creature_name_format").format({"skull": skull, "legs": legs, "adj": adj}).strip_edges()


static func _part(equipped: Dictionary, slot: String, field: String) -> String:
	var inst: Dictionary = equipped.get(slot, {})
	var b := GameData.bone(String(inst.get("id", "")))
	if b.is_empty() or String(b.get("rarity", "")) == "basic":
		return TranslationServer.translate("name_empty_adj" if field == "adjective" else "name_empty_part")
	return TranslationServer.translate(String(b.get(field, "")))
