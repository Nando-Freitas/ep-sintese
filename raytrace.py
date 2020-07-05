# Numpy para fazer as contas
import numpy as np
# matplotlib para salvar a imagem ou plottar
import matplotlib.pyplot as plt

# A ideia eh fazer um raytracing bem simples, em python single thread mesmo usando esferas e um plano

def intersecao_plano(O, D, P, N):
    # Retorna a distancia do Objeto O a intersecao do raio (Objeto, Direcao) com o Plano (Plano, Normal), ou +infinito se nao ha intersecao
    # Objeto e Plano sao pontos 3D, Direcao e Normal sao vetores normalizados
    denom = np.dot(D, N)
    if np.abs(denom) < 1e-6:
        return np.inf
    d = np.dot(P - O, N) / denom
    if d < 0:
        return np.inf
    return d

def intersecao_esfera(O, D, S, R):
    # Bem parecido com o do plano, mas para esfera é um pouco mais simples porque da pra saber se há intersecao baseado no raio
    # Retorna a distancia do Objeto O ate a intersecao do raio (Objeto, Direcao) com a esfera (Esfera S, Raio), ou mais infinito se nao ha intersecao
    # Objeto e Esfera S sao pontos 3D, Direcao eh um vetor normalizado, Raio R é um escalar
    # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection
    # a = raio * raio
    # Precisa usar o dot porque sao vetores
    a = np.dot(D, D)
    # Diferenca do objeto - esfera
    OS = O - S
    # b = raio * diferenca 
    b = 2 * np.dot(D, OS)
    # c = diferenca * diferenca - raio * raio
    c = np.dot(OS, OS) - R * R
    # Calcula o discriminante (La do Bhaskara)
    disc = b * b - 4 * a * c
    if disc > 0:
        distSqrt = np.sqrt(disc)
        q = (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0
        t0 = q / a
        t1 = c / q
        t0, t1 = min(t0, t1), max(t0, t1)
        if t1 >= 0:
            return t1 if t0 < 0 else t0
    return np.inf

def intersecao(O, D, obj):
    # Precisa definir se a intersecao eh com plano ou com esfera
    if obj['type'] == 'plane':
        return intersecao_plano(O, D, obj['position'], obj['normal'])
    elif obj['type'] == 'sphere':
        return intersecao_esfera(O, D, obj['position'], obj['radius'])

def normalizar(x):
    x /= np.linalg.norm(x)
    return x

def get_normal(obj, M):
    # Precisa calcular a normal que varia de acordo com esfera ou plano
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

def tracar_raio(rayO, rayD):
    # Encontra o primeiro ponto de interesao com a cena
    t = np.inf
    for i, obj in enumerate(scene):
        t_obj = intersecao(rayO, rayD, obj)
        if t_obj < t:
            t, obj_idx = t_obj, i
    # Retorna None se o raio nao intercepta nenhum objeto
    if t == np.inf:
        return
    # Encontra o objeto
    obj = scene[obj_idx]
    # Encontra o ponto de intersecao com o objeto
    M = rayO + rayD * t
    # Encontra as propriedades do objeto
    N = get_normal(obj, M)
    color = get_color(obj, M)
    toL = normalizar(L - M)
    toO = normalizar(O - M)
    # Define se o objeto tem ou nao sombra
    l = [intersecao(M + N * .0001, toL, obj_sh) 
            for k, obj_sh in enumerate(scene) if k != obj_idx]
    if l and min(l) < np.inf:
        return
    # Entao precisa computar cor, 
    col_ray = ambient
    # shading (difusao de Lambert) e 
    col_ray += obj.get('diffuse_c', diffuse_c) * max(np.dot(N, toL), 0) * color
    # a parte especular com Phong
    col_ray += obj.get('specular_c', specular_c) * max(np.dot(N, normalizar(toL + toO)), 0) ** specular_k * color_light
    return obj, M, N, col_ray

def add_esfera(position, radius, color):
    # precisa retornar o dict da esfera
    return dict(type='sphere', position=np.array(position), 
        radius=np.array(radius), color=np.array(color), reflection=.5)
    
def add_plano(position, normal):
    # precisa retornar o dict do plano
    return dict(type='plane', position=np.array(position), 
        normal=np.array(normal),
        color=lambda M: (color_plane0 
            if (int(M[0] * 2) % 2) == (int(M[2] * 2) % 2) else color_plane1),
        diffuse_c=.75, specular_c=.5, reflection=.25)
    
# Lista de objetos
color_plane0 = 1. * np.ones(3)
color_plane1 = 1. * np.ones(3)
scene = [add_esfera([.0, .1, 1.], .2, [0., 0., 1.]),
         add_esfera([-.75, .5, 1.], .5, [.5, .223, .5]),
         add_esfera([-1.5, 1.1, 1.], .2, [1., .572, .184]),
         add_esfera([0.75, 1.9, 1.], .5, [0.5, .863, .184]),
         add_esfera([1.5, .1, 1.], .1, [0.321, 0., .864]),
         add_esfera([.0, .1, 0.5], .4, [0., 0., 1.]),
         add_esfera([-.75, .7, 0.5], .2, [.5, .223, .5]),
         add_esfera([-1.5, 1.2, 0.5], .3, [1., .572, .184]),
         add_esfera([0.75, 1.6, 0.5], .5, [0.5, .863, .184]),
         add_esfera([1.5, .15, 0.5], .1, [0.321, 0., .864]),
         add_esfera([0.75, .1, 1.5], .2, [0., 0., 1.]),
         add_esfera([1.5, .5, 1.5], .4, [.5, .223, .5]),
         add_esfera([-1.5, 1.1, 1.5], .5, [1., .572, .184]),
         add_esfera([0., 1.9, 1.5], .2, [0.5, .863, .184]),
         add_esfera([-.75, .1, 1.5], .3, [0.321, 0., .864]),
         add_plano([0., -.5, 0.], [0., 1., 0.]),
    ]

# Largura e Altura
w = 400
h = 400

# Posicao da luz e cor
L = np.array([5., 5., -10.])
color_light = np.ones(3)

# Definicao de propriedades
ambient = .05
diffuse_c = 1.
specular_c = 1.
specular_k = 50

depth_max = 5  # Nr max de reflexoes de luz
col = np.zeros(3)  # Cor atual
O = np.array([0., 0.35, -1.])  # Camera.
Q = np.array([0., 0., 0.])  # Posicionamento Camera
img = np.zeros((h, w, 3))

r = float(w) / h
# Coordenadas da tela: x0, y0, x1, y1.
S = (-1., -1. / r + .25, 1., 1. / r + .25)

# Loop por todos os pixels da imagem
for i, x in enumerate(np.linspace(S[0], S[2], w)):
    if i % 10 == 0:
        print ((i / float(w) * 100), "%")
    for j, y in enumerate(np.linspace(S[1], S[3], h)):
        col[:] = 0
        Q[:2] = (x, y)
        D = normalizar(Q - O)
        depth = 0
        rayO, rayD = O, D
        reflection = 1.
        # Loop nos raios
        while depth < depth_max:
            traced = tracar_raio(rayO, rayD)
            if not traced:
                break
            obj, M, N, col_ray = traced
            # reflexao, que cria um novo raio
            rayO, rayD = M + N * .0001, normalizar(rayD - 2 * np.dot(rayD, N) * N)
            depth += 1
            col += reflection * col_ray
            reflection *= obj.get('reflection', 1.)
        img[h - j - 1, i, :] = np.clip(col, 0, 1)

plt.imsave('raytracing4.png', img)