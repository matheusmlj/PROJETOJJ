gfrom typing import List
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

white_rumble = pygame.Color(255, 255, 255)
black_rumble = pygame.Color(0, 0, 0)
dark_road = pygame.Color(105, 105, 105)
light_road = pygame.Color(107, 107, 107)
light_orange = pygame.Color(255, 200, 100)
dark_orange = pygame.Color(255, 140, 0)


class Menu:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(None, 60)
        self.options = ["Iniciar Jogo", "Créditos", "Sair"]
        self.selected_option = 0

    def draw(self):
        self.surface.fill((0, 0, 0))  # Fundo preto
        title_text = self.font.render("MackRacing", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.surface.blit(title_text, title_rect)

        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_option else (100, 100, 100)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, 200 + idx * 100))
            self.surface.blit(text, rect)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected_option
        return None

    def show_menu(self):
        while True:
            self.draw()
            pygame.display.flip()

            option = self.handle_input()
            if option is not None:
                return option


class Line:
    def __init__(self):
        self.x = self.y = self.z = 0.0
        self.X = self.Y = self.W = 0.0
        self.scale = 0.0

        self.spriteX = 0.0
        self.clip = 0.0
        self.sprite: pygame.Surface = None

    def project(self, camX: int, camY: int, camZ: int):
        # Limite o valor de self.z para evitar escalas excessivamente grandes
        self.z = max(0.1, self.z)  # Evitar que o valor de z seja zero ou muito pequeno

        self.scale = camD / (self.z - camZ)
        
        # Garantir que o valor de self.X e self.Y não sejam excessivamente grandes
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * roadW * WINDOW_WIDTH / 2

        # Previne que W se torne um valor muito grande ou muito pequeno
        self.W = min(self.W, WINDOW_WIDTH * 2)
        self.W = max(self.W, 10)



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
        self.dt = 0
        self.incline_angle = 0
        self.max_incline = 20
        self.time_elapsed = 0
        self.bounce_amplitude = 10
        self.bounce_frequency = 4
        self.lives = 3  # Sistema de vidas

        # Carregar imagens
        try:
            self.background_image = pygame.image.load("FundoJogo.png").convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.motoqueiro_img = pygame.image.load("motoqueiro.png").convert_alpha()
            self.motoqueiro_img = pygame.transform.scale(self.motoqueiro_img, (200, 200))
            self.sprite_5 = pygame.image.load("carro.png").convert_alpha()
            car_width, car_height = self.sprite_5.get_size()
            self.sprite_5 = pygame.transform.scale(self.sprite_5, (car_width // 3, car_height // 3))
        except pygame.error as e:
            print(f"Erro ao carregar imagens: {e}")
            sys.exit()

        self.menu = Menu(self.window_surface)
        self.reset_game()

    def reset_game(self):
        # Carregar as imagens de fundo antes de começar
        self.background_images = [
            pygame.transform.scale(pygame.image.load("FundoJogo.png").convert_alpha(), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            pygame.transform.scale(pygame.image.load("FundoJogo2.png").convert_alpha(), (WINDOW_WIDTH, WINDOW_HEIGHT)),
            pygame.transform.scale(pygame.image.load("FundoJogo3.png").convert_alpha(), (WINDOW_WIDTH, WINDOW_HEIGHT)),
        ]
        
        # Inicializa o fundo e as cores da pista
        self.current_background = self.background_images[0]
        self.road_colors = [(107, 107, 107), (90, 90, 90), (70, 70, 70)]  # Tons progressivamente mais escuros
        self.current_phase = 0  # Fase inicial
        self.base_speed = 200  # Velocidade base do motoqueiro
        self.current_speed = self.base_speed  # Velocidade inicial do motoqueiro

        # Definindo cores das fases
        self.dark_orange_colors = [(255, 140, 0), (87, 46, 0), (15, 8, 0)]
        self.light_orange_colors = [(255, 200, 100), (130, 71, 3), (0, 25, 153)]
        self.update_orange_colors(0)  # Cor inicial

        # Redefine as variáveis do jogo
        self.lines: List[Line] = [Line() for i in range(1600)]
        self.score = 0
        for i, line in enumerate(self.lines):
            line.z = i * segL + 0.00001

        self.pos = 0
        self.playerX = 0
        self.lives = 3
        self.ensure_car_generation(spacing=100)


    def check_phase_progression(self):
        """Verifica a pontuação e faz a troca de fase uma vez."""
        if self.score >= 200 and self.current_phase < 2:
            self.update_phase(2, new_base_speed=1000)  # Ajuste a velocidade conforme necessário para a fase 3
        elif self.score >= 100 and self.current_phase < 1:
            self.update_phase(1, new_base_speed=400)  # Ajuste a velocidade para a fase 2

    def update_phase(self, phase, new_base_speed):
        """Atualiza a fase, ajustando a velocidade base e os parâmetros visuais de forma direta."""
        if self.current_phase != phase:
            self.current_phase = phase
            self.current_background = self.background_images[phase]
            self.update_road_colors(self.road_colors[phase])
            self.update_orange_colors(phase)

            # Define a nova velocidade base para o motoqueiro
            self.base_speed = new_base_speed
            self.current_speed = self.base_speed

    def update(self):
        """Atualiza o estado do jogo, incluindo a velocidade e a posição do jogador."""
        if self.velocity_smooth:
            elapsed_time = pygame.time.get_ticks() - self.speed_change_start_time
            if elapsed_time < self.transition_duration:
                # Interpolação linear
                progress = elapsed_time / self.transition_duration
                self.current_speed = self.base_speed + (self.target_speed - self.base_speed) * progress
            else:
                self.current_speed = self.target_speed
                self.velocity_smooth = False

        # Atualização da posição do jogador
        self.pos += self.current_speed * self.dt
        if self.pos > len(self.lines) * segL:
            self.pos %= len(self.lines) * segL
    
    def smooth_velocity_change(self, target_speed_factor, duration=2):
        """Suaviza a mudança de velocidade, sem bloquear a execução."""
        target_speed = self.base_speed * target_speed_factor
        current_speed = self.current_speed
        self.speed_change_start_time = pygame.time.get_ticks()
        self.target_speed = target_speed
        self.transition_duration = duration * 1  # Converte para milissegundos
        self.velocity_smooth = True

    def update_position(self):
        """Atualiza a posição do jogador com base na velocidade e tempo passado."""
        max_pos_change = self.current_speed * self.dt
        self.pos += max_pos_change

        # Previne que a posição do jogador mude muito rápido
        if self.pos > len(self.lines) * segL:
            self.pos %= len(self.lines) * segL

    def update_orange_colors(self, phase_index):
        """Atualiza as cores dark_orange e light_orange com base na fase atual."""
        global dark_orange, light_orange
        dark_orange = pygame.Color(*self.dark_orange_colors[phase_index])
        light_orange = pygame.Color(*self.light_orange_colors[phase_index])


    def update_road_colors(self, new_color):
        """Atualiza as cores da estrada para um tom mais escuro."""
        global light_road, dark_road
        dark_road = pygame.Color(new_color[0] - 10, new_color[1] - 10, new_color[2] - 10)
        light_road = pygame.Color(*new_color)


        
    def ensure_car_generation(self, spacing=100):
        """Gera carros a 300 linhas de distância do jogador, espaçados por um intervalo grande."""
        # Calcula a linha que está 300 segmentos à frente do jogador
        target_line_index = int((self.pos // segL + 300) % len(self.lines))
        target_line = self.lines[target_line_index]

        # Gera carro em uma linha específica e espaçada se ainda não houver um carro lá
        if target_line.sprite is None and random.randint(1, spacing) == 1:
            target_line.sprite = self.sprite_5
            target_line.spriteX = random.choice([-3000, 0, 3000])

    def draw_credits(self):
        """Desenha a tela de créditos"""
        self.window_surface.fill((0, 0, 0))
        font = pygame.font.Font(None, 60)
        credit_lines = ["Créditos", "", "Pedro", "Yuri", "Matheus"]

        for idx, line in enumerate(credit_lines):
            text = font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, 200 + idx * 60))
            self.window_surface.blit(text, rect)

        pygame.display.flip()

        # Espera até o usuário pressionar Enter para voltar ao menu
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return
    def draw_road(self):
        """Desenha a estrada e os carros"""
        N = len(self.lines)
        startPos = int(self.pos // segL) % N
        maxy = WINDOW_HEIGHT

        for n in range(startPos, startPos + 300):
            current = self.lines[n % N]
            current.project(self.playerX, 1500, self.pos - (N * segL if n >= N else 0))
            current.clip = maxy

            if current.Y >= maxy:
                continue
            maxy = current.Y

            prev = self.lines[(n - 1) % N]
            grass_color = light_orange if (n // 3) % 2 else dark_orange
            rumble_color = white_rumble if (n // 3) % 2 else black_rumble
            road_color = light_road if (n // 3) % 2 else dark_road

            drawQuad(self.window_surface, grass_color, 0, prev.Y, WINDOW_WIDTH, 0, current.Y, WINDOW_WIDTH)
            drawQuad(self.window_surface, rumble_color, prev.X, prev.Y, prev.W * 1.2, current.X, current.Y, current.W * 1.2)
            drawQuad(self.window_surface, road_color, prev.X, prev.Y, prev.W, current.X, current.Y, current.W)

        for n in range(startPos + 300, startPos, -1):
            self.lines[n % N].drawSprite(self.window_surface)
        for n in range(startPos + 300, startPos, -1):
            current = self.lines[n % N]
            current.drawSprite(self.window_surface)

            # Verifique se o carro passou da tela (destY > WINDOW_HEIGHT)
            if current.Y > WINDOW_HEIGHT and current.sprite is not None:
                self.score += 10  # Incrementa 10 pontos
                current.sprite = None  # Remove o carro da tela


    def draw_motoqueiro(self):
        """Desenha o motoqueiro na tela"""
        bounce_offset = math.sin(self.time_elapsed * self.bounce_frequency) * self.bounce_amplitude
        rotated_img = pygame.transform.rotate(self.motoqueiro_img, self.incline_angle)
        motoqueiro_rect = rotated_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150 + bounce_offset))

        self.window_surface.blit(rotated_img, motoqueiro_rect)
        

        return motoqueiro_rect

    def check_collision(self, motoqueiro_rect):
        """Verifica colisão entre o motoqueiro e os carros na estrada."""
        for line in self.lines:
            if line.sprite:
                destX = line.X + line.scale * line.spriteX * WINDOW_WIDTH / 2
                destY = line.Y
                destW = max(1, min(line.sprite.get_width() * line.W / 266, WINDOW_WIDTH))
                destH = max(1, min(line.sprite.get_height() * line.W / 266, WINDOW_HEIGHT))

                # Verificação para garantir que todos os valores sejam números válidos
                if isinstance(destX, (int, float)) and isinstance(destY, (int, float)) and isinstance(destW, (int, float)) and isinstance(destH, (int, float)):
                    # Garantir que os valores não são NaN ou negativos
                    if all(val > 0 and not math.isnan(val) for val in [destX, destY, destW, destH]):
                        try:
                            # Verifica se os valores não são extremamente grandes antes de criar o retângulo
                            if abs(destX) > WINDOW_WIDTH * 10 or abs(destY) > WINDOW_HEIGHT * 10:
                                continue  # Ignora se os valores forem absurdos

                            # Criar o retângulo de colisão
                            car_rect = pygame.Rect(int(destX - destW / 2), int(destY - destH / 1.5), int(destW), int(destH))

                            # Verificar colisão com o motoqueiro
                            if motoqueiro_rect.colliderect(car_rect):
                                print("Colisão detectada!")
                                self.lives -= 1
                                print(f"Vidas restantes: {self.lives}")

                                # Remover o carro da estrada após a colisão
                                line.sprite = None
                                return True
                        except Exception as e:
                            print(f"Erro ao criar o retângulo de colisão: {e}")
                else:
                    print(f"Valores inválidos para o carro: destX={destX}, destY={destY}, destW={destW}, destH={destH}")
                    line.sprite = None

        return False



    
    def run(self):
        """ Método principal do jogo """
        while True:
            # Mostrar o menu inicial
            option = self.menu.show_menu()

            if option == 0:  # Iniciar Jogo
                self.reset_game()
                self.play_game()
            elif option == 1:  # Créditos
                self.draw_credits()
            elif option == 2:  # Sair
                pygame.quit()
                sys.exit()

    def draw_lives(self):
        """Desenha o número de vidas no canto superior esquerdo da tela."""
        font = pygame.font.Font(None, 40)  # Define a fonte e o tamanho
        lives_text = font.render(f"Vidas: {self.lives}", True, (255, 0, 0))  # Texto vermelho
        self.window_surface.blit(lives_text, (20, 20))  # Posição no canto superior esquerdo

    def draw_score(self):
        """Desenha o score no canto superior direito da tela."""
        font = pygame.font.Font(None, 40)  # Define a fonte e o tamanho
        score_text = font.render(f"Pontos: {self.score}", True, (255, 255, 0))  # Texto amarelo
        self.window_surface.blit(score_text, (WINDOW_WIDTH - 200, 20))  # Posição no canto superior direito

    def play_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.playerX += self.current_speed
                self.incline_angle = -self.max_incline
            elif keys[pygame.K_LEFT]:
                self.playerX -= self.current_speed
                self.incline_angle = self.max_incline
            else:
                self.incline_angle = 0

            # Atualização incremental de posição
            self.pos += self.current_speed
            if self.pos >= len(self.lines) * segL:
                self.pos %= len(self.lines) * segL

            # Limita a posição do jogador na estrada
            self.playerX = max(-roadW / 1.3, min(roadW / 1.3, self.playerX))

            # Atualiza fase, cores e velocidade quando a pontuação for atingida
            self.check_phase_progression()

            # Desenha o fundo e as linhas da estrada
            self.window_surface.blit(self.current_background, (0, 0))
            self.draw_road()

            # Atualiza o offset de pulo e verifica colisão
            bounce_offset = math.sin(self.time_elapsed * self.bounce_frequency) * self.bounce_amplitude
            rotated_img = pygame.transform.rotate(self.motoqueiro_img, self.incline_angle)
            motoqueiro_rect = rotated_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150 + bounce_offset))

            # Reduz hitbox lateral para o motoqueiro
            motoqueiro_rect.width *= 0.6
            motoqueiro_rect.centerx = WINDOW_WIDTH // 2

            if self.check_collision(motoqueiro_rect):
                if self.lives <= 0:
                    print("Jogo encerrado! Retornando ao menu.")
                    return

            # Tempo e atualização de elementos visuais
            self.time_elapsed += self.dt
            self.draw_motoqueiro()
            self.draw_lives()
            self.draw_score()

            # Geração otimizada de carros com espaçamento e atualização a cada 300 linhas
            self.ensure_car_generation(spacing=100)

            # Atualiza a tela e controla FPS
            pygame.display.flip()
            self.clock.tick(60)



def run_game():
    game = GameWindow()
    game.run()

if __name__ == "__main__":
    run_game()
