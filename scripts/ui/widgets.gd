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
	var power := Body.instance_power(inst)
	if power > 1.0:
		var now := Body.stats_compare_text({}, Body.instance_stats(inst))
		var gain := TranslationServer.translate("bone_gain_power") % int(roundf((power - 1.0) * 100.0))
		v.add_child(Style.label(gain + ("\n" + now if now != "" else ""), 18 if compact else 20, Style.C_HEAL, HORIZONTAL_ALIGNMENT_CENTER))
	return p


## Quadro "O que muda": cada atributo do osso equipado → novo, com a diferença
## em verde (melhora) ou vermelho (piora), e o efeito especial ganho/perdido.
static func bone_compare(cur: Dictionary, new: Dictionary, font := 20) -> PanelContainer:
	var p := Style.panel(Color(0, 0, 0, 0.28), Color(Style.C_EDGE, 0.8), 16)
	var v := Style.vbox(6)
	p.add_child(v)
	# título com o veredito: "O que muda · Melhor que o seu"
	var head := Style.hbox(8)
	head.alignment = BoxContainer.ALIGNMENT_CENTER
	head.add_child(Style.nowrap(Style.bold(TranslationServer.translate("cmp_title"), font, Style.C_MUTED)))
	var verdict := Body.compare_verdict(cur, new)
	if verdict != "empty":
		head.add_child(Style.nowrap(Style.bold("· " + TranslationServer.translate("cmp_verdict_" + verdict), font, verdict_color(verdict))))
	v.add_child(head)
	var g := GridContainer.new()
	g.columns = 4
	g.add_theme_constant_override("h_separation", 14)
	g.add_theme_constant_override("v_separation", 4)
	g.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(g)
	var rows := Body.compare_rows(cur, new)
	for r in rows:
		var col := Style.C_HEAL if int(r.sign) > 0 else (Style.C_DANGER if int(r.sign) < 0 else Style.C_MUTED)
		g.add_child(Style.nowrap(Style.label(String(r.name), font, Style.C_TEXT)))
		g.add_child(Style.nowrap(Style.label(String(r.cur), font, Style.C_MUTED, HORIZONTAL_ALIGNMENT_RIGHT)))
		g.add_child(Style.nowrap(Style.bold("→ " + String(r.new), font, col)))
		g.add_child(Style.nowrap(Style.bold(String(r.delta), font, col, HORIZONTAL_ALIGNMENT_RIGHT)))
	var sc := Body.special_change(cur, new)
	if sc != 0:
		var key: String = {1: "cmp_special_gain", -1: "cmp_special_lose", 2: "cmp_special_swap"}[sc]
		var c := Style.C_HEAL if sc == 1 else (Style.C_DANGER if sc == -1 else Style.C_CANDLE)
		v.add_child(Style.bold(TranslationServer.translate(key), font, c, HORIZONTAL_ALIGNMENT_CENTER))
	if rows.is_empty() and sc == 0:
		v.add_child(Style.label(TranslationServer.translate("cmp_no_change"), font, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	return p


static func verdict_color(verdict: String) -> Color:
	match verdict:
		"better", "empty":
			return Style.C_HEAL
		"worse":
			return Style.C_DANGER
		"mixed":
			return Style.C_CANDLE
	return Style.C_MUTED


## Cartão de osso deitado (imagem à esquerda, textos à direita): ocupa menos
## altura, para a troca de braços caber em telas baixas.
static func bone_card_row(inst: Dictionary, header: String = "") -> PanelContainer:
	var bone_id := String(inst.get("id", ""))
	var b := GameData.bone(bone_id)
	var rarity := Body.instance_rarity(inst)
	var rc := Style.rarity_color(rarity)
	var fam := String(b.get("family", ""))
	var fc := GameData.family_color(fam) if fam != "" else Style.C_BONE
	var p := Style.panel(Color(Style.C_PANEL_2, 0.98), rc.darkened(0.2), 20)
	var h := Style.hbox(12)
	p.add_child(h)
	var art := PanelContainer.new()
	art.add_theme_stylebox_override("panel", Style.flat_box(Color(0, 0, 0, 0.35), Color(fc, 0.6), 14, 2, 4))
	art.add_child(icon(GameData.bone_texture_path(bone_id), 84.0))
	art.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(art)
	var v := Style.vbox(2)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(v)
	var lvl := int(inst.get("level", 1))
	var name_text := String(TranslationServer.translate(String(b.get("name", bone_id))))
	if lvl > 1:
		name_text += " +" + str(lvl - 1)
	if header != "":
		name_text = header + ": " + name_text
	v.add_child(Style.bold(name_text, 22, rc))
	var tags := String(TranslationServer.translate("rarity_" + rarity))
	if fam != "":
		tags += " · " + TranslationServer.translate(String(GameData.families[fam].get("name", fam)))
	v.add_child(Style.label(tags, 17, fc if fam != "" else Style.C_MUTED))
	v.add_child(Style.label(TranslationServer.translate(String(b.get("desc", ""))), 18, Style.C_TEXT))
	var now := Body.stats_compare_text({}, Body.instance_stats(inst))
	if Body.instance_power(inst) > 1.0 and now != "":
		v.add_child(Style.label(now, 17, Style.C_HEAL))
	return p


## Linha colorida curta (BBCode), para mercador e braços.
static func rich_line(text: String, font := 19, align := HORIZONTAL_ALIGNMENT_CENTER) -> RichTextLabel:
	var r := RichTextLabel.new()
	r.bbcode_enabled = true
	r.fit_content = true
	r.scroll_active = false
	r.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	r.text = "[center]%s[/center]" % text if align == HORIZONTAL_ALIGNMENT_CENTER else text
	r.add_theme_font_size_override("normal_font_size", font)
	r.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## Fundo escuro de diálogo que bloqueia toques.
static func dim_overlay(parent: Node, alpha := 0.72) -> ColorRect:
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.01, 0.03, 0.0)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	parent.add_child(bg)
	var tw := bg.create_tween()
	tw.tween_property(bg, "color:a", alpha, 0.2)
	return bg


## Aviso curto no rodapé da tela (some sozinho).
static func toast(text: String, seconds := 2.4) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null:
		return
	var layer := CanvasLayer.new()
	layer.layer = 110
	tree.root.add_child(layer)
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", Style.flat_box(Color(0.08, 0.06, 0.09, 0.95), Color(Style.C_CANDLE, 0.6), 18, 2, 14))
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var l := Style.label(text, 24, Style.C_TEXT, HORIZONTAL_ALIGNMENT_CENTER)
	p.add_child(l)
	p.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	p.offset_left = -320
	p.offset_right = 320
	p.offset_top = -230
	p.offset_bottom = -150
	layer.add_child(p)
	pop_in(p)
	var tw := p.create_tween()
	tw.tween_interval(seconds)
	tw.tween_property(p, "modulate:a", 0.0, 0.3)
	tw.tween_callback(layer.queue_free)


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


## Tela bloqueada com "Carregando…" enquanto um anúncio ou uma compra está aberto.
## Impede tocar em outro botão no meio (ex.: "Coletar" enquanto o anúncio carrega),
## que fechava a tela e fazia o fim do anúncio mexer em nós já destruídos.
static func busy_overlay(text: String) -> CanvasLayer:
	var tree := Engine.get_main_loop() as SceneTree
	var layer := CanvasLayer.new()
	layer.layer = 100
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.01, 0.03, 0.55)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	layer.add_child(bg)
	var l := Style.bold(text, 30, Style.C_BONE, HORIZONTAL_ALIGNMENT_CENTER)
	l.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	l.offset_left = -300
	l.offset_right = 300
	l.offset_top = -30
	l.offset_bottom = 30
	bg.add_child(l)
	tree.root.add_child(layer)
	return layer

