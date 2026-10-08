extends Node
## Vibração do celular, respeitando a opção do jogador.


func pulse(ms: int = 40, amplitude: float = 0.6) -> void:
	if not Profile.setting("vibration"):
		return
	if OS.has_feature("mobile"):
		Input.vibrate_handheld(ms, amplitude)


func light() -> void:
	pulse(18, 0.3)


func medium() -> void:
	pulse(45, 0.6)


func heavy() -> void:
	pulse(90, 1.0)
