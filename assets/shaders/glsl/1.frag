#version 330
uniform sampler2D u_tex0;
uniform ivec2 u_canvas;
uniform int u_tv_count;
uniform ivec4 u_tvdata[9];
in vec2 v_uv;
out vec4 fragColor;

vec4 sample_tv(vec2 pos, ivec4 tvdata) {
    float tv_width = float(tvdata.x) / float(max(u_canvas.x, 1));
    float tv_height = float(tvdata.y) / float(max(u_canvas.y, 1));
    float tv_x = float(tvdata.z) / float(max(u_canvas.x, 1));
    float tv_y = float(tvdata.w) / float(max(u_canvas.y, 1));
    vec2 mapped = pos;

    if (abs(tv_width) < abs(tv_height)) {
        float temp = mapped.x;
        mapped.x = tv_x + tv_width - tv_width * mapped.y;
        mapped.y = tv_y + tv_height * temp;
    } else {
        mapped.x = tv_x + tv_width * mapped.x;
        mapped.y = tv_y + tv_height * mapped.y;
    }

    return texture(u_tex0, mapped);
}

void main() {
    fragColor = sample_tv(v_uv, u_tvdata[0]);
}
