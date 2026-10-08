extends Control
## Tela de título (versão do Passo 1; o hub completo vem nos passos seguintes).


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Style.C_BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var box := Style.vbox(24)
	box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	box.offset_left = 40
	box.offset_right = -40
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(box)
	box.add_child(Style.title(tr("game_title"), 96))
	box.add_child(Style.label(tr("title_tagline"), 26, Style.C_MUTED, HORIZONTAL_ALIGNMENT_CENTER))
	box.add_child(Style.bold(tr("hero_name"), 34, Style.C_CANDLE, HORIZONTAL_ALIGNMENT_CENTER))
