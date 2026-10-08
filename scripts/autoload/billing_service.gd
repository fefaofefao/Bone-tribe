extends Node
## Fachada de compras no app (Google Play Billing no lançamento).
## Hoje usa MockBillingProvider: aprova a compra depois de uma confirmação
## simulada. Os produtos e preços ficam em data/shop.json -> "iap".
## A entrega do conteúdo é feita por Store (scripts/core/store.gd).

signal purchase_finished(product_id: String, success: bool)

var provider: Node


func _ready() -> void:
	provider = load("res://scripts/services/mock_billing_provider.gd").new()
	add_child(provider)


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
