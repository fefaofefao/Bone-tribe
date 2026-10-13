extends Node
## Compras reais pelo Google Play Billing (plugin oficial GodotGooglePlayBilling).
## Consumíveis (diamantes e Cartão do Coveiro de 30 dias) são consumidos; os
## demais (Kit 24h, sem anúncios, apoiador, skins) são reconhecidos.
## O conteúdo só é entregue depois que a Google confirma o consumo ou o
## reconhecimento, então uma compra interrompida é concluída na próxima abertura.

signal restored(product_id: String)

const CONSUMABLE_KINDS := ["diamonds", "subscription"]
const RECONNECT_S := 5.0

var client: BillingClient
var details := {}
var _waiting := {}
var _token_product := {}


static func available() -> bool:
	return OS.get_name() == "Android" and Engine.has_singleton("GodotGooglePlayBilling")


func _ready() -> void:
	client = BillingClient.new()
	add_child(client)
	client.connected.connect(_on_connected)
	client.disconnected.connect(_on_disconnected)
	client.connect_error.connect(func(_code, _msg): _on_disconnected())
	client.query_product_details_response.connect(_on_details)
	client.query_purchases_response.connect(_on_query_purchases)
	client.on_purchase_updated.connect(_on_purchase_updated)
	client.consume_purchase_response.connect(_on_token_response)
	client.acknowledge_purchase_response.connect(_on_token_response)
	client.start_connection()


func _product_ids() -> PackedStringArray:
	var ids := PackedStringArray()
	for p in GameData.shop.get("iap", []):
		ids.append(String(p.id))
	return ids


func _on_connected() -> void:
	client.query_product_details(_product_ids(), BillingClient.ProductType.INAPP)
	client.query_purchases(BillingClient.ProductType.INAPP)


func _on_disconnected() -> void:
	get_tree().create_timer(RECONNECT_S, true).timeout.connect(func():
		if not client.is_ready():
			client.start_connection())


func _on_details(r: Dictionary) -> void:
	if int(r.get("response_code", -1)) != BillingClient.BillingResponseCode.OK:
		return
	for d in r.get("product_details", []):
		details[String(d.product_id)] = d


## Preço da Play Store já formatado na moeda do jogador ("" se ainda não chegou).
func formatted_price(product_id: String) -> String:
	var d: Dictionary = details.get(product_id, {})
	var offers: Variant = d.get("one_time_purchase_offer_details_list")
	if offers is Array and not (offers as Array).is_empty():
		return String(offers[0].get("formatted_price", ""))
	return ""


# -------------------------------------------------------------- comprar

func purchase(product_id: String) -> bool:
	if not client.is_ready() or not details.has(product_id):
		Widgets.toast(tr("iap_unavailable"))
		if not client.is_ready():
			client.start_connection()
		return false
	var state := {"done": false, "ok": false}
	_waiting[product_id] = state
	var option_id := ""
	var offers: Variant = details[product_id].get("one_time_purchase_offer_details_list")
	if offers is Array and not (offers as Array).is_empty():
		option_id = String(offers[0].get("purchase_option_id", ""))
	var r: Dictionary = client.purchase(product_id, option_id)
	if int(r.get("response_code", -1)) != BillingClient.BillingResponseCode.OK:
		_waiting.erase(product_id)
		Widgets.toast(tr("iap_unavailable"))
		return false
	while not state.done:
		await get_tree().create_timer(0.2, true, false, true).timeout
	_waiting.erase(product_id)
	return state.ok


func _finish_waiting(ok: bool) -> void:
	for id in _waiting:
		_waiting[id].ok = ok
		_waiting[id].done = true


func _on_purchase_updated(r: Dictionary) -> void:
	var code := int(r.get("response_code", -1))
	if code == BillingClient.BillingResponseCode.OK:
		for p in r.get("purchases", []):
			_handle_purchase(p)
		return
	if code == BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED:
		client.query_purchases(BillingClient.ProductType.INAPP)
	elif code != BillingClient.BillingResponseCode.USER_CANCELED:
		Widgets.toast(tr("iap_failed"))
	_finish_waiting(false)


func _on_query_purchases(r: Dictionary) -> void:
	if int(r.get("response_code", -1)) != BillingClient.BillingResponseCode.OK:
		return
	for p in r.get("purchases", []):
		_handle_purchase(p)


func _handle_purchase(p: Dictionary) -> void:
	var state := int(p.get("purchase_state", 0))
	var ids: Array = Array(p.get("product_ids", []))
	if state == BillingClient.PurchaseState.PENDING:
		for id in ids:
			if _waiting.has(id):
				Widgets.toast(tr("iap_pending"), 3.5)
				_waiting[id].done = true
		return
	if state != BillingClient.PurchaseState.PURCHASED or ids.is_empty():
		return
	var id := String(ids[0])
	var token := String(p.get("purchase_token", ""))
	var kind := String(Billing.product(id).get("kind", ""))
	if CONSUMABLE_KINDS.has(kind):
		_token_product[token] = id
		client.consume_purchase(token)
	elif not bool(p.get("is_acknowledged", false)):
		_token_product[token] = id
		client.acknowledge_purchase(token)
	else:
		_deliver(id)


func _on_token_response(r: Dictionary) -> void:
	var token := String(r.get("token", ""))
	var id := String(_token_product.get(token, ""))
	_token_product.erase(token)
	if id == "":
		return
	var ok := int(r.get("response_code", -1)) == BillingClient.BillingResponseCode.OK
	if ok:
		_deliver(id)
	elif _waiting.has(id):
		_waiting[id].done = true


## Entrega: se o jogador está esperando esta compra, quem entrega é a loja;
## senão é uma compra restaurada (reinstalação ou compra interrompida).
func _deliver(id: String) -> void:
	if _waiting.has(id):
		_waiting[id].ok = true
		_waiting[id].done = true
	else:
		restored.emit(id)
