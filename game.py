import pygame
import random
from PIL import Image

import os

class Game:
    def __init__(self):
        pygame.init()
        # Display Setup
        self.VIRTUAL_WIDTH = 800
        self.VIRTUAL_HEIGHT = 400
        
        # Start in Windowed Mode
        self.screen = pygame.display.set_mode((self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT), pygame.RESIZABLE)
        self.canvas = pygame.Surface((self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT))
        self.fullscreen = False
        
        pygame.display.set_caption("Blink to Jump! (Press 'F' for Fullscreen)")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game constants
        self.GRAVITY = 0.8
        self.JUMP_STRENGTH = -15
        self.GAME_SPEED = 5
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        
        # Player attributes
        # Increased size as requested (Approx 60x90 or 80x80 depending on sprite)
        self.PLAYER_WIDTH = 70
        self.PLAYER_HEIGHT = 90
        # Player attributes
        # Increased size as requested (Approx 60x90 or 80x80 depending on sprite)
        self.PLAYER_WIDTH = 70
        self.PLAYER_HEIGHT = 90
        # Use VIRTUAL dimensions for logic
        self.player_rect = pygame.Rect(50, self.VIRTUAL_HEIGHT - self.PLAYER_HEIGHT, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.player_vel_y = 0
        self.is_jumping = False
        
        # Load Pokemon Animated Sprite
        self.player_frames = []
        self.current_frame_index = 0.0
        self.animation_speed = 0.3 # Frames per update
        
        try:
            pil_image = Image.open("pokeman.gif")
            try:
                while True:
                    # Convert to RGBA
                    frame = pil_image.copy().convert("RGBA")
                    # Convert to Pygame surface
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    pygame_image = pygame.image.fromstring(data, size, mode)
                    # Scale
                    pygame_image = pygame.transform.scale(pygame_image, (self.PLAYER_WIDTH, self.PLAYER_HEIGHT))
                    self.player_frames.append(pygame_image)
                    pil_image.seek(pil_image.tell() + 1)
            except EOFError:
                pass # End of frames
        except Exception as e:
            print(f"Could not load pokeman.gif: {e}")
            self.player_frames = []
        
        # Obstacle attributes
        self.obstacles = []
        self.obstacle_timer = 0
        self.MIN_OBSTACLE_GAP = 60  # frames
        
        # Load Obstacle Images
        self.obstacle_images = []
        try:
            # Small Rock
            small_rock = pygame.image.load("small-rock.png")
            small_rock = pygame.transform.scale(small_rock, (50, 50))
            
            self.obstacle_images = [
                {"image": small_rock, "type": "small"}
            ]
        except pygame.error as e:
            print(f"Could not load obstacle images: {e}")
            self.obstacle_images = []
        
        # Load Background
        self.bg_image = None
        self.bg_x = 0
        # Load Background
        self.bg_image = None
        self.bg_x = 0
        self.bg_x2 = self.VIRTUAL_WIDTH
        try:
            self.bg_image = pygame.image.load("background.gif")
            self.bg_image = pygame.transform.scale(self.bg_image, (self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT))
        except pygame.error as e:
            print(f"Could not load background.gif: {e}")
            
        # Score and Game Over
        self.score = 0
        self.high_score = self.load_high_score()
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.game_over_start_time = 0

    def load_high_score(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read())
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def handle_input(self, input_active):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
                if event.key == pygame.K_SPACE and not self.is_jumping:
                    self.jump()
        
        if input_active:
            if self.game_over:
                # 5 Second Delay Check
                current_time = pygame.time.get_ticks()
                if current_time - self.game_over_start_time > 5000:
                    self.reset_game()
            elif not self.is_jumping:
                self.jump()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT), pygame.RESIZABLE)

    def jump(self):
        self.player_vel_y = self.JUMP_STRENGTH
        self.is_jumping = True

    def update(self):
        if self.game_over:
            return

        # Player physics
        self.player_vel_y += self.GRAVITY
        self.player_rect.y += self.player_vel_y
        
        # Ground collision
        if self.player_rect.bottom >= self.VIRTUAL_HEIGHT:
            self.player_rect.bottom = self.VIRTUAL_HEIGHT
            self.is_jumping = False
            self.player_vel_y = 0

        # Background Scroll
        if self.bg_image:
            self.bg_x -= 2  # Scroll speed
            self.bg_x2 -= 2
            
            if self.bg_x < -self.VIRTUAL_WIDTH:
                self.bg_x = self.VIRTUAL_WIDTH
            if self.bg_x2 < -self.VIRTUAL_WIDTH:
                self.bg_x2 = self.VIRTUAL_WIDTH
        
        # Obstacle generation
        self.obstacle_timer += 1
        if self.obstacle_timer > self.MIN_OBSTACLE_GAP + random.randint(0, 40):
            if self.obstacle_images:
                obs_data = random.choice(self.obstacle_images)
                image = obs_data["image"]
                width, height = image.get_size()
                obstacle_rect = pygame.Rect(self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT - height, width, height)
                self.obstacles.append({"rect": obstacle_rect, "image": image})
            else:
                # Fallback to rects
                obstacle_height = random.randint(30, 70)
                obstacle_rect = pygame.Rect(self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT - obstacle_height, 30, obstacle_height)
                self.obstacles.append({"rect": obstacle_rect, "image": None})
                
            self.obstacle_timer = 0
            
        # Obstacle specific update
        for obstacle in self.obstacles:
            obstacle["rect"].x -= self.GAME_SPEED
            
        # Remove off-screen obstacles
        self.obstacles = [obs for obs in self.obstacles if obs["rect"].x + obs["rect"].width > 0]
        
        # Collision detection
        player_hit = False
        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle["rect"]):
                player_hit = True
                break
        
        if player_hit:
            self.game_over = True
            self.game_over_start_time = pygame.time.get_ticks()
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        else:
            self.score += 1

    def reset_game(self):
        self.score = 0
        self.obstacles = []
        self.player_rect.bottom = self.VIRTUAL_HEIGHT
        self.player_vel_y = 0
        self.is_jumping = False
        self.game_over = False

    def render(self):
        # Draw Background
        if self.bg_image:
            self.canvas.blit(self.bg_image, (self.bg_x, 0))
            self.canvas.blit(self.bg_image, (self.bg_x2, 0))
        else:
            self.canvas.fill(self.WHITE)
        
        # Draw player
        if self.player_frames:
            # Update frame index
            self.current_frame_index += self.animation_speed
            if self.current_frame_index >= len(self.player_frames):
                self.current_frame_index = 0
            
            current_frame = self.player_frames[int(self.current_frame_index)]
            self.canvas.blit(current_frame, self.player_rect)
        else:
            pygame.draw.rect(self.canvas, self.BLACK, self.player_rect)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            if obstacle["image"]:
                self.canvas.blit(obstacle["image"], obstacle["rect"])
            else:
                pygame.draw.rect(self.canvas, self.RED, obstacle["rect"])
            
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.BLACK)
        self.canvas.blit(score_text, (10, 10))
        
        # Draw Game Over
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.canvas.blit(overlay, (0, 0))
            
            # Game Over Text
            go_text = self.font.render("GAME OVER", True, self.WHITE)
            score_final_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, self.WHITE)
            replay_text = self.font.render("Raise Finger to Replay", True, self.WHITE)
            
            center_x = self.VIRTUAL_WIDTH // 2
            
            self.canvas.blit(go_text, (center_x - go_text.get_width() // 2, 100))
            self.canvas.blit(score_final_text, (center_x - score_final_text.get_width() // 2, 150))
            self.canvas.blit(high_score_text, (center_x - high_score_text.get_width() // 2, 190))
            
            # replay text only after 5 seconds
            if pygame.time.get_ticks() - self.game_over_start_time > 5000:
                self.canvas.blit(replay_text, (center_x - replay_text.get_width() // 2, 250))
            else:
                 # Optional: Show countdown
                 time_left = 5 - (pygame.time.get_ticks() - self.game_over_start_time) // 1000
                 wait_text = self.font.render(f"Wait {time_left}s...", True, self.WHITE)
                 self.canvas.blit(wait_text, (center_x - wait_text.get_width() // 2, 250))

        # Scale and draw canvas to screen
        scaled_canvas = pygame.transform.scale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled_canvas, (0, 0))

        pygame.display.flip()

    def step(self):
        self.clock.tick(60)

