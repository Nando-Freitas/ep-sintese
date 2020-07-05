# Numpy para fazer as contas
import numpy as np
# matplotlib para salvar a imagem ou plottar
import matplotlib.pyplot as plt

# A ideia eh fazer um raytracing bem simples, em python single thread mesmo usando esferas e um plano


def intersecao_plano(O, D, P, N):
    # Retorna a distancia do Objeto O a intersecao do raio (Objeto, Direcao) com o Plano (Plano, Normal), ou +infinito se nao ha intersecao
    # Objeto e Plano sao pontos 3D, Direcao e Normal sao vetores normalizados
    denominador = np.dot(D, N)
    if np.abs(denominador) < 1e-6:
        return np.inf
    distancia = np.dot(P - O, N) / denominador
    if distancia < 0:
        return np.inf
    return distancia


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
    discriminante = b * b - 4 * a * c
    if discriminante > 0:
        raizdiscriminante = np.sqrt(discriminante)
        if b < 0:
            q = (-b - raizdiscriminante) / 2
        else:
            q = (-b + raizdiscriminante) / 2
        t0 = q / a
        t1 = c / a
        t0 = min(t0, t1)
        t1 = max(t0, t1)
        if t1 >= 0:
            if t0 < 0:
                return t1
            else:
                return t0
    return np.inf

def intersecao(O, D, obj):
    # Precisa definir se a intersecao eh com plano ou com esfera
    if obj['type'] == 'plano':
        return intersecao_plano(O, D, obj['posicao'], obj['normal'])
    if obj['type'] == 'esfera':
        return intersecao_plano(O, D, obj['posicao'], obj['raio'])

def normalizar(x) :
    x /= np.linalg.norm(x)
    return x


def get_normal(obj, ponto_intersec):
    # Precisa calcular a normal que varia de acordo com esfera ou plano
    if obj['type'] == 'esfera':
        N = normalizar(ponto_intersec - obj['posicao'])
    elif obj['type'] == 'plano':
        N = obj['normal']
    return N
    

def get_color(obj, ponto_intersec):
    # Retorna a cor que vai ser definida pelo usuario, provavalmente usando RGB
    color = obj['color']
    if not hasattr(color, '__len__'):
        color = color(ponto_intersec)
    return color


def tracar_raio(raioO, raioD):
  # Encontra o primeiro ponto de interesao com a cena
  inter = np.inf
  for i, obj in enumerate(cena):
      inter_obj = intersecao(raioO, raioD, obj)
      if inter_obj < inter:
          inter, indice_obj = inter_obj, i
  # Retorna None se o raio nao intercepta nenhum objeto
  if inter == np.inf:
      return
  # Encontra o objeto
  obj = cena[indice_obj]
  # Encontra o ponto de intersecao com o objeto
  ponto_interseccao = raioO + raioD * inter
  # Encontra as propriedades do objeto
  N = get_normal(obj, ponto_interseccao)
  color = get_color(obj, ponto_interseccao)
  paraL = normalizar(L - ponto_interseccao)
  paraO = normalizar(O - ponto_interseccao)
  # Define se o objeto tem ou nao sombra
  sombra = [intersecao(ponto_interseccao + N * 0.0001, paraL, sombra_objeto) 
        for k, sombra_objeto in enumerate(cena) if k != indice_obj]
  if sombra and min(sombra) < np.inf:
      return 

  # Entao precisa computar cor, 
  cor_raio = ambiente
  # shading (difusao) e a parte especular com Phong, provavelmente.
  cor_raio = obj.get('especular_c', especular_c) * max(np.dot(N, normalizar(paraL + paraO)), 0) ** especular_k * cor_luz
  return obj, ponto_interseccao, N, cor_raio  


def add_esfera(posicao, raio, cor):
    # precisa retornar o dict da esfera
    return dict(type='esfera', position=np.array(posicao), 
        radius=np.array(raio), color=np.array(cor), reflection=.5)

def add_plane(posicao, normal):
    # precisa retornar o dict do plano


