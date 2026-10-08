class_name Dev
extends RefCounted
## Atalhos de desenvolvimento (variáveis BT_*). Só funcionam em builds de
## depuração; na versão release publicada são sempre ignorados.


static func env(name: String) -> String:
	if not OS.is_debug_build():
		return ""
	return OS.get_environment(name)
