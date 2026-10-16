
import json
import math
import random
import sys
from pathlib import Path

import pygame
from pygame.math import Vector2


LARGURA, ALTURA = 800, 600
FPS = 60
ARQ_RECORDE = Path(__file__).resolve().parent / "recorde.json"  # caminho relativo ao projeto

MENU, JOGANDO, PAUSADO, FIM = "menu", "jogando", "pausado", "fim"

BRANCO = (240, 240, 250)
AMARELO = (255, 220, 90)
CIANO = (90, 210, 255)


def colidem(pos_a, raio_a, pos_b, raio_b):
    
    return (pos_a - pos_b).length_squared() < (raio_a + raio_b) ** 2



class CampoEstrelas:
    
    CAMADAS = [(25, 1, 80, 0.05), (60, 1, 140, 0.10), (120, 2, 220, 0.20)]

    def __init__(self):
        self.estrelas = [
            [random.uniform(0, LARGURA), random.uniform(0, ALTURA), c]
            for c in range(len(self.CAMADAS)) for _ in range(40)
        ]

    def atualizar(self, dt, vel_x=0.0, impulso=1.0):
        for e in self.estrelas:
            vel_y, _, _, fator = self.CAMADAS[e[2]]
            e[1] += vel_y * impulso * dt
            e[0] = (e[0] - vel_x * fator * dt) % LARGURA
            if e[1] > ALTURA:                     
                e[1] = 0
                e[0] = random.uniform(0, LARGURA)

    def desenhar(self, superficie):
        for x, y, c in self.estrelas:
            _, tam, brilho, _ = self.CAMADAS[c]
            cor = (brilho, brilho, min(255, brilho + 30))
            pygame.draw.circle(superficie, cor, (int(x), int(y)), tam)


class Particulas:
   
    def __init__(self):
        self.lista = []  

    def emitir(self, pos, quantidade, cor, vel_max=200, vida=0.8, tamanho=3):
        for _ in range(quantidade):
          
            vel = Vector2(random.uniform(20, vel_max), 0).rotate(random.uniform(0, 360))
            v = vida * random.uniform(0.5, 1.0)
            self.lista.append([Vector2(pos), vel, v, v, cor, tamanho])

    def atualizar(self, dt):
        for p in self.lista:
            p[2] -= dt
            p[0] += p[1] * dt
            p[1] *= max(0.0, 1 - 1.5 * dt)        
        self.lista = [p for p in self.lista if p[2] > 0]

    def desenhar(self, superficie):
        for pos, _, vida, total, cor, tam in self.lista:
            f = vida / total                        
            cor_f = tuple(int(c * f) for c in cor)
            pygame.draw.circle(superficie, cor_f, (int(pos.x), int(pos.y)), max(1, int(tam * f + 0.5)))



class Tiro:
    raio = 4

    def __init__(self, pos, vel):
        self.pos, self.vel, self.viva = Vector2(pos), Vector2(vel), True

    def atualizar(self, dt):
        self.pos += self.vel * dt
        if self.pos.y < -20 or not -20 < self.pos.x < LARGURA + 20:
            self.viva = False

    def desenhar(self, s):
        pygame.draw.line(s, AMARELO, self.pos, self.pos + Vector2(0, 14), 3)
        pygame.draw.circle(s, (255, 255, 210), self.pos, 3)


class Asteroide:

    def __init__(self, pos, raio, vel):
        self.pos, self.raio, self.vel = Vector2(pos), raio, Vector2(vel)
        self.vida = 1 if raio < 20 else 2 if raio < 34 else 3   
        self.angulo = random.uniform(0, 360)
        self.giro = random.uniform(-90, 90)                      
        self.base = self._gerar_sprite()
        self.viva = True

    def _gerar_sprite(self):
        tam = self.raio * 2 + 6
        s = pygame.Surface((tam, tam), pygame.SRCALPHA)
        c = tam / 2
        n = random.randint(9, 12)
        pontos = []
        for i in range(n):
            a = 2 * math.pi * i / n
            r = self.raio * random.uniform(0.75, 1.05)
            pontos.append((c + r * math.cos(a), c + r * math.sin(a)))
        pygame.draw.polygon(s, (115, 100, 92), pontos)
        pygame.draw.polygon(s, (190, 175, 160), pontos, 2)
        for _ in range(3):
            cp = Vector2(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)) * self.raio
            pygame.draw.circle(s, (85, 72, 66), (c + cp.x, c + cp.y), max(2, self.raio // 6))
        return s

    def atualizar(self, dt):
        self.pos += self.vel * dt
        self.angulo += self.giro * dt
       
        if self.pos.x < self.raio or self.pos.x > LARGURA - self.raio:
            self.vel.x *= -1
            self.pos.x = max(self.raio, min(LARGURA - self.raio, self.pos.x))
        if self.pos.y > ALTURA + self.raio + 10:
            self.viva = False

    def desenhar(self, s):
        # TRANSFORMAÇÃO: rotaciona o sprite base e o centraliza na posição
        img = pygame.transform.rotate(self.base, self.angulo)
        s.blit(img, img.get_rect(center=self.pos))


class PowerUp:
    raio = 13
    TIPOS = {"escudo": ((80, 160, 255), "E"), "triplo": ((255, 190, 60), "T")}

    def __init__(self, pos, tipo):
        self.pos, self.tipo, self.t, self.viva = Vector2(pos), tipo, 0.0, True

    def atualizar(self, dt):
        self.t += dt
        self.pos.y += 90 * dt
        if self.pos.y > ALTURA + 20:
            self.viva = False

    def desenhar(self, s, fonte):
        cor, letra = self.TIPOS[self.tipo]
        pulso = 3 * math.sin(self.t * 6)          
        pygame.draw.circle(s, tuple(c // 3 for c in cor), self.pos, self.raio + 5 + pulso)
        pygame.draw.circle(s, cor, self.pos, self.raio + pulso * 0.5)
        txt = fonte.render(letra, True, (10, 10, 30))
        s.blit(txt, txt.get_rect(center=self.pos))


def criar_frames_nave():
    frames = []
    for chama in (6, 13, 20):
        s = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.polygon(s, (255, 150, 40), [(14, 38), (26, 38), (20, 38 + chama)])
        pygame.draw.polygon(s, (255, 240, 130), [(17, 38), (23, 38), (20, 38 + chama * 0.6)])
        pygame.draw.polygon(s, (80, 200, 255), [(20, 2), (35, 38), (20, 31), (5, 38)])
        pygame.draw.polygon(s, (30, 95, 165), [(20, 2), (20, 31), (5, 38)])
        pygame.draw.circle(s, (230, 250, 255), (20, 21), 4)
        frames.append(s)
    return frames


class Jogador:
    VELOCIDADE = 300
    RAIO = 13  
    def __init__(self):
        self.frames = criar_frames_nave()
        self.reiniciar()

    def reiniciar(self):
        self.pos = Vector2(LARGURA / 2, ALTURA - 80)
        self.vidas, self.recarga, self.invul = 3, 0.0, 0.0
        self.escudo, self.triplo = 0.0, 0.0      
        self.vel_x, self.inclinacao, self.tempo = 0.0, 0.0, 0.0

    def atualizar(self, dt, teclas):
        # Direção a partir das teclas (setas ou WASD): True/False vira 1/0
        dx = (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a])
        dy = (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - (teclas[pygame.K_UP] or teclas[pygame.K_w])
        direcao = Vector2(dx, dy)
        if direcao.length_squared() > 0:
            direcao = direcao.normalize()         
        self.pos += direcao * self.VELOCIDADE * dt
      
        self.pos.x = max(22, min(LARGURA - 22, self.pos.x))
        self.pos.y = max(ALTURA * 0.45, min(ALTURA - 35, self.pos.y))
        self.vel_x = direcao.x * self.VELOCIDADE
       
        alvo = -direcao.x * 14
        self.inclinacao += (alvo - self.inclinacao) * min(1, 10 * dt)
        self.tempo += dt
        self.recarga = max(0, self.recarga - dt)
        self.invul = max(0, self.invul - dt)
        self.escudo = max(0, self.escudo - dt)
        self.triplo = max(0, self.triplo - dt)

    def atirar(self):
        if self.recarga > 0:
            return []
        self.recarga = 0.22
        angulos = (-12, 0, 12) if self.triplo > 0 else (0,)
        return [Tiro(self.pos + Vector2(0, -26), Vector2(0, -620).rotate(a)) for a in angulos]

    def desenhar(self, s):
        if self.invul > 0 and int(self.invul * 10) % 2:  
            return
        quadro = self.frames[int(self.tempo * 15) % len(self.frames)]
        img = pygame.transform.rotate(quadro, self.inclinacao)  
        s.blit(img, img.get_rect(center=self.pos))
        if self.escudo > 0:
            r = 28 + 2 * math.sin(self.tempo * 8)
            pygame.draw.circle(s, (80, 160, 255), self.pos, r, 2)


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Chuva de Meteoros")
        self.relogio = pygame.time.Clock()
       
        self.cena = pygame.Surface((LARGURA, ALTURA))
        self.f_titulo = pygame.font.Font(None, 84)
        self.f_media = pygame.font.Font(None, 34)
        self.f_peq = pygame.font.Font(None, 24)
        self.veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.veu.fill((0, 0, 0, 160))
        self.estrelas, self.particulas = CampoEstrelas(), Particulas()
        self.jogador = Jogador()
        self.icone_vida = pygame.transform.smoothscale(self.jogador.frames[0], (20, 30))  # escala
        self.recorde = self.carregar_recorde()
        self.estado = MENU
        self.limpar_partida()

   
    def carregar_recorde(self):
        try:
            return int(json.loads(ARQ_RECORDE.read_text())["recorde"])
        except (OSError, ValueError, KeyError):
            return 0

    def salvar_recorde(self):
        try:
            ARQ_RECORDE.write_text(json.dumps({"recorde": self.recorde}))
        except OSError:
            pass  

   
    def limpar_partida(self):
        self.asteroides, self.tiros, self.powerups = [], [], []
        self.pontos, self.nivel, self.tempo_spawn = 0, 1, 1.0
        self.tremor, self.aviso, self.novo_recorde = 0.0, 0.0, False
        self.jogador.reiniciar()

    def novo_jogo(self):
        self.limpar_partida()
        self.estado = JOGANDO
        self.aviso = 2.0

    def voltar_menu(self):
        self.limpar_partida()
        self.estado = MENU

    def sair(self):
        pygame.quit()
        sys.exit()

  
    def executar(self):
        while True:
          
            dt = min(self.relogio.tick(FPS) / 1000, 0.05)
            self.tratar_eventos()     
            self.atualizar(dt)        
            self.desenhar()          

    def tratar_eventos(self):
        K = pygame
        for e in pygame.event.get():
            if e.type == K.QUIT:
                self.sair()
            if e.type != K.KEYDOWN:
                continue
            if self.estado == MENU:
                if e.key in (K.K_RETURN, K.K_SPACE):
                    self.novo_jogo()
                elif e.key == K.K_ESCAPE:
                    self.sair()
            elif self.estado == JOGANDO:
                if e.key in (K.K_p, K.K_ESCAPE):
                    self.estado = PAUSADO
            elif self.estado == PAUSADO:
                if e.key in (K.K_p, K.K_ESCAPE):
                    self.estado = JOGANDO
                elif e.key == K.K_r:
                    self.novo_jogo()
                elif e.key == K.K_m:
                    self.voltar_menu()
            elif self.estado == FIM:
                if e.key == K.K_RETURN:
                    self.novo_jogo()
                elif e.key == K.K_ESCAPE:
                    self.voltar_menu()

    
    def atualizar(self, dt):
        if self.estado == PAUSADO:
            return
        vel_x = self.jogador.vel_x if self.estado == JOGANDO else 0
        self.estrelas.atualizar(dt, vel_x, 1 + 0.15 * (self.nivel - 1))
        self.particulas.atualizar(dt)
        self.tremor = max(0, self.tremor - 2 * dt)
        self.aviso = max(0, self.aviso - dt)
        if self.estado == JOGANDO:
            self.atualizar_partida(dt)

    def atualizar_partida(self, dt):
        j = self.jogador
        teclas = pygame.key.get_pressed()
        j.atualizar(dt, teclas)
        if teclas[pygame.K_SPACE]:
            self.tiros += j.atirar()
       
        if random.random() < 0.6:
            self.particulas.emitir(j.pos + Vector2(0, 30), 1, (255, 150, 50), 60, 0.35, 3)

        
        novo_nivel = 1 + self.pontos // 500
        if novo_nivel > self.nivel:
            self.nivel, self.aviso = novo_nivel, 2.0
        self.tempo_spawn -= dt
        if self.tempo_spawn <= 0:
            self.criar_asteroide()
            self.tempo_spawn = max(0.25, 1.2 - 0.1 * (self.nivel - 1)) * random.uniform(0.7, 1.3)

        for lista in (self.tiros, self.asteroides, self.powerups):
            for obj in lista:
                obj.atualizar(dt)

        self.tratar_colisoes()

        self.tiros = [t for t in self.tiros if t.viva]
        self.asteroides = [a for a in self.asteroides if a.viva]
        self.powerups = [p for p in self.powerups if p.viva]

    def criar_asteroide(self):
        raio = random.choice([14, 22, 22, 30, 40])
        vel = Vector2(random.uniform(-40, 40), random.uniform(90, 150) + 12 * self.nivel)
        self.asteroides.append(Asteroide((random.uniform(raio, LARGURA - raio), -raio), raio, vel))

    
    def tratar_colisoes(self):
        j = self.jogador
        novos = []

        
        for tiro in self.tiros:
            for ast in self.asteroides:
                if ast.viva and colidem(tiro.pos, tiro.raio, ast.pos, ast.raio):
                    tiro.viva = False
                    ast.vida -= 1
                    self.particulas.emitir(tiro.pos, 6, (255, 220, 150), 120, 0.3, 2)
                    if ast.vida <= 0:
                        novos += self.destruir(ast, dar_pontos=True)
                    break

       
        if j.invul <= 0:
            for ast in self.asteroides:
                if ast.viva and colidem(j.pos, j.RAIO, ast.pos, ast.raio):
                    novos += self.destruir(ast, dar_pontos=False)
                    if j.escudo > 0:
                        j.escudo, j.invul = 0, 0.6      # escudo absorve o golpe
                    else:
                        j.vidas -= 1
                        j.invul, self.tremor = 2.0, 0.5
                        self.particulas.emitir(j.pos, 30, (255, 120, 80), 260, 0.9, 4)
                        if j.vidas <= 0:
                            self.fim_de_jogo()
                    break

       
        for p in self.powerups:
            if colidem(j.pos, j.RAIO, p.pos, p.raio):
                p.viva = False
                if p.tipo == "escudo":
                    j.escudo = 8.0
                else:
                    j.triplo = 8.0
                self.particulas.emitir(p.pos, 20, PowerUp.TIPOS[p.tipo][0], 180, 0.6, 3)

        self.asteroides += novos

    def destruir(self, ast, dar_pontos):
        """Destrói o asteroide; os grandes se dividem em dois menores."""
        ast.viva = False
        if dar_pontos:
            self.pontos += int(ast.raio) * 2
        self.particulas.emitir(ast.pos, int(ast.raio) + 8, (255, 170, 90), 220, 0.8, 3)
        self.tremor = max(self.tremor, ast.raio / 120)
        filhos = []
        if ast.raio >= 28:
            for lado in (-1, 1):
                v = Vector2(lado * random.uniform(50, 100), random.uniform(60, 120))
                filhos.append(Asteroide(ast.pos + Vector2(lado * 12, 0), int(ast.raio * 0.6), v))
        if dar_pontos and random.random() < 0.12:
            self.powerups.append(PowerUp(ast.pos, random.choice(list(PowerUp.TIPOS))))
        return filhos

    def fim_de_jogo(self):
        self.estado = FIM
        self.tremor = 1.0
        self.particulas.emitir(self.jogador.pos, 90, (255, 200, 120), 340, 1.2, 4)
        if self.pontos > self.recorde:
            self.recorde, self.novo_recorde = self.pontos, True
            self.salvar_recorde()

  
    def texto(self, txt, fonte, cor, centro=None, topo_esq=None, topo_dir=None):
        """Desenha texto com sombra para melhorar a legibilidade."""
        sombra = fonte.render(txt, True, (0, 0, 0))
        img = fonte.render(txt, True, cor)
        pos = {}
        if centro:
            pos["center"] = centro
        if topo_esq:
            pos["topleft"] = topo_esq
        if topo_dir:
            pos["topright"] = topo_dir
        r = img.get_rect(**pos)
        self.tela.blit(sombra, r.move(2, 2))
        self.tela.blit(img, r)

    def desenhar(self):
       
        c = self.cena
        c.fill((8, 8, 22))
        self.estrelas.desenhar(c)
        if self.estado != MENU:
            for p in self.powerups:
                p.desenhar(c, self.f_peq)
            for a in self.asteroides:
                a.desenhar(c)
            for t in self.tiros:
                t.desenhar(c)
            if self.estado != FIM:
                self.jogador.desenhar(c)
        self.particulas.desenhar(c)

       
        m = int(self.tremor * 14)
        desloc = (random.randint(-m, m), random.randint(-m, m)) if m else (0, 0)
        self.tela.fill((0, 0, 0))
        self.tela.blit(c, desloc)

        
        if self.estado == MENU:
            self.desenhar_menu()
        else:
            self.desenhar_hud()
            if self.estado == PAUSADO:
                self.desenhar_pausa()
            elif self.estado == FIM:
                self.desenhar_fim()
        pygame.display.flip()

    def desenhar_hud(self):
        j = self.jogador
        self.texto(f"PONTOS {self.pontos}", self.f_media, BRANCO, topo_esq=(16, 12))
        self.texto(f"RECORDE {self.recorde}", self.f_peq, (170, 170, 200), topo_esq=(16, 42))
        self.texto(f"NÍVEL {self.nivel}", self.f_media, CIANO, centro=(LARGURA // 2, 26))
        for i in range(j.vidas):
            self.tela.blit(self.icone_vida, (LARGURA - 34 - i * 26, 12))
       
        y = ALTURA - 22
        for nome, restante, cor in (("ESCUDO", j.escudo, (80, 160, 255)), ("TIRO TRIPLO", j.triplo, (255, 190, 60))):
            if restante > 0:
                self.texto(nome, self.f_peq, cor, topo_esq=(16, y - 4))
                pygame.draw.rect(self.tela, cor, (130, y, int(restante / 8 * 120), 10))
                y -= 22
        if self.aviso > 0 and self.estado == JOGANDO:
            self.texto(f"NÍVEL {self.nivel}", self.f_titulo, AMARELO, centro=(LARGURA // 2, 150))

    def desenhar_menu(self):
        self.texto("CHUVA DE METEOROS", self.f_titulo, AMARELO, centro=(LARGURA // 2, 130))
        self.texto("Sobreviva, destrua os asteroides e suba de nível!", self.f_media, BRANCO, centro=(LARGURA // 2, 210))
        linhas = ["SETAS ou WASD ... mover a nave", "ESPAÇO ........... atirar (segure)",
                  "P ou ESC ........ pausar", "E = escudo   |   T = tiro triplo"]
        for i, l in enumerate(linhas):
            self.texto(l, self.f_media, CIANO, centro=(LARGURA // 2, 290 + i * 34))
        if int(pygame.time.get_ticks() / 500) % 2:
            self.texto("ENTER para jogar  -  ESC para sair", self.f_media, BRANCO, centro=(LARGURA // 2, 480))
        self.texto(f"Recorde: {self.recorde}", self.f_media, (170, 170, 200), centro=(LARGURA // 2, 540))

    def desenhar_pausa(self):
        self.tela.blit(self.veu, (0, 0))
        self.texto("PAUSADO", self.f_titulo, AMARELO, centro=(LARGURA // 2, 220))
        self.texto("P ou ESC: continuar", self.f_media, BRANCO, centro=(LARGURA // 2, 310))
        self.texto("R: reiniciar    M: menu", self.f_media, BRANCO, centro=(LARGURA // 2, 350))

    def desenhar_fim(self):
        self.tela.blit(self.veu, (0, 0))
        self.texto("FIM DE JOGO", self.f_titulo, (255, 110, 100), centro=(LARGURA // 2, 200))
        self.texto(f"Pontos: {self.pontos}   Nível: {self.nivel}", self.f_media, BRANCO, centro=(LARGURA // 2, 280))
        if self.novo_recorde:
            self.texto("NOVO RECORDE!", self.f_media, AMARELO, centro=(LARGURA // 2, 320))
        self.texto("ENTER: jogar de novo    ESC: menu", self.f_media, BRANCO, centro=(LARGURA // 2, 390))


if __name__ == "__main__":
    Jogo().executar()