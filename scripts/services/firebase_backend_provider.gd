extends "res://scripts/services/mock_backend_provider.gd"
## Backend com Firebase (só no Android, quando o plugin BoneTribeFirebase existe).
## Mantém o horário de rede e o registro local do provedor base e, além disso,
## envia os eventos ao Google Analytics 4 e lê o Remote Config.
## Os nomes do jogo também viram os eventos padrão do GA4 (level_start,
## level_end, earn/spend_virtual_currency…), que alimentam os relatórios prontos.

var plugin: Object


func _init(p_plugin: Object) -> void:
	plugin = p_plugin
	plugin.initialize(OS.is_debug_build())


func log_event(event_name: String, params: Dictionary) -> void:
	super.log_event(event_name, params)
	plugin.logEvent(event_name.left(40), _clean(params))
	for ev in _ga4(event_name, params):
		plugin.logEvent(String(ev[0]), _clean(ev[1]))


## Eventos padrão do GA4 equivalentes aos do jogo.
func _ga4(event_name: String, p: Dictionary) -> Array:
	match event_name:
		"run_start":
			var out := [["level_start", {"level_name": "tower_%d" % int(p.get("tower", 1))}]]
			# início da 2ª partida = terminou a primeira (o "tutorial")
			if int(p.get("runs", 0)) == 1 and not bool(p.get("demo", false)):
				out.append(["tutorial_complete", {}])
			return out
		"run_end":
			return [["level_end", {"level_name": "tower_%d" % int(p.get("tower", 1)), "success": int(not bool(p.get("dead", true))), "floor": int(p.get("floor", 0))}]]
		"currency_dust", "currency_diamonds":
			var amount := int(p.get("amount", 0))
			var currency := "bone_dust" if event_name == "currency_dust" else "diamonds"
			if amount >= 0:
				return [["earn_virtual_currency", {"virtual_currency_name": currency, "value": amount}]]
			return [["spend_virtual_currency", {"virtual_currency_name": currency, "value": -amount, "item_name": String(p.get("source", ""))}]]
		"card_share":
			return [["share", {"content_type": "creature_card", "item_id": String(p.get("name", ""))}]]
	return []


## Chaves com até 40 caracteres e só tipos que o Firebase aceita.
func _clean(p: Dictionary) -> Dictionary:
	var out := {}
	for k in p:
		var key := String(k).left(40)
		var v: Variant = p[k]
		match typeof(v):
			TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING:
				out[key] = v
			_:
				out[key] = str(v)
	return out


func remote_config(key: String, fallback: Variant) -> Variant:
	if not plugin.isRemoteConfigReady():
		return fallback
	var s: String = plugin.getRemoteString(key)
	if s == "":
		return fallback
	match typeof(fallback):
		TYPE_INT:
			return int(s) if s.is_valid_int() else fallback
		TYPE_FLOAT:
			return float(s) if s.is_valid_float() else fallback
		TYPE_BOOL:
			return s == "true" or s == "1"
		TYPE_DICTIONARY, TYPE_ARRAY:
			var parsed: Variant = JSON.parse_string(s)
			return parsed if typeof(parsed) == typeof(fallback) else fallback
	return s


func set_collection_enabled(enabled: bool) -> void:
	plugin.setCollectionEnabled(enabled)
