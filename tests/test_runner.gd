extends Node
## Testes automáticos (rodados no CI antes do build do AAB):
##   godot --headless --path . res://tests/TestRunner.tscn
## Sai com código 0 se tudo passar, 1 se algo falhar.

var failures: Array = []
var checks := 0


func _ready() -> void:
	for f in _suites():
		call(f)
	print("")
	print("Testes: %d verificações, %d falhas" % [checks, failures.size()])
	for msg in failures:
		print("  FALHA: ", msg)
	get_tree().quit(1 if failures.size() > 0 else 0)


func _suites() -> Array:
	var out := []
	for m in get_method_list():
		if String(m.name).begins_with("test_"):
			out.append(m.name)
	out.sort()
	return out


func check(cond: bool, msg: String) -> void:
	checks += 1
	if not cond:
		failures.append(msg)


func tr_all(key: String) -> bool:
	for loc in ["pt_BR", "en_US", "es"]:
		TranslationServer.set_locale(loc)
		if TranslationServer.translate(key) == key:
			Profile.apply_locale()
			return false
	Profile.apply_locale()
	return true


func test_00_data_loaded() -> void:
	check(GameData.load_errors.is_empty(), "erros ao ler JSON: %s" % [GameData.load_errors])
	check(not GameData.skeleton.is_empty(), "skeleton.json carregado")


func test_01_i18n_basics() -> void:
	for key in ["hero_name", "game_title"]:
		check(tr_all(key), "tradução em 3 idiomas: " + key)
	TranslationServer.set_locale("pt_BR")
	check(TranslationServer.translate("hero_name") == "Ossinho", "hero_name pt_BR = Ossinho")
	TranslationServer.set_locale("en_US")
	check(TranslationServer.translate("hero_name") == "Bonesy", "hero_name en_US = Bonesy")
	TranslationServer.set_locale("es")
	check(TranslationServer.translate("hero_name") == "Huesito", "hero_name es_419 = Huesito")
	Profile.apply_locale()
