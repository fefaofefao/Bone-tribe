extends Node
## Compra simulada: mostra "processando" e aprova. Nenhum pagamento real.


## Na versão de loja do Android a compra simulada nunca aprova: se o plugin
## real não carregou, a loja fica indisponível em vez de entregar de graça.
static func allowed() -> bool:
	return OS.get_name() != "Android" or OS.is_debug_build()


func purchase(_product_id: String) -> bool:
	if not allowed():
		Widgets.toast(tr("iap_unavailable"))
		return false
	var layer := CanvasLayer.new()
	layer.layer = 100
	get_tree().root.add_child(layer)
	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 0.8)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	layer.add_child(bg)
	var label := Label.new()
	label.text = tr("iap_mock_processing")
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	label.add_theme_font_size_override("font_size", 36)
	bg.add_child(label)
	await get_tree().create_timer(1.0, true, false, true).timeout
	layer.queue_free()
	return true
