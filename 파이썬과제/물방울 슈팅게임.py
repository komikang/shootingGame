from tkinter import *
import random
import time
import pygame

pygame.mixer.init()

class Enemy:
    def __init__(self, canvas, image, x, y, speed):
        self.canvas = canvas
        self.image = image
        self.speed = speed
        self.id = self.canvas.create_image(x, y, image=self.image, anchor=NW)
        self.speed_y = random.randint(2,3) 
        self.move_dir = 1

    def move(self):
        self.canvas.move(self.id, -self.speed, 0)
        x, y = self.canvas.coords(self.id) 
        if y <= 0 or y >= 700: 
            self.move_dir *= -1 
        self.canvas.move(self.id, 0, self.speed_y * self.move_dir)

    def get_pos(self):
        return self.canvas.coords(self.id)

    def delete(self):
        self.canvas.delete(self.id)

class ShootingGame:
    def __init__(self):
        self.window = Tk()
        self.window.title("물방울 슈팅게임")
        self.window.geometry("820x983")
        self.window.resizable(0,0)

        self.canvas = Canvas(self.window, width=820, height=983)
        self.canvas.pack()

        # 이미지
        self.bg_image = PhotoImage(file="image/background.png")
        self.player_image = PhotoImage(file="image/player.png").subsample(7)
        self.life_bubble_image = PhotoImage(file="image/bubble_life.png").subsample(16)
        self.bubble_image = PhotoImage(file="image/bubble_attack.png").subsample(40)
        self.shark_image = PhotoImage(file="image/shark.png").subsample(2)
        self.fish1_image = PhotoImage(file="image/fish1.png").subsample(8)
        self.fish2_image = PhotoImage(file="image/fish2.png").subsample(10)
        self.explosion_image = PhotoImage(file="image/explosion.png").subsample(8)

        self.canvas.create_image(0, 0, image=self.bg_image, anchor=NW)

        self.bubble_sound = pygame.mixer.Sound("sound/pop.mp3")
        self.miss_sound = pygame.mixer.Sound("sound/pop2.mp3")
        self.gameover_sound = pygame.mixer.Sound("sound/gameover.mp3")
        pygame.mixer.music.load("sound/back2.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)

        self.player = self.canvas.create_image(10, 250, image=self.player_image, anchor=NW)
        self.keys = set()
        self.window.bind("<KeyPress>", self.key_press)
        self.window.bind("<KeyRelease>", self.key_release)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.bullets = []
        self.enemies = [] 
        self.last_shot = time.time()
        self.enemy_timer = time.time()
        self.running = True

        self.score = 0
        self.score_text = self.canvas.create_text(737, 40, text=f"Score  {self.score}",
                                                  font=("Britannic", 22, "bold"), fill="blue")

        self.lives = 3
        self.lives_icons = []
        self.update_life_icons()

        self.game_loop()
        self.window.mainloop()

    # 키 이벤트
    def key_press(self, event):
        self.keys.add(event.keysym)

    def key_release(self, event):
        if event.keysym in self.keys:
            self.keys.remove(event.keysym)


    def update_life_icons(self):
        for icon in self.lives_icons:
            self.canvas.delete(icon)
        self.lives_icons.clear()

        for i in range(self.lives):
            icon = self.canvas.create_image(515 + i*48, 6, image=self.life_bubble_image, anchor=NW)
            self.lives_icons.append(icon)

    def fire_bullet(self):
        px, py = self.canvas.coords(self.player)
        bullet = self.canvas.create_image(px + self.player_image.width(), py + self.player_image.height()//2,
                                          image=self.bubble_image, anchor=NW)
        self.bullets.append(bullet)

   # 랜덤
    def create_enemy(self): 
        y = random.randint(130, 630) 
        rand = random.random() 
        
        if rand < 0.2: 
            enemy = Enemy(self.canvas, self.shark_image, 800, y, speed=10.5) 
        elif rand < 0.6:
            enemy = Enemy(self.canvas, self.fish1_image, 800, y, speed=8) 
        else: enemy = Enemy(self.canvas, self.fish2_image, 800, y, speed=7) 
        
        self.enemies.append(enemy)

    def game_loop(self):
        if not self.running:
            return
        
        px, py = self.canvas.coords(self.player)
        if "Up" in self.keys and py > 0:
            self.canvas.move(self.player, 0, -10)
        if "Down" in self.keys and py + self.player_image.height() < 983:
            self.canvas.move(self.player, 0, 10)
        if "Left" in self.keys and px > 0: 
            self.canvas.move(self.player, -10, 0) 
        if "Right" in self.keys and px + self.player_image.width() < 820: 
            self.canvas.move(self.player, 10, 0)
        if "space" in self.keys:
            if time.time() - self.last_shot > 0.3:
                self.fire_bullet()
                self.last_shot = time.time()

        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 12, 0)
            bx, by = self.canvas.coords(bullet)
            if bx > 800:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # 적
        if time.time() - self.enemy_timer > 1.3:
            self.create_enemy()
            self.enemy_timer = time.time()

        for enemy in self.enemies[:]:
            enemy.move()
            ex, ey = enemy.get_pos()

            if ex < -100: 
                enemy.delete() 
                self.enemies.remove(enemy) 
                
                self.lives -= 1 
                self.update_life_icons() 
                self.miss_sound.play()
                
                if self.lives <= 0: 
                    self.game_over() 
                    
                continue
 
        for bullet in self.bullets[:]:
            bx, by = self.canvas.coords(bullet)
            bw = self.bubble_image.width()
            bh = self.bubble_image.height()

            overlaps = self.canvas.find_overlapping(bx, by, bx + bw, by + bh)
            
            for enemy in self.enemies[:]:
                if enemy.id in overlaps:
                    self.canvas.delete(bullet)
                    self.bullets.remove(bullet)

                    ex, ey = enemy.get_pos()
                    enemy.delete()
                    self.enemies.remove(enemy)
                    self.bubble_sound.play()

                    explosion = self.canvas.create_image(
                        ex, ey, image=self.explosion_image, anchor=NW)
                    self.window.after(100, lambda e=explosion: self.canvas.delete(e))

                    self.score += 10
                    self.canvas.itemconfig(self.score_text, text=f"Score {self.score}")
                
                    break

        px, py = self.canvas.coords(self.player)
        pw = self.player_image.width()
        ph = self.player_image.height()

        overlaps = self.canvas.find_overlapping(px, py, px + pw, py + ph)

        for enemy in self.enemies[:]:
            if enemy.id in overlaps:
                enemy.delete()
                self.enemies.remove(enemy)
                self.lives -= 1
                self.update_life_icons()
                self.miss_sound.play()
                
                if self.lives <= 0:
                    self.game_over()
                break

        self.window.after(33, self.game_loop)

    # 종료
    def game_over(self):
        self.running = False
        self.gameover_sound.play()
        pygame.mixer.music.stop()
        self.canvas.create_text(400, 490, text="GAME OVER", font=("Stencil", 40), fill="red")

    def on_close(self):
        self.running = False
        pygame.mixer.music.stop()
        self.window.destroy()


ShootingGame()