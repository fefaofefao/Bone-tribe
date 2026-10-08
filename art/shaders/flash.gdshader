shader_type canvas_item;
// Pisca a sprite numa cor (dano, encaixe) mantendo a transparência.
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);

void fragment() {
	vec4 c = texture(TEXTURE, UV) * COLOR * tint;
	COLOR = vec4(mix(c.rgb, flash_color.rgb, flash), c.a);
}
