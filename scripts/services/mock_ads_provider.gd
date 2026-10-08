extends Node
## Anúncio simulado: uma tela escura com contagem regressiva.
## Todo texto vem de res://i18n/.

const REWARDED_SECONDS := 2.0
const INTERSTITIAL_SECONDS := 1.5


## Na versão de loja do Android o anúncio simulado não é usado: sem o plugin
## real, o jogo avisa que não há anúncio e não entrega a recompensa.
static func allowed() -> bool:
	return OS.get_name() != "Android" or OS.is_debug_build()


func show_rewarded(placement: String) -> bool:
	if not allowed():
		Widgets.toast(tr("ad_unavailable"))
		return false
	await _overlay("ad_mock_rewarded", REWARDED_SECONDS, placement)
	return true


func show_interstitial() -> bool:
	if not allowed():
		return false
	await _overlay("ad_mock_interstitial", INTERSTITIAL_SECONDS, "interstitial")
	return true


func _overlay(title_key: String, seconds: float, placement: String) -> void:
	var layer := CanvasLayer.new()
	layer.layer = 100
	get_tree().root.add_child(layer)
	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 0.92)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	layer.add_child(bg)
	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 24)
	bg.add_child(box)
	box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var title := Label.new()
	title.text = tr(title_key)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 40)
	box.add_child(title)
	var sub := Label.new()
	sub.text = tr("ad_mock_placement") % tr("ad_place_" + placement)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.modulate = Color(1, 1, 1, 0.6)
	box.add_child(sub)
	var count := Label.new()
	count.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	count.add_theme_font_size_override("font_size", 64)
	box.add_child(count)
	var t := seconds
	while t > 0.0:
		count.text = str(ceili(t))
		await get_tree().create_timer(0.25, true, false, true).timeout
		t -= 0.25
	layer.queue_free()
