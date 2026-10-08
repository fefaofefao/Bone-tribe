class_name TouchScroll
extends ScrollContainer
## Rolagem por arrasto em qualquer ponto da área: sobre botões, cartões, textos
## ou espaços vazios. Um toque curto continua sendo um toque (o botão funciona);
## se o dedo arrastar mais que DRAG_START, a página rola e o toque no botão é
## cancelado. Ao soltar, a rolagem continua com inércia.

const DRAG_START := 14.0
const FRICTION := 5.0
const MIN_SPEED := 30.0

var _pressing := false
var _dragging := false
var _start := Vector2.ZERO
var _start_scroll := 0.0
var _last_y := 0.0
var _last_t := 0.0
var _velocity := 0.0


func _ready() -> void:
	horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	# a rolagem por arrasto nativa fica desligada: quem cuida é este script
	scroll_deadzone = 100000


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	var pos := Vector2.ZERO
	var is_press := false
	var is_release := false
	var is_motion := false
	if event is InputEventScreenTouch:
		if event.index != 0:
			return
		pos = event.position
		is_press = event.pressed
		is_release = not event.pressed
	elif event is InputEventScreenDrag:
		if event.index != 0:
			return
		pos = event.position
		is_motion = true
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if DisplayServer.is_touchscreen_available():
			return  # no celular os eventos de toque já chegam acima
		pos = event.position
		is_press = event.pressed
		is_release = not event.pressed
	elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT):
		if DisplayServer.is_touchscreen_available():
			return
		pos = event.position
		is_motion = true
	else:
		return

	if is_press:
		if not get_global_rect().has_point(pos) or not _is_on_top(pos):
			return
		_pressing = true
		_dragging = false
		_velocity = 0.0
		_start = pos
		_start_scroll = scroll_vertical
		_last_y = pos.y
		_last_t = Time.get_ticks_msec() / 1000.0
	elif is_motion and _pressing:
		if not _dragging and absf(pos.y - _start.y) > DRAG_START:
			_dragging = true
			_start = pos
			_start_scroll = scroll_vertical
			# cancela o toque em andamento no botão debaixo do dedo
			propagate_notification(NOTIFICATION_SCROLL_BEGIN)
		if _dragging:
			scroll_vertical = int(_start_scroll - (pos.y - _start.y))
			var t := Time.get_ticks_msec() / 1000.0
			var dt := maxf(t - _last_t, 0.001)
			_velocity = lerpf(_velocity, -(pos.y - _last_y) / dt, 0.5)
			_last_y = pos.y
			_last_t = t
			get_viewport().set_input_as_handled()
	elif is_release and _pressing:
		_pressing = false
		if _dragging:
			_dragging = false
			propagate_notification(NOTIFICATION_SCROLL_END)
			if Time.get_ticks_msec() / 1000.0 - _last_t > 0.08:
				_velocity = 0.0


func _process(delta: float) -> void:
	if _dragging or absf(_velocity) < MIN_SPEED:
		_velocity = 0.0 if not _dragging else _velocity
		return
	var before := scroll_vertical
	scroll_vertical = int(scroll_vertical + _velocity * delta)
	_velocity *= exp(-FRICTION * delta)
	if scroll_vertical == before:
		_velocity = 0.0  # chegou no começo ou no fim


## Não rola quando há uma janela (popup) por cima desta área.
func _is_on_top(pos: Vector2) -> bool:
	var hovered := get_viewport().gui_get_hovered_control()
	if hovered == null:
		return true
	return hovered == self or is_ancestor_of(hovered)
