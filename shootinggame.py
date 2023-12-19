import pygame
import sys
import random
import math

class Player:
    def __init__(self, x, y, size, speed, bullet_speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.bullet_speed = bullet_speed
        self.bullets = []

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
        # 画面外にプレイヤーが出ないように制限
        self.x = max(0, min(width - self.size, self.x))

    def shoot(self):
        self.bullets.append(Bullet(self.x + self.size // 2, self.y, self.bullet_speed))
    
    def draw(self):
        pygame.draw.circle(screen, white, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)

class Enemy:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.is_alive = True

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, white, (self.x, self.y, self.size, self.size))

class Bullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.circle(screen, white, (self.x, self.y), 5)

class Item:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 20, 20))

# 初期化
pygame.init()

# 画面設定
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("横スクロールシューティングゲーム")

# 色の設定
white = (255, 255, 255)
black = (0, 0, 0)

# プレイヤーの初期位置と速度
player = Player(width // 2 - 25, height - 100, 50, 10, 15)

# 敵の初期位置と速度
enemy_speed = 5
enemies = []

# アイテムの初期速度
item_speed = 5
items = []

# フォントの設定
font = pygame.font.Font(None, 36)

def spawn_enemy():
    if random.randint(0, 100) < 5:
        enemy_x = random.randint(0, width - 50)
        enemy_y = 0
        enemies.append(Enemy(enemy_x, enemy_y, 50, enemy_speed))

def spawn_item(x, y):
    items.append(Item(x, y, item_speed))

# ゲームループ
clock = pygame.time.Clock()
score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move("left")
    elif keys[pygame.K_RIGHT]:
        player.move("right")

    # 弾の発射
    if keys[pygame.K_SPACE]:
        player.shoot()

    # 敵とアイテムの生成
    spawn_enemy()

    # アイテムの移動
    for item in items:
        item.move()

    # アイテムの描画
    for item in items:
        item.draw()

    # 弾とアイテムの移動および衝突判定
    for bullet in player.bullets:
        bullet.move()
        for enemy in enemies:
            if (
                enemy.x < bullet.x < enemy.x + enemy.size
                and enemy.y < bullet.y < enemy.y + enemy.size
            ):
                player.bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                if random.randint(0, 100) < 50:  # 50%の確率でアイテムドロップ
                    spawn_item(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2)

    # アイテムとプレイヤーの衝突判定
    for item in items:
        if (
            player.x < item.x < player.x + player.size
            and player.y < item.y < player.y + player.size
        ):
            items.remove(item)
            player.bullet_speed = 20  # アイテム取得で弾の速度を上げる
            for angle in range(0, 360, 120):  # 120度ごとに弾を追加
                player.bullets.append(Bullet(player.x + player.size // 2, player.y, player.bullet_speed))

    # 敵の移動およびプレイヤーとの衝突判定
    for enemy in enemies:
        enemy.move()
        if (
            player.x < enemy.x < player.x + player.size
            and player.y < enemy.y < player.y + player.size
        ):
            pygame.quit()
            sys.exit()

    # 画面のクリア
    screen.fill(black)

    # プレイヤーの描画
    player.draw()

    # 敵の描画
    for enemy in enemies:
        enemy.draw()

    # 弾の描画
    for bullet in player.bullets:
        bullet.draw()

    # スコアの表示
    score_text = font.render("Score: " + str(score), True, white)
    screen.blit(score_text, (10, 10))

    # 画面の更新
    pygame.display.flip()

    # フレームレートの設定
    clock.tick(30)
