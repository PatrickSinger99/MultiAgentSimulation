import pygame


class Button:
    # Adapted from https://thepythoncode.com/article/make-a-button-using-pygame-in-python

    color = {
        'normal': '#ffffff',
        'hover': '#666666',
        'pressed': '#333333',
    }

    def __init__(self, x, y, width, height, text, font, on_click_function=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click_function = on_click_function
        self.font = font
        self.already_pressed = False

        self.button_surface = pygame.Surface((self.width, self.height))
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.button_surf = font.render(text, True, (20, 20, 20))

    def process(self, screen):

        mouse_position = pygame.mouse.get_pos()
        self.button_surface.fill(Button.color['normal'])

        if self.button_rect.collidepoint(mouse_position):
            self.button_surface.fill(Button.color['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.button_surface.fill(Button.color['pressed'])

                if not self.already_pressed:
                    self.on_click_function()
                    self.already_pressed = True

            else:
                self.already_pressed = False

        self.button_surface.blit(self.button_surf, [
            self.button_rect.width/2 - self.button_surf.get_rect().width/2,
            self.button_rect.height/2 - self.button_surf.get_rect().height/2
        ])

        screen.blit(self.button_surface, self.button_rect)

    def set_text(self, text):
        self.button_surf = self.font.render(text, True, (20, 20, 20))
