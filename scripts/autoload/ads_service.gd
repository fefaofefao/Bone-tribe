extends Node
## Fachada de anúncios (AdMob no lançamento). Hoje usa MockAdsProvider,
## que mostra uma tela simulada de alguns segundos. Sem SDK e sem IDs reais.
## Os limites de cada recompensa ficam em data/shop.json -> "ads".

signal rewarded_finished(placement: String, granted: bool)

var provider: Node


func _ready() -> void:
	provider = load("res://scripts/services/mock_ads_provider.gd").new()
	add_child(provider)


func limit(placement: String) -> int:
	return int(GameData.shop.get("ads", {}).get(placement, {}).get("limit", 0))


## Mostra um anúncio recompensado. Use com await: retorna true se a recompensa
## deve ser entregue.
func show_rewarded(placement: String) -> bool:
	Backend.log_event("ad_rewarded_start", {"placement": placement})
	var granted: bool = await provider.show_rewarded(placement)
	Backend.log_event("ad_rewarded_end", {"placement": placement, "granted": granted})
	rewarded_finished.emit(placement, granted)
	return granted


## Intersticial só a partir da 3ª partida, no máximo um a cada 3 minutos,
## sempre entre partidas. Retorna true se mostrou.
func maybe_show_interstitial() -> bool:
	var cfg: Dictionary = GameData.shop.get("ads", {}).get("interstitial", {})
	var ads: Dictionary = Profile.data.ads
	if ads.removed:
		return false
	if int(Profile.data.runs_played) < int(cfg.get("min_runs", 3)):
		return false
	if Backend.now() - int(ads.last_interstitial) < int(cfg.get("min_interval_s", 180)):
		return false
	await provider.show_interstitial()
	ads.interstitials_seen = int(ads.interstitials_seen) + 1
	ads.last_interstitial = Backend.now()
	Profile.save()
	Backend.log_event("ad_interstitial", {"count": ads.interstitials_seen})
	return true
