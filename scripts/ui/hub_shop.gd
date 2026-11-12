extends HubPage
## Loja: Kit das primeiras 24 horas, ofertas do dia, itens por diamantes, skins,
## pacotes de diamantes, Cartão do Coveiro, remover anúncios e pacote apoiador.
## Compras com dinheiro passam pelo Billing simulado; nada é cobrado de verdade.

var rng := RandomNumberGenerator.new()
var _kit_timer: Label
var _daily_timer: Label


func build() -> void:
	rng.randomize()
	# Cartão do Coveiro é o carro-chefe: sempre o primeiro da loja
	_subscription()
	if Store.kit_available():
		_kit()
	_daily()
	_items()
	_skins()
	_diamonds()
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
		var sub_skin := String(s.get("source", "")) == "subscription"
		if not owns and String(s.get("source", "")) != "shop" and not sub_skin:
			continue
		var tint := Color(String(s.get("glow", "#ffffff")))
		var c := card(Color(tint.darkened(0.82), 0.96), Style.C_CANDLE if equipped == id else Color(tint, 0.55))
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var v := Style.vbox(6)
		c.add_child(v)
		var prev := SkinPreview.new()
		prev.custom_minimum_size = Vector2(0, 250)
		prev.skin_id = id
		v.add_child(prev)
		v.add_child(Style.bold(tr(String(s.name)), 21, tint.lightened(0.25), HORIZONTAL_ALIGNMENT_CENTER))
		var dl := Style.label(tr(String(s.get("desc", ""))), 15, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER)
		dl.custom_minimum_size = Vector2(0, 40)
		v.add_child(dl)
		if owns:
			var eb := Style.button(tr("skin_equipped") if equipped == id else tr("skin_equip"), "DarkButton", 56)
			eb.disabled = equipped == id
			var sid: String = id
			eb.pressed.connect(func():
				Store.equip_skin(sid)
				Haptics.light()
				rebuild())
			v.add_child(eb)
		elif sub_skin:
			# exclusiva do Cartão do Coveiro: não se compra avulsa
			v.add_child(Style.bold(tr("skin_card_only"), 18, Color("d8c4ff"), HORIZONTAL_ALIGNMENT_CENTER))
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
	var active := Store.subscription_active()
	var val := Store.card_value()
	var c := card(Color(0.13, 0.09, 0.19, 0.98), Color("b48cff"))
	var sb: StyleBoxFlat = c.get_theme_stylebox("panel").duplicate()
	sb.set_border_width_all(4)
	sb.shadow_color = Color(0.7, 0.45, 1.0, 0.35)
	sb.shadow_size = 14
	c.add_theme_stylebox_override("panel", sb)
	var v := Style.vbox(12)
	c.add_child(v)
	v.add_child(_card_cover(p, val))
	# na hora
	v.add_child(Style.bold(tr("card_now_title"), 24, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
	var now_row := HFlowContainer.new()
	now_row.alignment = FlowContainer.ALIGNMENT_CENTER
	now_row.add_theme_constant_override("h_separation", 8)
	now_row.add_theme_constant_override("v_separation", 8)
	for r in val.now:
		now_row.add_child(_value_chip(r))
	v.add_child(now_row)
	# em 30 dias
	v.add_child(Style.bold(tr("card_month_title"), 24, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
	var g := GridContainer.new()
	g.columns = 2
	g.add_theme_constant_override("h_separation", 10)
	g.add_theme_constant_override("v_separation", 6)
	for r in val.month:
		g.add_child(_value_line(r))
	g.add_child(_benefit_line("res://art/ui/ui_levelup_quick_knees.png", tr("card_b_x2")))
	g.add_child(_benefit_line("res://art/ui/ui_icon_dust.png", tr("card_b_rundust") % int(roundf(float(p.get("run_dust_bonus", 0.0)) * 100.0))))
	v.add_child(g)
	# você paga x você recebe
	v.add_child(_value_bars(val))
	if active:
		v.add_child(_card_earned_panel())
		v.add_child(Style.bold(tr("subscription_active") % Store.subscription_days_left(), 22, Style.C_HEAL, HORIZONTAL_ALIGNMENT_CENTER))
	var price := Billing.price_text("iap_gravedigger_card")
	var b := Style.button(tr("btn_card_renew") % price if active else price + "  ·  " + tr("per_month"), "CandleButton", 92)
	b.add_theme_font_size_override("font_size", 32 if not active else 26)
	b.pressed.connect(func():
		var res: Array = await Store.buy_iap("iap_gravedigger_card", rng)
		if not res.is_empty():
			res.append_array(Store.claim_subscription(rng))
			_show(res))
	v.add_child(b)
	if not active:
		var tw := b.create_tween().set_loops()
		tw.tween_property(b, "scale", Vector2(1.03, 1.03), 0.8).set_trans(Tween.TRANS_SINE)
		tw.tween_property(b, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_SINE)
		b.resized.connect(func(): b.pivot_offset = b.size * 0.5)
	v.add_child(Style.label(tr("card_no_autorenew"), 16, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	body.add_child(c)


## Capa: cemitério à noite (art/ui/ui_card_cover.png) com o Ossinho vestindo
## a skin do Coveiro, selo, nome e "vale até Nx o preço".
func _card_cover(p: Dictionary, val: Dictionary) -> Control:
	var cover := PanelContainer.new()
	cover.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0), Color("b48cff", 0.6), 16, 2, 0))
	cover.custom_minimum_size = Vector2(0, 286)
	cover.clip_contents = true
	var bg := TextureRect.new()
	bg.texture = load("res://art/ui/ui_card_cover.png")
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cover.add_child(bg)
	var h := Style.hbox(0)
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cover.add_child(h)
	var skin := String(p.get("skin", ""))
	if skin != "" and GameData.skins.has(skin):
		var prev := SkinPreview.new()
		prev.skin_id = skin
		prev.custom_minimum_size = Vector2(230, 280)
		h.add_child(prev)
	var shade := PanelContainer.new()
	shade.add_theme_stylebox_override("panel", Style.flat_box(Color(0.07, 0.04, 0.11, 0.62), Color(0, 0, 0, 0), 16, 0, 10))
	shade.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shade.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(shade)
	var tv := Style.vbox(6)
	tv.alignment = BoxContainer.ALIGNMENT_CENTER
	tv.mouse_filter = Control.MOUSE_FILTER_IGNORE
	shade.add_child(tv)
	var badge := PanelContainer.new()
	badge.add_theme_stylebox_override("panel", Style.flat_box(Style.C_CANDLE, Color(1, 1, 1, 0.0), 12, 0, 6))
	badge.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	badge.add_child(Style.nowrap(Style.bold(tr("card_badge"), 18, Style.C_INK, HORIZONTAL_ALIGNMENT_CENTER)))
	tv.add_child(badge)
	var t := Style.title(tr("iap_gravedigger_card_name"), 46, Color("e6d8ff"))
	t.add_theme_constant_override("outline_size", 10)
	t.add_theme_color_override("font_outline_color", Color(0.06, 0.03, 0.1, 0.9))
	tv.add_child(t)
	if int(val.x) >= 2:
		var vx := Style.bold(tr("card_value_upto") % int(val.x), 28, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER)
		vx.add_theme_constant_override("outline_size", 8)
		vx.add_theme_color_override("font_outline_color", Color(0.06, 0.03, 0.1, 0.9))
		tv.add_child(vx)
	var sl := Style.bold(tr("card_skin_line"), 18, Color("9dffc4"), HORIZONTAL_ALIGNMENT_CENTER)
	sl.add_theme_constant_override("outline_size", 6)
	sl.add_theme_color_override("font_outline_color", Color(0.06, 0.03, 0.1, 0.9))
	tv.add_child(sl)
	return cover


func _value_icon(t: String) -> String:
	match t:
		"diamonds":
			return "res://art/ui/ui_icon_diamond.png"
		"dust":
			return "res://art/ui/ui_icon_dust.png"
		"relic_rare":
			return "res://art/ui/ui_relic_amulet.png"
		"chest_rare":
			return "res://art/ui/ui_bone_chest.png"
		"skin":
			return "res://art/skins/acc_gravedigger_hat.png"
		"rare_start_token":
			return GameData.bone_texture_path("bone_skull_cyclops")
		"extra_revive":
			return "res://art/ui/ui_icon_heart.png"
		"no_ads":
			return "res://art/ui/ui_icon_shield.png"
	return "res://art/ui/ui_logo.png"


func _value_text(r: Dictionary) -> String:
	var n := int(r.amount)
	match String(r.type):
		"diamonds":
			return tr("card_v_diamonds") % Style.num(n)
		"dust":
			return tr("card_v_dust") % Style.num(n)
		"relic_rare":
			return tr("card_v_relic")
		"chest_rare":
			return tr("card_v_chest_one") if n == 1 else tr("card_v_chest") % n
		"skin":
			return tr("card_b_skin")
		"rare_start_token":
			return tr("card_v_rare_bones") % n
		"extra_revive":
			return tr("card_v_revives") % n
		"no_ads":
			return tr("card_b_noads")
	return ""


## Chip do "na hora": ícone grande e o que vem.
func _value_chip(r: Dictionary) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(0.22, 0.15, 0.3, 0.95), Color(Style.C_CANDLE, 0.7), 14, 2, 8))
	var v := Style.vbox(2)
	p.add_child(v)
	var ic := Widgets.icon(_value_icon(String(r.type)), 54)
	ic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(ic)
	var l := Style.bold(_value_text(r), 16, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	l.custom_minimum_size = Vector2(108, 0)
	v.add_child(l)
	return p


func _value_line(r: Dictionary) -> Control:
	return _benefit_line(_value_icon(String(r.type)), _value_text(r))


func _benefit_line(icon_path: String, text: String) -> Control:
	var row := Style.hbox(8)
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(Widgets.icon(icon_path, 38))
	var l := Style.label(text, 18, Style.C_TEXT)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	return row


## "Você paga" (barra curta) x "Você recebe" (barra cheia), em diamantes.
func _value_bars(val: Dictionary) -> Control:
	var box := Style.panel(Color(0, 0, 0, 0.3), Color(Style.C_EDGE, 0.8), 16)
	var v := Style.vbox(6)
	box.add_child(v)
	var pay := Style.hbox(10)
	var pl := Style.nowrap(Style.bold(tr("card_you_pay"), 18, Style.C_MUTED))
	pl.custom_minimum_size = Vector2(150, 0)
	pay.add_child(pl)
	var pbar := ColorRect.new()
	pbar.color = Style.C_MUTED
	pbar.custom_minimum_size = Vector2(26, 30)
	pay.add_child(pbar)
	pay.add_child(Style.nowrap(Style.bold(Billing.price_text("iap_gravedigger_card"), 20, Style.C_TEXT)))
	v.add_child(pay)
	var get := Style.hbox(10)
	var gl := Style.nowrap(Style.bold(tr("card_you_get"), 18, Style.C_HEAL))
	gl.custom_minimum_size = Vector2(150, 0)
	get.add_child(gl)
	var gbar := PanelContainer.new()
	gbar.add_theme_stylebox_override("panel", Style.flat_box(Style.C_HEAL, Color(0, 0, 0, 0), 6, 0, 4))
	gbar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gbar.add_child(Style.nowrap(Style.bold(tr("card_get_diamonds") % Style.num(int(val.total)), 20, Style.C_INK, HORIZONTAL_ALIGNMENT_CENTER)))
	get.add_child(gbar)
	v.add_child(get)
	v.add_child(Style.label(tr("card_value_note"), 15, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	return box


## Assinante: quanto o Cartão já rendeu (desde a 1ª compra).
func _card_earned_panel() -> Control:
	var e := Store.card_earned()
	var box := Style.panel(Color(0.1, 0.22, 0.14, 0.6), Color("7dffb0", 0.7), 16)
	var v := Style.vbox(4)
	box.add_child(v)
	v.add_child(Style.bold(tr("card_earned_title"), 20, Color("9dffc4"), HORIZONTAL_ALIGNMENT_CENTER))
	var parts := []
	if int(e.get("diamonds", 0)) > 0:
		parts.append(tr("card_v_diamonds") % Style.num(int(e.diamonds)))
	if int(e.get("dust", 0)) + int(e.get("run_dust", 0)) > 0:
		parts.append(tr("card_v_dust") % Style.num(int(e.get("dust", 0)) + int(e.get("run_dust", 0))))
	if int(e.get("tokens", 0)) > 0:
		parts.append(tr("card_v_rare_bones") % int(e.tokens))
	if int(e.get("revives", 0)) > 0:
		parts.append(tr("card_v_revives") % int(e.revives))
	if int(e.get("ads", 0)) > 0:
		parts.append(tr("card_v_ads_skipped") % int(e.ads))
	v.add_child(Style.label(" · ".join(parts) if not parts.is_empty() else tr("card_earned_empty"), 18, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	return box


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
