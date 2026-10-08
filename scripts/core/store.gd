class_name Store
extends RefCounted
## Economia de diamantes e loja: entrega de recompensas, calendários de login,
## ofertas do dia, Kit das primeiras 24 horas, Cartão do Coveiro (assinatura),
## anúncios na loja e compras simuladas. Tudo usa o horário do servidor (Backend).


# ------------------------------------------------------------ recompensas

## Entrega uma lista de recompensas e devolve o que foi ganho (para mostrar).
static func grant(rewards: Array, rng: RandomNumberGenerator, source: String = "") -> Array:
	var out := []
	for r in rewards:
		var t := String(r.get("type", ""))
		match t:
			"dust":
				Profile.add_dust(int(r.amount), source)
				out.append({"type": "dust", "amount": int(r.amount)})
			"diamonds":
				Profile.add_diamonds(int(r.amount), source)
				out.append({"type": "diamonds", "amount": int(r.amount)})
			"curiosity":
				out.append(_curiosity(rng, false))
			"curiosity_chest_rare":
				out.append(_curiosity(rng, true))
			"relic":
				var rid := Meta.random_relic(String(r.get("rarity", "rare")), rng)
				Meta.add_relic(rid)
				out.append({"type": "relic", "id": rid})
			"relic_id":
				Meta.add_relic(String(r.id))
				out.append({"type": "relic", "id": String(r.id)})
			"companion":
				Meta.unlock_companion(String(r.id))
				out.append({"type": "companion", "id": String(r.id)})
			"skin":
				add_skin(String(r.id))
				out.append({"type": "skin", "id": String(r.id)})
			"bone_chest":
				out.append(Meta.open_bone_chest(rng))
			"bone_chest_rare":
				if rng.randf() < 0.5:
					var rid2 := Meta.random_relic("rare", rng)
					Meta.add_relic(rid2)
					out.append({"type": "relic", "id": rid2})
				else:
					out.append(_curiosity(rng, true))
			"extra_revive":
				Profile.data.extra_revives = int(Profile.data.extra_revives) + 1
				out.append({"type": "extra_revive"})
			"rare_start_token":
				Profile.data.rare_start_tokens = int(Profile.data.rare_start_tokens) + 1
				out.append({"type": "rare_start_token"})
			"remove_ads":
				Profile.data.ads.removed = true
				out.append({"type": "remove_ads"})
			"supporter":
				Profile.data.supporter = true
				out.append({"type": "supporter"})
	Profile.save()
	return out


## Curiosidades "raras" são as que caem de chefes e eventos raros.
static func curiosity_is_rare(id: String) -> bool:
	var src := String(GameData.curiosities.get(id, {}).get("source", ""))
	return src.begins_with("boss_") or src == "rare"


## Chances do baú de curiosidades (mostradas antes da compra).
static func curiosity_chest_odds(rare: bool) -> Dictionary:
	var ids: Array = GameData.curiosities.keys()
	if rare:
		ids = ids.filter(func(x): return curiosity_is_rare(x))
	return {"count": ids.size(), "each": 100.0 / maxf(1.0, ids.size())}


static func _curiosity(rng: RandomNumberGenerator, rare: bool) -> Dictionary:
	var ids: Array = GameData.curiosities.keys()
	if rare:
		ids = ids.filter(func(x): return curiosity_is_rare(x))
	var id: String = ids[rng.randi() % ids.size()]
	var stars := Meta.add_curiosity(id)
	return {"type": "curiosity", "id": id, "stars": stars}


# ------------------------------------------------------------------- skins

static func owns_skin(id: String) -> bool:
	return (Profile.data.skins.owned as Array).has(id)


static func add_skin(id: String) -> void:
	if not owns_skin(id):
		Profile.data.skins.owned.append(id)
	if String(Profile.data.skins.get("equipped", "")) == "":
		Profile.data.skins.equipped = id
	Profile.save()


static func equip_skin(id: String) -> void:
	Profile.data.skins.equipped = id if (id == "" or owns_skin(id)) else ""
	Profile.save()


static func skin_tint() -> Color:
	var id := String(Profile.data.skins.get("equipped", ""))
	var s: Dictionary = GameData.skins.get(id, {})
	if s.is_empty():
		return Color.WHITE
	var c := Color(String(s.get("tint", "#ffffff")))
	c.a = float(s.get("alpha", 1.0))
	return c


# ------------------------------------------------------------ calendários

static func today() -> int:
	return Backend.server_day()


static func first7_done() -> bool:
	return int(Profile.data.login.first7_claimed) >= 7


static func calendar_id() -> String:
	return "cycle28" if first7_done() else "first7"


static func calendar_days() -> Array:
	return GameData.login.get(calendar_id(), [])


## Índice (0..) do próximo dia a resgatar no calendário atual.
static func calendar_index() -> int:
	var l: Dictionary = Profile.data.login
	if not first7_done():
		return int(l.first7_claimed)
	return int(l.cycle_claimed) % maxi(1, calendar_days().size())


static func can_claim_login() -> bool:
	var l: Dictionary = Profile.data.login
	var t := today()
	return int(l.first7_last_day) != t and int(l.cycle_last_day) != t


## Resgata o dia atual (um por dia do servidor; dias sem login não contam).
static func claim_login(rng: RandomNumberGenerator) -> Array:
	if not can_claim_login():
		return []
	var days := calendar_days()
	var idx := calendar_index()
	var rewards: Array = days[idx].get("rewards", []) if idx < days.size() else []
	var l: Dictionary = Profile.data.login
	if calendar_id() == "first7":
		l.first7_claimed = int(l.first7_claimed) + 1
		l.first7_last_day = today()
	else:
		l.cycle_claimed = int(l.cycle_claimed) + 1
		l.cycle_last_day = today()
	Profile.save()
	Backend.log_event("login_claim", {"calendar": calendar_id(), "day": idx + 1})
	return grant(rewards, rng, "login")


# ------------------------------------------------------------- Kit 24 horas

static func kit_seconds_left() -> int:
	var window := int(GameData.shop.get("kit24", {}).get("window_s", 86400))
	return int(Profile.data.first_open_time) + window - Backend.now()


## O Kit aparece ao fim da 1ª partida e some 24 h depois da instalação.
## Uma compra por conta; depois de comprado ou expirado, não volta.
static func kit_available() -> bool:
	var k: Dictionary = Profile.data.kit24
	if bool(k.bought):
		return false
	if int(Profile.data.runs_played) < 1:
		return false
	return kit_seconds_left() > 0


static func format_time(seconds: int) -> String:
	seconds = maxi(0, seconds)
	return "%02d:%02d:%02d" % [seconds / 3600, (seconds % 3600) / 60, seconds % 60]


# ------------------------------------------------------------ ofertas do dia

## Três itens com desconto que mudam à meia-noite do servidor.
static func daily_offers() -> Array:
	var cfg: Dictionary = GameData.shop.get("daily_offers", {})
	var pool: Array = (cfg.get("pool", []) as Array).duplicate()
	var rng := RandomNumberGenerator.new()
	rng.seed = today() * 7919 + 17
	var out := []
	for i in mini(int(cfg.get("count", 3)), pool.size()):
		var j := rng.randi() % pool.size()
		var item := diamond_item(String(pool[j]))
		pool.remove_at(j)
		var disc := snappedf(rng.randf_range(float(cfg.get("discount_min", 0.2)), float(cfg.get("discount_max", 0.5))), 0.05)
		out.append({"id": item.id, "price": int(roundf(int(item.price) * (1.0 - disc))), "full": int(item.price), "discount": disc})
	return out


static func daily_bought(id: String) -> bool:
	var s: Dictionary = Profile.data.shop
	if int(s.get("daily_day", -1)) != today():
		return false
	return (s.get("daily_bought", []) as Array).has(id)


static func diamond_item(id: String) -> Dictionary:
	for it in GameData.shop.get("diamond_items", []):
		if it.id == id:
			return it
	return {}


## Compra um item por diamantes. Devolve o que foi ganho ou [] se faltou saldo.
static func buy_with_diamonds(id: String, price: int, rng: RandomNumberGenerator, daily := false) -> Array:
	var item := diamond_item(id)
	if item.is_empty() or not Profile.spend_diamonds(price, "shop_" + id):
		return []
	if daily:
		var s: Dictionary = Profile.data.shop
		if int(s.get("daily_day", -1)) != today():
			s.daily_day = today()
			s.daily_bought = []
		s.daily_bought.append(id)
	Backend.log_event("shop_diamond_buy", {"item": id, "price": price})
	return grant(item.get("content", []), rng, "shop")


static func skin_diamond_price(id: String) -> int:
	return int(GameData.skins.get(id, {}).get("diamonds", 0))


static func buy_skin_with_diamonds(id: String) -> bool:
	var price := skin_diamond_price(id)
	if price <= 0 or owns_skin(id) or not Profile.spend_diamonds(price, "skin_" + id):
		return false
	add_skin(id)
	return true


# --------------------------------------------------------- anúncios da loja

static func ad_limit(placement: String) -> int:
	return int(GameData.shop.get("ads", {}).get(placement, {}).get("limit", 0))


static func shop_ads_left() -> int:
	var s: Dictionary = Profile.data.shop
	if int(s.get("ad_day", -1)) != today():
		return ad_limit("shop_diamonds")
	return maxi(0, ad_limit("shop_diamonds") - int(s.get("ad_count", 0)))


static func reward_shop_ad() -> int:
	var s: Dictionary = Profile.data.shop
	if int(s.get("ad_day", -1)) != today():
		s.ad_day = today()
		s.ad_count = 0
	s.ad_count = int(s.ad_count) + 1
	var n := int(GameData.shop.get("ads", {}).get("shop_diamonds", {}).get("diamonds", 5))
	Profile.add_diamonds(n, "shop_ad")
	return n


# ----------------------------------------------------- compras (simuladas)

static func iap(id: String) -> Dictionary:
	return Billing.product(id)


## Compra com dinheiro (Google Play Billing simulado). Use com await.
static func buy_iap(id: String, rng: RandomNumberGenerator) -> Array:
	var p := iap(id)
	if p.is_empty():
		return []
	var ok: bool = await Billing.purchase(id)
	if not ok:
		return []
	var purchases: Dictionary = Profile.data.shop.purchases
	purchases[id] = int(purchases.get(id, 0)) + 1
	var out := []
	match String(p.get("kind", "")):
		"kit24":
			Profile.data.kit24.bought = true
			out = grant(p.get("content", []), rng, "iap")
		"subscription":
			var sub: Dictionary = Profile.data.subscription
			sub.until = maxi(int(sub.until), Backend.now()) + int(p.get("days", 30)) * 86400
			Profile.save()
			out = [{"type": "subscription"}]
		_:
			out = grant(p.get("content", []), rng, "iap")
	Backend.log_event("iap_revenue", {"product": id, "usd": p.get("price_usd", 0)})
	return out


# --------------------------------------------------- Cartão do Coveiro

static func subscription_active() -> bool:
	return int(Profile.data.subscription.until) > Backend.now()


static func subscription_days_left() -> int:
	return maxi(0, int(ceil((int(Profile.data.subscription.until) - Backend.now()) / 86400.0)))


## Recompensas diárias (30 diamantes + pó) e o baú raro semanal da assinatura.
static func claim_subscription(rng: RandomNumberGenerator) -> Array:
	if not subscription_active():
		return []
	var sub: Dictionary = Profile.data.subscription
	var p := iap("iap_gravedigger_card")
	var out := []
	if int(sub.last_daily_day) != today():
		sub.last_daily_day = today()
		out.append_array(grant(p.get("daily", []), rng, "subscription"))
	var week := int(today() / 7)
	if int(sub.last_chest_week) != week:
		sub.last_chest_week = week
		out.append_array(grant(p.get("weekly", []), rng, "subscription"))
	Profile.save()
	return out


static func free_revive_available() -> bool:
	return subscription_active() and int(Profile.data.subscription.free_revive_day) != today()


static func use_free_revive() -> void:
	Profile.data.subscription.free_revive_day = today()
	Profile.save()


# --------------------------------------------------------- ofertas especiais

static func remove_ads_offer_visible() -> bool:
	var p := iap("iap_remove_ads")
	return not bool(Profile.data.ads.removed) and int(Profile.data.ads.interstitials_seen) >= int(p.get("show_after_interstitials", 10))


static func supporter_visible() -> bool:
	return not bool(Profile.data.supporter) and Profile.boss_wins(String(iap("iap_supporter").get("requires_boss", "boss_ancient_dragon"))) > 0
