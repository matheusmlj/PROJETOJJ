from typing import List
import pygame
import time
import sys
import math
import random

# Dimensões da janela
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 760

# Parâmetros do jogo
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

        self.spriteX = 0.0
        self.clip = 0.0
        self.sprite: pygame.Surface = None

    def project(self, camX: int, camY: int, camZ: int):
        self.scale = camD / (self.z - camZ)
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * roadW * WINDOW_WIDTH / 2

    def drawSprite(self, draw_surface: pygame.Surface):
        if self.sprite is None:
            return

        destX = self.X + self.scale * self.spriteX * WINDOW_WIDTH / 2
        destY = self.Y
        destW = max(1, min(self.sprite.get_width() * self.W / 266, WINDOW_WIDTH))
        destH = max(1, min(self.sprite.get_height() * self.W / 266, WINDOW_HEIGHT))

        if not isinstance(destW, (int, float)) or not isinstance(destH, (int, float)):
            print(f"Erro: destW ou destH não são numéricos: destW={destW}, destH={destH}")
            return

        destX -= destW / 2
        destY -= destH / 1.5

        if destY < WINDOW_HEIGHT:
            try:
                scaled_sprite = pygame.transform.scale(self.sprite, (int(destW), int(destH)))
                draw_surface.blit(scaled_sprite, (int(destX), int(destY)))

                # Desenhar a hitbox do carro (cor azul)
                hitbox_rect = pygame.Rect(int(destX), int(destY), int(destW), int(destH))
                pygame.draw.rect(draw_surface, (0, 0, 255), hitbox_rect, 2)
            except pygame.error as e:
                print(f"Erro ao redimensionar o sprite: {e}")

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

        try:
            self.background_image = pygame.image.load("FundoJogo.png").convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.motoqueiro_img = pygame.image.load("motoqueiro.png").convert_alpha()
            self.motoqueiro_img = pygame.transform.scale(self.motoqueiro_img, (200, 200))
            self.sprite_5 = pygame.image.load("carro.png").convert_alpha()
            
            # Redimensionar a imagem do carro para um terço do tamanho original
            car_width, car_height = self.sprite_5.get_size()
            self.sprite_5 = pygame.transform.scale(self.sprite_5, (car_width // 3, car_height // 3))
        except pygame.error as e:
            print(f"Erro ao carregar imagens: {e}")
            sys.exit()

        self.incline_angle = 0
        self.max_incline = 20
        self.time_elapsed = 0
        self.bounce_amplitude = 10
        self.bounce_frequency = 4

    def draw_motoqueiro(self):
        bounce_offset = math.sin(self.time_elapsed * self.bounce_frequency) * self.bounce_amplitude
        rotated_img = pygame.transform.rotate(self.motoqueiro_img, self.incline_angle)
        motoqueiro_rect = rotated_img.get_rect()
        motoqueiro_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150 + bounce_offset)
        
        # Desenhar o motoqueiro na tela
        self.window_surface.blit(rotated_img, motoqueiro_rect)
        
        # Desenhar a hitbox do motoqueiro (cor vermelha)
        pygame.draw.rect(self.window_surface, (255, 0, 0), motoqueiro_rect, 2)

    def run(self):
        lines: List[Line] = []
        for i in range(1600):
            line = Line()
            line.z = i * segL + 0.00001

            # Randomizar a aparição do carro
            if random.randint(1, 200) == 1:
                line.sprite = self.sprite_5
                line.spriteX = random.choice([-3000, 0, 3000])

            lines.append(line)

        N = len(lines)
        pos = 0
        playerX = 0

        self.dt = time.time() - self.last_time
        self.last_time = time.time()

        while True:
            self.window_surface.blit(self.background_image, (0, 0))

            for event in pygame.event.get([pygame.QUIT]):
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()

            pos += 200
            if pos >= N * segL:
                pos %= N * segL

            if keys[pygame.K_RIGHT]:
                playerX += 200
                self.incline_angle = -self.max_incline
            elif keys[pygame.K_LEFT]:
                playerX -= 200
                self.incline_angle = self.max_incline
            else:
                self.incline_angle = 0

            playerX = max(-roadW / 1.3, min(roadW / 1.3, playerX))

            startPos = int(pos // segL) % N
            maxy = WINDOW_HEIGHT

            for n in range(startPos, startPos + 300):
                current = lines[n % N]
                current.project(playerX, 1500, pos - (N * segL if n >= N else 0))
                current.clip = maxy

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
            self.draw_motoqueiro()

            for n in range(startPos + 300, startPos, -1):
                lines[n % N].drawSprite(self.window_surface)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = GameWindow()
    game.run()
