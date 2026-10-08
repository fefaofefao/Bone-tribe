extends Node
## Fachada do backend (Firebase no lançamento).
## Fornece horário do servidor (logins, ofertas do dia, Kit 24h) e analytics.
## Hoje usa MockBackendProvider; o provedor real deve implementar os mesmos métodos.

signal server_time_synced(unix_time: int)

var provider: RefCounted


func _ready() -> void:
	provider = load("res://scripts/services/mock_backend_provider.gd").new()
	provider.sync_time()
	server_time_synced.emit(now())


## Horário do servidor em segundos Unix (UTC). Nunca use o relógio do aparelho
## diretamente para recompensas.
func now() -> int:
	return provider.server_now()


## Dia do servidor (troca à meia-noite UTC).
func server_day() -> int:
	return int(floor(now() / 86400.0))


func seconds_to_next_day() -> int:
	return (server_day() + 1) * 86400 - now()


func log_event(event_name: String, params: Dictionary = {}) -> void:
	provider.log_event(event_name, params)


func remote_config(key: String, fallback: Variant) -> Variant:
	return provider.remote_config(key, fallback)


## Apenas para testes (menu de depuração): avança o relógio simulado.
func debug_advance(seconds: int) -> void:
	if provider.has_method("debug_advance"):
		provider.debug_advance(seconds)
