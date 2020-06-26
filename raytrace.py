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


def tracar_raio(rayO, rayD):
  # Encontra o primeiro ponto de interesao com a cena
  # Retorna None se o raio nao intercepta nenhum objeto
  # Encontra o objeto
  # Encontra o ponto de intersecao com o objeto
  # Encontra as propriedades do objeto
  # Define se o objeto tem ou nao sombra
  # Entao precisa computar cor, shading (difusao) e a parte especular com Phong, provavelmente.