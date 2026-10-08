extends RefCounted
## Compartilhamento nativo do Android sem plugin extra: usa o AndroidRuntime e
## o JavaClassWrapper do Godot para abrir o menu "Compartilhar" com a imagem.
## O arquivo precisa estar em user:// (o FileProvider do Godot já cobre essa pasta).

const ACTION_SEND := "android.intent.action.SEND"
const EXTRA_STREAM := "android.intent.extra.STREAM"
const EXTRA_TEXT := "android.intent.extra.TEXT"
const FLAG_GRANT_READ_URI_PERMISSION := 1


static func available() -> bool:
	return OS.get_name() == "Android" and Engine.has_singleton("AndroidRuntime")


## Retorna true se o menu de compartilhamento foi aberto.
static func share_image(user_path: String, text: String, title: String) -> bool:
	if not available():
		return false
	var runtime: Object = Engine.get_singleton("AndroidRuntime")
	var activity: Object = runtime.getActivity()
	if activity == null:
		return false
	var file_class: Object = JavaClassWrapper.wrap("java.io.File")
	var provider_class: Object = JavaClassWrapper.wrap("androidx.core.content.FileProvider")
	var intent_class: Object = JavaClassWrapper.wrap("android.content.Intent")
	if file_class == null or provider_class == null or intent_class == null:
		return false
	var file: Object = file_class.File(ProjectSettings.globalize_path(user_path))
	var authority := String(activity.getPackageName()) + ".fileprovider"
	var uri: Object = provider_class.getUriForFile(activity, authority, file)
	var intent: Object = intent_class.Intent(ACTION_SEND)
	if uri == null or intent == null:
		return false
	intent.setType("image/png")
	intent.putExtra(EXTRA_STREAM, uri)
	intent.putExtra(EXTRA_TEXT, text)
	intent.addFlags(FLAG_GRANT_READ_URI_PERMISSION)
	var chooser: Object = intent_class.createChooser(intent, title)
	if chooser == null:
		return false
	activity.runOnUiThread(runtime.createRunnableFromGodotCallable(func(): activity.startActivity(chooser)))
	return true
