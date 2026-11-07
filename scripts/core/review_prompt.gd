class_name ReviewPrompt
extends RefCounted
## Pedido de avaliação no Google Play (In-App Review), num momento bom: ao voltar de
## uma partida em que o jogador venceu um chefe, a partir da 3ª partida. No máximo
## 2 vezes no total, com 45 dias entre elas (o Google ainda tem o próprio limite).
## Nesse retorno não mostra o intersticial (anúncio e pedido de avaliação juntos irritam).

const MAX_ASKS := 2
const MIN_DAYS := 45
const MIN_RUNS := 3


static func _data() -> Dictionary:
	if not Profile.data.has("review"):
		Profile.data["review"] = {"count": 0, "last": 0, "pending": false}
	return Profile.data.review


## Fim de partida: venceu um chefe ou liberou torre → guarda o pedido para o hub.
static func note_run(beat_boss: bool, tower_cleared: bool) -> void:
	if not (beat_boss or tower_cleared):
		return
	if int(Profile.data.get("runs_played", 0)) < MIN_RUNS:
		return
	_data().pending = true


static func should_ask() -> bool:
	var d := _data()
	if not bool(d.get("pending", false)) or int(d.get("count", 0)) >= MAX_ASKS:
		return false
	var last := int(d.get("last", 0))
	return last <= 0 or Backend.now() - last >= MIN_DAYS * 86400


static func available() -> bool:
	return Engine.has_singleton("BoneTribeReview")


## Pede a avaliação (só no Android com o plugin). Use com await.
static func ask() -> void:
	var d := _data()
	d.pending = false
	if not available():
		Profile.save()
		return
	d.count = int(d.get("count", 0)) + 1
	d.last = Backend.now()
	Profile.save()
	Backend.log_event("review_prompt", {"count": int(d.count)})
	var plugin: Object = Engine.get_singleton("BoneTribeReview")
	plugin.requestReview()
	await (Engine.get_main_loop() as SceneTree).create_timer(0.2).timeout
