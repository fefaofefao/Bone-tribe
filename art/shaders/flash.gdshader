shader_type canvas_item;
// Ossos do Ossinho: pisca numa cor (dano, encaixe) e aplica o estilo da skin.
// Estilo da skin: paleta (claro/escuro pela luminância), contorno brilhante,
// faixa de brilho que atravessa o corpo e faíscas. Tudo zero = osso normal.
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);

uniform float remap : hint_range(0.0, 1.0) = 0.0;
uniform vec4 pal_dark : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform vec4 pal_light : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 rim_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float rim = 0.0;
uniform float rim_width = 3.0;
uniform float pulse = 0.0;
uniform vec4 sheen_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float sheen = 0.0;
uniform float sparkle = 0.0;
uniform float skin_alpha : hint_range(0.0, 1.0) = 1.0;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec4 base = texture(TEXTURE, UV) * COLOR;
	vec3 col = base.rgb;
	if (remap > 0.0) {
		float lum = dot(base.rgb, vec3(0.299, 0.587, 0.114));
		vec3 pal = mix(pal_dark.rgb, pal_light.rgb, smoothstep(0.05, 0.95, lum));
		col = mix(col, pal, remap);
	}
	col *= tint.rgb;
	float a = base.a * tint.a * skin_alpha;
	if (rim > 0.0 && base.a > 0.05) {
		vec2 o = TEXTURE_PIXEL_SIZE * rim_width;
		float m = min(min(texture(TEXTURE, UV + vec2(o.x, 0.0)).a, texture(TEXTURE, UV - vec2(o.x, 0.0)).a),
			min(texture(TEXTURE, UV + vec2(0.0, o.y)).a, texture(TEXTURE, UV - vec2(0.0, o.y)).a));
		float edge = clamp(base.a - m, 0.0, 1.0);
		float p = 1.0 + pulse * 0.35 * sin(TIME * 3.0);
		col += rim_color.rgb * edge * rim * p;
		a = max(a, base.a * edge * min(rim, 1.0));
	}
	if (sheen > 0.0) {
		float d = (FRAGCOORD.x + FRAGCOORD.y) * 0.004 - TIME * 0.35;
		float band = smoothstep(0.0, 0.08, fract(d)) * (1.0 - smoothstep(0.08, 0.16, fract(d)));
		col += sheen_color.rgb * band * sheen * base.a;
	}
	if (sparkle > 0.0) {
		vec2 cell = floor(FRAGCOORD.xy / 9.0);
		float h = hash(cell);
		float tw = pow(max(0.0, sin(TIME * (1.5 + h * 3.0) + h * 40.0)), 24.0);
		col += vec3(1.0) * tw * step(0.93, h) * sparkle * base.a;
	}
	COLOR = vec4(mix(col, flash_color.rgb, flash), a);
}
