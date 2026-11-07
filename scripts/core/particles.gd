class_name Particles
extends RefCounted
## Partículas na CPU. Alguns drivers de vídeo Android (ex.: MediaTek mt6855) caem ao
## compilar o shader de processamento das GPUParticles no renderizador de compatibilidade
## (glLinkProgram dentro de "Update GPUParticles"). As partículas do jogo são poucas, então
## montamos tudo como GPUParticles2D (mais fácil de configurar) e convertemos para
## CPUParticles2D, que não compila esse shader e fica igual na tela.


static func to_cpu(g: GPUParticles2D) -> CPUParticles2D:
	var c := CPUParticles2D.new()
	c.convert_from_particles(g)
	c.position = g.position
	c.z_index = g.z_index
	c.material = g.material
	c.texture = g.texture
	c.modulate = g.modulate
	c.emitting = g.emitting
	c.preprocess = g.preprocess
	g.free()
	return c
