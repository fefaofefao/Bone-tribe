class_name Offline
extends RefCounted
## O Ossudo junta pó de osso enquanto o jogador está fora (até max_hours).
## Usa a hora do servidor (Backend); o valor acompanha a torre mais alta liberada.


static func cfg() -> Dictionary:
	return GameData.bal("offline", {})


static func rate_per_hour() -> float:
	return float(cfg().get("dust_per_hour", 50)) * float(GameData.tower(Meta.tower_unlocked()).get("dust_mult", 1.0))


static func cap() -> int:
	return int(roundf(rate_per_hour() * float(cfg().get("max_hours", 8))))


static func cap_seconds() -> int:
	return int(float(cfg().get("max_hours", 8)) * 3600.0)


## Soma o pó do tempo fora desde a última vez que o jogo salvou.
static func accrue() -> void:
	var o: Dictionary = Profile.data.offline
	var now := Backend.now()
	var last := int(o.get("last_seen", 0))
	o.last_seen = now
	if last <= 0 or int(Profile.data.get("runs_played", 0)) < 1:
		return
	var away := now - last
	if away < int(float(cfg().get("min_minutes", 10)) * 60.0):
		return
	var gain := rate_per_hour() * minf(away, cap_seconds()) / 3600.0
	o.pending = mini(cap(), int(o.get("pending", 0)) + int(gain))


static func pending() -> int:
	return int(Profile.data.offline.get("pending", 0))


static func ad_left() -> int:
	var o: Dictionary = Profile.data.offline
	if int(o.get("ad_day", -1)) != Backend.server_day():
		return Ads.limit("offline_double")
	return maxi(0, Ads.limit("offline_double") - int(o.get("ad_count", 0)))


static func collect(doubled: bool) -> int:
	var o: Dictionary = Profile.data.offline
	var n := pending() * (2 if doubled else 1)
	if n <= 0:
		return 0
	o.pending = 0
	if doubled:
		if int(o.get("ad_day", -1)) != Backend.server_day():
			o.ad_day = Backend.server_day()
			o.ad_count = 0
		o.ad_count = int(o.get("ad_count", 0)) + 1
	Profile.add_dust(n, "offline")
	Backend.log_event("offline_collect", {"dust": n, "doubled": doubled})
	return n
