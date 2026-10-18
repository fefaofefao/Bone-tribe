extends Node
## Notificações locais (só Android, plugin BoneTribeNotify). Ao sair do jogo
## agenda os lembretes; ao voltar, cancela. Nada sai do aparelho.
##   1 = prêmio diário, missões e ofertas novas (depois da virada do dia)
##   2 = Ossudo encheu o saco de pó (tempo máximo offline)
##   3 = o Caçador está com um osso seu

const IDS := [1, 2, 3]

var plugin: Object = null
## Agendadas (id -> {delay, title, body}); também usado pelos testes.
var scheduled: Dictionary = {}


func _ready() -> void:
	if OS.get_name() == "Android" and Engine.has_singleton("BoneTribeNotify"):
		plugin = Engine.get_singleton("BoneTribeNotify")
	cancel_all()


func enabled() -> bool:
	return bool(Profile.setting("notifications")) if Profile.data.settings.has("notifications") else true


## Pede a permissão do Android 13+ uma vez, depois da 1ª partida (nunca ao abrir o jogo).
func maybe_ask_permission() -> void:
	if plugin == null or not enabled() or int(Profile.data.runs_played) < 1:
		return
	if bool(Profile.data.notify.get("asked", false)):
		return
	Profile.data.notify.asked = true
	Profile.save()
	if not plugin.hasPermission():
		plugin.requestPermission()


func cancel_all() -> void:
	scheduled.clear()
	if plugin:
		for id in IDS:
			plugin.cancel(id)


func reschedule() -> void:
	cancel_all()
	if not enabled() or int(Profile.data.runs_played) < 1:
		return
	_add(1, "notif_daily_title", "notif_daily_body", Backend.seconds_to_next_day() + 600)
	_add(2, "notif_offline_title", "notif_offline_body", Offline.cap_seconds())
	var stolen := Meta.hunter_stolen()
	if not stolen.is_empty():
		var bone := tr(String(GameData.bone(String(stolen[-1].id)).get("name", "")))
		_add(3, "notif_hunter_title", tr("notif_hunter_body") % bone, 20 * 3600, true)


func _add(id: int, title_key: String, body: String, delay: int, body_ready := false) -> void:
	# lembretes muito próximos de outro já agendado são pulados
	for k in scheduled:
		if absi(int(scheduled[k].delay) - delay) < 3600:
			return
	var title := tr(title_key)
	var text := body if body_ready else tr(body)
	scheduled[id] = {"delay": delay, "title": title, "body": text}
	if plugin:
		plugin.schedule(id, title, text, delay)


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		reschedule()
	elif what == NOTIFICATION_APPLICATION_RESUMED:
		cancel_all()
