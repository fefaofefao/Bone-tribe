extends Node
## Simulação de equilíbrio (não altera o perfil real):
##   godot --headless --path . res://tests/BalanceSim.tscn [-- players=40 runs=6]
##   godot --headless --path . res://tests/BalanceSim.tscn -- mode=towers [players=12 runs=120]
## Simula jogadores novos: a cada partida o pó de osso vira melhorias do Ossuário.

func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=")
		if kv.size() == 2:
			args[kv[0]] = kv[1]
	if args.get("mode", "") == "towers":
		_towers(int(args.get("players", "12")), int(args.get("runs", "120")))
		return
	var players := int(args.get("players", "40"))
	var runs := int(args.get("runs", "6"))
	var backup: Dictionary = Profile.data.duplicate(true)
	var boss_floors: Dictionary = GameData.bal("run/boss_floors", {})
	var stats := []
	for r in runs:
		stats.append({"floor": 0.0, "bosses": {}, "dust": 0.0, "level": 0.0, "bones": 0.0, "dead": 0})
	var first_win := {}
	for p in players:
		Profile.data.ossuary = {"hp": 0, "atk": 0, "def": 0, "drop": 0}
		var bank := 0
		for r in runs:
			var ar := AutoRunner.new({"seed": p * 1000 + r})
			var st := ar.play()
			var rew := st.end_rewards()
			bank += int(rew.total)
			var s: Dictionary = stats[r]
			s.floor += st.floor_n
			s.dust += int(rew.total)
			s.level += st.level
			s.bones += st.non_basic_bones().size()
			if st.dead:
				s.dead += 1
			if args.has("debug") and st.bosses_beaten.has("boss_ancient_dragon") and r < 3:
				var parts := []
				for sl in st.equipped:
					parts.append("%s:%s+%d" % [String(sl).replace("slot_", ""), String(st.equipped[sl].id).replace("bone_", ""), int(st.equipped[sl].level) - 1])
				var hf := st.make_hero()
				print("vitória sobre o Dragão (partida %d) nível %d: %s | vida %d atk %.1f def %.0f crit %.2f esq %.2f regen %.2f roubo %.2f formas %s" % [r + 1, st.level, ", ".join(parts), hf.max_hp, hf.atk, hf.def, hf.crit, hf.dodge, hf.regen, hf.lifesteal, Body.active_forms(st.equipped)])
			for b in st.bosses_beaten:
				s.bosses[b] = int(s.bosses.get(b, 0)) + 1
				var key := "%d:%s" % [p, b]
				if not first_win.has(key):
					first_win[key] = r + 1
			# gasta o pó no Ossuário (ataque, vida, defesa, chance de osso)
			var order := ["atk", "hp", "atk", "hp", "def", "drop"]
			var i := 0
			while true:
				var stat: String = order[i % order.size()]
				var cost := Meta.ossuary_cost(stat)
				if cost > bank:
					break
				bank -= cost
				Profile.data.ossuary[stat] = Meta.ossuary_level(stat) + 1
				i += 1
	print("")
	print("== Simulação: %d jogadores x %d partidas (modo %s) ==" % [players, runs, "protótipo" if GameData.bal("run/prototype_mode", false) else "completo"])
	for r in runs:
		var s: Dictionary = stats[r]
		var line := "partida %d: andar médio %.1f, nível %.1f, ossos %.1f, pó %.0f, mortes %d%%" % [r + 1, s.floor / players, s.level / players, s.bones / players, s.dust / players, 100 * s.dead / players]
		for b in boss_floors.values():
			line += ", %s %d%%" % [b, 100 * int(s.bosses.get(b, 0)) / players]
		print(line)
	for b in boss_floors.values():
		var firsts := []
		for k in first_win:
			if String(k).ends_with(b):
				firsts.append(first_win[k])
		if firsts.size() > 0:
			var sum := 0
			for x in firsts:
				sum += x
			print("%s: %d%% dos jogadores venceram; 1ª vitória em média na partida %.1f" % [b, 100 * firsts.size() / players, float(sum) / firsts.size()])
	Profile.data = backup
	Profile.save()
	get_tree().quit()


## Gasta todo o pó no Ossuário (ataque, vida, defesa, chance de osso).
func _spend(bank: int) -> int:
	var order := ["atk", "hp", "atk", "hp", "def", "drop"]
	var i := 0
	while i < 400:
		var stat: String = order[i % order.size()]
		i += 1
		if Meta.ossuary_level(stat) >= Meta.ossuary_max():
			continue
		var cost := Meta.ossuary_cost(stat)
		if cost > bank:
			break
		bank -= cost
		Profile.data.ossuary[stat] = Meta.ossuary_level(stat) + 1
	return bank


## Progressão pelas torres: cada jogador sempre joga a torre mais alta liberada;
## vencer o Dragão Ancião libera a próxima. Mostra em que partida cada torre cai
## e quantas partidas da torre em curso terminam em derrota.
func _towers(players: int, runs: int) -> void:
	var backup: Dictionary = Profile.data.duplicate(true)
	var n_towers := GameData.towers.size()
	var first := []
	var tries := []
	var fails := []
	var floors := []
	for t in n_towers:
		first.append([])
		tries.append(0)
		fails.append(0)
		floors.append(0)
	var final_tower := 0.0
	for p in players:
		Profile.data.ossuary = {"hp": 0, "atk": 0, "def": 0, "drop": 0}
		var bank := 0
		var unlocked := 1
		for r in runs:
			var t := unlocked
			var st := AutoRunner.new({"seed": p * 7919 + r, "tower": t}).play()
			bank += int(st.end_rewards().total)
			tries[t - 1] += 1
			floors[t - 1] += st.floor_n
			if st.bosses_beaten.has("boss_ancient_dragon"):
				if unlocked == t and t <= n_towers:
					first[t - 1].append(r + 1)
					unlocked = mini(n_towers + 1, t + 1)
			else:
				fails[t - 1] += 1
			bank = _spend(bank)
			if unlocked > n_towers:
				break
		final_tower += mini(unlocked, n_towers)
	MonsterFactory.tower = 1
	print("")
	print("== Torres: %d jogadores x até %d partidas ==" % [players, runs])
	for t in n_towers:
		var f: Array = first[t]
		var avg := 0.0
		for x in f:
			avg += x
		var line := "torre %2d: " % (t + 1)
		if f.size() > 0:
			f.sort()
			line += "%3d%% venceram; 1ª vitória na partida média %.1f (mín %d, máx %d)" % [100 * f.size() / players, avg / f.size(), f[0], f[-1]]
		else:
			line += "ninguém venceu"
		if tries[t] > 0:
			line += " | derrotas %d%% de %d partidas, andar médio %.1f" % [100 * fails[t] / tries[t], tries[t], float(floors[t]) / tries[t]]
		print(line)
	print("torre média ao fim: %.1f" % (final_tower / players))
	Profile.data = backup
	Profile.save()
	get_tree().quit()
