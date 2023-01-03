import pygame
import os
import sys


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Character(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(all_sprites)

        self.frames = []
        self.sheet = sheet

        self.cut_sheet(self.sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

        self.mask = pygame.mask.from_surface(self.image)
        self.stay = True

    def cut_sheet(self, sheet, columns, rows):
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.stay:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet_idle, sheet_run, sheet_death, sheet_attack, pos_x, pos_y):
        super().__init__(all_sprites, player_group)

        self.sheet_idle = sheet_idle
        self.sheet_run = sheet_run
        self.sheet_death = sheet_death
        self.sheet_attack2 = sheet_attack

        self.rect = pygame.Rect(0, 0, 250, 250)
        self.change_animation(self.sheet_idle, 8, 1)
        self.image = self.frames[self.cur_frame]

        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.health = 100

        self.stay_ = True
        self.death_ = False
        self.attack_ = False
        self.run_ = False

    def move(self, movement):
        if not pygame.sprite.spritecollide(self, walls_group, False):
            if movement == 'UP':
                self.rect.y -= go
                if pygame.sprite.spritecollide(self, walls_group, False):
                    self.rect.y += go
            if movement == 'DOWN':
                self.rect.y += go
                if pygame.sprite.spritecollide(self, walls_group, False):
                    self.rect.y -= go
            if movement == 'RIGHT':
                self.rect.x += go
                if pygame.sprite.spritecollide(self, walls_group, False):
                    self.rect.x -= go
            if movement == 'LEFT':
                self.rect.x -= go
                if pygame.sprite.spritecollide(self, walls_group, False):
                    self.rect.x += go

    def attack(self):
        self.change_animation(self.sheet_attack2, 8, 1)

    # доделать
    def attacking(self, pos):
        print(pos)

    def stay(self):
        self.change_animation(self.sheet_idle, 8, 1)

    def run(self):
        self.change_animation(self.sheet_run, 8, 1)

    def death(self):
        self.change_animation(self.sheet_death, 7, 1)

    def cut_sheet(self, sheet, columns, rows):
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def change_animation(self, sheet, columns, rows):
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0

    def update(self):
        if self.health <= 0:
            self.death_ = True
        if self.stay_ and iteration % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.run_ and iteration % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.attack_ and iteration % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.death_ and iteration % 3 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]


class Monster(Character):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows)


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, bullets_group)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))

        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except:
        print('Неправильный файл')
        terminate()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y).add(walls_group)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(load_image('evil_wizard_idle.png'),
                                    load_image('evil_wizard_run.png'),
                                    load_image('evil_wizard_death.png'),
                                    load_image('evil_wizard_attack2.png'), x, y)
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    # pygame.key.set_repeat(200, 70)

    size = WIDTH, HEIGHT = 500, 500
    screen = pygame.display.set_mode(size)

    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }

    tile_width = tile_height = 50
    go = 3

    pygame.display.set_caption('Shitty Hack\'n\'Slash')
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    FPS = 60
    clock = pygame.time.Clock()
    iteration = 0
    camera = Camera()

    level_map = load_level('map2.txt')
    player, level_x, level_y = generate_level(level_map)
    start_screen()
    keys = set()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and not player.death_:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    keys.add('UP')
                    player.stay_ = False
                    player.run_ = True
                    player.run()
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    keys.add('DOWN')
                    player.stay_ = False
                    player.run_ = True
                    player.run()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    keys.add('RIGHT')
                    player.stay_ = False
                    player.run_ = True
                    player.run()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    keys.add('LEFT')
                    player.stay_ = False
                    player.run_ = True
                    player.run()
                if event.key == pygame.K_q:
                    player.health = 0
                    player.stay_ = False
                    player.run_ = False
                    player.death()
            if event.type == pygame.KEYUP and not player.death_:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    keys.discard('UP')
                    if len(keys) == 0:
                        player.stay_ = True
                        player.run_ = False
                        player.stay()
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    keys.discard('DOWN')
                    if len(keys) == 0:
                        player.stay_ = True
                        player.run_ = False
                        player.stay()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    keys.discard('RIGHT')
                    if len(keys) == 0:
                        player.stay_ = True
                        player.run_ = False
                        player.stay()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    keys.discard('LEFT')
                    if len(keys) == 0:
                        player.stay_ = True
                        player.run_ = False
                        player.stay()
            if event.type == pygame.MOUSEBUTTONDOWN and not player.death_:
                if event.button == 1:
                    player.attack_ = True
                    player.stay_ = False
                    player.run_ = False
                    player.attack()
                    if player.cur_frame % len(player.frames) == 0:
                        player.attacking(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and not player.death_:
               if event.button == 1:
                  player.attack_ = False
                  player.stay_ = True
                  player.stay()
        camera.update(player)

        for i in keys:
            player.move(i)
        for sprite in all_sprites:
            camera.apply(sprite)

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        iteration += 1

        pygame.display.flip()
        clock.tick(FPS)
