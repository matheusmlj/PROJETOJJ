from typing import List
import pygame
import time
import sys
import math

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 760

roadW = 4000
segL = 200
camD = 0.84

# Cores
dark_grass = pygame.Color(0, 154, 0)
light_grass = pygame.Color(16, 200, 16)
white_rumble = pygame.Color(255, 255, 255)
black_rumble = pygame.Color(0, 0, 0)
dark_road = pygame.Color(105, 105, 105)
light_road = pygame.Color(107, 107, 107)
light_orange = pygame.Color(255, 200, 100)
dark_orange = pygame.Color(255, 140, 0)

class Line:
    def __init__(self):
        self.x = self.y = self.z = 0.0
        self.X = self.Y = self.W = 0.0
        self.scale = 0.0

    def project(self, camX: int, camY: int, camZ: int):
        self.scale = camD / (self.z - camZ)
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * roadW * WINDOW_WIDTH / 2

def drawQuad(surface: pygame.Surface, color: pygame.Color, x1: int, y1: int, w1: int, x2: int, y2: int, w2: int):
    pygame.draw.polygon(surface, color, [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)])

class GameWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("MackRacing")
        self.window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0

        # Carregar a imagem de fundo
        try:
            self.background_image = pygame.image.load("FundoJogo.png").convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error as e:
            print(f"Erro ao carregar a imagem de fundo: {e}")
            sys.exit()

        # Carregar a imagem do motoqueiro
        self.motoqueiro_img = pygame.image.load("motoqueiro.png").convert_alpha()
        self.motoqueiro_img = pygame.transform.scale(self.motoqueiro_img, (200, 200))

        # Variáveis para inclinação do motoqueiro
        self.incline_angle = 0
        self.max_incline = 20  # Ângulo máximo de inclinação

        # Variável para o movimento de "pulinhos"
        self.time_elapsed = 0
        self.bounce_amplitude = 10  # Amplitude do movimento vertical
        self.bounce_frequency = 4   # Frequência dos "pulinhos"

    def draw_motoqueiro(self):
        """Desenha a imagem do motoqueiro com inclinação e efeito de 'pulinhos'."""
        # Calcular o movimento de pulinhos usando uma função senoidal
        bounce_offset = math.sin(self.time_elapsed * self.bounce_frequency) * self.bounce_amplitude

        # Rotacionar a imagem com base na inclinação
        rotated_img = pygame.transform.rotate(self.motoqueiro_img, self.incline_angle)
        motoqueiro_rect = rotated_img.get_rect()
        motoqueiro_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150 + bounce_offset)
        self.window_surface.blit(rotated_img, motoqueiro_rect)

    def run(self):
        lines: List[Line] = []
        for i in range(1600):
            line = Line()
            line.z = i * segL + 0.00001
            lines.append(line)

        N = len(lines)
        pos = 0
        playerX = 0

        self.dt = time.time() - self.last_time
        self.last_time = time.time()

        while True:
            # Desenhar o fundo antes de qualquer outra coisa
            self.window_surface.blit(self.background_image, (0, 0))

            for event in pygame.event.get([pygame.QUIT]):
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()

            # Avançar automaticamente para frente
            pos += 200
            if pos >= N * segL:
                pos %= N * segL

            # Movimento para os lados e inclinação
            if keys[pygame.K_RIGHT]:
                playerX += 200
                self.incline_angle = -self.max_incline
            elif keys[pygame.K_LEFT]:
                playerX -= 200
                self.incline_angle = self.max_incline
            else:
                self.incline_angle = 0

            while pos >= N * segL:
                pos -= N * segL
            while pos < 0:
                pos += N * segL

            max_playerX = roadW / 1.3
            min_playerX = -roadW / 1.3
            playerX = max(min_playerX, min(max_playerX, playerX))

            startPos = int(pos // segL) % N
            maxy = WINDOW_HEIGHT

            for n in range(startPos, startPos + 300):
                current = lines[n % N]
                current.project(playerX, 1500, pos - (N * segL if n >= N else 0))

                if current.Y >= maxy:
                    continue
                maxy = current.Y

                prev = lines[(n - 1) % N]

                grass_color = light_orange if (n // 3) % 2 else dark_orange
                rumble_color = white_rumble if (n // 3) % 2 else black_rumble
                road_color = light_road if (n // 3) % 2 else dark_road

                drawQuad(self.window_surface, grass_color, 0, prev.Y, WINDOW_WIDTH, 0, current.Y, WINDOW_WIDTH)
                drawQuad(self.window_surface, rumble_color, prev.X, prev.Y, prev.W * 1.2, current.X, current.Y, current.W * 1.2)
                drawQuad(self.window_surface, road_color, prev.X, prev.Y, prev.W, current.X, current.Y, current.W)

            self.time_elapsed += self.dt

            # Desenhar o motoqueiro
            self.draw_motoqueiro()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = GameWindow()
    game.run()
