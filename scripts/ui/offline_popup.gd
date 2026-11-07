class_name OfflinePopup
extends RefCounted
## "Enquanto você estava fora, o Ossudo juntou X de pó": coletar ou dobrar com anúncio.


## Devolve o fundo do diálogo (espere `tree_exited` para saber quando fechou) ou null.
static func open(parent: Node, on_close: Callable = Callable()) -> Control:
	var amount := Offline.pending()
	if amount <= 0:
		return null
	var bg := Widgets.dim_overlay(parent, 0.8)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(600, 0)
	center.add_child(p)
	var v := Style.vbox(14)
	p.add_child(v)
	v.add_child(Style.title(TranslationServer.translate("offline_title"), 44))
	var row := Style.hbox(14)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_child(Widgets.icon("res://art/ui/companion_ossudo.png", 110))
	row.add_child(Widgets.icon("res://art/ui/ui_icon_dust.png", 72))
	v.add_child(row)
	v.add_child(Style.label(TranslationServer.translate("offline_text"), 22, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(Style.bold("+" + Style.num(amount), 40, Style.C_DUST, HORIZONTAL_ALIGNMENT_CENTER))
	var closed := [false]
	var close := func(n: int):
		# fecha uma vez só: o fim do anúncio podia chegar depois de "Coletar" já ter fechado a tela
		if closed[0]:
			return
		closed[0] = true
		if n > 0:
			Audio.play("offline")
			Haptics.medium()
		if is_instance_valid(bg) and not bg.is_queued_for_deletion():
			bg.queue_free()
		if on_close.is_valid():
			on_close.call()
	if Offline.ad_left() > 0:
		var dbl := Style.button(TranslationServer.translate("offline_double") % Style.num(amount * 2), "CandleButton", 84)
		dbl.pressed.connect(func():
			dbl.disabled = true
			var ok: bool = await Ads.show_rewarded("offline_double")
			if closed[0]:
				return
			close.call(Offline.collect(ok)))
		v.add_child(dbl)
	# dobrar com diamantes (1.4): divide o limite diário com o anúncio
	if Offline.ad_left() > 0:
		var price := Store.use_price("offline_double")
		var dd := Style.button(TranslationServer.translate("offline_double_diamonds") % [Style.num(amount * 2), price], "DarkButton", 72)
		dd.icon = load("res://art/ui/ui_icon_diamond.png")
		dd.expand_icon = true
		dd.add_theme_constant_override("icon_max_width", 30)
		dd.disabled = Profile.diamonds() < price
		dd.pressed.connect(func():
			if not closed[0] and Store.pay_use("offline_double"):
				close.call(Offline.collect(true)))
		v.add_child(dd)
	var take := Style.button(TranslationServer.translate("offline_collect"), "" if Offline.ad_left() > 0 else "CandleButton", 76)
	take.pressed.connect(func():
		if not closed[0]:
			close.call(Offline.collect(false)))
	v.add_child(take)
	Audio.play("ui_open")
	Widgets.pop_in(p)
	return bg
