class_name Tutorial
extends RefCounted
## Tutorial guiado: dicas curtas que aparecem uma vez cada, na hora certa,
## durante as primeiras partidas (até MAX_RUNS) e na tela inicial.

const MAX_RUNS := 3


## true na primeira vez que a dica `key` deve aparecer (e já marca como vista).
static func take(key: String, any_run := false) -> bool:
	var t: Dictionary = Profile.data.tutorial
	if t.has(key):
		return false
	if not any_run and int(Profile.data.runs_played) >= MAX_RUNS:
		return false
	t[key] = true
	Backend.log_event("tutorial_step", {"step": key})
	return true


static func seen(key: String) -> bool:
	return Profile.data.tutorial.has(key)
