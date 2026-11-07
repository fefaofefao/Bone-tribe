class_name RunSave
extends RefCounted
## "Continuar a partida": a partida em andamento é gravada no começo de cada
## andar em user://run_save.json (arquivo separado do perfil, que não muda).
## Ao morrer, desistir ou terminar, o arquivo é apagado antes de pagar o pó.

const PATH := "user://run_save.json"
const VERSION := 1


static func save(state: RunState) -> void:
	if state == null or state.demo or state.dead:
		return
	var d := {"version": VERSION, "saved_at": Backend.now(), "app": String(ProjectSettings.get_setting("application/config/version", "")), "state": state.to_dict()}
	var tmp := PATH + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify(d))
	f.close()
	# troca de uma vez: um arquivo pela metade nunca fica no lugar do bom
	DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(PATH))


static func clear() -> void:
	if FileAccess.file_exists(PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))


static func _read() -> Dictionary:
	if not FileAccess.file_exists(PATH):
		return {}
	var txt := FileAccess.get_file_as_string(PATH)
	var parsed: Variant = JSON.parse_string(txt)
	if not (parsed is Dictionary) or int(parsed.get("version", 0)) != VERSION or not (parsed.get("state") is Dictionary):
		return {}
	return parsed


## Resumo para o botão "Continuar" ({} quando não há partida para continuar).
static func info() -> Dictionary:
	var d := _read()
	if d.is_empty():
		return {}
	var st: Dictionary = d.state
	if load_state() == null:
		clear()
		return {}
	return {"tower": int(st.get("tower", 1)), "floor": int(st.get("floor_n", 0)) + 1, "level": int(st.get("level", 1)), "endless": bool(st.get("endless", false))}


static func has_save() -> bool:
	return not info().is_empty()


static func load_state() -> RunState:
	var d := _read()
	if d.is_empty():
		return null
	return RunState.from_dict(d.state)
