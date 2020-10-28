from typing import List, Sequence, Tuple, Union

import pygame
import pygame.freetype


# Ratio of the edge length which determines
# how close to the corner the cut should be made.
RATIO = 0.25
# Number of iterations per keypress.
ITERATIONS = 1
# Alpha of the overlay surface for a fading effect.
# Set to 0 to not erase previous steps.
ALPHA = 15
BACKGROUND_COLOR = (0, 0, 0)
# Invert the order of new corners for spiky results.
INVERT = False


class Polygon:
    def __init__(self,
                 corners: Sequence[Union[pygame.Vector2, Tuple[int, int]]],
                 color: Union[pygame.Color, Tuple[int, int, int], List[int], int, str],
                 closed: bool = True,
                 filled: bool = False,
                 remember: bool = True) -> None:
        """Setting "remember" to False will disable the undo functionality."""
        self.corners: List[pygame.math.Vector2] = []
        for p in corners:
            if not isinstance(p, pygame.Vector2):
                p = pygame.Vector2(p)
            self.corners.append(p)
        self.closed = closed
        self.color = color
        self.filled = filled
        self.remember = remember
        self.memory: List[List[pygame.math.Vector2]] = []

        if closed and filled:
            self.draw = self.draw_closed_filled
        else:
            self.draw = self.draw_empty

    def draw_empty(self, target_surface: pygame.surface.Surface) -> None:
        pygame.draw.aalines(
            target_surface,
            self.color,
            self.closed,
            self.corners
        )

    def draw_closed_filled(self, target_surface: pygame.surface.Surface) -> None:
        # Pygame does not have filled antialiased shapes. But you can combine
        # the empty antialiased shape and the filled version to achieve
        # an acceptable result.
        self.draw_empty(target_surface)
        pygame.draw.polygon(
            target_surface,
            self.color,
            self.corners
        )

    def cut(self, ratio: float, iterations: int = 1) -> None:
        """ Chaikin's corner cutting: https://sighack.com/post/chaikin-curves

        ratio: Ratio (between 0 and 1) of the edge length which
            determines how close to the corner the cut should be made.
        iterations: Number of iterations of the cutting algorithm.
        """
        if self.remember:
            self.memory.append(self.corners)

        # Avoid cutting over the line midpoint:
        if ratio > 0.5:
            ratio = 1 - ratio

        for _ in range(iterations):
            new_corners = []
            n_corners = len(self.corners)
            if not self.closed:
                n_corners -= 1

            for i in range(n_corners):
                a = self.corners[i]
                b = self.corners[(i + 1) % len(self.corners)]
                new_corners.append(a.lerp(b, ratio))
                new_corners.append(b.lerp(a, ratio))

                if INVERT:
                    new_corners[-1], new_corners[-2] = new_corners[-2], new_corners[-1]

            # For open polygons keep the original endpoints:
            if not self.closed:
                new_corners[0] = self.corners[0]
                new_corners[-1] = self.corners[-1]
            self.corners = new_corners

    def undo_cut(self) -> None:
        if len(self.memory) > 0:
            self.corners = self.memory.pop()


def run(polygons: Sequence[Polygon]) -> None:
    pygame.init()
    pygame.freetype.init()

    display = pygame.display.set_mode((1200, 800))
    display.fill(BACKGROUND_COLOR)

    transparent_surf = pygame.Surface(display.get_size())
    transparent_surf.set_alpha(ALPHA)

    font = pygame.freetype.SysFont("monospace", 20)
    font.fgcolor = (255, 255, 255)

    iteration_count = 0
    corner_count = sum(len(p.corners) for p in polygons)

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    # Protect against app or system crashes caused
                    # by too many corners:
                    if corner_count > 1e6:
                        print("Number of corners limit reached.")
                        continue
                    for p in polygons:
                        p.cut(RATIO, ITERATIONS)
                    iteration_count += ITERATIONS
                    corner_count = sum(len(p.corners) for p in polygons)
                elif event.key == pygame.K_BACKSPACE:
                    for p in polygons:
                        p.undo_cut()
                    iteration_count = max(0, iteration_count - ITERATIONS)
                    corner_count = sum(len(p.corners) for p in polygons)

        display.blit(transparent_surf, (0, 0))
        for p in polygons:
            p.draw(display)
        font.render_to(display, (5, 5), f"iterations: {iteration_count}")
        font.render_to(display, (5, 25), f"corners: {corner_count}")
        pygame.display.flip()


if __name__ == "__main__":
    triangle_closed = Polygon(
        corners=((50, 50), (400, 75), (45, 300)),
        color=(255, 128, 0)
    )
    triangle_open = Polygon(
        corners=((1000, 750), (1150, 600), (600, 650)),
        color=(0, 128, 255),
        closed=False
    )
    s = Polygon(
        corners=((100, 400), (200, 600), (300, 500), (400, 700)),
        color=(0, 255, 0),
        closed=False
    )
    pebble_1 = Polygon(
        corners=((650, 350), (550, 350), (500, 450), (575, 500), (650, 450)),
        color=(200, 200, 200)
    )
    pebble_2 = Polygon(
        corners=((650, 350), (950, 350), (900, 450), (650, 550)),
        color=(200, 200, 200),
        filled=True
    )
    pebble_3 = Polygon(
        corners=((650, 350), (950, 350), (900, 50), (650, 75)),
        color=(200, 200, 200)
    )
    pebble_4 = Polygon(
        corners=((650, 350), (450, 350), (350, 150), (450, 75), (650, 100)),
        color=(200, 200, 200),
        filled=True
    )
    braid = Polygon(
        corners=((1075, 25), (1000, 138), (1150, 250), (1000, 363), (1075, 475),
                 (1150, 363), (1000, 250), (1150, 138)),
        color=(255, 0, 255)
    )
    run((
        triangle_closed,
        triangle_open,
        s,
        pebble_1,
        pebble_2,
        pebble_3,
        pebble_4,
        braid
    ))
