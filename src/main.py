import math
import random
import sys
import webbrowser
from pathlib import Path

import pygame


WIDTH = 960
HEIGHT = 540
FPS = 60

TITLE = "Diskette Demolition"

pygame.init()
pygame.display.set_caption(TITLE)

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Courier New", 18, bold=True)
SMALL = pygame.font.SysFont("Courier New", 14, bold=True)
BIG = pygame.font.SysFont("Courier New", 34, bold=True)


# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------

BLACK = (8, 8, 8)
DARK = (20, 20, 24)
GRAY = (65, 65, 70)
LIGHT_GRAY = (160, 160, 165)
WHITE = (235, 235, 235)
GREEN = (80, 255, 110)
ORANGE = (255, 150, 40)
RED = (255, 70, 70)
BLUE = (60, 150, 255)
CYAN = (80, 230, 255)


# ---------------------------------------------------------------------------
# SIMPLE VOXEL / 2.5D RENDERING
# ---------------------------------------------------------------------------

def iso(x, y, z):
    """
    Tiny isometric projection.

    This isn't a full 3D engine; that's intentional.
    It gives the game a chunky voxel-diorama appearance
    while keeping the program extremely small.
    """
    sx = WIDTH / 2 + (x - y) * 34
    sy = 300 + (x + y) * 17 - z * 34
    return int(sx), int(sy)


def cube(surface, x, y, z, size, color):
    """
    Draw a little voxel cube.
    """

    x0, y0 = iso(x, y, z)
    x1, y1 = iso(x + size, y, z)
    x2, y2 = iso(x + size, y + size, z)
    x3, y3 = iso(x, y + size, z)

    xt0, yt0 = iso(x, y, z + size)
    xt1, yt1 = iso(x + size, y, z + size)
    xt2, yt2 = iso(x + size, y + size, z + size)
    xt3, yt3 = iso(x, y + size, z + size)

    # Top
    pygame.draw.polygon(
        surface,
        tuple(min(255, c + 35) for c in color),
        [(xt0, yt0), (xt1, yt1), (xt2, yt2), (xt3, yt3)]
    )

    # Left
    pygame.draw.polygon(
        surface,
        color,
        [(xt0, yt0), (xt3, yt3), (x3, y3), (x0, y0)]
    )

    # Right
    darker = tuple(max(0, c - 35) for c in color)

    pygame.draw.polygon(
        surface,
        darker,
        [(xt1, yt1), (xt2, yt2), (x2, y2), (x1, y1)]
    )

    pygame.draw.line(
        surface,
        BLACK,
        (xt0, yt0),
        (xt1, yt1),
        2
    )


# ---------------------------------------------------------------------------
# DISKETTE
# ---------------------------------------------------------------------------

LABELS = [
    "AUTOEXEC.BAT",
    "README.TXT",
    "GAME.EXE",
    "COOLPIC.BMP",
    "FINAL.DOC",
    "HOMEWORK",
    "1998_BACKUP",
    "TAXES",
    "VERY_IMPORTANT",
    "DO_NOT_DELETE",
    "FINAL_FINAL.DOC",
    "TOTALLY_NOT_WINDOWS",
]


class Diskette:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0
        self.vx = random.uniform(-0.018, 0.018)
        self.vy = random.uniform(-0.018, 0.018)
        self.rotation = random.randint(0, 3)

        self.label = random.choice(LABELS)

        self.files = [
            self.label,
            "DISKINFO.TXT",
            "README.TXT",
        ]

        if random.random() < 0.25:
            self.files.append("MYSTERY.EXE")

        self.dead = False
        self.age = 0

    def update(self):
        self.age += 1

        self.x += self.vx
        self.y += self.vy

        if self.x < -5 or self.x > 5:
            self.vx *= -1

        if self.y < -5 or self.y > 5:
            self.vy *= -1

    def draw(self, surface):
        if self.dead:
            return

        # Main disk body
        cube(
            surface,
            self.x,
            self.y,
            0,
            0.75,
            (55, 55, 60)
        )

        # Disk label
        px, py = iso(
            self.x + 0.08,
            self.y + 0.05,
            0.78
        )

        pygame.draw.rect(
            surface,
            (225, 225, 215),
            (px - 10, py - 6, 21, 12)
        )

        # Center hole
        pygame.draw.rect(
            surface,
            BLACK,
            (px - 3, py - 2, 6, 4)
        )

    def destroy(self):
        self.dead = True


# ---------------------------------------------------------------------------
# FILE WINDOW
# ---------------------------------------------------------------------------

class DiskWindow:
    def __init__(self):
        self.open = False
        self.disk = None

    def show(self, disk):
        self.disk = disk
        self.open = True

    def close(self):
        self.open = False
        self.disk = None

    def draw(self, surface):
        if not self.open or self.disk is None:
            return

        rect = pygame.Rect(
            WIDTH // 2 - 220,
            HEIGHT // 2 - 150,
            440,
            300
        )

        pygame.draw.rect(surface, (185, 185, 185), rect)
        pygame.draw.rect(surface, BLACK, rect, 3)

        title = "A:\\"
        surface.blit(
            FONT.render(title, True, BLACK),
            (rect.x + 12, rect.y + 10)
        )

        pygame.draw.line(
            surface,
            BLACK,
            (rect.x, rect.y + 42),
            (rect.right, rect.y + 42),
            2
        )

        y = rect.y + 58

        for filename in self.disk.files:
            surface.blit(
                SMALL.render(filename, True, BLACK),
                (rect.x + 20, y)
            )
            y += 25

        hint = "[B] BIN    [U] UPLOAD    [ESC] CLOSE"

        surface.blit(
            SMALL.render(hint, True, BLACK),
            (rect.x + 20, rect.bottom - 30)
        )


# ---------------------------------------------------------------------------
# PLAYER
# ---------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.cooldown = 0

    def update(self):
        keys = pygame.key.get_pressed()

        speed = 0.055

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += speed

        self.x = max(-5, min(5, self.x))
        self.y = max(-5, min(5, self.y))

        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        cube(
            surface,
            self.x,
            self.y,
            0,
            0.7,
            ORANGE
        )

        px, py = iso(
            self.x + 0.35,
            self.y + 0.35,
            0.7
        )

        pygame.draw.rect(
            surface,
            BLACK,
            (px - 4, py - 3, 3, 3)
        )

        pygame.draw.rect(
            surface,
            BLACK,
            (px + 2, py - 3, 3, 3)
        )

    def smash(self, disks):
        if self.cooldown > 0:
            return 0

        self.cooldown = 15

        destroyed = 0

        for disk in disks:
            if disk.dead:
                continue

            dx = self.x - disk.x
            dy = self.y - disk.y

            if math.sqrt(dx * dx + dy * dy) < 1.1:
                disk.destroy()
                destroyed += 1

        return destroyed


# ---------------------------------------------------------------------------
# MAIN GAME
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        self.running = True
        self.score = 0
        self.disks = []
        self.player = Player()
        self.disk_window = DiskWindow()

        self.spawn_timer = 0
        self.game_over = False

        self.message = ""
        self.message_timer = 0

        self.bin_count = 0

        self.spawn_disk()

    def spawn_disk(self):
        self.disks.append(
            Diskette(
                random.uniform(-4.5, 4.5),
                random.uniform(-4.5, 4.5)
            )
        )

    def nearest_disk(self):
        best = None
        best_distance = 999

        for disk in self.disks:
            if disk.dead:
                continue

            dx = self.player.x - disk.x
            dy = self.player.y - disk.y

            d = math.sqrt(dx * dx + dy * dy)

            if d < best_distance:
                best_distance = d
                best = disk

        return best

    def open_nearest(self):
        disk = self.nearest_disk()

        if disk is not None:
            self.disk_window.show(disk)

    def delete_disk(self):
        if self.disk_window.disk:
            disk = self.disk_window.disk

            if not disk.dead:
                disk.destroy()
                self.bin_count += 1
                self.score += 50

                self.message = "DISKETTE SENT TO THE BIN."
                self.message_timer = 100

            self.disk_window.close()

    def upload_disk(self):
        if self.disk_window.disk:
            # Open the real Internet Archive homepage in the user's browser.
            webbrowser.open("https://archive.org/")

            self.message = "NETSCAPE: CONNECTING TO THE INTERNET..."
            self.message_timer = 160

    def update(self):
        if self.game_over:
            return

        self.player.update()

        for disk in self.disks:
            disk.update()

        self.disks = [
            disk for disk in self.disks
            if not disk.dead
        ]

        self.spawn_timer += 1

        # Gradually increase difficulty.
        interval = max(
            25,
            110 - self.score // 250
        )

        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self.spawn_disk()

        # Too many disks = disaster.
        if len(self.disks) > 30:
            self.game_over = True
            self.message = "DISK OVERFLOW."
            self.message_timer = 999999

        if self.message_timer > 0:
            self.message_timer -= 1

    def draw_desktop(self):
        screen.fill((35, 45, 48))

        # Floor
        for x in range(-6, 7):
            for y in range(-6, 7):
                cube(
                    screen,
                    x,
                    y,
                    -0.12,
                    0.95,
                    (35, 45, 48)
                )

        # Desk computer
        cube(
            screen,
            -1.2,
            -1.3,
            0,
            2.4,
            (75, 75, 80)
        )

        # CRT
        cube(
            screen,
            -0.7,
            -0.75,
            1.0,
            1.5,
            (45, 45, 50)
        )

        # CRT screen
        sx, sy = iso(
            -0.62,
            -0.69,
            2.48
        )

        pygame.draw.rect(
            screen,
            (20, 80, 35),
            (sx - 28, sy - 20, 56, 40)
        )

        # Desktop text
        screen.blit(
            SMALL.render(
                "C:\\WINDOWS>",
                True,
                GREEN
            ),
            (sx - 22, sy - 10)
        )

        # Bin
        cube(
            screen,
            3.0,
            -1.8,
            0,
            1.0,
            (100, 100, 105)
        )

        bx, by = iso(3.2, -1.6, 1.0)

        screen.blit(
            SMALL.render("BIN", True, WHITE),
            (bx - 14, by - 5)
        )

    def draw_hud(self):
        pygame.draw.rect(
            screen,
            BLACK,
            (0, 0, WIDTH, 54)
        )

        screen.blit(
            FONT.render(
                f"DISKETTE DEMOLITION   SCORE: {self.score}",
                True,
                GREEN
            ),
            (15, 15)
        )

        screen.blit(
            SMALL.render(
                f"DISKS: {len(self.disks)}",
                True,
                WHITE
            ),
            (WIDTH - 100, 18)
        )

        if self.message_timer > 0:
            msg = FONT.render(
                self.message,
                True,
                ORANGE
            )

            screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    HEIGHT - 45
                )
            )

    def draw_help(self):
        help_text = (
            "WASD/ARROWS MOVE   SPACE SMASH   E OPEN DISK   "
            "ESC CLOSE"
        )

        screen.blit(
            SMALL.render(help_text, True, WHITE),
            (15, HEIGHT - 25)
        )

    def draw_game_over(self):
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        text = BIG.render(
            "DISK OVERFLOW",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                HEIGHT // 2 - 50
            )
        )

        text2 = FONT.render(
            f"FINAL SCORE: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            text2,
            (
                WIDTH // 2 - text2.get_width() // 2,
                HEIGHT // 2 + 5
            )
        )

        text3 = SMALL.render(
            "PRESS R TO RESTART",
            True,
            GREEN
        )

        screen.blit(
            text3,
            (
                WIDTH // 2 - text3.get_width() // 2,
                HEIGHT // 2 + 45
            )
        )

    def draw(self):
        self.draw_desktop()

        # Draw disks behind player.
        for disk in sorted(
            self.disks,
            key=lambda d: d.x + d.y
        ):
            disk.draw(screen)

        self.player.draw(screen)

        self.draw_hud()
        self.draw_help()
        self.disk_window.draw(screen)

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def restart(self):
        self.__init__()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if self.disk_window.open:
                        self.disk_window.close()
                    else:
                        self.running = False

                elif event.key == pygame.K_SPACE:
                    destroyed = self.player.smash(self.disks)

                    if destroyed:
                        self.score += destroyed * 100
                        self.message = (
                            f"SMASHED {destroyed} DISKETTE"
                            + ("S!" if destroyed != 1 else "!")
                        )
                        self.message_timer = 80

                elif event.key == pygame.K_e:
                    if not self.disk_window.open:
                        self.open_nearest()

                elif event.key == pygame.K_b:
                    if self.disk_window.open:
                        self.delete_disk()

                elif event.key == pygame.K_u:
                    if self.disk_window.open:
                        self.upload_disk()

                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.restart()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
