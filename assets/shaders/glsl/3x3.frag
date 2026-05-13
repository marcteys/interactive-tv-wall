#version 330
uniform sampler2D u_tex0;
uniform ivec2 u_canvas;
uniform int u_tv_count;
uniform ivec4 u_tvdata[9];
in vec2 v_uv;
out vec4 fragColor;

vec4 sample_tv(vec2 pos, ivec4 tvdata, float x_index, float y_index) {
    float tv_width = float(tvdata.x) / float(max(u_canvas.x, 1));
    float tv_height = float(tvdata.y) / float(max(u_canvas.y, 1));
    float tv_x = float(tvdata.z) / float(max(u_canvas.x, 1));
    float tv_y = float(tvdata.w) / float(max(u_canvas.y, 1));
    vec2 mapped = pos;

    if (abs(tv_width) < abs(tv_height)) {
        float temp = mapped.x;
        mapped.x = tv_x + tv_width - 3.0 * tv_width * (mapped.y - y_index / 3.0);
        mapped.y = tv_y + 3.0 * tv_height * (temp - x_index / 3.0);
    } else {
        mapped.x = tv_x + 3.0 * tv_width * (mapped.x - x_index / 3.0);
        mapped.y = tv_y + 3.0 * tv_height * (mapped.y - y_index / 3.0);
    }

    return texture(u_tex0, mapped);
}

void main() {
    int x_index = min(int(floor(v_uv.x * 3.0)), 2);
    int y_index = min(int(floor(v_uv.y * 3.0)), 2);
    int tv_index = clamp(y_index * 3 + x_index, 0, min(u_tv_count, 9) - 1);
    fragColor = sample_tv(v_uv, u_tvdata[tv_index], float(x_index), float(y_index));
}
