extends RefCounted
## Provedor simulado do Firebase. Não faz rede e não usa credenciais.
## O horário "do servidor" é o relógio do sistema mais um deslocamento de teste
## persistido em user://mock_backend.json.

const STATE_PATH := "user://mock_backend.json"
const LOG_PATH := "user://analytics_mock.log"

var offset := 0
var _synced_at := 0


func sync_time() -> void:
	if FileAccess.file_exists(STATE_PATH):
		var d: Variant = JSON.parse_string(FileAccess.get_file_as_string(STATE_PATH))
		if typeof(d) == TYPE_DICTIONARY:
			offset = int(d.get("offset", 0))
	_synced_at = int(Time.get_unix_time_from_system())


func server_now() -> int:
	return int(Time.get_unix_time_from_system()) + offset


func debug_advance(seconds: int) -> void:
	offset += seconds
	var f := FileAccess.open(STATE_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"offset": offset}))


func log_event(event_name: String, params: Dictionary) -> void:
	var line := "%d %s %s" % [server_now(), event_name, JSON.stringify(params)]
	if OS.is_debug_build():
		print("[analytics] ", line)
	var f := FileAccess.open(LOG_PATH, FileAccess.READ_WRITE if FileAccess.file_exists(LOG_PATH) else FileAccess.WRITE)
	if f:
		f.seek_end()
		f.store_line(line)


func remote_config(_key: String, fallback: Variant) -> Variant:
	return fallback
