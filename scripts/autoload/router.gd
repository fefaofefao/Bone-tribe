extends Node
## Troca de cenas com transição suave (escurece, troca, clareia).
## `params` carrega dados para a próxima cena (ex.: resultado da partida).

const SCENES := {
	"title": "res://scenes/TitleScreen.tscn",
	"run": "res://scenes/Run.tscn",
	"card": "res://scenes/CreatureCard.tscn",
}

var params: Dictionary = {}
var _layer: CanvasLayer
var _fade: ColorRect
var _busy := false


func _ready() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 90
	add_child(_layer)
	_fade = ColorRect.new()
	_fade.color = Color(0.03, 0.02, 0.04, 0.0)
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_layer.add_child(_fade)
	_debug_capture()
	var start := Dev.env("BT_START")
	if start != "":
		await get_tree().process_frame
		go(start, {"demo": Dev.env("BT_DEMO") == "1"})


## Ferramenta de desenvolvimento: BT_SHOT=<arquivo.png> [BT_SHOT_DELAY=s]
## captura a tela depois do atraso e fecha o jogo. BT_SHOTS=n tira n capturas.
func _debug_capture() -> void:
	var path := Dev.env("BT_SHOT")
	if path == "":
		return
	var delay := float(Dev.env("BT_SHOT_DELAY")) if Dev.env("BT_SHOT_DELAY") != "" else 2.0
	var shots := maxi(1, int(Dev.env("BT_SHOTS")))
	for i in shots:
		await get_tree().create_timer(delay, true, false, true).timeout
		var img := get_viewport().get_texture().get_image()
		var p := path if shots == 1 else path.replace(".png", "_%02d.png" % i)
		img.save_png(p)
		print("[shot] ", p)
	get_tree().quit()


func go(scene_key: String, new_params: Dictionary = {}) -> void:
	if _busy:
		return
	_busy = true
	params = new_params
	_fade.mouse_filter = Control.MOUSE_FILTER_STOP
	var tw := create_tween()
	tw.tween_property(_fade, "color:a", 1.0, 0.28)
	await tw.finished
	get_tree().paused = false
	Engine.time_scale = 1.0
	get_tree().change_scene_to_file(SCENES.get(scene_key, scene_key))
	await get_tree().process_frame
	await get_tree().process_frame
	var tw2 := create_tween()
	tw2.tween_property(_fade, "color:a", 0.0, 0.35)
	await tw2.finished
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_busy = false
