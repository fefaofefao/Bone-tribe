extends Node
## Fachada do backend (Firebase no lançamento).
## Fornece horário do servidor (logins, ofertas do dia, Kit 24h) e analytics.
## Hoje usa MockBackendProvider; o provedor real deve implementar os mesmos métodos.

signal server_time_synced(unix_time: int)

var provider: RefCounted


const TIME_URL := "https://www.google.com/generate_204"

var _http: HTTPRequest


func _ready() -> void:
	provider = load("res://scripts/services/mock_backend_provider.gd").new()
	provider.sync_time()
	server_time_synced.emit(now())
	if not OS.is_debug_build() or OS.get_name() == "Android":
		sync_network_time()


## Acerta o relógio pelo cabeçalho "Date" de um servidor do Google, para que
## mudar o relógio do celular não libere logins e ofertas antes da hora.
func sync_network_time() -> void:
	if _http == null:
		_http = HTTPRequest.new()
		_http.timeout = 8.0
		add_child(_http)
		_http.request_completed.connect(_on_time_response)
	if _http.get_http_client_status() == HTTPClient.STATUS_DISCONNECTED:
		_http.request(TIME_URL, PackedStringArray(), HTTPClient.METHOD_HEAD)


func _on_time_response(result: int, _code: int, headers: PackedStringArray, _body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	for h in headers:
		if h.to_lower().begins_with("date:"):
			var t := parse_http_date(h.substr(5).strip_edges())
			if t > 0 and provider.has_method("set_server_time"):
				provider.set_server_time(t)
				server_time_synced.emit(now())
			return


## "Wed, 08 Oct 2026 17:00:00 GMT" -> segundos Unix (0 se inválido).
static func parse_http_date(s: String) -> int:
	const MONTHS := ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
	var parts := s.split(" ", false)
	if parts.size() < 5:
		return 0
	var month := MONTHS.find(parts[2].to_lower().left(3)) + 1
	var hms := parts[4].split(":")
	if month <= 0 or hms.size() != 3:
		return 0
	return Time.get_unix_time_from_datetime_dict({"year": int(parts[3]), "month": month, "day": int(parts[1]),
		"hour": int(hms[0]), "minute": int(hms[1]), "second": int(hms[2])})


func _notification(what: int) -> void:
	# ao voltar para o jogo, confere o relógio de novo
	if what == NOTIFICATION_APPLICATION_RESUMED and _http != null:
		sync_network_time()
	elif what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		if provider and provider.has_method("_save"):
			provider._save()


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
