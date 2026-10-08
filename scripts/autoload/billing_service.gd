extends Node
## Fachada de compras no app. No Android usa o Google Play Billing real
## (PlayBillingProvider); no computador e nos testes usa MockBillingProvider,
## que aprova depois de uma confirmação simulada. Os produtos ficam em
## data/shop.json -> "iap" (os IDs são os mesmos da Play Console).
## A entrega do conteúdo é feita por Store (scripts/core/store.gd).

signal purchase_finished(product_id: String, success: bool)

var provider: Node


func _ready() -> void:
	if OS.get_name() == "Android" and Engine.has_singleton("GodotGooglePlayBilling"):
		provider = load("res://scripts/services/play_billing_provider.gd").new()
		provider.restored.connect(_on_restored)
	else:
		provider = load("res://scripts/services/mock_billing_provider.gd").new()
	add_child(provider)


func is_real() -> bool:
	return provider.get_script().resource_path.ends_with("play_billing_provider.gd")


## Compra concluída fora do fluxo normal (reinstalação ou compra interrompida).
## Itens permanentes já entregues neste aparelho não são entregues de novo.
func _on_restored(product_id: String) -> void:
	var p := product(product_id)
	if p.is_empty():
		return
	var kind := String(p.get("kind", ""))
	var owned := int(Profile.data.shop.purchases.get(product_id, 0)) > 0
	if owned and not ["diamonds", "subscription"].has(kind):
		return
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	Store.deliver_iap(product_id, rng)
	Widgets.toast(tr("iap_restored") % tr(String(p.get("name", product_id))))
	purchase_finished.emit(product_id, true)


func product(product_id: String) -> Dictionary:
	for p in GameData.shop.get("iap", []):
		if p.id == product_id:
			return p
	return {}


## Preço formatado para o país do jogador (simulado pelo idioma).
func price_text(product_id: String) -> String:
	var p := product(product_id)
	if p.is_empty():
		return ""
	if provider.has_method("formatted_price"):
		var real_price: String = provider.formatted_price(product_id)
		if real_price != "":
			return real_price
	if Profile.current_locale() == "pt_BR":
		return tr("price_brl") % _fmt(float(p.get("price_brl", 0.0)), ",")
	return tr("price_usd") % _fmt(float(p.get("price_usd", 0.0)), ".")


func _fmt(v: float, sep: String) -> String:
	return ("%.2f" % v).replace(".", sep)


## Use com await. Retorna true se a compra foi concluída.
func purchase(product_id: String) -> bool:
	Backend.log_event("iap_start", {"product": product_id})
	var ok: bool = await provider.purchase(product_id)
	Backend.log_event("iap_end", {"product": product_id, "success": ok})
	purchase_finished.emit(product_id, ok)
	return ok
