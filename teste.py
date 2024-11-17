import pygame
import sys
import random

# Inicializa o Pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Fonte
font = pygame.font.SysFont(None, 48)

# Carrega e redimensiona a imagem de fundo
background_image = pygame.image.load("fundo.png").convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Configurações da Moto e Carros
MOTO_WIDTH, MOTO_HEIGHT = 50, 100
moto_x, moto_y = screen_width // 2 - MOTO_WIDTH // 2, screen_height - MOTO_HEIGHT - 10
moto_speed = 5
CAR_WIDTH, CAR_HEIGHT = 50, 100
car_speed = 5
cars = []

# Função para desenhar a pista e as divisões
def draw_track():
    screen.fill(GRAY)
    pygame.draw.line(screen, WHITE, (screen_width // 3, 0), (screen_width // 3, screen_height), 5)
    pygame.draw.line(screen, WHITE, (2 * screen_width // 3, 0), (2 * screen_width // 3, screen_height), 5)

# Função para adicionar novos carros
def spawn_car():
    lane = random.choice([screen_width // 6 - CAR_WIDTH // 2, screen_width // 2 - CAR_WIDTH // 2, 5 * screen_width // 6 - CAR_WIDTH // 2])
    cars.append(pygame.Rect(lane, -CAR_HEIGHT, CAR_WIDTH, CAR_HEIGHT))

# Função para atualizar os carros
def update_cars():
    global cars
    for car in cars:
        car.y += car_speed
    cars = [car for car in cars if car.y < screen_height]

# Função para desenhar os carros e a moto
def draw_objects(moto, cars):
    pygame.draw.rect(screen, RED, moto)
    for car in cars:
        pygame.draw.rect(screen, BLACK, car)

# Função para verificar colisões
def check_collision(moto, cars):
    for car in cars:
        if moto.colliderect(car):
            return True
    return False

# Função principal do jogo
def play_game():
    global moto_x
    moto = pygame.Rect(moto_x, moto_y, MOTO_WIDTH, MOTO_HEIGHT)
    clock = pygame.time.Clock()
    spawn_timer = 0

    running = True
    while running:
        screen.fill(GRAY)
        draw_track()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and moto.x - moto_speed >= 0:
            moto.x -= moto_speed
        if keys[pygame.K_RIGHT] and moto.x + moto_speed <= screen_width - MOTO_WIDTH:
            moto.x += moto_speed

        spawn_timer += clock.get_time()
        if spawn_timer > 1000:
            spawn_car()
            spawn_timer = 0

        update_cars()
        if check_collision(moto, cars):
            print("Game Over")
            return

        draw_objects(moto, cars)
        pygame.display.flip()
        clock.tick(60)

# Função para mostrar créditos
def show_credits():
    running = True
    while running:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 36)
        text = font.render("Desenvolvido por: Seu Nome", True, BLACK)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()

# Função para desenhar o menu
def draw_menu(selected_option):
    screen.blit(background_image, (0, 0))
    options = ["Jogar", "Créditos", "Sair"]
    
    for i, option in enumerate(options):
        if i == selected_option:
            text = font.render(option, True, GREEN)
        else:
            text = font.render(option, True, WHITE)
        
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 60))
        screen.blit(text, text_rect)

    pygame.display.flip()

def main():
    selected_option = 0
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        play_game()  # Inicia o jogo
                    elif selected_option == 1:
                        show_credits()  # Mostra os créditos
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()

        draw_menu(selected_option)
        clock.tick(60)

if __name__ == "__main__":
    main()
