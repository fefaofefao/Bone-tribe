class_name Widgets
extends RefCounted
## Componentes de interface montados por código (todos os textos via TranslationServer.translate()).


static func icon(path: String, size: float = 48.0) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load(path) if ResourceLoader.exists(path) else null
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.custom_minimum_size = Vector2(size, size)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


## Cartão de osso: imagem, nome, raridade, família e efeito.
static func bone_card(inst: Dictionary, header: String = "", compact := false) -> PanelContainer:
	var bone_id := String(inst.get("id", ""))
	var b := GameData.bone(bone_id)
	var rarity := Body.instance_rarity(inst)
	var rc := Style.rarity_color(rarity)
	var fam := String(b.get("family", ""))
	var fc := GameData.family_color(fam) if fam != "" else Style.C_BONE
	var p := Style.panel(Color(Style.C_PANEL_2, 0.98), rc.darkened(0.2), 20)
	var v := Style.vbox(6)
	p.add_child(v)
	if header != "":
		v.add_child(Style.bold(header, 20, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	var art_box := PanelContainer.new()
	var sb := Style.flat_box(Color(0, 0, 0, 0.35), Color(fc, 0.6), 16, 2, 6)
	art_box.add_theme_stylebox_override("panel", sb)
	var img := icon(GameData.bone_texture_path(bone_id), 96.0 if compact else 132.0)
	art_box.add_child(img)
	v.add_child(art_box)
	var lvl := int(inst.get("level", 1))
	var name_text := String(TranslationServer.translate(String(b.get("name", bone_id))))
	if lvl > 1:
		name_text += " +" + str(lvl - 1)
	v.add_child(Style.bold(name_text, 24 if not compact else 21, rc, HORIZONTAL_ALIGNMENT_CENTER))
	var tags := String(TranslationServer.translate("rarity_" + rarity))
	if fam != "":
		tags += " · " + TranslationServer.translate(String(GameData.families[fam].get("name", fam)))
	var tl := Style.label(tags, 18, fc if fam != "" else Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(tl)
	v.add_child(Style.label(TranslationServer.translate(String(b.get("desc", ""))), 19 if compact else 21, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER))
	return p


## Fundo escuro de diálogo que bloqueia toques.
static func dim_overlay(parent: Node, alpha := 0.72) -> ColorRect:
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.01, 0.03, 0.0)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	parent.add_child(bg)
	var tw := bg.create_tween()
	tw.tween_property(bg, "color:a", alpha, 0.2)
	return bg


## Entrada animada de um painel (sobe e aparece).
static func pop_in(c: Control, delay := 0.0) -> void:
	c.modulate.a = 0.0
	c.pivot_offset = c.size * 0.5
	c.scale = Vector2(0.92, 0.92)
	var tw := c.create_tween()
	if delay > 0.0:
		tw.tween_interval(delay)
	tw.tween_property(c, "modulate:a", 1.0, 0.18)
	tw.parallel().tween_property(c, "scale", Vector2.ONE, 0.28).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## Fileira de estrelas desenhadas (sem depender de glifos da fonte).
static func stars(n: int, total: int, size: float = 20.0) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_theme_constant_override("separation", 2)
	for i in total:
		var t := icon("res://art/fx/fx_spark.png", size)
		t.modulate = Style.C_CANDLE if i < n else Color(1, 1, 1, 0.18)
		h.add_child(t)
	return h
