class_name RewardPopup
extends Control
## Mostra o que o jogador ganhou (calendário, loja, baús) com uma entrada animada.

signal closed

var title_key := "rewards_title"
var results: Array = []


static func show_on(parent: Node, p_title_key: String, p_results: Array) -> RewardPopup:
	var p := RewardPopup.new()
	p.title_key = p_title_key
	p.results = p_results
	parent.add_child(p)
	return p


static func result_icon(r: Dictionary) -> String:
	match String(r.get("type", "")):
		"dust":
			return "res://art/ui/ui_icon_dust.png"
		"diamonds":
			return "res://art/ui/ui_icon_diamond.png"
		"relic", "curiosity", "companion":
			return "res://art/ui/%s.png" % String(r.id)
		"skin":
			return "res://art/ui/ui_app_icon.png"
		"extra_revive":
			return "res://art/ui/ui_icon_heart.png"
		"rare_start_token":
			return GameData.bone_texture_path("bone_skull_cyclops")
		"subscription":
			return "res://art/ui/ui_bone_chest.png"
		_:
			return "res://art/ui/ui_logo.png"


static func result_text(r: Dictionary) -> String:
	var tsv := TranslationServer
	match String(r.get("type", "")):
		"dust":
			return String(tsv.translate("reward_dust")) % Style.num(int(r.amount))
		"diamonds":
			return String(tsv.translate("reward_diamonds")) % int(r.amount)
		"relic":
			return String(tsv.translate(String(GameData.relics[r.id].name)))
		"curiosity":
			return String(tsv.translate(String(GameData.curiosities[r.id].name))) + "  " + String(tsv.translate("stars_n")) % int(r.get("stars", 1))
		"companion":
			return String(tsv.translate(String(GameData.companions[r.id].name)))
		"skin":
			return String(tsv.translate("reward_skin")) % String(tsv.translate(String(GameData.skins[r.id].name)))
		_:
			return String(tsv.translate("reward_" + String(r.type)))


static func result_color(r: Dictionary) -> Color:
	if String(r.get("type", "")) == "skin":
		return Color(String(GameData.skins.get(r.id, {}).get("tint", "#ffffff")))
	return Color.WHITE


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	Haptics.heavy()
	var bg := Widgets.dim_overlay(self, 0.82)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.add_child(center)
	var p := Style.panel()
	p.custom_minimum_size = Vector2(580, 0)
	center.add_child(p)
	var v := Style.vbox(14)
	p.add_child(v)
	v.add_child(Style.title(tr(title_key), 50, Style.C_CANDLE))
	var i := 0
	for r in results:
		var row := Style.hbox(14)
		var ic := Widgets.icon(result_icon(r), 72)
		ic.modulate = result_color(r)
		row.add_child(ic)
		var l := Style.bold(result_text(r), 26, Style.C_BONE)
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		row.add_child(l)
		v.add_child(row)
		Widgets.pop_in(row, 0.15 + i * 0.12)
		i += 1
	var ok := Style.button(tr("btn_continue"), "CandleButton", 76)
	ok.pressed.connect(func():
		closed.emit()
		queue_free())
	v.add_child(ok)
	Widgets.pop_in(p)
