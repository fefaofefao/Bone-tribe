extends Node
## Sons e músicas. Cada som é tocado no mesmo quadro do efeito visual que ele
## acompanha (golpe, encaixe, morte...): os arquivos ficam carregados na memória
## e cada som tem seu próprio reprodutor com várias vozes, então tocar é imediato.
## Configuração em data/audio.json; arquivos gerados por tools/gen_audio.py.

const SFX_DIR := "res://audio/sfx/%s.wav"
const MUSIC_DIR := "res://audio/music/%s.ogg"
const FADE := 0.8

var _cfg: Dictionary = {}
var _players: Dictionary = {}     # id -> Array de AudioStreamPlayer (variações)
var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_id := ""
var _ad_muted := false
var _duck := 0.0
## Registro do que tocou (testes conferem a sincronia com a tela).
var history: Array = []
var record_history := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var f := FileAccess.open("res://data/audio.json", FileAccess.READ)
	if f:
		_cfg = JSON.parse_string(f.get_as_text())
	for id in _cfg.get("sfx", {}):
		var c: Dictionary = _cfg.sfx[id]
		var list := []
		var variants := int(c.get("variants", 0))
		var files: Array = [id] if variants <= 0 else range(1, variants + 1).map(func(i): return "%s_%d" % [id, i])
		for fname in files:
			var path := SFX_DIR % fname
			if not ResourceLoader.exists(path):
				continue
			var p := AudioStreamPlayer.new()
			p.stream = load(path)
			p.max_polyphony = 4
			p.volume_db = float(c.get("vol", 0))
			add_child(p)
			list.append(p)
		_players[id] = list
	_music_a = _new_music_player()
	_music_b = _new_music_player()


func _new_music_player() -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.volume_db = -80.0
	add_child(p)
	return p


func sound_on() -> bool:
	return bool(Profile.setting("sound")) if Profile.data.settings.has("sound") else true


func music_on() -> bool:
	return bool(Profile.setting("music")) if Profile.data.settings.has("music") else true


## Toca o som `id` agora. pitch multiplica o tom (ex.: 0.8 mais grave).
func play(id: String, pitch := 1.0, vol_offset := 0.0) -> void:
	if record_history:
		history.append(id)
	if not sound_on() or _ad_muted:
		return
	var list: Array = _players.get(id, [])
	if list.is_empty():
		return
	var p: AudioStreamPlayer = list[randi() % list.size()]
	var c: Dictionary = _cfg.sfx.get(id, {})
	var var_ := float(c.get("pitch_var", 0.0))
	p.pitch_scale = clampf(pitch * (1.0 + randf_range(-var_, var_)), 0.25, 3.0)
	p.volume_db = float(c.get("vol", 0)) + vol_offset
	p.play()


## Troca a música com transição suave ("" para parar).
func music(track: String) -> void:
	if track == _music_id:
		return
	_music_id = track
	var out := _music_a
	var into := _music_b
	if _music_b.playing and not _music_a.playing:
		out = _music_b
		into = _music_a
	elif _music_a.playing:
		out = _music_a
		into = _music_b
	if out.playing:
		var t1 := create_tween()
		t1.tween_property(out, "volume_db", -60.0, FADE)
		t1.tween_callback(out.stop)
	var file := String(_cfg.get("music", {}).get(track, ""))
	if file == "" or not ResourceLoader.exists(MUSIC_DIR % file):
		return
	var st: AudioStream = load(MUSIC_DIR % file)
	if st is AudioStreamOggVorbis:
		(st as AudioStreamOggVorbis).loop = true
	into.stream = st
	into.volume_db = -60.0
	if not music_on():
		return
	into.play()
	var t2 := create_tween()
	t2.tween_property(into, "volume_db", _music_target(), FADE)


func current_music() -> String:
	return _music_id


func _music_target() -> float:
	return float(_cfg.get("music_db", -9.0)) - _duck


## Abaixa a música por um momento (chefe, transformação), para o efeito aparecer.
func duck(db: float, hold: float) -> void:
	_duck = db
	_apply_music_volume(0.15)
	await get_tree().create_timer(hold, true, false, true).timeout
	_duck = 0.0
	_apply_music_volume(0.6)


func _apply_music_volume(t: float) -> void:
	for p in [_music_a, _music_b]:
		if p.playing and p.stream and p.stream.resource_path.ends_with((String(_cfg.get("music", {}).get(_music_id, "?"))) + ".ogg"):
			create_tween().tween_property(p, "volume_db", _music_target(), t)


## Opções: liga/desliga música e efeitos.
func refresh_settings() -> void:
	if not music_on():
		_music_a.stop()
		_music_b.stop()
	else:
		var id := _music_id
		_music_id = ""
		music(id)


## Durante anúncios o jogo fica mudo (o anúncio tem som próprio).
func set_ad_mute(on: bool) -> void:
	_ad_muted = on
	AudioServer.set_bus_mute(0, on)


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED:
		AudioServer.set_bus_mute(0, true)
	elif what == NOTIFICATION_APPLICATION_RESUMED:
		AudioServer.set_bus_mute(0, _ad_muted)
