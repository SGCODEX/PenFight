import pygame
import string
from enum import Enum


class Options(Enum):
    BACKGROUND = "background"
    FOREGROUND = "foreground"
    FONT = "font"
    BORDER = "border"
    BORDER_WIDTH = "border_width"
    HOVERED_BACKGROUND = "hovered_background"
    CLICKED_BACKGROUND = "clicked_background"
    TOGGLED_BACKGROUND = "toggled_background"


class GUI:
    default_options = {}
    defaults_created = False

    @staticmethod
    def create_defaults():
        GUI.default_options = {
            Label.__name__: {
                Options.BACKGROUND: (255, 255, 255),
                Options.FOREGROUND: (0, 0, 0),
                Options.FONT: pygame.font.SysFont("Comic Sans MS", 20),
                Options.BORDER: (0, 0, 0),
                Options.BORDER_WIDTH: 2
            },
            Button.__name__: {
                Options.BACKGROUND: (255, 255, 255),
                Options.FOREGROUND: (0, 0, 0),
                Options.FONT: pygame.font.SysFont("Comic Sans MS", 20),
                Options.BORDER: (0, 0, 0),
                Options.BORDER_WIDTH: 2,
                Options.HOVERED_BACKGROUND: (200, 200, 200),
                Options.CLICKED_BACKGROUND: (100, 100, 100),
            },
            ToggleButton.__name__: {
                Options.BACKGROUND: (255, 255, 255),
                Options.FOREGROUND: (0, 0, 0),
                Options.FONT: pygame.font.SysFont("Comic Sans MS", 20),
                Options.BORDER: (0, 0, 0),
                Options.BORDER_WIDTH: 2,
                Options.HOVERED_BACKGROUND: (200, 200, 200),
                Options.CLICKED_BACKGROUND: (100, 100, 100),
                Options.TOGGLED_BACKGROUND: (100, 100, 100)
            },
            Image.__name__: {
                Options.BACKGROUND: (255, 255, 255),
                Options.BORDER: (0, 0, 0),
                Options.BORDER_WIDTH: 0,
                Options.HOVERED_BACKGROUND: (200, 200, 200),
                Options.CLICKED_BACKGROUND: (100, 100, 100),
            },
            Textbox.__name__: {
                Options.BACKGROUND: (255, 255, 255),
                Options.FOREGROUND: (0, 0, 0),
                Options.FONT: pygame.font.SysFont("Comic Sans MS", 20),
                Options.BORDER: (0, 0, 0),
                Options.BORDER_WIDTH: 2,
                Options.HOVERED_BACKGROUND: (200, 200, 200),
                Options.CLICKED_BACKGROUND: (100, 100, 100),
            }
        }

    def get_default_options(self):
        if not GUI.defaults_created:
            GUI.defaults_created = True
            GUI.create_defaults()
        return GUI.default_options[self.__class__.__name__]


class Label(GUI):
    def __init__(self, rect, text, options=None):
        self.rect = rect
        self.text = text
        self.rendered, self.rendered_rect = None, None
        self.options = self.get_default_options().copy()
        self.options.update(options or {})

    def draw(self, screen):
        pygame.draw.rect(screen, self.options[Options.BACKGROUND], self.rect)

        border_width = self.options[Options.BORDER_WIDTH]
        if border_width > 0:
            pygame.draw.rect(screen, self.options[Options.BORDER], self.rect.inflate(border_width, border_width),
                             border_width)

        if self.rendered is None:
            self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
            self.rendered_rect = self.rendered.get_rect(center=self.rect.center)
        screen.blit(self.rendered, self.rendered_rect)

    def update(self, event):
        return

    def recreate(self, center=True):
        self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
        if center:
            self.rendered_rect = self.rendered.get_rect(center=self.rect.center)
        else:
            self.rendered_rect = self.rendered.get_rect(topleft=self.rect.topleft)

class Button(GUI):
    def __init__(self, rect, text, options=None):
        self.rect = rect
        self.text = text
        self.clicked, self.hovered = False, False
        self.enabled = True
        self.rendered, self.rendered_rect = None, None
        self.options = self.get_default_options().copy()
        self.options.update(options or {})

    def draw(self, screen):
        bg_color = self.options[(Options.CLICKED_BACKGROUND if self.clicked else (
            Options.HOVERED_BACKGROUND if self.hovered else Options.BACKGROUND))]
        pygame.draw.rect(screen, bg_color, self.rect)

        border_width = self.options[Options.BORDER_WIDTH]
        if border_width > 0:
            pygame.draw.rect(screen, self.options[Options.BORDER],
                             self.rect.inflate(border_width, border_width), border_width)

        if self.rendered is None:
            self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
            self.rendered_rect = self.rendered.get_rect(center=self.rect.center)

        if not self.enabled:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)

        screen.blit(self.rendered, self.rendered_rect)

    def update(self, event):
        if self.enabled:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])
            self.clicked = (event.type == pygame.MOUSEBUTTONDOWN) and self.hovered

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not self.enabled:
            self.hovered, self.clicked = False, False

    def recreate(self):
        self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
        self.rendered_rect = self.rendered.get_rect(center=self.rect.center)


class ToggleButton(Button):
    def __init__(self, rect, text, options=None):
        super().__init__(rect, text, options)
        self.toggled = False
        self.group = None

    def set_group(self, group):
        self.group = group

    def update(self, event):
        if self.enabled:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])
            self.clicked = not self.toggled and (event.type == pygame.MOUSEBUTTONDOWN) and self.hovered
            if self.clicked:
                self.toggle()

    def toggle(self):
        self.toggled = not self.toggled

        if self.group is not None:
            for elt in self.group:
                if elt.toggled and elt != self:
                    elt.toggled = False

    def draw(self, screen):
        bg_color = self.options[Options.TOGGLED_BACKGROUND if self.toggled else (
            (Options.CLICKED_BACKGROUND if self.clicked else (
             Options.HOVERED_BACKGROUND if self.hovered else Options.BACKGROUND)))]
        pygame.draw.rect(screen, bg_color, self.rect)

        border_width = self.options[Options.BORDER_WIDTH]
        if border_width > 0:
            pygame.draw.rect(screen, self.options[Options.BORDER],
                             self.rect.inflate(border_width, border_width), border_width)

        if self.rendered is None:
            self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
            self.rendered_rect = self.rendered.get_rect(center=self.rect.center)

        if not self.enabled:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)

        screen.blit(self.rendered, self.rendered_rect)


class Image(GUI):
    def __init__(self, rect, image, options=None):
        self.rect = rect
        self.image = image
        self.clicked, self.hovered = False, False
        self.enabled = True
        self.options = self.get_default_options().copy()
        self.options.update(options or {})

    def draw(self, screen):
        if self.image is None:
            return

        bg_color = self.options[(Options.CLICKED_BACKGROUND if self.clicked else (
            Options.HOVERED_BACKGROUND if self.hovered else Options.BACKGROUND))]
        pygame.draw.rect(screen, bg_color, self.rect)

        border_width = self.options[Options.BORDER_WIDTH]
        if border_width > 0:
            pygame.draw.rect(screen, self.options[Options.BORDER],
                             self.rect.inflate(border_width, border_width), border_width)

        if not self.enabled:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)

        screen.blit(self.image, self.image.get_rect(center=self.rect.center))

    def update(self, event):
        if self.enabled:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])
            self.clicked = (event.type == pygame.MOUSEBUTTONDOWN) and self.hovered

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not self.enabled:
            self.hovered, self.clicked = False, False


class Textbox(GUI):
    valid_text = (string.ascii_letters + string.digits + string.punctuation + " ")

    def __init__(self, rect, text="", options=None):
        self.rect = rect
        self.buffer = ([] if text is None else list(text))
        self.focused = False
        self.text = None
        self.text_changed = False
        self.blink, self.blink_timer, self.blink_speed = True, 0, 500
        self.rendered, self.rendered_rect, self.render_area = None, None, None

        self.options = self.get_default_options().copy()
        self.options.update(options or {})

        self.calculate_rendered_text()

    def draw(self, screen):

        pygame.draw.rect(screen, self.options[Options.BACKGROUND], self.rect)

        border_width = self.options[Options.BORDER_WIDTH]
        if border_width > 0:
            pygame.draw.rect(screen, self.options[Options.BORDER], self.rect.inflate(border_width, border_width),
                             border_width)

        if self.rendered is not None:
            screen.blit(self.rendered, self.rendered_rect, self.render_area)

        ticks = pygame.time.get_ticks()
        if ticks - self.blink_timer > self.blink_speed:
            self.blink = not self.blink
            self.blink_timer = ticks

        if self.blink and self.focused and self.rendered:
            cursor_start = (self.rendered_rect.left + self.render_area.width, self.rendered_rect.top)
            cursor_end = (self.rendered_rect.left + self.render_area.width, self.rendered_rect.bottom)
            pygame.draw.line(screen, (0, 0, 0), cursor_start, cursor_end, 2)

    def update(self, event):

        if self.focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(self.buffer) > 0:
                self.buffer.pop()

            elif event.unicode in self.valid_text:
                self.buffer.append(event.unicode)

            self.calculate_rendered_text()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            self.focused = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])

    def set_text(self, text):
        self.buffer = [c for c in text]
        self.calculate_rendered_text()

    def calculate_rendered_text(self):
        new_text = "".join(self.buffer)
        self.text_changed = new_text != self.text

        if self.text_changed:
            self.text = new_text
            self.rendered = self.options[Options.FONT].render(self.text, True, self.options[Options.FOREGROUND])
            self.rendered_rect = self.rendered.get_rect(x=self.rect.x + 5, centery=self.rect.centery)

            if self.rendered_rect.width > self.rect.width - 6:
                offset = self.rendered_rect.width - (self.rect.width - 6)
                self.render_area = pygame.Rect(offset, 0, self.rect.width - 6, self.rendered_rect.height)
            else:
                self.render_area = self.rendered.get_rect()
