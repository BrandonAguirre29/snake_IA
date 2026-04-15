# ─── main.py ─────────────────────────────────────────────────
import pygame
from config import WIDTH, HEIGHT, FPS, GREEN_BRIGHT, RED_APPLE, HIT_PAUSE_MS
from entidades import Snake, Cube
from niveles import get_level, get_walls, find_safe_spawn, randomSnack, place_obstacle, SCORE_WIN
from hud import redraw, draw_level_up, draw_fase_4b_warning
from datos import init_csv, save_row, count_data
from musica import init_music, play_level_music, play_gameover_music, play_victory_music
from rival import Rival
from menu import show_menu, show_game_over, show_victory

SNACK_MOVE_TICKS = 12


def get_music_key(score, level):
    if level < 4:
        return level
    return "4b" if score >= 25 else "4a"


def hit_pause(win, s, snack, poison_apple, life_apple,
              walls, obstacles, score, lives, level,
              data_count, obstacles_placed, tick,
              rival=None, fase_4b=False, snack_timer=None):
    deadline = pygame.time.get_ticks() + HIT_PAUSE_MS
    while pygame.time.get_ticks() < deadline:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        redraw(win, s, snack, poison_apple, life_apple,
               walls, obstacles, score, lives, level,
               data_count, obstacles_placed, tick,
               rival=rival, fase_4b=fase_4b,
               flash=True, snack_timer=snack_timer)
        pygame.time.delay(30)


def game_loop(win, start_level=1):
    """
    start_level: nivel desde el que arranca la partida.
    El jugador lo elige en el menú (1, 2 o 3).
    """
    init_csv()
    clock = pygame.time.Clock()

    # ── Calcular score inicial según nivel elegido ──
    # get_level() sube de nivel cuando el score alcanza ciertos umbrales.
    # Para arrancar en nivel 2 o 3 necesitamos un score que ya esté
    # dentro de ese rango. Usamos el mínimo score de cada nivel:
    #   nivel 1 → score 0
    #   nivel 2 → score 10
    #   nivel 3 → score 20
    #   nivel 4 → score 28  (no seleccionable desde el menú)
    MIN_SCORE = {1: 0, 2: 10, 3: 20}
    initial_score = MIN_SCORE.get(start_level, 0)

    current_level = start_level
    walls         = get_walls(current_level)
    obstacles     = set()

    s     = Snake(GREEN_BRIGHT, (10, 10))
    s.addCube()
    snack = Cube(randomSnack(s.body, walls | obstacles, level=current_level), color=RED_APPLE)

    score               = initial_score
    lives               = 3
    position_history    = []
    last_obstacle_score = initial_score
    obstacles_placed    = 0
    tick                = 0

    # ── Manzana envenenada ──
    poison_apple       = None
    poison_timer       = 0
    poison_spawn_every = 80

    # ── Manzana vida extra ──
    life_apple       = None
    life_timer       = 0
    life_spawn_every = 150

    flash_timer = 0

    # ── Nivel 3: timer de manzana moviéndose ──
    snack_timer = None

    # ── Nivel 4: rival ──
    rival         = None
    fase_4b       = False
    fase_4b_shown = False

    # Si arranca en nivel 3 (score >= 20), las manzanas ya se mueven
    if current_level == 3:
        snack_timer = SNACK_MOVE_TICKS
        if rival is None:
            rival = Rival((5, 5))

    play_level_music(get_music_key(score, current_level))

    # Mostrar pantalla de nivel si arranca desde nivel 2 o 3
    if start_level > 1:
        draw_level_up(win, current_level)

    while True:
        pygame.time.delay(50)
        clock.tick(FPS)
        tick += 1

        data_count = count_data()

        # ── Victoria ──
        if score >= SCORE_WIN:
            play_victory_music()
            return show_victory(win, score, data_count)

        # ── Cambio de nivel ──
        new_level = get_level(score)
        if new_level != current_level:
            current_level = new_level
            walls         = get_walls(current_level)
            obstacles     = set()
            poison_apple  = None
            life_apple    = None
            snack_timer   = None
            fase_4b_shown = False

            if current_level == 3:
                rival = Rival((5, 5))

            play_level_music(get_music_key(score, current_level))
            draw_level_up(win, current_level)
            spawn = find_safe_spawn(walls, current_level)
            s.reset(spawn)
            s.addCube()
            snack = Cube(randomSnack(s.body, walls | obstacles, level=current_level), color=RED_APPLE)
            redraw(win, s, snack, poison_apple, life_apple,
                   walls, obstacles, score, lives, current_level,
                   data_count, obstacles_placed, tick, rival=rival)
            continue

        # ── Fase 4b ──
        if current_level == 3 and score >= 25 and not fase_4b:
            fase_4b = True
            play_level_music("4b")
        if fase_4b and not fase_4b_shown:
            fase_4b_shown = True
            draw_fase_4b_warning(win)

        # ── Timer de manzana moviéndose (nivel 3) ──
        if current_level == 3:
            if snack_timer is None:
                snack_timer = SNACK_MOVE_TICKS
            else:
                snack_timer -= 1
                if snack_timer <= 0:
                    snack = Cube(
                        randomSnack(s.body, walls | obstacles,
                                    {poison_apple} if poison_apple else set(),
                                    level=current_level),
                        color=RED_APPLE)
                    snack_timer = SNACK_MOVE_TICKS
        else:
            snack_timer = None

        # ── Spawn manzana envenenada ──
        if poison_apple is None and tick % poison_spawn_every == 0 and score >= 3:
            exclude      = {snack.pos} | walls | obstacles
            px, py       = randomSnack(s.body, walls | obstacles, exclude, level=current_level)
            poison_apple = (px, py)
            poison_timer = 40

        if poison_apple:
            poison_timer -= 1
            if poison_timer <= 0:
                poison_apple = None

        # ── Spawn manzana vida extra ──
        if life_apple is None and tick % life_spawn_every == 0 and score >= 5:
            exclude2   = {snack.pos} | walls | obstacles | ({poison_apple} if poison_apple else set())
            lx, ly     = randomSnack(s.body, walls | obstacles, exclude2, level=current_level)
            life_apple = (lx, ly)
            life_timer = 50

        if life_apple:
            life_timer -= 1
            if life_timer <= 0:
                life_apple = None

        # ── Eventos ──
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        # ── Mover serpiente ──
        s.move(events)
        headPos = s.head.pos

        position_history.append(headPos)
        save_row(headPos[0], headPos[1], s.last_dir, len(s.body), score, current_level)

        all_blocked = walls | obstacles

        # ── Actualizar rival (nivel 3) ──
        if rival and current_level == 3:
            rival.update(score, snack.pos, s.body, walls,
                         life_apple=life_apple)

            if life_apple and rival.head.pos == life_apple:
                rival.lives = min(rival.lives + 1, 3)
                life_apple  = None

            if rival.head.pos == snack.pos:
                rival.addCube()
                snack = Cube(
                    randomSnack(s.body, all_blocked,
                                {poison_apple} if poison_apple else set(),
                                level=current_level),
                    color=RED_APPLE)
                if current_level == 3:
                    snack_timer = SNACK_MOVE_TICKS

            if rival.is_dead(walls):
                died_completely = rival.lose_life()
                if died_completely:
                    rival.respawn()

            if rival.collides_with_player(s.body):
                lives -= 1
                if lives <= 0:
                    play_gameover_music()
                    return show_game_over(win, score, current_level, count_data())
                spawn = find_safe_spawn(walls, current_level)
                s.reset(spawn)
                s.addCube()
                snack        = Cube(randomSnack(s.body, all_blocked, level=current_level), color=RED_APPLE)
                poison_apple = None
                life_apple   = None
                hit_pause(win, s, snack, poison_apple, life_apple,
                          walls, obstacles, score, lives, current_level,
                          data_count, obstacles_placed, tick,
                          rival=rival, fase_4b=fase_4b, snack_timer=snack_timer)
                continue

        # ── Colisión con paredes / bordes / obstáculos ──
        hit = (headPos[0] >= 20 or headPos[0] < 0 or
               headPos[1] >= 20 or headPos[1] < 0 or
               headPos in all_blocked)

        if hit:
            lives -= 1
            if lives <= 0:
                play_gameover_music()
                return show_game_over(win, score, current_level, count_data())
            spawn = find_safe_spawn(walls, current_level)
            s.reset(spawn)
            s.addCube()
            snack        = Cube(randomSnack(s.body, all_blocked, level=current_level), color=RED_APPLE)
            poison_apple = None
            life_apple   = None
            if current_level == 3:
                snack_timer = SNACK_MOVE_TICKS
            hit_pause(win, s, snack, poison_apple, life_apple,
                      walls, obstacles, score, lives, current_level,
                      data_count, obstacles_placed, tick,
                      rival=rival, fase_4b=fase_4b, snack_timer=snack_timer)
            continue

        # ── Come manzana normal ──
        if s.body[0].pos == snack.pos:
            s.addCube()
            score += 1
            snack  = Cube(
                randomSnack(s.body, all_blocked,
                            {poison_apple} if poison_apple else set(),
                            level=current_level),
                color=RED_APPLE)
            if current_level == 3:
                snack_timer = SNACK_MOVE_TICKS

            if score % 2 == 0 and score > last_obstacle_score and current_level < 4:
                obstacles = place_obstacle(
                    position_history, obstacles, s.body, snack.pos, walls,
                    level=current_level)
                last_obstacle_score = score
                obstacles_placed   += 1

        # ── Come manzana vida extra ──
        if life_apple and s.body[0].pos == life_apple:
            lives      = min(3, lives + 1)
            life_apple = None

        # ── Come manzana envenenada ──
        if poison_apple and s.body[0].pos == poison_apple:
            lives       -= 1
            poison_apple = None
            flash_timer  = 3
            if lives <= 0:
                play_gameover_music()
                return show_game_over(win, score, current_level, count_data())

        # ── Colisión consigo misma ──
        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x+1:])):
                lives -= 1
                if lives <= 0:
                    play_gameover_music()
                    return show_game_over(win, score, current_level, count_data())
                spawn = find_safe_spawn(walls, current_level)
                s.reset(spawn)
                s.addCube()
                snack        = Cube(randomSnack(s.body, all_blocked, level=current_level), color=RED_APPLE)
                poison_apple = None
                life_apple   = None
                if current_level == 3:
                    snack_timer = SNACK_MOVE_TICKS
                hit_pause(win, s, snack, poison_apple, life_apple,
                          walls, obstacles, score, lives, current_level,
                          data_count, obstacles_placed, tick,
                          rival=rival, fase_4b=fase_4b, snack_timer=snack_timer)
                break

        if flash_timer > 0:
            flash_timer -= 1

        redraw(win, s, snack, poison_apple, life_apple,
               walls, obstacles, score, lives, current_level,
               data_count, obstacles_placed, tick,
               rival=rival, fase_4b=fase_4b,
               flash=(flash_timer > 0),
               snack_timer=snack_timer)


def main():
    pygame.init()
    init_music()

    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Snake")

    while True:
        start_level = show_menu(win)  # ahora devuelve 1, 2, 3 o False
        if not start_level:
            break
        if not game_loop(win, start_level=start_level):
            break

    pygame.quit()


if __name__ == "__main__":
    main()
