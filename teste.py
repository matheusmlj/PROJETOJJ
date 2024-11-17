import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Fonte
font = pygame.font.SysFont(None, 48)

# Carrega e redimensiona a imagem de fundo
background_image = pygame.image.load("fundo.png").convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Função para desenhar o menu
def draw_menu(selected_option):
    screen.blit(background_image, (0, 0))  # Desenha o fundo
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
                        print("Iniciar jogo...")  # Aqui você pode chamar a função do jogo
                    elif selected_option == 1:
                        print("Mostrar créditos...")  # Aqui você pode mostrar os créditos
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()

        draw_menu(selected_option)
        clock.tick(60)

if __name__ == "__main__":
    main()
