@tool
extends EditorPlugin
## Notificações locais no Android: copia o código Java e o ícone para o
## projeto Gradle do Godot e registra o plugin, o receptor e a permissão
## POST_NOTIFICATIONS (Android 13+) no manifesto.

var _export: EditorExportPlugin


func _enter_tree() -> void:
	_export = NotifyExport.new()
	add_export_plugin(_export)


func _exit_tree() -> void:
	remove_export_plugin(_export)
	_export = null


class NotifyExport extends EditorExportPlugin:
	const SRC := "res://addons/bonetribe_notify/android/"
	const BUILD_DIR := "res://android/build"
	const JAVA_DIR := "res://android/build/src/main/java/com/bonetribe/notify/"
	const RES_DIR := "res://android/build/res/drawable/"
	const FILES := {"BoneTribeNotify.java": JAVA_DIR, "BoneTribeNotifyReceiver.java": JAVA_DIR, "bonetribe_notify_icon.xml": RES_DIR}

	func _get_name() -> String:
		return "BoneTribeNotify"

	func _supports_platform(platform: EditorExportPlatform) -> bool:
		return platform is EditorExportPlatformAndroid

	func _get_android_manifest_element_contents(_platform: EditorExportPlatform, _debug: bool) -> String:
		return """
	<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
		"""

	func _get_android_manifest_application_element_contents(_platform: EditorExportPlatform, _debug: bool) -> String:
		return """
		<meta-data
			android:name="org.godotengine.plugin.v2.BoneTribeNotify"
			android:value="com.bonetribe.notify.BoneTribeNotify" />
		<receiver
			android:name="com.bonetribe.notify.BoneTribeNotifyReceiver"
			android:exported="false" />
		"""

	func _export_begin(features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
		if not features.has("android"):
			return
		if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(BUILD_DIR)):
			push_error("BoneTribeNotify: projeto Gradle do Android não encontrado (use 'Use Gradle Build').")
			return
		for f in FILES:
			var dst: String = FILES[f]
			DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dst))
			DirAccess.copy_absolute(ProjectSettings.globalize_path(SRC + f), ProjectSettings.globalize_path(dst + f))
