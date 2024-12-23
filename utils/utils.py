import pygame
import math

def draw_spinner(screen, loading=True):
    if loading:
        # Obtener las dimensiones de la pantalla
        width, height = screen.get_size()
        
        # Configurar el color y tamaño del spinner
        spinner_color = (255, 255, 255)  # Blanco
        spinner_radius = 50
        spinner_line_width = 6
        
        # Calcular el ángulo de rotación (basado en el tiempo)
        angle = pygame.time.get_ticks() / 100  # Velocidad de rotación (ajustable)
        
        # Limpiar la pantalla (opcional)
        screen.fill((0, 0, 0))  # Fondo negro
        
        # Dibujar el spinner
        center_x, center_y = width // 2, height // 2
        for i in range(12):  # Dibujar 12 segmentos
            # Calcular el ángulo de cada línea del spinner
            line_angle = math.radians(angle + i * 30)
            line_x = center_x + int(spinner_radius * math.cos(line_angle))
            line_y = center_y + int(spinner_radius * math.sin(line_angle))
            
            # Dibujar cada línea del spinner
            pygame.draw.line(screen, spinner_color, (center_x, center_y), (line_x, line_y), spinner_line_width)
        
        # Actualizar la pantalla para mostrar el spinner
        pygame.display.flip()