import pygame
import sys
import random
from collections import deque

largura, altura = 600, 600
linhas, colunas = 11, 11
tamanho = 40
margem = 5

fundo = (240, 240, 240)
livre = (200, 200, 200)
bloqueado = (50, 50, 50)
gato = (255, 150, 0)
borda = (255, 0, 0)
TEXTO = (20, 20, 20)

pygame.init()
FONTE = pygame.font.SysFont("arial", 32, bold=True)

def criaTabuleiro():
    tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
    gato = (linhas//2, colunas//2)
    tabuleiro[gato[0]][gato[1]] = 2

    numBloqueios = (linhas*colunas)//11
    bloqueados = 0
    while bloqueados < numBloqueios:
        i = random.randint(0, linhas-1)
        j = random.randint(0, colunas-1)
        if tabuleiro[i][j] == 0:
            tabuleiro[i][j] = 1
            bloqueados += 1

    return tabuleiro, gato

def movimentosValidos(pos, tab):
    i, j = pos
    moves = []
    if i%2 == 0:
        direcoes = [(-1,0), (0,-1), (1,0), (0,1)]
    else:
        direcoes = [(-1,0), (0,-1), (1,0), (0,1)]
    for di, dj in direcoes:
        ni, nj = i+di, j+dj
        if 0 <= ni < linhas and 0 <= nj < colunas and tab[ni][nj] == 0:
            moves.append((ni, nj))
    return moves

def gatoGanhou(pos):
    i, j = pos
    return i == 0 or i == linhas-1 or j == 0 or j == colunas-1

def jogadorGanhou(pos, tab):
    return len(movimentosValidos(pos, tab)) == 0

def menorDistanciaBorda(tab, start):
    visitado = set([start])
    fila = deque([(start, 0)])
    while fila:
        (i, j), dist = fila.popleft()
        if i == 0 or j == 0 or i == linhas-1 or j == colunas-1:
            return dist
        for ni, nj in movimentosValidos((i, j), tab):
            if (ni, nj) not in visitado:
                visitado.add((ni, nj))
                fila.append(((ni, nj), dist+1))
    return None  #sem caminho

def avaliar_estado(tab, pos):
    dist = menorDistanciaBorda(tab, pos)
    if dist is None:
        return 1000  #gato preso
    return -dist    #menor distância é melhor pro gato

def minimax(tab, pos, prof, maximizando):
    if gatoGanhou(pos):
        return 1000 if maximizando else -1000
    if jogadorGanhou(pos, tab):
        return -1000 if maximizando else 1000
    if prof == 0:
        return avaliar_estado(tab, pos)

    if maximizando: 
        melhor = -9999
        for mov in movimentosValidos(pos, tab):
            val = minimax(tab, mov, prof-1, False)
            melhor = max(melhor, val)
        return melhor
    else:
        melhor = 9999
        for i in range(linhas):
            for j in range(colunas):
                if tab[i][j] == 0:
                    tab[i][j] = 1
                    val = minimax(tab, pos, prof-1, True)
                    tab[i][j] = 0
                    melhor = min(melhor, val)
        return melhor

def melhorMovimento(tab, pos):
    melhor = -9999
    escolha = None
    for mov in movimentosValidos(pos, tab):
        val = minimax(tab, mov, 2, False) 
        if val > melhor:
            melhor = val
            escolha = mov
    return escolha

def desenhaTabuleiro(tela, tab, mensagem=None):
    tela.fill(fundo)
    for i in range(linhas):
        for j in range(colunas):
            x = j*(tamanho + margem) + (i%2)*(tamanho//2)
            y = i*(tamanho + margem)
            cor = livre
            if tab[i][j] == 1:
                cor = bloqueado
            elif tab[i][j] == 2:
                cor = gato
            pygame.draw.circle(tela, cor, (x+tamanho//2, y+tamanho//2), tamanho//2)
            if i == 0 or j == 0 or i == linhas-1 or j == colunas-1:
                pygame.draw.circle(tela, borda, (x+tamanho//2, y+tamanho//2), tamanho//2, 2)

    if mensagem:
        texto = FONTE.render(mensagem, True, TEXTO)
        tela.blit(texto, (largura//2 - texto.get_width()//2, altura-50))

def main():
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Prenda o gato")

    tabuleiro, gato = criaTabuleiro()
    turnoJogador = True
    fim = False
    mensagem = None

    clock = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:  #reiniciar
                    tabuleiro, gato = criaTabuleiro()
                    turnoJogador = True
                    fim = False
                    mensagem = None

            if evento.type == pygame.MOUSEBUTTONDOWN and turnoJogador and not fim:
                mx, my = pygame.mouse.get_pos()
                for i in range(linhas):
                    for j in range(colunas):
                        x = j*(tamanho + margem) + (i%2)*(tamanho//2)
                        y = i*(tamanho + margem)
                        rect = pygame.Rect(x, y, tamanho, tamanho)
                        if rect.collidepoint(mx, my) and tabuleiro[i][j] == 0:
                            tabuleiro[i][j] = 1
                            turnoJogador = False

        if not turnoJogador and not fim:
            mov = melhorMovimento(tabuleiro, gato)
            if mov:
                tabuleiro[gato[0]][gato[1]] = 0
                gato = mov
                tabuleiro[gato[0]][gato[1]] = 2

            if gatoGanhou(gato):
                mensagem = "O gato venceu! (R para reiniciar)"
                fim = True
            elif jogadorGanhou(gato, tabuleiro):
                mensagem = "Você venceu! (R para reiniciar)"
                fim = True
            else:
                turnoJogador = True

        desenhaTabuleiro(tela, tabuleiro, mensagem)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
