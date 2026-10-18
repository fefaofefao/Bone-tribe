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
	var close := func(n: int):
		if n > 0:
			Audio.play("offline")
			Haptics.medium()
		bg.queue_free()
		if on_close.is_valid():
			on_close.call()
	if Offline.ad_left() > 0:
		var dbl := Style.button(TranslationServer.translate("offline_double") % Style.num(amount * 2), "CandleButton", 84)
		dbl.pressed.connect(func():
			dbl.disabled = true
			var ok: bool = await Ads.show_rewarded("offline_double")
			close.call(Offline.collect(ok)))
		v.add_child(dbl)
	var take := Style.button(TranslationServer.translate("offline_collect"), "" if Offline.ad_left() > 0 else "CandleButton", 76)
	take.pressed.connect(func(): close.call(Offline.collect(false)))
	v.add_child(take)
	Audio.play("ui_open")
	Widgets.pop_in(p)
	return bg
