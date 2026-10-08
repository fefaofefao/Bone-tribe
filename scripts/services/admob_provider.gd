extends Node
## Anúncios reais com o plugin Poing AdMob (só no Android).
## Pede o consentimento (UMP/GDPR) antes de iniciar o SDK, mantém um
## recompensado e um intersticial pré-carregados e recarrega depois de cada uso.
## Os IDs vêm de data/admob.json (o workflow troca pelos IDs reais).

const LOAD_WAIT_S := 6.0
const RETRY_S := 30.0

var _rewarded: RewardedAd
var _interstitial: InterstitialAd
var _rewarded_loader: RewardedAdLoader
var _interstitial_loader: InterstitialAdLoader
var _initialized := false
var _loading_rewarded := false
var _loading_interstitial := false
var privacy_options_required := false


static func available() -> bool:
	return OS.get_name() == "Android" and Engine.has_singleton("PoingGodotAdMob")


func _ready() -> void:
	_request_consent()


func _cfg(key: String) -> String:
	return String(GameData.admob.get(key, ""))


# --------------------------------------------------------- consentimento

func _request_consent() -> void:
	var params := ConsentRequestParameters.new()
	UserMessagingPlatform.consent_information.update(params, _on_consent_updated, func(_e): _init_sdk())


func _on_consent_updated() -> void:
	var info := UserMessagingPlatform.consent_information
	if info.get_is_consent_form_available() and info.get_consent_status() == ConsentInformation.ConsentStatus.REQUIRED:
		UserMessagingPlatform.load_consent_form(
			func(form: ConsentForm): form.show(func(_e): _init_sdk()),
			func(_e): _init_sdk())
	else:
		_init_sdk()


## Formulário "Opções de privacidade" (exigido pelo GDPR quando aplicável).
func show_privacy_options() -> void:
	UserMessagingPlatform.show_privacy_options_form(func(_e): pass)


func _init_sdk() -> void:
	if _initialized:
		return
	_initialized = true
	var info := UserMessagingPlatform.consent_information
	privacy_options_required = info.get_privacy_options_requirement_status() == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED
	var conf := RequestConfiguration.new()
	conf.max_ad_content_rating = _cfg("max_ad_content_rating")
	MobileAds.set_request_configuration(conf)
	var listener := OnInitializationCompleteListener.new()
	listener.on_initialization_complete = func(_status): _preload_all()
	MobileAds.initialize(listener)


func _preload_all() -> void:
	_load_rewarded()
	_load_interstitial()


# ------------------------------------------------------------ carregar

func _load_rewarded() -> void:
	if _rewarded or _loading_rewarded or not _initialized:
		return
	_loading_rewarded = true
	if _rewarded_loader == null:
		_rewarded_loader = RewardedAdLoader.new()
	var cb := RewardedAdLoadCallback.new()
	cb.on_ad_loaded = func(ad: RewardedAd):
		_rewarded = ad
		_loading_rewarded = false
	cb.on_ad_failed_to_load = func(_err):
		_loading_rewarded = false
		get_tree().create_timer(RETRY_S, true).timeout.connect(_load_rewarded)
	_rewarded_loader.load(_cfg("rewarded"), AdRequest.new(), cb)


func _load_interstitial() -> void:
	if _interstitial or _loading_interstitial or not _initialized:
		return
	_loading_interstitial = true
	if _interstitial_loader == null:
		_interstitial_loader = InterstitialAdLoader.new()
	var cb := InterstitialAdLoadCallback.new()
	cb.on_ad_loaded = func(ad: InterstitialAd):
		_interstitial = ad
		_loading_interstitial = false
	cb.on_ad_failed_to_load = func(_err):
		_loading_interstitial = false
		get_tree().create_timer(RETRY_S, true).timeout.connect(_load_interstitial)
	_interstitial_loader.load(_cfg("interstitial"), AdRequest.new(), cb)


## Espera até `seconds` pelo anúncio pedido (quando o jogador toca antes de carregar).
func _wait_for(kind: String, seconds: float) -> bool:
	var t := 0.0
	while t < seconds:
		if (kind == "rewarded" and _rewarded) or (kind == "interstitial" and _interstitial):
			return true
		await get_tree().create_timer(0.25, true, false, true).timeout
		t += 0.25
	return false


# ------------------------------------------------------------- mostrar

func show_rewarded(_placement: String) -> bool:
	if _rewarded == null:
		_load_rewarded()
		if not await _wait_for("rewarded", LOAD_WAIT_S):
			Widgets.toast(tr("ad_unavailable"))
			return false
	var ad := _rewarded
	_rewarded = null
	var state := {"earned": false, "done": false}
	ad.full_screen_content_callback.on_ad_dismissed_full_screen_content = func(): state.done = true
	ad.full_screen_content_callback.on_ad_failed_to_show_full_screen_content = func(_e): state.done = true
	var listener := OnUserEarnedRewardListener.new()
	listener.on_user_earned_reward = func(_item): state.earned = true
	ad.show(listener)
	while not state.done:
		await get_tree().create_timer(0.1, true, false, true).timeout
	# a recompensa às vezes chega logo depois do fechamento
	if not state.earned:
		await get_tree().create_timer(0.4, true, false, true).timeout
	ad.destroy()
	_load_rewarded()
	return state.earned


func show_interstitial() -> bool:
	if _interstitial == null:
		_load_interstitial()
		return false
	var ad := _interstitial
	_interstitial = null
	var state := {"done": false}
	ad.full_screen_content_callback.on_ad_dismissed_full_screen_content = func(): state.done = true
	ad.full_screen_content_callback.on_ad_failed_to_show_full_screen_content = func(_e): state.done = true
	ad.show()
	while not state.done:
		await get_tree().create_timer(0.1, true, false, true).timeout
	ad.destroy()
	_load_interstitial()
	return true
