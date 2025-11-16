import pytest
import pygame

from player import Player


@pytest.fixture(scope="module")
def pygame_env():
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def dummy_sprite_sheet(pygame_env):
    """
    Membuat Surface dummy ukuran 192x128, sesuai ukuran rpg_sprite_walk.png
      - TotalFrames = 8  -> frame_width = 192 / 8 = 24
      - ROWS = 4        -> frame_height = 128 / 4 = 32
    """
    width, height = 192, 128
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    return surface


@pytest.fixture
def boundary_rect():
    """Boundary mirip ukuran window 800x600."""
    return pygame.Rect(0, 0, 800, 600)


def create_player(dummy_sprite_sheet):
    """Helper untuk membuat Player dengan posisi awal (50, 50)."""
    return Player(start_pos=(50, 50), sprite_sheet=dummy_sprite_sheet, step_px=10)


def test_initial_frame_size_and_state(dummy_sprite_sheet):
    player = create_player(dummy_sprite_sheet)

    # Ukuran frame harus sesuai dengan logika C#:
    # frameWidth  = sheetWidth / TotalFrames
    # frameHeight = sheetHeight / 4
    assert player.frame_width == 24
    assert player.frame_height == 32

    # State awal
    assert player.current_frame == 0
    assert player.current_row == Player.ROW_DOWN
    assert player.is_moving is False

    # Rect player harus sesuai frame dan start_pos
    assert player.rect.width == player.frame_width
    assert player.rect.height == player.frame_height
    assert player.rect.topleft == (50, 50)

    # Surface image sudah terbentuk dan ukurannya sesuai frame
    assert player.image is not None
    assert player.image.get_width() == player.frame_width
    assert player.image.get_height() == player.frame_height


def test_walk_down_moves_player_and_sets_row(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)

    old_y = player.rect.y
    player.walk(pygame.K_DOWN, boundary_rect)

    # Harus bergerak 10 px ke bawah
    assert player.rect.y == old_y + player.step_px
    assert player.current_row == Player.ROW_DOWN
    assert player.is_moving is True


def test_walk_up_left_right_set_correct_rows(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)

    player.walk(pygame.K_UP, boundary_rect)
    assert player.current_row == Player.ROW_UP

    player.walk(pygame.K_LEFT, boundary_rect)
    assert player.current_row == Player.ROW_LEFT

    player.walk(pygame.K_RIGHT, boundary_rect)
    assert player.current_row == Player.ROW_RIGHT


def test_walk_clamped_at_left_boundary(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)
    # Paksa posisi di paling kiri
    player.rect.x = 0

    player.walk(pygame.K_LEFT, boundary_rect)

    # Tidak boleh negatif (keluar layar)
    assert player.rect.x == 0


def test_walk_clamped_at_top_boundary(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)
    player.rect.y = 0

    player.walk(pygame.K_UP, boundary_rect)

    # Tidak boleh negatif
    assert player.rect.y == 0


def test_walk_clamped_at_right_boundary(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)
    player.rect.x = boundary_rect.width - player.rect.width

    player.walk(pygame.K_RIGHT, boundary_rect)

    # Tidak boleh melewati boundary
    assert player.rect.right == boundary_rect.width


def test_walk_clamped_at_bottom_boundary(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)
    player.rect.y = boundary_rect.height - player.rect.height

    player.walk(pygame.K_DOWN, boundary_rect)

    assert player.rect.bottom == boundary_rect.height


def test_stop_walking_resets_frame_and_flag(dummy_sprite_sheet, boundary_rect):
    player = create_player(dummy_sprite_sheet)

    # Buat seolah-olah sedang bergerak & animasi
    player.walk(pygame.K_DOWN, boundary_rect)
    player.is_moving = True
    player.current_frame = 3

    player.stop_walking()

    assert player.is_moving is False
    assert player.current_frame == 0


def test_animate_only_advances_when_moving(dummy_sprite_sheet):
    player = create_player(dummy_sprite_sheet)

    # Kalau tidak bergerak → frame tidak berubah
    player.is_moving = False
    start_frame = player.current_frame
    player.animate()
    assert player.current_frame == start_frame

    # Kalau bergerak → frame bertambah (modulo TotalFrames)
    player.is_moving = True
    player.current_frame = 0
    player.animate()
    assert player.current_frame == 1

    # Uji wrap di batas TOTAL_FRAMES
    player.current_frame = player.TOTAL_FRAMES - 1
    player.animate()
    assert player.current_frame == 0
