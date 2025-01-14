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
uniform vec4 faceColor;

out float Var;
out vec4 Kai;
out vec4 Kdi;
out vec4 Ksi;
out vec3 normal_eye;
out vec3 position_eye;

out vec3 fragPos;
out vec3 viewDir; // 视点方向
void main() {
    vec4 translate_center = translation * center;
    vec4 translate_position = translation * vec4(position, 1.0);

    // 将顶点坐标平移到旋转中心点的位置
    vec3 centeredPosition = translate_position.xyz - translate_center.xyz;

    // 进行旋转变换
    vec4 rotatedPosition =rotation * vec4(centeredPosition, 1.0);

    // 将顶点坐标再平移到原来的位置
    vec4 finalPosition =  vec4(rotatedPosition.xyz + translate_center.xyz, 1.0);

    gl_Position =projection * view * finalPosition;  // 顶点的最终位置
    //gl_Position = projection * view  * rotation * translate_position;  // 顶点的最终位置


    // 计算视点方向
    vec4 viewPos = view * center;

    // 更新传递给片段着色器的变量
    fragPos =  vec3(finalPosition) - center.xyz; 
    viewDir = fragPos - viewPos.xyz;

    position_eye = vec3 (view * rotation * vec4 (position, 1.0));
    normal_eye = vec3 (view * rotation * vec4 (normal, 0.0));
    normal_eye = normalize(normal_eye);

    Kai = vec4(51.0/255.0,43.0/255.0,33.3/255.0,1.0); // 阴影效果
    // Kdi = vec4(255.0/255.0,228.0/255.0,58.0/255.0,1.0);
    // Ksi = vec4(255.0/255.0,235.0/255.0,80.0/255.0,1.0);

    Kdi = faceColor;
    // 计算一个稍微暗一点的 Ksi
    float darkeningFactor = 0.97; // 你可以调整这个值来使颜色更暗或更亮
    Ksi = vec4(faceColor.rgb * darkeningFactor, faceColor.a);


    Var = var.z;

    gl_PointSize = 2.0; // 设置点的大小为 10.0

}
"""

fragment_src = """
#version 330 core

in vec3 fragPos;
in vec3 viewDir;
in float Var;

vec3 Ls = vec3(1, 1, 1);
vec3 Ld = vec3(1, 1, 1);
vec3 La = vec3(1, 1, 1);
in vec4 Ksi;
in vec4 Kdi;
in vec4 Kai;

in vec3 position_eye;
in vec3 normal_eye;
out vec4 FragColor;

uniform vec4 edgeColor;          // 边的颜色
uniform vec4 pointColor;         // 点的颜色
uniform bool isEdge;
uniform bool isPoint;
uniform bool isGmsh;
uniform bool isVar;
uniform vec3 light_position_eye;
uniform vec3 gmsh_light_position_eye;
uniform float double_sided;

void main() {
    float specular_exponent = 35.0;
    float lighting_factor = 0.8;

    vec3 normalizedViewDir = normalize(viewDir);
    vec3 normalizedNormal = normalize(fragPos);
    float intensity = dot(normalizedViewDir, normalizedNormal); // 计算夹角

    vec3 reflection_eye = reflect(-normalizedViewDir, normalize(normal_eye));
    vec3 surface_to_viewer_eye = normalize(-position_eye);
    float dot_prod_specular = dot(reflection_eye, surface_to_viewer_eye);
    dot_prod_specular = max(dot_prod_specular, 0.0);
    float specular_factor = pow(dot_prod_specular, specular_exponent);

    vec3 Ia = La * vec3(Kai); // ambient intensity

    vec3 vector_to_light_eye = light_position_eye - position_eye;
    vec3 direction_to_light_eye = normalize(vector_to_light_eye);
    float dot_prod = dot(direction_to_light_eye, normalize(normal_eye));
    float clamped_dot_prod = abs(dot_prod);

    vec3 Id = Ld * vec3(Kdi) * clamped_dot_prod; // diffuse intensity
    vec3 Is = Ls * vec3(Ksi) * specular_factor; // specular intensity

    vec4 color = vec4(lighting_factor * (Is + Id) + Ia, (Kai.a + Ksi.a + Kdi.a) / 3);

    if (isEdge) {
            FragColor = edgeColor;
    }else if (isPoint) {   // 如果是点
            FragColor = pointColor;  // 应用点的颜色
    }else if (isGmsh) {
         // 根据光源位置计算某个点距离到光源的距离，根据位置的不同，颜色也不同
        // 定义三种颜色：黑色、深绿色和浅绿色,利用距离来进一步实现颜色的过渡
        vec4 blackColor = vec4(0.2, 0.2, 0.2, 1.0);  // 黑色
        vec4 deepGreenColor = vec4(0.0, 0.5, 0.0, 1.0);  // 深绿色
        vec4 lightGreenColor = vec4(0.5, 1.0, 0.5, 1.0);  // 浅绿色

        vec3 gmsh_vector_to_light_eye = gmsh_light_position_eye - position_eye;
        vec3 gmsh_direction_to_light_eye = normalize(gmsh_vector_to_light_eye);
        // 计算点到光源的平方和距离
        float t = (gmsh_direction_to_light_eye.x + gmsh_direction_to_light_eye.y + gmsh_direction_to_light_eye.z);

        // 根据 t 的值来选择颜色
        if (t > 0.5) {
             if (intensity < 0.0) {
                 FragColor = blackColor;  // 如果夹角小于 0，就是黑色
             }else{
                FragColor = mix(blackColor, deepGreenColor, (t-0.5) * 2.0);  // 从黑色到深绿色过渡
             }
        } else {
             FragColor = mix(deepGreenColor, lightGreenColor, t * 2.0);  // 从深绿色到浅绿色过渡
        }
    }else if (isVar) {
        vec4 redColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red
        vec4 yellowColor = vec4(1.0, 1.0, 0.0, 1.0);  // Yellow
        vec4 blueColor = vec4(0.0, 0.0, 1.0, 1.0);  // Blue

        if (Var < 0.5) {
            FragColor = mix(blueColor, yellowColor, Var * 2.0);  // 从红色到黄色过渡
        }else{
            FragColor = mix(yellowColor, redColor, (Var - 0.5) * 2.0);  // 从黄色到蓝色过渡
        }
    }else{
            FragColor = color;
    }
}
"""

# 为了绘制小坐标轴
axes_vertex_src = '''
#version 330 core
layout (location = 0) in vec3 position;
uniform mat4 rotation; // 用于坐标轴的旋转
uniform mat4 fixedRotation; // 用于保持字母不旋转
uniform bool isLetter; // 判断是否为字母

void main()
{
    if (isLetter) {
        // 如果是字母，保持它们不旋转，只应用平移
        gl_Position = rotation * fixedRotation * vec4(position, 1.0);
    } else {
        // 如果是坐标轴，应用旋转矩阵
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