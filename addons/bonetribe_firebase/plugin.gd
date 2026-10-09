@tool
extends EditorPlugin
## Liga o Firebase na exportação Android quando existe o google-services.json
## (o workflow do GitHub grava esse arquivo a partir de um secret; ele não vai
## para o repositório). Sem o arquivo, nada muda no build.

var _export: EditorExportPlugin


func _enter_tree() -> void:
	_export = FirebaseExport.new()
	add_export_plugin(_export)


func _exit_tree() -> void:
	remove_export_plugin(_export)
	_export = null


class FirebaseExport extends EditorExportPlugin:
	const CONFIG := "res://addons/bonetribe_firebase/google-services.json"
	const JAVA_SRC := "res://addons/bonetribe_firebase/android/BoneTribeFirebase.java"
	const BUILD_DIR := "res://android/build"
	const JAVA_DST := "res://android/build/src/main/java/com/bonetribe/firebase/BoneTribeFirebase.java"
	const GMS_PLUGIN := "com.google.gms:google-services:4.4.2"
	const DEPS := [
		"com.google.firebase:firebase-analytics:22.1.2",
		"com.google.firebase:firebase-config:22.0.1",
	]

	func _get_name() -> String:
		return "BoneTribeFirebase"

	func _enabled() -> bool:
		return FileAccess.file_exists(CONFIG)

	func _supports_platform(platform: EditorExportPlatform) -> bool:
		return platform is EditorExportPlatformAndroid

	func _get_android_dependencies(_platform: EditorExportPlatform, _debug: bool) -> PackedStringArray:
		return PackedStringArray(DEPS) if _enabled() else PackedStringArray()

	func _get_android_manifest_application_element_contents(_platform: EditorExportPlatform, _debug: bool) -> String:
		if not _enabled():
			return ""
		# registro do plugin Android v2 do Godot
		return """
		<meta-data
			android:name="org.godotengine.plugin.v2.BoneTribeFirebase"
			android:value="com.bonetribe.firebase.BoneTribeFirebase" />
		"""

	func _export_begin(features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
		if not features.has("android"):
			return
		if not _enabled():
			_remove_patch()
			return
		if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(BUILD_DIR)):
			push_error("BoneTribeFirebase: projeto Gradle do Android não encontrado (use 'Use Gradle Build').")
			return
		# 1) configuração do Firebase na raiz do módulo do app
		DirAccess.copy_absolute(ProjectSettings.globalize_path(CONFIG), ProjectSettings.globalize_path(BUILD_DIR + "/google-services.json"))
		# 2) código Java do plugin, compilado junto com o app
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(JAVA_DST.get_base_dir()))
		DirAccess.copy_absolute(ProjectSettings.globalize_path(JAVA_SRC), ProjectSettings.globalize_path(JAVA_DST))
		# 3) plugin google-services do Gradle (gera os recursos a partir do json)
		_patch_gradle()

	func _patch_gradle() -> void:
		var path := BUILD_DIR + "/build.gradle"
		var content := FileAccess.get_file_as_string(path)
		if content.is_empty() or content.contains(GMS_PLUGIN):
			return
		var head := "buildscript {\n    repositories {\n        google()\n        mavenCentral()\n    }\n    dependencies {\n        classpath '%s'\n    }\n}\n\n" % GMS_PLUGIN
		content = head + content + "\n// Firebase (Bone Tribe)\napply plugin: 'com.google.gms.google-services'\n"
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f:
			f.store_string(content)

	## Sem configuração: garante que um build anterior com Firebase não deixe restos.
	func _remove_patch() -> void:
		var path := BUILD_DIR + "/build.gradle"
		if FileAccess.file_exists(path):
			var content := FileAccess.get_file_as_string(path)
			if content.contains(GMS_PLUGIN):
				var start := content.find("buildscript {")
				var end := content.find("\n\n", start)
				if start == 0 and end > 0:
					content = content.substr(end + 2)
				content = content.replace("\n// Firebase (Bone Tribe)\napply plugin: 'com.google.gms.google-services'\n", "")
				var f := FileAccess.open(path, FileAccess.WRITE)
				if f:
					f.store_string(content)
		for p in [JAVA_DST, BUILD_DIR + "/google-services.json"]:
			if FileAccess.file_exists(p):
				DirAccess.remove_absolute(ProjectSettings.globalize_path(p))
