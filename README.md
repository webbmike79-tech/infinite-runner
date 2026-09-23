# Python Infinite Runner

A simple 2D infinite runner game built with [Pygame](https://www.pygame.org/).

You play as the blue block. Red obstacles spawn off-screen to the right and
move left; jump over them to survive. The game speeds up as your score climbs.

## Run it

```bash
pip install -r requirements.txt
python runner.py
```

## Controls

- **SPACE** — start / jump
- **P** — pause / resume
- After game over, press **SPACE** to restart

## Features

- **High score** persisted to `highscore.txt` between runs.
- **Sound effects** — jump chirp and crash noise, synthesized in code
  (no audio files needed); silently disabled if no audio device is present.
- **Difficulty scaling:** every 5 dodged obstacles, obstacles get faster
  *and* spawn more frequently. The hitbox is slightly forgiving.

## How it works

- **Illusion of movement:** the player stays locked at a fixed x position
  while obstacles move toward them.
- **Gravity engine:** jumping applies a negative Y velocity and gravity pulls
  the player back down each frame.
- **Collision detection:** Pygame's `colliderect()` checks the player and
  obstacle rectangles for overlap.
- **Difficulty scaling:** every 5 dodged obstacles, obstacle speed increases.

## Ideas for upgrades

- Replace the `draw.rect()` blocks with sprites via
  `pygame.image.load('your_image.png')` and `screen.blit()`.
- Add scrolling background layers (parallax).
