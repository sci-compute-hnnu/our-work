vertex_src = """
#version 330 core
layout (location = 0) in vec3 position;
in vec3 normal;
in vec3 var;

uniform mat4 projection;// 投影矩阵
uniform mat4 translation;// 平移矩阵
uniform mat4 rotation;// 旋转矩阵
uniform mat4 view; // 观察矩阵
uniform vec4 center;

out float Var;
out vec3 viewPos;      // 视空间中的顶点位置
out vec3 viewNormal;   // 视空间中的法向量

void main() {
    // 先平移，然后绕中心旋转
    vec4 translate_center = translation * center;
    vec4 translate_position = translation * vec4(position, 1.0);

    // 将顶点坐标平移到旋转中心
    vec3 centeredPosition = translate_position.xyz - translate_center.xyz;

    // 旋转变换
    vec4 rotatedPosition = rotation * vec4(centeredPosition, 1.0);

    // 平移回原位置 → 世界坐标
    vec4 worldPos = vec4(rotatedPosition.xyz + translate_center.xyz, 1.0);

    // 裁剪坐标
    gl_Position = projection * view * worldPos;

    // 传递视空间中的位置（相机在原点）
    viewPos = vec3(view * worldPos);

    // 法向量变换到视空间（平移不影响法向量，view 和 rotation 都是正交矩阵）
    viewNormal = normalize(mat3(view) * mat3(rotation) * normal);

    Var = var.z;

    gl_PointSize = 2.0;
}
"""

fragment_src = """
#version 330 core

in vec3 viewPos;       // 视空间顶点位置（相机在原点）
in vec3 viewNormal;    // 视空间法向量
in float Var;

out vec4 FragColor;

uniform vec4 faceColor;            // 面颜色
uniform vec4 edgeColor;            // 边的颜色
uniform vec4 pointColor;           // 点的颜色
uniform bool isEdge;
uniform bool isPoint;
uniform bool isGmsh;
uniform bool isVar;
uniform vec3 light_position_eye;       // 主光源在视空间中的位置
uniform vec3 gmsh_light_position_eye;  // Gmsh 光源在视空间中的位置
uniform float ambientStrength;         // 环境光强度 [0, 1]
uniform float specularStrength;        // 镜面反射强度 [0, 1]
uniform float shininess;               // 高光锐度
uniform vec3 lightColor;               // 光源颜色

// 计算 Blinn-Phong 光照 + Fresnel 边缘光
vec3 blinnPhong(vec3 N, vec3 V, vec3 L, vec3 albedo) {
    vec3 H = normalize(L + V);   // Blinn-Phong 半向量

    // 环境光
    vec3 ambient = ambientStrength * lightColor;

    // 漫反射 (Lambert)
    float NdotL = max(dot(N, L), 0.0);
    vec3 diffuse = NdotL * lightColor;

    // 镜面反射 (Blinn-Phong)
    float NdotH = max(dot(N, H), 0.0);
    vec3 specular = specularStrength * pow(NdotH, shininess) * lightColor;

    // Fresnel 边缘光 — 让边缘更亮，增强立体感
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    vec3 rim = fresnel * lightColor * 0.2;

    return albedo * (ambient + diffuse + rim) + specular;
}

void main() {
    // 归一化视空间向量
    vec3 N = normalize(viewNormal);
    vec3 V = normalize(-viewPos);   // 相机在原点，视线方向 = 原点 → 顶点

    // 双面光照：背面时翻转法线，使内部面也有正确光照
    if (!gl_FrontFacing) {
        N = -N;
    }

    // ---- 边模式 ----
    if (isEdge) {
        FragColor = edgeColor;
        return;
    }

    // ---- 点模式 ----
    if (isPoint) {
        FragColor = pointColor;
        return;
    }

    // ---- Gmsh 线框风格 ----
    if (isGmsh) {
        vec3 L_gmsh = normalize(gmsh_light_position_eye - viewPos);
        float NdotL = max(dot(N, L_gmsh), 0.0);

        // 基于到光源距离的颜色渐变
        float dist = length(gmsh_light_position_eye - viewPos);
        float t = clamp(dist / 8.0, 0.0, 1.0);

        // 冷色调 → 暖色调过渡
        vec3 coolColor  = vec3(0.18, 0.28, 0.38);
        vec3 warmColor  = vec3(0.48, 0.65, 0.45);
        vec3 baseColor  = mix(warmColor, coolColor, t);

        // Lambert 光照
        float lighting = 0.18 + 0.82 * NdotL;
        vec3 result = baseColor * lighting;

        // Gamma 校正
        result = pow(result, vec3(1.0 / 2.2));
        FragColor = vec4(result, 1.0);
        return;
    }

    // ---- 变量着色模式 ----
    if (isVar) {
        // ParaView "Cool to Warm" 风格 colormap：蓝 → 浅蓝 → 白 → 橙 → 红
        // 5 段分段线性插值，比蓝→黄→红更柔和、更接近 ParaView 默认效果
        float t = clamp(Var, 0.0, 1.0);

        const vec3 c0 = vec3(0.12, 0.16, 0.55);  // 深蓝 (cold)
        const vec3 c1 = vec3(0.25, 0.42, 0.65);  // 中蓝
        const vec3 c2 = vec3(0.62, 0.62, 0.67);  // 浅灰 (中点)
        const vec3 c3 = vec3(0.68, 0.36, 0.14);  // 中橙
        const vec3 c4 = vec3(0.50, 0.01, 0.08);  // 深红 (warm)

        vec3 varColor;
        if (t < 0.25) {
            varColor = mix(c0, c1, t / 0.25);
        } else if (t < 0.5) {
            varColor = mix(c1, c2, (t - 0.25) / 0.25);
        } else if (t < 0.75) {
            varColor = mix(c2, c3, (t - 0.5) / 0.25);
        } else {
            varColor = mix(c3, c4, (t - 0.75) / 0.25);
        }

        vec3 L = normalize(light_position_eye - viewPos);
        vec3 result = blinnPhong(N, V, L, varColor);

        // Gamma 校正
        result = pow(result, vec3(1.0 / 2.2));
        FragColor = vec4(result, faceColor.a);
        return;
    }

    // ---- 默认面渲染 ----
    vec3 L = normalize(light_position_eye - viewPos);
    vec3 result = blinnPhong(N, V, L, faceColor.rgb);

    // Gamma 校正
    result = pow(result, vec3(1.0 / 2.2));
    FragColor = vec4(result, faceColor.a);
}
"""

# 为了绘制小坐标轴
axes_vertex_src = '''
#version 330 core
layout (location = 0) in vec3 position;
uniform mat4 rotation;       // 模型旋转+缩放矩阵（轴和箭头使用）
uniform mat4 fixedRotation;  // 旋转的逆矩阵，用于抵消字母的旋转
uniform bool isLetter;       // 是否为字母（字母始终面朝相机）

void main()
{
    if (isLetter) {
        // 字母: rotation * fixedRotation ≈ 仅缩放（fixedRotation 抵消了旋转部分）
        // 所以字母不跟随模型旋转，始终面朝相机，可读
        gl_Position = rotation * fixedRotation * vec4(position, 1.0);
    } else {
        // 坐标轴/箭头: 跟随模型旋转，显示当前朝向
        gl_Position = rotation * vec4(position, 1.0);
    }
}
'''

axes_fragment_src = '''
#version 330 core
out vec4 FragColor;
uniform vec3 color;

void main()
{
    FragColor = vec4(color, 1.0); // 颜色作为输入，控制每根轴的颜色
}
'''