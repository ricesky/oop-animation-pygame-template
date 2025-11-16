# oop-animation-pygame

Tutorial ini memperkenalkan **Object-Oriented Programming (OOP)** menggunakan Python dan **PyGame** dengan studi kasus **Sprite Animation**. Mahasiswa akan mempelajari bagaimana memodelkan karakter game sebagai objek `Player`, melakukan animasi sprite sheet, serta menangani input keyboard menggunakan pendekatan OOP.


## Capaian Pembelajaran

1. Mahasiswa memahami konsep sprite sheet dan dasar-dasar animasi 2D.
2. Mahasiswa mampu membuat class `Player` menggunakan paradigma OOP (atribut, state, behavior).
3. Mahasiswa mampu melakukan **cropping frame** dari sprite sheet.
4. Mahasiswa mampu mengimplementasikan animasi karakter (idle, walk) menggunakan OOP dan PyGame.
5. Mahasiswa memahami game loop dan mampu menggabungkan input keyboard dengan animasi sprite.

---

## Lingkungan Pengembangan

1. Platform: Python 3.12+
2. Bahasa: Python
3. Editor/IDE yang disarankan:
   - VS Code + Python Extension
   - Terminal
4. Library:
   - pygame 2.6.1
---

## Cara Menjalankan Project

1. Clone repositori project `oop-animation-pygame` ke direktori lokal Anda:
   ```bash
   git clone https://github.com/USERNAME/oop-animation-pygame.git
   cd oop-animation-pygame
   ````

2. Buat dan aktifkan virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux/macOS
   .venv\Scripts\activate           # Windows
   ```

3. Install dependensi:

   ```bash
   pip install -r requirements.txt
   ```

4. Menjalankan tutorial

   ```bash
   python -m src.main
   ```

5. Menjalankan test

   ```bash
   pytest -q
   ```

> PERINGATAN: Pastikan file audio dan gambar yang dibutuhkan sudah diletakkan di folder `assets/` sebelum menjalankan contoh yang membutuhkan resource tersebut.

---

# Tutorial Sprite Animation dengan PyGame (OOP)

Pada tutorial ini kita akan membangun animasi karakter menggunakan **PyGame** dan **pemrograman berorientasi objek (OOP)**.
Kita akan membuat:

1. Window game
2. Class `Player`
3. Animasi berlari (8 frame per arah)
4. Pergerakan karakter menggunakan tombol panah
5. Class `Level` sebagai game loop OOP

---

# Bagian 1 — Mengenal Sprite Sheet

Sprite sheet yang digunakan berada di:

```
assets/images/rpg_sprite_walk.png
```

Ukuran sprite sheet:

* **192 × 128 piksel**
* Dibagi menjadi **8 kolom** × **4 baris**
* Setiap frame: **24 × 32 piksel**

Mapping baris sprite:

| Row | Arah Karakter   |
| --- | --------------- |
| 0   | Menghadap bawah |
| 1   | Menghadap atas  |
| 2   | Menghadap kiri  |
| 3   | Menghadap kanan |

---

# Bagian 2 — Struktur Proyek

```
oop-animation-pygame/
│
├─ assets/
│   └─ images/
│       └─ rpg_sprite_walk.png
│
└─ src/
    ├─ player.py
    ├─ level.py
    └─ main.py
```

---

# Bagian 3 — Membuat Class Player

Class `Player` bertanggung jawab atas:

* posisi karakter
* frame animasi
* arah gerakan
* perilaku berjalan & berhenti
* menggambar sprite ke layar

---

## 1. Membuat File Player

Buat file:

```
src/player.py
```

Tambahkan kode berikut:

```python
import pygame

class Player:
    ROW_DOWN = 0
    ROW_UP = 1
    ROW_LEFT = 2
    ROW_RIGHT = 3

    TOTAL_FRAMES = 8
    ROWS = 4

    def __init__(self, start_pos, sprite_sheet: pygame.Surface, step_px=10):
        self.sprite_sheet = sprite_sheet
        self.sheet_width, self.sheet_height = self.sprite_sheet.get_size()

        self.frame_width = self.sheet_width // self.TOTAL_FRAMES     # 24 px
        self.frame_height = self.sheet_height // self.ROWS           # 32 px

        self.rect = pygame.Rect(start_pos[0], start_pos[1],
                                self.frame_width, self.frame_height)

        self.current_frame = 0
        self.current_row = self.ROW_DOWN
        self.is_moving = False
        self.step_px = step_px

        self.image = None
        self.update_sprite()
```

---

## 2. Menambahkan Pergerakan

Tambahkan method `walk()`:

```python
    def walk(self, key, boundary_rect):
        self.is_moving = True
        dx = dy = 0

        if key == pygame.K_DOWN:
            self.current_row = self.ROW_DOWN
            dy = self.step_px
        elif key == pygame.K_UP:
            self.current_row = self.ROW_UP
            dy = -self.step_px
        elif key == pygame.K_LEFT:
            self.current_row = self.ROW_LEFT
            dx = -self.step_px
        elif key == pygame.K_RIGHT:
            self.current_row = self.ROW_RIGHT
            dx = self.step_px
        else:
            self.is_moving = False

        if self.is_moving:
            new_x = self.rect.x + dx
            new_y = self.rect.y + dy

            new_x = max(0, min(new_x, boundary_rect.width - self.rect.width))
            new_y = max(0, min(new_y, boundary_rect.height - self.rect.height))

            self.rect.x = new_x
            self.rect.y = new_y
```

---

## 3. Animasi Frame

Tambahkan method `animate()` dan `stop_walking()`:

```python
    def stop_walking(self):
        self.is_moving = False
        self.current_frame = 0
        self.update_sprite()

    def animate(self):
        if self.is_moving:
            self.current_frame = (self.current_frame + 1) % self.TOTAL_FRAMES
            self.update_sprite()
```

---

## 4. Memotong Sprite (Cropping Frame)

Method ini mengambil frame tertentu dari sprite sheet:

```python
    def update_sprite(self):
        src_rect = pygame.Rect(
            self.current_frame * self.frame_width,
            self.current_row * self.frame_height,
            self.frame_width,
            self.frame_height
        )
        self.image = self.sprite_sheet.subsurface(src_rect)
```

---

## 5. Menggambar Player

```python
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
```

---

# Bagian 4 — Membuat Class Level

Class `Level` menjadi game loop utama.

Buat file:

```
src/level.py
```

Isi awalnya:

```python
import os
import pygame
from .player import Player
```

---

## 1. Menginisialisasi Level

```python
class Level:
    PLAYER_INITIAL_POSITION_X = 50
    PLAYER_INITIAL_POSITION_Y = 50
    ANIMATION_INTERVAL = 0.1

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("OOP Sprite Animation")

        self.font = pygame.font.SysFont("Arial", 16)
        self.total_frame_count = 0

        base_dir = os.path.dirname(os.path.dirname(__file__))
        sprite_path = os.path.join(base_dir, "assets", "images", "rpg_sprite_walk.png")

        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

        self.player = Player(
            start_pos=(self.PLAYER_INITIAL_POSITION_X,
                       self.PLAYER_INITIAL_POSITION_Y),
            sprite_sheet=sprite_sheet
        )

        self.animation_accumulator = 0
        self.clock = pygame.time.Clock()
        self.running = True
```

---

## 2. Event Handling (Keyboard)

```python
    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.running = False
        else:
            self.player.walk(event.key, self.screen.get_rect())

    def handle_keyup(self, event):
        self.player.stop_walking()
```

---

## 3. Game Loop

```python
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.animation_accumulator += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self.handle_keyup(event)

            while self.animation_accumulator >= self.ANIMATION_INTERVAL:
                self.animation_accumulator -= self.ANIMATION_INTERVAL
                self.total_frame_count += 1
                self.player.animate()

            self.render()
```

---

## 4. Render ke Layar

```python
    def render(self):
        self.screen.fill((211, 211, 211))

        label = self.font.render(
            f"Total frames: {self.total_frame_count}", True, (0, 0, 0)
        )
        self.screen.blit(label, (10, 10))

        self.player.draw(self.screen)
        pygame.display.flip()
```

---

# Bagian 5 — File main.py

Buat:

```
src/main.py
```

Isi:

```python
import pygame
from .level import Level

def main():
    pygame.init()
    try:
        level = Level()
        level.run()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
```

---

# Menjalankan Program

```bash
python -m src.main
```

---