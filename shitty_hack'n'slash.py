import pygame
import os
import sys


# TILE
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


# CHARACTER
class Character(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(all_sprites)
        self.change_animation(load_image("mario.png"), 1, 1)
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.stay = True

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
        self.mask = pygame.mask.from_surface(self.image)
        if self.stay:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


# PLAYER
# parent-class
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, ps, s):
        super().__init__(all_sprites, player_group)

        player_set = players_sets[ps]
        self.sheet_idle = player_set['idle']
        self.sheet_run = player_set['run']
        self.sheet_take_hit = player_set['take_hit']
        self.sheet_death = player_set['death']
        self.sheet_revive = player_set['revive']
        self.sheet_attack1 = player_set['attack1']
        self.sheet_attack2 = player_set['attack2']

        self.idle_w, self.idle_h = cols_rows[ps][self.sheet_idle]
        self.run_w, self.run_h = cols_rows[ps][self.sheet_run]
        self.take_hit_w, self.take_hit_h = cols_rows[ps][self.sheet_take_hit]
        self.death_w, self.death_h = cols_rows[ps][self.sheet_death]
        self.revive_w, self.revive_h = cols_rows[ps][self.sheet_revive]
        self.attack1_w, self.attack1_h = cols_rows[ps][self.sheet_attack1]
        self.attack2_w, self.attack2_h = cols_rows[ps][self.sheet_attack2]

        w, h = s
        self.rect = pygame.rect.Rect(0, 0, w, h)
        self.change_animation(self.sheet_idle, self.idle_w, self.idle_h)
        self.image = self.frames[self.cur_frame]

        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x + 15, TILE_HEIGHT * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.health = 100

        self.stay = True
        self.death = False
        self.revive = False
        self.attack = False
        self.attack_num = 1
        self.take_hit = False
        self.run = False

    def move(self, movement):
        if movement == 'UP':
            self.rect.y -= PL_SPEED
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.y += PL_SPEED
                    break
        if movement == 'DOWN':
            self.rect.y += PL_SPEED
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.y -= PL_SPEED
                    break
        if movement == 'RIGHT':
            self.rect.x += PL_SPEED
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.x -= PL_SPEED
                    break
        if movement == 'LEFT':
            self.rect.x -= PL_SPEED
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.x += PL_SPEED
                    break

    def taking_hit(self):
        if not self.death:
            self.change_animation(self.sheet_take_hit, self.take_hit_w, self.take_hit_h)
            self.health -= 10
            self.take_hit = True
            self.stay = False
            self.run = False
            self.attack = False

    def attacking(self, pos):
        if not self.death:
            if self.attack_num == 1:
                self.change_animation(self.sheet_attack1, self.attack1_w, self.attack1_h)
                self.attack_num = 2
            elif self.attack_num == 2:
                self.change_animation(self.sheet_attack2, self.attack2_w, self.attack2_h)
                self.attack_num = 1
            self.attack = True
            self.stay = False
            self.run = False
            self.revive = False

    def stop_attack(self):
        self.attack = False

    def staying(self):
        if not self.death:
            self.change_animation(self.sheet_idle, self.idle_w, self.idle_h)
            self.stay = True
            self.run = False
            self.revive = False
            self.take_hit = False

    def running(self):
        if not self.death and not self.attack:
            self.change_animation(self.sheet_run, self.run_w, self.run_h)
            self.run = True
            self.stay = False
            self.revive = False

    def is_alive(self):
        return not self.death

    def is_attacking(self):
        return self.attack

    def dying(self):
        if not self.death:
            self.change_animation(self.sheet_death, self.death_w, self.death_h)
            self.death = True
            self.revive = False
            self.stay = False
            self.run = False
            self.attack = False

    def reviving(self):
        if self.death:
            if self.cur_frame == len(self.frames) - 1:
                self.health = 100
                self.revive = True
                self.death = False
                self.change_animation(self.sheet_revive, self.revive_w, self.revive_h)

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
        self.mask = pygame.mask.from_surface(self.image)
        if self.health <= 0:
            self.dying()
        if self.attack:
            ...
        elif self.stay and iteration % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.run and iteration % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.take_hit and iteration % 2 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            else:
                # tt
                if len(keys):
                    self.running()
                else:
                    self.staying()
        elif self.death and iteration % 3 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
        elif self.revive and iteration % 4 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            else:
                if len(keys):
                    self.running()
                else:
                    self.staying()


# child-classes:
class EvilWizard(Player):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'evil_wizard', (250, 250))
        self.pos = (0, 0)

    def attacking(self, pos):
        super().attacking(pos)
        if not self.death:
            self.pos = pos

    def update(self):
        super().update()
        if self.attack and iteration % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.cur_frame % len(self.frames) == 0:
                # Bullet(self.pos)
                print(self.pos)


class MartialHero(Player):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'martial_hero', (200, 200))

    def update(self):
        super().update()
        if self.attack and iteration % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            # collide


# MONSTERS
# parent-class
class Monster(Character):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows)


# child-classes:
class Goblin(Monster):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows)


class Skeleton(Monster):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows)


class Mushroom(Monster):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, character, ch_group, pos):
        super().__init__(all_sprites, bullets_group, ch_group)
        self.character = character


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
    except Exception:
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
            elif level[y][x] == 'W':
                Tile('empty', x, y)
                new_player = EvilWizard(x, y)
            elif level[y][x] == 'M':
                Tile('empty', x, y)
                new_player = MartialHero(x, y)
            elif level[y][x] == 'm':
                Tile('empty', x, y)
                new_player = Mushroom(..., ..., ...)
            elif level[y][x] == 'g':
                Tile('empty', x, y)
                new_player = Goblin(..., ..., ...)
            elif level[y][x] == 's':
                Tile('empty', x, y)
                new_player = Skeleton(..., ..., ...)
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
    # INITIALIZATION
    pygame.init()
    # pygame.key.set_repeat(200, 70)
    size = WIDTH, HEIGHT = 500, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Shitty Hack\'n\'Slash')

    # SPRITE SETS
    # tiles sprites sets
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }

    # players sprites sets
    evil_wizard_pl = {
        'idle': load_image('evil_wizard_idle.png'),
        'run': load_image('evil_wizard_run.png'),
        'attack1': load_image('evil_wizard_attack1.png'),
        'attack2': load_image('evil_wizard_attack2.png'),
        'take_hit': load_image('evil_wizard_take_hit.png'),
        'death': load_image('evil_wizard_death.png'),
        'revive': load_image('evil_wizard_jump.png')
    }
    martial_hero_pl = {
        'idle': load_image('martial_hero_idle.png'),
        'run': load_image('martial_hero_run.png'),
        'attack1': load_image('martial_hero_attack1.png'),
        'attack2': load_image('martial_hero_attack2.png'),
        'take_hit': load_image('martial_hero_take_hit.png'),
        'death': load_image('martial_hero_death.png'),
        'revive': load_image('martial_hero_jump.png')
    }
    necromancer_pl = load_image("necromancer_sheet.png")
    night_borne_pl = load_image("night_borne_sheet.png")
    players_sets = {
        'evil_wizard': evil_wizard_pl,
        'martial_hero': martial_hero_pl,
        'necromancer': necromancer_pl,
        'night_borne': night_borne_pl
    }

    # monsters sprites sets
    goblin_m = {
        'idle': load_image('goblin_idle.png'),
        'run': load_image('goblin_run.png'),
        'take_hit': load_image('goblin_take_hit.png'),
        'death': load_image('goblin_death.png')
    }
    skeleton_m = {
        'idle': load_image('skeleton_idle.png'),
        'run': load_image('skeleton_run.png'),
        'take_hit': load_image('skeleton_take_hit.png'),
        'death': load_image('skeleton_death.png')
    }
    mushroom_m = {
        'idle': load_image('mushroom_idle.png'),
        'run': load_image('mushroom_run.png'),
        'take_hit': load_image('mushroom_take_hit.png'),
        'death': load_image('mushroom_death.png')
    }
    demon_m = {
        'idle': load_image('demon_idle.png'),
        'run': load_image('demon_idle.png'),
        'take_hit': load_image('demon_idle.png'),
        'death': load_image('demon_idle.png'),
        'attack': load_image('demon_attack_breath.png')
    }
    ghost_m = {
        'idle': load_image('ghost_idle.png'),
        'run': load_image('demon_idle.png'),
        'take_hit': load_image('demon_idle.png'),
        'death': load_image('demon_idle.png')
    }
    trash_monster_m = load_image("trash_monster_sheet.png")
    monsters_sets = {
        'goblin': goblin_m,
        'skeleton': skeleton_m,
        'mushroom': mushroom_m,
        'trash_monster': trash_monster_m,
        'demon': demon_m,
        'ghost': ghost_m
    }

    # COLUMNS-ROWS LISTS FOR SPRITES
    ew_cols_rows = {
        evil_wizard_pl['idle']: (8, 1),
        evil_wizard_pl['run']: (8, 1),
        evil_wizard_pl['attack1']: (8, 1),
        evil_wizard_pl['attack2']: (8, 1),
        evil_wizard_pl['take_hit']: (3, 1),
        evil_wizard_pl['death']: (7, 1),
        evil_wizard_pl['revive']: (2, 1)
    }
    mh_cols_rows = {
        martial_hero_pl['idle']: (4, 1),
        martial_hero_pl['run']: (8, 1),
        martial_hero_pl['attack1']: (4, 1),
        martial_hero_pl['attack2']: (4, 1),
        martial_hero_pl['take_hit']: (3, 1),
        martial_hero_pl['death']: (7, 1),
        martial_hero_pl['revive']: (2, 1)
    }
    cols_rows = {
        'evil_wizard': ew_cols_rows,
        'martial_hero': mh_cols_rows
    }

    # SPRITE GROUPS
    all_sprites = pygame.sprite.Group()

    # tiles groups
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()

    # characters groups
    characters_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    monsters_group = pygame.sprite.Group()

    # bullets groups
    bullets_group = pygame.sprite.Group()
    pl_bullets_group = pygame.sprite.Group()
    en_bullets_group = pygame.sprite.Group()

    # CONSTANTS
    TILE_WIDTH = TILE_HEIGHT = 50
    PL_SPEED = 3

    # time
    FPS = 60
    clock = pygame.time.Clock()
    iteration = 0

    # CAMERA INITIALIZATION
    camera = Camera()

    # LOADING MAP AND PLAYER INITIALIZATION
    level_map = load_level('map2.txt')
    player, level_x, level_y = generate_level(level_map)

    # MENU
    start_screen()

    # GAME BEGIN
    keys = set()
    while True:
        for event in pygame.event.get():
            # quit checking
            if event.type == pygame.QUIT:
                terminate()
            # movement start checking
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    keys.add('UP')
                    player.running()
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    keys.add('DOWN')
                    player.running()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    keys.add('RIGHT')
                    player.running()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    keys.add('LEFT')
                    player.running()
                if event.key == pygame.K_q:
                    keys = set()
                    player.dying()
                if event.key == pygame.K_r:
                    player.reviving()
                if event.key == pygame.K_h:
                    player.taking_hit()
            # movement end checking
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    keys.discard('UP')
                    if not len(keys) and not player.is_attacking():
                        player.staying()
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    keys.discard('DOWN')
                    if not len(keys) and not player.is_attacking():
                        player.staying()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    keys.discard('RIGHT')
                    if not len(keys) and not player.is_attacking():
                        player.staying()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    keys.discard('LEFT')
                    if not len(keys) and not player.is_attacking():
                        player.staying()
            # attack start checking
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attacking(event.pos)
            # attack end checking
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    player.stop_attack()
                    if len(keys) == 0:
                        player.staying()
                    else:
                        player.running()
        camera.update(player)

        # moving if player is alive
        if player.is_alive():
            for k in keys:
                player.move(k)
        # camera
        for sprite in all_sprites:
            camera.apply(sprite)

        # iteration and updating
        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        iteration += 1

        pygame.display.flip()
        clock.tick(FPS)
