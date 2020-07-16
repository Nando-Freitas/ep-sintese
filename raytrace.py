# Numpy para fazer as contas
import numpy as np
# matplotlib para salvar a imagem ou plottar
import matplotlib.pyplot as plt

# A ideia eh fazer um raytracing bem simples, em python single thread mesmo usando esferas e um plano

def phong(obj, N, toL, toO):
    # Calcula a parte especular usando Phong
    # https://www.scratchapixel.com/lessons/3d-basic-rendering/phong-shader-BRDF
    return obj.get('specular_c', specular_c) * max(np.dot(N, normalizar(toL + toO)), 0) ** specular_k * color_light


def shading(obj, N, toL, color):
    # calcula o shading usando difusao de Lambert
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.lambertw.html
    return obj.get('diffuse_c', diffuse_c) * max(np.dot(N, toL), 0) * color

def check_shadow(M, N, toL, obj_idx) :
    # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
    return [intersecao(M + N * .0001, toL, obj_sh) 
            for k, obj_sh in enumerate(scene) if k != obj_idx]


def check_properties(rayO, rayD, obj, t):
    # Encontra o ponto de intersecao com o objeto
    ponto_intersec = rayO + rayD * t
    # Encontra as propriedades do objeto
    N = get_normal(obj, ponto_intersec)
    color = get_color(obj, ponto_intersec)
    toL = normalizar(L - ponto_intersec)
    toO = normalizar(O - ponto_intersec)
    return ponto_intersec, N, color, toL, toO


def compute_color(obj, N, toL, toO, color):
    col_ray = ambient
    col_ray += shading(obj, N, toL, color)
    col_ray += phong(obj, N, toL, toO)
    return col_ray


def tracar_raio(rayO, rayD):
    # Encontra o primeiro ponto de intersecao com a cena
    t = np.inf
    for i, obj in enumerate(scene):
        t_obj = intersecao(rayO, rayD, obj)
        if t_obj < t:
            t, obj_idx = t_obj, i
    # Retorna se o raio nao intercepta nenhum objeto
    if t == np.inf:
        return
    # Encontra o objeto
    obj = scene[obj_idx]
    # Pega as propriedades do objeto da intersecao
    M, N, color, toL, toO = check_properties(rayO, rayD, obj, t)
    # Define se o objeto tem ou nao sombra
    l = check_shadow(M, N, toL, obj_idx)
    if l and min(l) < np.inf:
        return
    # Computa a cor
    col_ray = compute_color(obj, N, toL, toO, color)
    return obj, M, N, col_ray


def calc_dist(P, O, N, denom):
    # Calcula a distancia
    return np.dot(P - O, N) / denom


def intersecao_plano(O, D, P, N):
    # Retorna a distancia do Objeto O a intersecao do raio (Objeto, Direcao) com o Plano (Plano, Normal), ou +infinito se nao ha intersecao
    # Objeto e Plano sao pontos 3D, Direcao e Normal sao vetores normalizados
    denom = np.dot(D, N)
    if np.abs(denom) < 1e-6:
        return np.inf
    # d = np.dot(P - O, N) / denom
    d = calc_dist(P, O, N, denom)
    if d < 0:
        return np.inf
    return d


def calc_a(D):
    # a = raio * raio
    # Precisa usar o dot porque sao vetores
    return np.dot(D, D)


def calc_O_to_S(O, S):
     # Diferenca do objeto - esfera
    return O - S


def calc_b(D, OS):
    # b = raio * diferenca 
    return 2 * np.dot(D, OS)

def calc_c(OS, R):
    # c = diferenca * diferenca - raio * raio
    return np.dot(OS, OS) - R * R


def calc_discriminante(a, b, c):
    # discriminante = b2 - 4ac
    return b * b - 4 * a * c

def calc_q(b, distSqrt):
    # usado para achar as intersecoes
    return (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0


def intersecao_esfera(O, D, S, R):
    # Bem parecido com o do plano, mas para esfera é um pouco mais simples porque da pra saber se há intersecao baseado no raio
    # Retorna a distancia do Objeto O ate a intersecao do raio (Objeto, Direcao) com a esfera (Esfera S, Raio), ou mais infinito se nao ha intersecao
    # Objeto e Esfera S sao pontos 3D, Direcao eh um vetor normalizado, Raio R é um escalar
    # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection
    a = calc_a(D)
    OS = calc_O_to_S(O, S)
    b = calc_b(D, OS)
    c = calc_c(OS, R)
    disc = calc_discriminante(a, b, c)
    if disc > 0:
        distSqrt = np.sqrt(disc)
        q = calc_q(b, distSqrt)
        t0 = q / a
        t1 = c / q
        t0, t1 = min(t0, t1), max(t0, t1)
        if t1 >= 0:
            return t1 if t0 < 0 else t0
    return np.inf

def intersecao(O, D, obj):
    # Precisa definir se a intersecao eh com plano ou com esfera
    # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
    if obj['type'] == 'plane':
        return intersecao_plano(O, D, obj['position'], obj['normal'])
    elif obj['type'] == 'sphere':
        return intersecao_esfera(O, D, obj['position'], obj['radius'])

def normalizar(x):
    x /= np.linalg.norm(x)
    return x

def get_normal(obj, M):
    # Precisa calcular a normal que varia de acordo com esfera ou plano
    # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
    if obj['type'] == 'sphere':
        N = normalizar(M - obj['position'])
    elif obj['type'] == 'plane':
        N = obj['normal']
    return N
    
def get_color(obj, M):
    # Retorna a cor que vai ser definida pelo usuario, provavalmente usando RGB
    color = obj['color']
    if not hasattr(color, '__len__'):
        color = color(M)
    return color


def add_esfera(position, radius, color):
    # precisa retornar o dict da esfera
    # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
    return dict(type='sphere', position=np.array(position), 
        radius=np.array(radius), color=np.array(color), reflection=.5)
    
def add_plano(position, normal):
    # precisa retornar o dict do plano
    # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
    return dict(type='plane', position=np.array(position), 
        normal=np.array(normal),
        color=lambda M: (color_plane0 
            if (int(M[0] * 2) % 2) == (int(M[2] * 2) % 2) else color_plane1),
        diffuse_c=.75, specular_c=.5, reflection=.25)


def define_properties(ambient = 0.08, diffuse_c = 1.2, specular_c = 1.2, specular_k = 42):
    ambient = ambient
    diffuse_c = diffuse_c
    specular_c = specular_c
    specular_k = specular_k

    return ambient, diffuse_c, specular_c, specular_k


def define_scene():
    scene = [add_esfera([.0, .1, 1.], .2, [0., 0., 1.]),
         add_esfera([-.75, .5, 1.], .5, [.5, .223, .5]),
         add_esfera([0.75, 1.9, 1.], .5, [0.863, .863, .184]),
         add_esfera([1.5, .1, 1.], .1, [0.321, 0., .864]),
         add_esfera([.0, .1, 0.5], .4, [0., 0., 1.]),
         add_esfera([-1.5, 1.2, 0.5], .3, [1., .572, .184]),
         add_esfera([0.75, 1.6, 0.5], .5, [0.5, .863, .184]),
         add_esfera([0.75, .1, 1.5], .2, [0., 0., 1.]),
         add_esfera([1.5, .5, 1.5], .4, [.5, .223, .5]),
         add_esfera([-1.5, 1.1, 1.5], .5, [1., .572, .863]),
         add_esfera([-.75, .1, 1.5], .3, [0.863, 0., .864]),
         add_plano([0., -.5, 0.], [0., 1., 0.]),
    ]
    return scene


def initialize_loop(color = 0, reflection = 1., Q = None, O = None):
    D = normalizar(Q - O)
    return color, reflection, O, D  


def calc_reflection(M, N, rayD):
    return M + N * .0001, normalizar(rayD - 2 * np.dot(rayD, N) * N)

    
# Lista de objetos
scene = define_scene()

# Largura e Altura
w = 400
h = 400
img = np.zeros((h, w, 3))

r = float(w) / h
# Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
# Coordenadas da tela: x0, y0, x1, y1.
screen = (-1., -1. / r + .25, 1., 1. / r + .25)

# Posicao da luz e cor
L = np.array([5., 5., -10.])
color_light = np.ones(3)

# Definicao de propriedades
ambient, diffuse_c, specular_c, specular_k = define_properties(0.08, 1.2, 1.2, 42)

# Definicao de parametros de reflexao
depth_max = 5  # Nr max de reflexoes de luz

# Definicao de parametros de cor
col = np.zeros(3)  # Cor atual

# Definicao de parametros de camera
O = np.array([0., 0., -2.])  # Camera.
Q = np.array([0., 0., 0.])  # Posicionamento Camera

# cores do plano
color_plane0 = 1. * np.ones(3)
color_plane1 = 1. * np.ones(3)

# Loop por todos os pixels da imagem
for i, x in enumerate(np.linspace(screen[0], screen[2], w)):
    if i % 10 == 0:
        print ((i / float(w) * 100), "%")
    for j, y in enumerate(np.linspace(screen[1], screen[3], h)):
        # Baseado no código disponivel em https://gist.github.com/sklam/362c883eff73d297134c
        Q[:2] = (x, y)
        col[:], reflection, rayO, rayD = initialize_loop(0, 1., Q, O)
        depth = 0 # Profundidade inicial
        # Loop nos raios
        while depth < depth_max:
            traced = tracar_raio(rayO, rayD)
            if not traced:
                break
            obj, M, N, col_ray = traced
            # reflexao, que cria um novo raio
            rayO, rayD = calc_reflection(M, N, rayD)
            col += reflection * col_ray
            reflection *= obj.get('reflection', 1.)
        img[h - j - 1, i, :] = np.clip(col, 0, 1)

plt.imsave('raytracing0.png', img)