extends HubPage
## Loja: Kit das primeiras 24 horas, ofertas do dia, itens por diamantes, skins,
## pacotes de diamantes, Cartão do Coveiro, remover anúncios e pacote apoiador.
## Compras com dinheiro passam pelo Billing simulado; nada é cobrado de verdade.

var rng := RandomNumberGenerator.new()
var _kit_timer: Label
var _daily_timer: Label


func build() -> void:
	rng.randomize()
	if Store.kit_available():
		_kit()
	_daily()
	_items()
	_skins()
	_diamonds()
	_subscription()
	_specials()


func _process(_d: float) -> void:
	if _kit_timer and is_instance_valid(_kit_timer):
		_kit_timer.text = tr("kit_ends_in") % Store.format_time(Store.kit_seconds_left())
	if _daily_timer and is_instance_valid(_daily_timer):
		_daily_timer.text = tr("daily_resets_in") % Store.format_time(Backend.seconds_to_next_day())


func _show(results: Array) -> void:
	if results.is_empty():
		return
	var pop := RewardPopup.show_on(self, "rewards_title", results)
	await pop.closed
	rebuild()


# ----------------------------------------------------------------- kit 24h

func _kit() -> void:
	var p := Store.iap("iap_kit24")
	var c := card(Color(0.26, 0.16, 0.06, 0.97), Style.C_CANDLE)
	var v := Style.vbox(10)
	c.add_child(v)
	v.add_child(Style.title(tr("iap_kit24_name"), 46, Style.C_CANDLE))
	_kit_timer = Style.bold("", 22, Color("ffd9a0"), HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(_kit_timer)
	var row := Style.hbox(10)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	for r in p.content:
		var cell := Style.vbox(2)
		var ic := Widgets.icon(_content_icon(r), 70)
		ic.modulate = RewardPopup.result_color(r)
		cell.add_child(ic)
		cell.add_child(Style.label(_content_text(r), 16, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
		cell.custom_minimum_size = Vector2(140, 0)
		row.add_child(cell)
	v.add_child(row)
	var value := int(p.get("value_diamonds", 850))
	v.add_child(Style.bold(tr("kit_value") % [value, int(roundf(100.0 - 100.0 * float(p.price_usd) / (value * 9.99 / 1200.0)))], 20, Style.C_HEAL, HORIZONTAL_ALIGNMENT_CENTER))
	var buy := Style.button(Billing.price_text("iap_kit24"), "CandleButton", 86)
	buy.add_theme_font_size_override("font_size", 34)
	buy.pressed.connect(func():
		var res: Array = await Store.buy_iap("iap_kit24", rng)
		_show(res))
	v.add_child(buy)
	v.add_child(Style.label(tr("kit_once"), 16, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	body.add_child(c)


func _content_icon(r: Dictionary) -> String:
	match String(r.type):
		"relic_id":
			return "res://art/ui/%s.png" % String(r.id)
		_:
			return RewardPopup.result_icon(r)


func _content_text(r: Dictionary) -> String:
	match String(r.type):
		"relic_id":
			return tr(String(GameData.relics[r.id].name))
		_:
			return RewardPopup.result_text(r)


# ------------------------------------------------------------ ofertas do dia

func _daily() -> void:
	var box := section("daily_title")
	_daily_timer = Style.bold("", 20, Style.C_MUTED)
	box.add_child(_daily_timer)
	var row := Style.hbox(10)
	box.add_child(row)
	for o in Store.daily_offers():
		var item := Store.diamond_item(String(o.id))
		var c := card(Color(Style.C_PANEL_2, 0.96), Style.C_DIAMOND.darkened(0.3))
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var v := Style.vbox(4)
		c.add_child(v)
		v.add_child(Style.bold("-%d%%" % int(roundf(float(o.discount) * 100)), 22, Style.C_HEAL, HORIZONTAL_ALIGNMENT_CENTER))
		v.add_child(Widgets.icon(_item_icon(item), 64))
		v.add_child(Style.label(tr(String(item.name)), 17, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
		var bought := Store.daily_bought(String(o.id))
		var b := price_button(int(o.price), "diamond", not bought and Profile.diamonds() >= int(o.price), "CandleButton")
		if bought:
			b.text = tr("sold_out")
			b.icon = null
		var id := String(o.id)
		var price := int(o.price)
		b.pressed.connect(func(): _show(Store.buy_with_diamonds(id, price, rng, true)))
		v.add_child(b)
		row.add_child(c)


func _item_icon(item: Dictionary) -> String:
	var dir := String(item.get("icon_dir", "ui"))
	return "res://art/%s/%s.png" % [dir, String(item.get("icon", "ui_icon_diamond"))]


# --------------------------------------------------------- itens/diamantes

func _items() -> void:
	var box := section("shop_items_title", tr("shop_items_sub"))
	for item in GameData.shop.get("diamond_items", []):
		if String(item.id) == "item_companion_lumi" and Meta.companion_unlocked("companion_lumi"):
			continue
		var c := card()
		var h := Style.hbox(14)
		c.add_child(h)
		h.add_child(Widgets.icon(_item_icon(item), 72))
		var tv := Style.vbox(2)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(Style.bold(tr(String(item.name)), 24, Style.C_BONE))
		tv.add_child(Style.label(tr(String(item.desc)), 18, Style.C_MUTED))
		if item.get("random", false):
			tv.add_child(Style.label(_odds(String(item.id)), 16, Style.C_CANDLE))
		var owned := _owned_count(String(item.id))
		if owned != "":
			tv.add_child(Style.label(owned, 16, Style.C_HEAL))
		h.add_child(tv)
		var price := int(item.price)
		var b := price_button(price, "diamond", Profile.diamonds() >= price)
		var id := String(item.id)
		b.pressed.connect(func(): _show(Store.buy_with_diamonds(id, price, rng)))
		h.add_child(b)
		box.add_child(c)


func _owned_count(id: String) -> String:
	match id:
		"item_extra_revive":
			return tr("owned_n") % int(Profile.data.extra_revives) if int(Profile.data.extra_revives) > 0 else ""
		"item_rare_start_bone":
			return tr("owned_n") % int(Profile.data.rare_start_tokens) if int(Profile.data.rare_start_tokens) > 0 else ""
	return ""


## Itens aleatórios mostram a chance de cada resultado antes da compra.
func _odds(id: String) -> String:
	match id:
		"item_curiosity_chest_rare":
			var o := Store.curiosity_chest_odds(true)
			return tr("odds_curiosity_rare") % [int(o.count), snappedf(float(o.each), 0.1)]
		"item_relic_rare":
			var n := 0
			for rid in GameData.relics:
				if String(GameData.relics[rid].rarity) == "rare":
					n += 1
			return tr("odds_relic_rare_item") % [n, snappedf(100.0 / maxf(1, n), 0.1)]
	return ""


# ------------------------------------------------------------------- skins

func _skins() -> void:
	var box := section("skins_title", tr("skins_sub"))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	box.add_child(grid)
	var equipped := String(Profile.data.skins.get("equipped", ""))
	for id in GameData.skins:
		var s: Dictionary = GameData.skins[id]
		var owns := Store.owns_skin(id)
		if not owns and String(s.get("source", "")) != "shop":
			continue
		var tint := Color(String(s.tint))
		var c := card(Color(tint.darkened(0.8), 0.96), Style.C_CANDLE if equipped == id else Color(tint, 0.5))
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var v := Style.vbox(6)
		c.add_child(v)
		var prev := SkinPreview.new()
		prev.custom_minimum_size = Vector2(0, 150)
		prev.skin_id = id
		v.add_child(prev)
		v.add_child(Style.bold(tr(String(s.name)), 20, tint, HORIZONTAL_ALIGNMENT_CENTER))
		if owns:
			var eb := Style.button(tr("skin_equipped") if equipped == id else tr("skin_equip"), "DarkButton", 56)
			eb.disabled = equipped == id
			var sid: String = id
			eb.pressed.connect(func():
				Store.equip_skin(sid)
				Haptics.light()
				rebuild())
			v.add_child(eb)
		else:
			var row := Style.hbox(6)
			var price := int(s.get("diamonds", 0))
			var bd := price_button(price, "diamond", Profile.diamonds() >= price)
			bd.custom_minimum_size = Vector2(0, 56)
			bd.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var sid2: String = id
			bd.pressed.connect(func():
				if Store.buy_skin_with_diamonds(sid2):
					_show([{"type": "skin", "id": sid2}]))
			row.add_child(bd)
			var iap_id := String(s.get("iap", ""))
			if iap_id != "":
				var bm := Style.button(Billing.price_text(iap_id), "DarkButton", 56)
				bm.add_theme_font_size_override("font_size", 20)
				bm.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				bm.pressed.connect(func():
					var res: Array = await Store.buy_iap(iap_id, rng)
					_show(res))
				row.add_child(bm)
			v.add_child(row)
		grid.add_child(c)
	if equipped != "":
		var none := Style.button(tr("skin_none"), "DarkButton", 56)
		none.pressed.connect(func():
			Store.equip_skin("")
			rebuild())
		box.add_child(none)


# ---------------------------------------------------------------- diamantes

func _diamonds() -> void:
	var box := section("diamonds_title", tr("diamonds_sub"))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	box.add_child(grid)
	for p in GameData.shop.get("iap", []):
		if String(p.kind) != "diamonds":
			continue
		var c := card(Color(0.08, 0.14, 0.2, 0.96), Style.C_DIAMOND.darkened(0.3))
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var v := Style.vbox(4)
		c.add_child(v)
		v.add_child(Widgets.icon("res://art/ui/ui_icon_diamond.png", 64))
		v.add_child(Style.bold(tr(String(p.name)), 20, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
		v.add_child(Style.bold(Style.num(int(p.content[0].amount)), 30, Style.C_DIAMOND, HORIZONTAL_ALIGNMENT_CENTER))
		var b := Style.button(Billing.price_text(String(p.id)), "CandleButton", 60)
		var pid := String(p.id)
		b.pressed.connect(func():
			var res: Array = await Store.buy_iap(pid, rng)
			_show(res))
		v.add_child(b)
		grid.add_child(c)
	var left := Store.shop_ads_left()
	var ad := Style.button(tr("shop_ad_diamonds") % [int(GameData.shop.ads.shop_diamonds.diamonds), left], "DarkButton", 70)
	ad.icon = load("res://art/ui/ui_icon_diamond.png")
	ad.expand_icon = true
	ad.add_theme_constant_override("icon_max_width", 36)
	ad.disabled = left <= 0
	ad.pressed.connect(func():
		ad.disabled = true
		if await Ads.show_rewarded("shop_diamonds"):
			var n := Store.reward_shop_ad()
			_show([{"type": "diamonds", "amount": n}]))
	box.add_child(ad)


# -------------------------------------------------------- Cartão do Coveiro

func _subscription() -> void:
	var p := Store.iap("iap_gravedigger_card")
	var c := card(Color(0.12, 0.1, 0.16, 0.97), Color("b48cff"))
	var v := Style.vbox(8)
	c.add_child(v)
	var h := Style.hbox(12)
	h.add_child(Widgets.icon("res://art/props/prop_gravedigger.png", 96))
	var tv := Style.vbox(4)
	tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tv.add_child(Style.bold(tr("iap_gravedigger_card_name"), 26, Color("d8c4ff")))
	tv.add_child(Style.label(tr("iap_gravedigger_card_desc"), 18, Style.C_MUTED))
	h.add_child(tv)
	v.add_child(h)
	if Store.subscription_active():
		v.add_child(Style.bold(tr("subscription_active") % Store.subscription_days_left(), 20, Style.C_HEAL, HORIZONTAL_ALIGNMENT_CENTER))
	var b := Style.button(Billing.price_text("iap_gravedigger_card") + "  ·  " + tr("per_month"), "CandleButton", 72)
	b.pressed.connect(func():
		var res: Array = await Store.buy_iap("iap_gravedigger_card", rng)
		if not res.is_empty():
			var daily := Store.claim_subscription(rng)
			_show(daily if not daily.is_empty() else res))
	v.add_child(b)
	body.add_child(c)


func _specials() -> void:
	if Store.remove_ads_offer_visible():
		_special_card("iap_remove_ads", "iap_remove_ads_desc")
	if Store.supporter_visible():
		_special_card("iap_supporter", "iap_supporter_desc")


func _special_card(pid: String, desc_key: String) -> void:
	var p := Store.iap(pid)
	var c := card()
	var v := Style.vbox(6)
	c.add_child(v)
	v.add_child(Style.bold(tr(String(p.name)), 24, Style.C_BONE))
	v.add_child(Style.label(tr(desc_key), 18, Style.C_MUTED))
	var b := Style.button(Billing.price_text(pid), "CandleButton", 66)
	b.pressed.connect(func():
		var res: Array = await Store.buy_iap(pid, rng)
		_show(res))
	v.add_child(b)
	body.add_child(c)
