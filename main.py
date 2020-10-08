import pygame


RATIO = 0.25
ITERATIONS = 1
REPLACE = True
BACKGROUND_COLOR = (0, 0, 0)


class Polygon:
    def __init__(self, points, color, is_closed=True, width=1):
        """
        :param points: A list or tuple of points specified as lists, tuples
            or pygame.Vector2.
        :param is_closed: Should the polygon be open or closed?
        :param color: Line color.
        :param width: Line thickness. If the polygon is closed and width=0
            then the polygon is filled. Width must be > 0 for open polygons.
        """
        self.points = []
        for p in points:
            if not isinstance(p, pygame.Vector2):
                p = pygame.Vector2(p)
            self.points.append(p)
        self.is_closed = is_closed
        self.color = color
        self.width = width
        self.memory = []

        if is_closed:
            self.draw = self.draw_closed
        elif width > 0:
            self.draw = self.draw_open
        else:
            raise ValueError("\"width\" must be > 0 for open polygons.")

        self.draw = self.draw_closed if is_closed else self.draw_open

    def draw_closed(self, target_surface):
        pygame.draw.polygon(
            target_surface,
            self.color,
            self.points,
            self.width
        )

    def draw_open(self, target_surface):
        # I'm not using draw_aalines because that looks broken
        # in pygame 2.0.0.dev12.
        pygame.draw.lines(
            target_surface,
            self.color,
            self.is_closed,
            self.points,
            self.width
        )

    def cut(self, ratio, iterations=1):
        """ Chaikin's corner cutting: https://sighack.com/post/chaikin-curves

        :param ratio: Float between 0 and 1. Ratio of the edg length which
            determines how close to the corner the cut should be made.
        :param iterations: Number of iterations of the cutting algorithm.
        """
        self.memory.append(self.points)

        # Avoid cuttin over the line midpoint:
        if ratio > 0.5:
            ratio = 1 - ratio

        for _ in range(iterations):
            new_points = []
            n_corners = len(self.points)
            if not self.is_closed:
                n_corners -= 1

            for i in range(n_corners):
                a = self.points[i]
                b = self.points[(i + 1) % len(self.points)]
                new_points.append(a.lerp(b, ratio))
                new_points.append(b.lerp(a, ratio))

            # For open polygons keep the original endpoints:
            if not self.is_closed:
                new_points[0] = self.points[0]
                new_points[-1] = self.points[-1]
            self.points = new_points

    def undo_cut(self):
        if len(self.memory) > 0:
            self.points = self.memory.pop()


def run(polygons):
    pygame.init()
    display = pygame.display.set_mode((1200, 800), pygame.SRCALPHA)
    transparent_surf = pygame.Surface(display.get_size()).convert_alpha()
    transparent_surf.fill((0, 0, 0, 32))

    display.fill(BACKGROUND_COLOR)
    for p in polygons:
        p.draw(display)

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
                    if REPLACE:
                        display.fill(BACKGROUND_COLOR)
                    else:
                        display.blit(transparent_surf, (0, 0))
                    for p in polygons:
                        p.cut(RATIO, ITERATIONS)
                        p.draw(display)
                    # print(f"New sum of corners of all polygons: {sum_corners}.")
                elif event.key == pygame.K_BACKSPACE:
                    if REPLACE:
                        display.fill(BACKGROUND_COLOR)
                    else:
                        display.blit(transparent_surf, (0, 0))
                    for p in polygons:
                        p.undo_cut()
                        p.draw(display)

        pygame.display.flip()


if __name__ == "__main__":
    triangle_closed = Polygon(
        points=((50, 50), (400, 75), (45, 300)),
        color=(255, 128, 0)
    )
    triangle_open = Polygon(
        points=((1000, 750), (1150, 600), (600, 650)),
        color=(0, 128, 255),
        is_closed=False,
        width=2
    )
    s = Polygon(
        points=((100, 400), (200, 600), (300, 500), (400, 700)),
        color=(0, 255, 0),
        is_closed=False,
        width=2
    )
    pebble_1 = Polygon(
        points=((650, 350), (550, 350), (500, 450), (575, 500), (650, 450)),
        color=(200, 200, 200),
        width=3
    )
    pebble_2 = Polygon(
        points=((650, 350), (950, 350), (900, 450), (650, 550)),
        color=(200, 200, 200),
        width=3
    )
    pebble_3 = Polygon(
        points=((650, 350), (950, 350), (900, 50), (650, 100)),
        color=(200, 200, 200),
        width=3
    )
    pebble_4 = Polygon(
        points=((650, 350), (450, 350), (350, 150), (450, 75), (650, 100)),
        color=(200, 200, 200),
        width=3
    )
    braid = Polygon(
        points=((1075, 25), (1000, 138), (1150, 250), (1000, 363), (1075, 475),
                (1150, 363), (1000, 250), (1150, 138)),
        color=(255, 0, 255),
        width=2
    )
    run([
        triangle_closed,
        triangle_open,
        s,
        pebble_1,
        pebble_2,
        pebble_3,
        pebble_4,
        braid
    ])
