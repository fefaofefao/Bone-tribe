@tool
extends EditorPlugin
## Avaliação no Google Play (In-App Review): copia o código Java para o projeto
## Gradle do Godot, adiciona a biblioteca com.google.android.play:review e registra o plugin.

var _export: EditorExportPlugin


func _enter_tree() -> void:
	_export = ReviewExport.new()
	add_export_plugin(_export)


func _exit_tree() -> void:
	remove_export_plugin(_export)
	_export = null


class ReviewExport extends EditorExportPlugin:
	const SRC := "res://addons/bonetribe_review/android/BoneTribeReview.java"
	const BUILD_DIR := "res://android/build"
	const JAVA_DIR := "res://android/build/src/main/java/com/bonetribe/review/"

	func _get_name() -> String:
		return "BoneTribeReview"

	func _supports_platform(platform: EditorExportPlatform) -> bool:
		return platform is EditorExportPlatformAndroid

	func _get_android_dependencies(_platform: EditorExportPlatform, _debug: bool) -> PackedStringArray:
		return PackedStringArray(["com.google.android.play:review:2.0.2"])

	func _get_android_manifest_application_element_contents(_platform: EditorExportPlatform, _debug: bool) -> String:
		return """
		<meta-data
			android:name="org.godotengine.plugin.v2.BoneTribeReview"
			android:value="com.bonetribe.review.BoneTribeReview" />
		"""

	func _export_begin(features: PackedStringArray, _is_debug: bool, _path: String, _flags: int) -> void:
		if not features.has("android"):
			return
		if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(BUILD_DIR)):
			push_error("BoneTribeReview: projeto Gradle do Android não encontrado (use 'Use Gradle Build').")
			return
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(JAVA_DIR))
		DirAccess.copy_absolute(ProjectSettings.globalize_path(SRC), ProjectSettings.globalize_path(JAVA_DIR + "BoneTribeReview.java"))
