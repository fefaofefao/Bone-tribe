class_name Fighter
extends RefCounted
## Um lutador no combate automático (o Ossinho, um monstro, um chefe ou um aliado).

var id: String = ""
var name_key: String = ""
var is_hero := false
var is_ally := false
var is_boss := false
var family: String = ""

var max_hp := 100.0
var hp := 100.0
var atk := 10.0
var def := 0.0
var crit := 0.05
var crit_mult := 1.5
var dodge := 0.0
var speed := 10.0
var lifesteal := 0.0
var reflect := 0.0
var regen := 0.0
var shield := 0.0
var damage_mult := 1.0
var poison_bonus := 0.0
var fire_bonus := 0.0
var fire_resist := false

## Efeitos de combate (lista de dicionários vindos dos JSON).
var effects: Array = []
## Estados: bleed {power, turns}, poison {power, turns}, stack_poison {stacks, power}, stun {turns}
var statuses: Dictionary = {}
var flags: Dictionary = {}

## Escudo do Golem: golpes restantes para quebrar.
var guard_hits := 0
var guard_max := 0
var guard_broken_turns := 0


func alive() -> bool:
	return hp > 0.0


func hp_ratio() -> float:
	return clampf(hp / max_hp, 0.0, 1.0) if max_hp > 0 else 0.0


func has_effect(type: String) -> bool:
	for e in effects:
		if e.get("type", "") == type:
			return true
	return false


func effects_of(type: String) -> Array:
	var out := []
	for e in effects:
		if e.get("type", "") == type:
			out.append(e)
	return out


func heal(amount: float) -> float:
	var before := hp
	hp = minf(max_hp, hp + amount)
	return hp - before


func stunned() -> bool:
	return statuses.has("stun") and int(statuses.stun.turns) > 0
