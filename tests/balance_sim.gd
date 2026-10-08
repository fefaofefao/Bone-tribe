extends Node
## Simulação de equilíbrio (não altera o perfil real):
##   godot --headless --path . res://tests/BalanceSim.tscn [-- players=40 runs=6]
## Simula jogadores novos: a cada partida o pó de osso vira melhorias do Ossuário.

func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=")
		if kv.size() == 2:
			args[kv[0]] = kv[1]
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
