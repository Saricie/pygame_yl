import pygame
# import pygame_gui
import os
import sys


# TILE
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


# BORDER
class Border(pygame.sprite.Sprite): # ttt
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites, all_borders)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.image.fill((255, 255, 255))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.image.fill((255, 255, 255))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


# CHARACTER
class Character(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, ch_s, ch_size, hp, speed):
        super().__init__(all_sprites, characters_group)

        ch_set = all_characters_group[ch_s]
        self.sheet_idle = ch_set['idle']
        self.sheet_run = ch_set['run']
        self.sheet_take_hit = ch_set['take_hit']
        self.sheet_death = ch_set['death']
        self.sheet_idle_f = ch_set['idle_f']
        self.sheet_run_f = ch_set['run_f']
        self.sheet_take_hit_f = ch_set['take_hit_f']
        self.sheet_death_f = ch_set['death_f']

        self.idle_w, self.idle_h = cols_rows[ch_s][self.sheet_idle]
        self.run_w, self.run_h = cols_rows[ch_s][self.sheet_run]
        self.take_hit_w, self.take_hit_h = cols_rows[ch_s][self.sheet_take_hit]
        self.death_w, self.death_h = cols_rows[ch_s][self.sheet_death]

        self.stay = True
        self.death = False
        self.take_hit = False
        self.run = False
        self.flipped = False

        w, h = ch_size
        self.rect = pygame.rect.Rect(0, 0, w, h)
        self.running()
        self.image = self.frames[self.cur_frame]

        # расположение rect относительно центра, а не всего спрайта???
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x + 15, TILE_HEIGHT * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.max_hp = hp
        self.health = hp
        self.speed = speed
        self.pos = (0, 0)

    def move(self, movement):
        if movement == 'UP':
            self.rect.y -= self.speed
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.y += self.speed
                    break
            ''''if not pygame.sprite.spritecollide(self, horizontal_borders, False):
                for border in horizontal_borders:
                    if not pygame.sprite.collide_mask(self, border):
                        self.rect.y -= self.speed
            else:
                self.rect.y += self.speed'''
        if movement == 'DOWN':
            self.rect.y += self.speed
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.y -= self.speed
                    break
            '''if not pygame.sprite.spritecollide(self, horizontal_borders, False):
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed'''
        if movement == 'RIGHT':
            self.rect.x += self.speed
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.x -= self.speed
                    break
            '''if not pygame.sprite.spritecollide(self, vertical_borders, False):
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed'''
        if movement == 'LEFT':
            self.rect.x -= self.speed
            for wall in walls_group:
                if pygame.sprite.collide_mask(self, wall):
                    self.rect.x += self.speed
                    break
            '''if not pygame.sprite.spritecollide(self, vertical_borders, False):
                self.rect.x -= self.speed
            else:
                self.rect.x += self.speed'''

    def taking_hit(self):
        if not self.death:
            if not self.flipped:
                self.change_animation(self.sheet_take_hit, self.take_hit_w, self.take_hit_h)
            else:
                self.change_animation(self.sheet_take_hit_f, self.take_hit_w, self.take_hit_h, True)
            self.health -= 10
            self.take_hit = True
            self.stay = False
            self.run = False

    def dying(self):
        if not self.death:
            if not self.flipped:
                self.change_animation(self.sheet_death, self.death_w, self.death_h)
            else:
                self.change_animation(self.sheet_death_f, self.death_w, self.death_h, True)
            self.death = True
            self.stay = False
            self.run = False

    def staying(self):
        if not self.death:
            if not self.flipped:
                self.change_animation(self.sheet_idle, self.idle_w, self.idle_h)
            else:
                self.change_animation(self.sheet_idle_f, self.idle_w, self.idle_h, True)
            self.stay = True
            self.run = False
            self.take_hit = False

    def running(self):
        if not self.death:
            if not self.flipped:
                self.change_animation(self.sheet_run, self.run_w, self.run_h)
            else:
                self.change_animation(self.sheet_run_f, self.run_w, self.run_h, True)
            self.run = True
            self.stay = False

    def is_alive(self):
        return not self.death

    def flip(self):
        self.flipped = not self.flipped
        if self.run:
            self.running()
        elif self.stay:
            self.staying()
        elif self.take_hit:
            self.taking_hit()
        elif self.death:
            self.dying()

    def is_flipped(self):
        return self.flipped

    def cut_sheet(self, sheet, columns, rows, is_flipped=False):
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        if is_flipped:
            self.frames = self.frames[::-1]

    def change_animation(self, sheet, columns, rows, is_flipped=False):
        self.frames = []
        self.cut_sheet(sheet, columns, rows, is_flipped)
        self.cur_frame = 0

    def update(self):
        self.mask = pygame.mask.from_surface(self.image)
        if self.health <= 0:
            self.dying()


# PLAYER
# parent-class
class Player(Character):
    def __init__(self, pos_x, pos_y, pl_s, pl_size, hp):
        self.revive = False
        self.attack = False
        self.attack_num = 1
        super().__init__(pos_x, pos_y, pl_s, pl_size, hp, PL_SPEED)
        self.add(player_group)

        player_set = players_sets[pl_s]
        self.sheet_revive = player_set['revive']
        self.sheet_attack1 = player_set['attack1']
        self.sheet_attack2 = player_set['attack2']
        self.sheet_revive_f = player_set['revive_f']
        self.sheet_attack1_f = player_set['attack1_f']
        self.sheet_attack2_f = player_set['attack2_f']

        self.revive_w, self.revive_h = cols_rows[pl_s][self.sheet_revive]
        self.attack1_w, self.attack1_h = cols_rows[pl_s][self.sheet_attack1]
        self.attack2_w, self.attack2_h = cols_rows[pl_s][self.sheet_attack2]

    def taking_hit(self):
        super().taking_hit()
        if not self.death:
            self.attack = False

    def attacking(self, pos):
        if not self.death:
            if self.attack_num == 1:
                if not self.flipped:
                    self.change_animation(self.sheet_attack1, self.attack1_w, self.attack1_h)
                else:
                    self.change_animation(self.sheet_attack1_f, self.attack1_w, self.attack1_h, True)
                self.attack_num = 2
            elif self.attack_num == 2:
                if not self.flipped:
                    self.change_animation(self.sheet_attack2, self.attack2_w, self.attack2_h)
                else:
                    self.change_animation(self.sheet_attack2_f, self.attack2_w, self.attack2_h, True)
                self.attack_num = 1
            self.attack = True
            self.stay = False
            self.run = False
            self.revive = False

    def is_attacking(self):
        return self.attack

    def stop_attack(self):
        self.attack = False

    def staying(self):
        super().staying()
        if not self.death:
            self.revive = False

    def running(self):
        if not self.death and not self.is_attacking():
            if not self.flipped:
                self.change_animation(self.sheet_run, self.run_w, self.run_h)
            else:
                self.change_animation(self.sheet_run_f, self.run_w, self.run_h, True)
            self.run = True
            self.stay = False
            self.revive = False

    def dying(self):
        super().dying()
        if not self.death:
            self.revive = False
            self.attack = False

    def reviving(self):
        if self.death:
            if self.cur_frame == len(self.frames) - 1:
                self.health = self.max_hp
                self.revive = True
                self.death = False
                if not self.flipped:
                    self.change_animation(self.sheet_revive, self.revive_w, self.revive_h)
                else:
                    self.change_animation(self.sheet_revive_f, self.revive_w, self.revive_h, True)

    def update(self):
        super().update()
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
        super().__init__(pos_x, pos_y, 'evil_wizard', (250, 250), 100)

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
        super().__init__(pos_x, pos_y, 'martial_hero', (200, 200), 120)

    def update(self):
        super().update()
        if self.attack and iteration % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.cur_frame % len(self.frames) == 0:
                self.attacking(self.pos)
        if pygame.sprite.spritecollide(self, monsters_group, False):
            if self.attack: # and iteration % 3 == 0
                for m in monsters_group:
                    if pygame.sprite.collide_mask(self, m):
                        m.taking_hit()
            elif iteration % 4 == 0:
                for m in monsters_group:
                    if m.is_alive() and pygame.sprite.collide_mask(self, m):
                        self.taking_hit()
                        break


# MONSTERS
# parent-class
class Monster(Character): # переделать move, movements и анимации
    def __init__(self, pos_x, pos_y, m_s, m_size, hp):
        super().__init__(pos_x, pos_y, m_s, m_size, hp, M_SPEED)
        self.add(monsters_group)

        monster_set = monsters_sets[m_s]
        self.movements = set()
        self.up = False
        self.down = False
        self.right = False
        self.left = False

    def move(self, movement):
        super().move(movement)
        self.movements = set()

    def update(self):
        super().update()

        if self.is_alive():
            pl_x = player.rect.x + player.rect.w // 2
            pl_y = player.rect.y + player.rect.h // 2
            m_x = self.rect.x + self.rect.w // 2
            m_y = self.rect.y + self.rect.h // 2
            movements = [self.up, self.down, self.right, self.left]

            if m_x < pl_x:
                self.right = True
                self.left = False
                if self.flipped:
                    self.flip()
                self.move('RIGHT')
            elif m_x > pl_x:
                self.right = False
                self.left = True
                if not self.flipped:
                    self.flip()
                self.move('LEFT')
            if m_y < pl_y:
                self.down = True
                self.up = False
                self.move('DOWN')
            elif m_y > pl_y:
                self.down = False
                self.up = True
                self.move('UP')

        if self.stay and iteration % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.run and iteration % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif self.take_hit and iteration % 2 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            else:
                # ttt
                if len(self.movements):
                    self.running()
                else:
                    self.staying()
        elif self.death and iteration % 3 == 0:
            if self.cur_frame != len(self.frames) - 1:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            elif self.cur_frame != len(self.frames) + 4:
                # do kill?
                self.kill()


# child-classes:
class Goblin(Monster):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'goblin', (150, 150), 30)


class Skeleton(Monster):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'skeleton', (150, 150), 30)


class Mushroom(Monster):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'mushroom', (150, 150), 40)


class Ghost(Monster):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'ghost', (64, 80), 20)


class Demon(Monster):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'demon', (160, 144), 100)


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


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):
    filename = "data/" + filename
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))
        max_height = len(level_map)

        return list(map(lambda x: x.ljust(max_width, '.'), level_map)), max_width, max_height
    except Exception:
        print('Неправильный файл')
        terminate()


def generate_level(level):
    new_player, x, y = None, None, None
    monsters = []
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
                monsters.append((Mushroom, x, y))
            elif level[y][x] == 'g':
                Tile('empty', x, y)
                monsters.append((Goblin, x, y))
            elif level[y][x] == 's':
                Tile('empty', x, y)
                monsters.append((Skeleton, x, y))
            elif level[y][x] == 'h':
                Tile('empty', x, y)
                monsters.append((Ghost, x, y))
            elif level[y][x] == 'd':
                Tile('empty', x, y)
                Demon(x, y)
    Border(0, 0, TOTAL_WIDTH, 0)
    Border(0, TOTAL_HEIGHT, TOTAL_WIDTH, TOTAL_HEIGHT)
    Border(0, 0, 0, TOTAL_HEIGHT)
    Border(TOTAL_WIDTH, 0, TOTAL_WIDTH, TOTAL_HEIGHT)
    return new_player, x, y, monsters


def terminate():
    pygame.quit()
    sys.exit()


def menu():
    intro_text = ["{Название игры придумать}", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    menu_background = pygame.transform.scale(load_image('night_town_background.png'), (WIDTH, HEIGHT))
    screen.blit(menu_background, (0, 0))
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
    size = WIDTH, HEIGHT = (1080, 600)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
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
        'idle_f': pygame.transform.flip(load_image('evil_wizard_idle.png'), True, False),
        'run': load_image('evil_wizard_run.png'),
        'run_f': pygame.transform.flip(load_image('evil_wizard_run.png'), True, False),
        'attack1': load_image('evil_wizard_attack1.png'),
        'attack1_f': pygame.transform.flip(load_image('evil_wizard_attack1.png'), True, False),
        'attack2': load_image('evil_wizard_attack2.png'),
        'attack2_f': pygame.transform.flip(load_image('evil_wizard_attack2.png'), True, False),
        'take_hit': load_image('evil_wizard_take_hit.png'),
        'take_hit_f': pygame.transform.flip(load_image('evil_wizard_take_hit.png'), True, False),
        'death': load_image('evil_wizard_death.png'),
        'death_f': pygame.transform.flip(load_image('evil_wizard_death.png'), True, False),
        'revive': load_image('evil_wizard_jump.png'),
        'revive_f': pygame.transform.flip(load_image('evil_wizard_jump.png'), True, False)
    }
    martial_hero_pl = {
        'idle': load_image('martial_hero_idle.png'),
        'idle_f': pygame.transform.flip(load_image('martial_hero_idle.png'), True, False),
        'run': load_image('martial_hero_run.png'),
        'run_f': pygame.transform.flip(load_image('martial_hero_run.png'), True, False),
        'attack1': load_image('martial_hero_attack1.png'),
        'attack1_f': pygame.transform.flip(load_image('martial_hero_attack1.png'), True, False),
        'attack2': load_image('martial_hero_attack2.png'),
        'attack2_f': pygame.transform.flip(load_image('martial_hero_attack2.png'), True, False),
        'take_hit': load_image('martial_hero_take_hit.png'),
        'take_hit_f': pygame.transform.flip(load_image('martial_hero_take_hit.png'), True, False),
        'death': load_image('martial_hero_death.png'),
        'death_f': pygame.transform.flip(load_image('martial_hero_death.png'), True, False),
        'revive': load_image('martial_hero_jump.png'),
        'revive_f': pygame.transform.flip(load_image('martial_hero_jump.png'), True, False)
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
    # как у игроков
    goblin_m = {
        'idle': load_image('goblin_idle.png'),
        'idle_f': pygame.transform.flip(load_image('goblin_idle.png'), True, False),
        'run': load_image('goblin_run.png'),
        'run_f': pygame.transform.flip(load_image('goblin_run.png'), True, False),
        'take_hit': load_image('goblin_take_hit.png'),
        'take_hit_f': pygame.transform.flip(load_image('goblin_take_hit.png'), True, False),
        'death': load_image('goblin_death.png'),
        'death_f': pygame.transform.flip(load_image('goblin_death.png'), True, False)
    }
    skeleton_m = {
        'idle': load_image('skeleton_idle.png'),
        'idle_f': pygame.transform.flip(load_image('skeleton_idle.png'), True, False),
        'run': load_image('skeleton_run.png'),
        'run_f': pygame.transform.flip(load_image('skeleton_run.png'), True, False),
        'take_hit': load_image('skeleton_take_hit.png'),
        'take_hit_f': pygame.transform.flip(load_image('skeleton_take_hit.png'), True, False),
        'death': load_image('skeleton_death.png'),
        'death_f': pygame.transform.flip(load_image('skeleton_death.png'), True, False)
    }
    mushroom_m = {
        'idle': load_image('mushroom_idle.png'),
        'idle_f': pygame.transform.flip(load_image('mushroom_idle.png'), True, False),
        'run': load_image('mushroom_run.png'),
        'run_f': pygame.transform.flip(load_image('mushroom_run.png'), True, False),
        'take_hit': load_image('mushroom_take_hit.png'),
        'take_hit_f': pygame.transform.flip(load_image('mushroom_take_hit.png'), True, False),
        'death': load_image('mushroom_death.png'),
        'death_f': pygame.transform.flip(load_image('mushroom_death.png'), True, False)
    }
    demon_m = {
        'idle_f': load_image('demon_idle.png'),
        'idle': pygame.transform.flip(load_image('demon_idle.png'), True, False),
        'run_f': load_image('demon_idle.png'),
        'run': pygame.transform.flip(load_image('demon_idle.png'), True, False),
        'take_hit_f': load_image('demon_idle.png'),
        'take_hit': pygame.transform.flip(load_image('demon_idle.png'), True, False),
        'death_f': load_image('demon_idle.png'),
        'death': pygame.transform.flip(load_image('demon_idle.png'), True, False),
        'attack_f': load_image('demon_attack_breath.png'),
        'attack': pygame.transform.flip(load_image('demon_attack_breath.png'), True, False),
    }
    ghost_m = {
        'idle_f': load_image('ghost_idle.png'),
        'idle': pygame.transform.flip(load_image('ghost_idle.png'), True, False),
        'run_f': load_image('ghost_idle.png'),
        'run': pygame.transform.flip(load_image('ghost_idle.png'), True, False),
        'take_hit_f': load_image('ghost_idle.png'),
        'take_hit': pygame.transform.flip(load_image('ghost_idle.png'), True, False),
        'death_f': load_image('ghost_idle.png'),
        'death': pygame.transform.flip(load_image('ghost_idle.png'), True, False),
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

    all_characters_group = {
        'evil_wizard': evil_wizard_pl,
        'martial_hero': martial_hero_pl,
        'necromancer': necromancer_pl,
        'night_borne': night_borne_pl,
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
    g_cols_rows = {
        goblin_m['idle']: (4, 1),
        goblin_m['run']: (8, 1),
        goblin_m['take_hit']: (4, 1),
        goblin_m['death']: (4, 1)
    }
    s_cols_rows = {
        skeleton_m['idle']: (4, 1),
        skeleton_m['run']: (4, 1),
        skeleton_m['take_hit']: (4, 1),
        skeleton_m['death']: (4, 1)
    }
    m_cols_rows = {
        mushroom_m['idle']: (4, 1),
        mushroom_m['run']: (8, 1),
        mushroom_m['take_hit']: (4, 1),
        mushroom_m['death']: (4, 1)
    }
    d_cols_rows = {
        demon_m['idle']: (6, 1),
        demon_m['run']: (6, 1),
        demon_m['take_hit']: (6, 1),
        demon_m['death']: (6, 1),
        demon_m['attack']: (11, 1)
    }
    gh_cols_rows = {
        ghost_m['idle']: (7, 1),
        ghost_m['run']: (7, 1),
        ghost_m['take_hit']: (7, 1),
        ghost_m['death']: (7, 1)
    }
    cols_rows = {
        'evil_wizard': ew_cols_rows,
        'martial_hero': mh_cols_rows,
        'goblin': g_cols_rows,
        'skeleton': s_cols_rows,
        'mushroom': m_cols_rows,
        'demon': d_cols_rows,
        'ghost': gh_cols_rows
    }

    # SPRITE GROUPS
    all_sprites = pygame.sprite.Group()

    # tiles and borders groups
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    all_borders = pygame.sprite.Group()

    # characters groups
    characters_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    monsters_group = pygame.sprite.Group()

    # bullets groups
    bullets_group = pygame.sprite.Group()
    pl_bullets_group = pygame.sprite.Group()
    en_bullets_group = pygame.sprite.Group()

    # LOADING MAP AND PLAYER INITIALIZATION
    level_map, max_width, max_height = load_level('map2.txt')

    # CONSTANTS
    TILE_WIDTH = TILE_HEIGHT = 50
    TOTAL_WIDTH = TILE_WIDTH * max_width
    TOTAL_HEIGHT = TILE_HEIGHT * max_height
    PL_SPEED = 3
    M_SPEED = 2

    player, level_x, level_y, monsters = generate_level(level_map)

    # time
    FPS = 60
    clock = pygame.time.Clock()
    iteration = 0

    # CAMERA INITIALIZATION
    camera = Camera()

    # MENU
    menu()

    # GAME BEGIN
    keys = set()
    while True:
        for event in pygame.event.get():
            # quit checking
            if event.type == pygame.QUIT:
                terminate()
            # player movement start checking
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
            # player movement end checking
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
            # player attack start checking
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.attacking(event.pos)
            # player attack end checking
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    player.stop_attack()
                    if len(keys) == 0:
                        player.staying()
                    else:
                        player.running()
            # player view checking
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if player.is_flipped() and x >= player.rect.x + player.rect.w // 2:
                    player.flip()
                elif not player.is_flipped() and x < player.rect.x + player.rect.w // 2:
                    player.flip()
        camera.update(player)

        # moving if player is alive
        if player.is_alive():
            for k in keys:
                player.move(k)
        # camera
        for sprite in all_sprites:
            camera.apply(sprite)

        # monsters spawn
        if iteration % (FPS * 10) == 0 and len(monsters_group) <= 6 and player.is_alive():
            for M, x, y in monsters:
                M(x, y)

        # iteration and updating
        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)
        characters_group.draw(screen)
        iteration += 1

        pygame.display.flip()
        clock.tick(FPS)
