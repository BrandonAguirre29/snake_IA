import pygame
import os
from config import MUSIC_FILES, MUSIC_GAMEOVER, MUSIC_VOLUME, MUSIC_WIN

_current_track = None

def init_music():
    pygame.mixer.init()

def play_level_music(level):
    global _current_track
    if _current_track == level:
        return
    path = MUSIC_FILES.get(level, "")
    if not os.path.exists(path):
        print(f"[Música] No encontrado: {path}")
        _current_track = level
        return
    try:
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1, fade_ms=800)
        _current_track = level
    except Exception as e:
        print(f"[Música] Error: {e}")

def play_gameover_music():
    global _current_track
    if not os.path.exists(MUSIC_GAMEOVER):
        print("[Música] gameover.mp3 no encontrado")
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(MUSIC_GAMEOVER)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(0)   # 0 = una sola vez
        _current_track = "gameover"
    except Exception as e:
        print(f"[Música] Error gameover: {e}")

def play_victory_music():
    global _current_track
    if not os.path.exists(MUSIC_WIN):
        print("[Música] Victory.mp3 no encontrado")
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(MUSIC_WIN)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(0)
        _current_track = "victory"
    except Exception as e:
        print(f"[Música] Error victory: {e}")

def stop_music():
    pygame.mixer.music.fadeout(800)
    global _current_track
    _current_track = None