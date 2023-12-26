import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int],boss_group):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.beam_type = 0
        self.boss_group = boss_group

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def change_beam_type(self, key, score:"Score"):
        # キーに応じてビームの種類を切り替える
        if key == pg.K_1 and score.value >= 50:
            self.kill()
            self.beam_type = 1
        elif key == pg.K_2 and score.value >= 100:
            self.kill()
            self.beam_type = 2
        elif key == pg.K_0:
            self.kill()
            self.beam_type = 0

    def create_beam(self):
        # 現在のビームの種類に応じてビームを作成する
        if self.beam_type == 1:
            return Beam1(self,self.boss_group)
        elif self.beam_type == 2:
            return Beam2(self,self.boss_group)
        elif self.beam_type == 0:
            return Beam(self,self.boss_group)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, boss_group: pg.sprite.Group):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        引数 boss_group：ボスのグループ
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        angle0 = 0
        angle += angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        self.rect.centery = bird.rect.centery + bird.rect.height * self.vy
        self.rect.centerx = bird.rect.centerx + bird.rect.width * self.vx
        self.speed = 10
        self.boss_group = boss_group  # ボスのグループを保持

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        """
        self.rect.move_ip(+self.speed * self.vx, +self.speed * self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

        # ボスに当たった場合
        boss_hit = pg.sprite.spritecollide(self, self.boss_group, False)
        if boss_hit:
            boss_hit[0].damage()  # ボスにダメージを与える
            self.kill()  # ビームを削除する


class Beam1(pg.sprite.Sprite):
    def __init__(self, bird: Bird, boss_group: pg.sprite.Group):
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        angle0 = 0
        angle += angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam_1.png"), angle, 0.5)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        self.boss_group = boss_group  # ボスのグループを保持

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
        # ボスに当たった場合
        boss_hit = pg.sprite.spritecollide(self, self.boss_group, False)
        if boss_hit:
            boss_hit[0].damage()  # ボスにダメージを与える
            self.kill()  # ビームを削除する


class Beam2(pg.sprite.Sprite):
    def __init__(self, bird: Bird, boss_group: pg.sprite.Group):
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        angle0 = 0
        angle += angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam_2.png"), angle, 0.5)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        self.boss_group = boss_group  # ボスのグループを保持

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
        # ボスに当たった場合
        boss_hit = pg.sprite.spritecollide(self, self.boss_group, False)
        if boss_hit:
            boss_hit[0].damage()  # ボスにダメージを与える
            self.kill()  # ビームを削除する


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"{MAIN_DIR}/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    右端から出現してランダムな角度で移動する
    ランダムな距離移動して止まる
    移動中に画面外に出そうになった時も止まる
    """
    imgs = [pg.image.load(f"{MAIN_DIR}/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH, random.randint(200, HEIGHT-200)
        self.vx = random.randint(-10, -6)
        self.vy = random.randint(-6, 6)
        self.bound = random.randint(WIDTH/2, WIDTH-100)  # 停止位置
        self.state = "down"  # 移動状態or停止状態
        self.interval = random.randint(50, 200)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vx, self.vyに基づき移動させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        """
        if self.rect.centerx < self.bound or self.rect.centery < 50 or HEIGHT-200 < self.rect.centery:  # xが停止位置に到達 or yが画面端になったら停止
            self.vx = 0
            self.vy = 0
            self.state = "stop"
        self.rect.centerx += self.vx
        self.rect.centery += self.vy

    def update(self):
        """
        敵機を速度ベクトルself.vx, self.vyに基づき移動させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        """
        if self.rect.centerx < self.bound or self.rect.centery < 50 or HEIGHT-200 < self.rect.centery:  # xが停止位置に到達 or yが画面端になったら停止
            self.vx = 0
            self.vy = 0
            self.state = "stop"
        self.rect.centerx += self.vx
        self.rect.centery += self.vy


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.score_value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50
        self.bird_life = 3
        self.score_image = self.font.render(f"Score: {self.score_value}", 0, self.color)
        self.load_life_image()  # 残機画像の読み込み
        self.score_rect = self.score_image.get_rect()
        self.score_rect.center = 100, HEIGHT-50
        self.life_images = [self.life_image.copy() for _ in range(self.bird_life)]
        self.life_rects = [
            self.life_images[i].get_rect(center=(250 + i * 40, HEIGHT-50)) for i in range(self.bird_life)
        ]

    def load_life_image(self):
        self.life_image = pg.image.load(f"{MAIN_DIR}/fig/2.png")

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        for life_rect in self.life_rects:
            screen.blit(self.life_image, life_rect)  # 同じ画像を表示
        screen.blit(self.image, self.rect)

    def decrease_life(self):
        """
        残機を減らすメソッド
        """
        if self.bird_life > 0:
            self.bird_life -= 1
            self.life_rects.pop()  # 残機画像のリストから最後の画像を取り除く  

    def set_score(self, value):
        """
        スコアを設定するメソッド
        """
        self.score_value = value

    def show_game_over(self, screen):
        """
        ゲームオーバー画面を表示するメソッド
        """
        # ダークなオーバーレイを描画
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # 黒色で透明度を指定

        # ゲームオーバーのテキストを描画
        game_over_font = pg.font.Font(None, 300)
        game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

        # スコアの表示
        score_font = pg.font.Font(None, 200)
        score_text = score_font.render(f"Score: {self.value}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

        # オーバーレイを画面に描画
        screen.blit(overlay, (0, 0))
        
        # テキストを描画
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        pg.display.flip()

        # キー入力を待つ
        wait_for_key = True
        while wait_for_key:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    wait_for_key = False

            pg.time.Clock().tick(30)  # イベントをチェックする頻度を制御
            
            
class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    def __init__(self):
        super().__init__()
        original_image = pg.image.load(f"{MAIN_DIR}/fig/alien1.png")
        self.image = pg.transform.scale(original_image, (200, 200))  # 画像のサイズを拡大
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH + self.rect.width // 2, HEIGHT // 2
        self.speed = 5
        self.max_x = 1400  # 移動を止めるx座標の上限
        self.hp = 15  # ボスのHP
        self.bombs = pg.sprite.Group()

    def update(self, bird: Bird, bombs: pg.sprite.Group) -> None:
        """
        ボスを上下に移動させ、速度ベクトル(-1, dy)に基づき移動させる
        """
        if self.hp <= 0:  # HPが0以下になったらボスは死亡
            self.kill()
            return

        # 上下に移動
        self.rect.centery += self.speed
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.speed *= -1  # 上下の境界に達したら速度の向きを反転

        if self.rect.left < self.max_x:  # 移動範囲の上限を超えていない場合
            self.rect.move_ip(-self.speed, 0)

        # 画面内に収まっているか確認
        if self.rect.left < 0:  
            self.rect.left = 0  # 左端に戻す

        if self.rect.right > WIDTH:  
            self.rect.right = WIDTH  # 右端に戻す
            
        # 定期的に爆弾を生成
        if pg.time.get_ticks() % 30 == 0:
            bomb = Bomb(self, bird)
            self.bombs.add(bomb)
            bombs.add(bomb)  # ボスの爆弾を全体の爆弾グループにも追加

    def damage(self):
        """
        ボスにダメージを与える
        """
        self.hp -= 1


class Drop(pg.sprite.Sprite):
    def __init__(self,enemy: Enemy):
        super().__init__()
        self.image = pg.Surface((15, 15))
        pg.draw.rect(self.image, (0,0,0),(0, 0, 15, 15))
        self.rect= self.image.get_rect(center=enemy.rect.center)
    
    def update(self):
        self.rect.centerx -= 9
        
        
def main():
    pg.display.set_caption("こうかとんシューティング")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)  # scroll 反転した背景を準備
    score = Score()
    boss_group = pg.sprite.Group()
    bird = Bird(3, (900, 400),boss_group)
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    drops = pg.sprite.Group()
    Bird_life = 3
    tmr = 0
    clock = pg.time.Clock()
    keytype = 0
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_0:
                    keytype = 0
                if event.key == pg.K_1:
                    keytype = 1
                if event.key == pg.K_2:
                    keytype = 2
                
                bird.change_beam_type(event.key,score)
                if event.key == pg.K_SPACE:
                    
                    if keytype == 0:
                        beams.add(Beam(bird,boss_group))
                    if keytype == 1 and score.value >= 50:
                        beams.add(Beam1(bird,boss_group))
                    if keytype == 2 and score.value >= 100:
                        beams.add(Beam2(bird,boss_group))
                    beams.add(bird.create_beam()) 
        if tmr * 8 < 9600:  # scroll tmrが一定の値以下の間スクロールする 6400n + 3200
            x = tmr * 8 % 3200
            screen.blit(bg_img, [-x, 0])
            screen.blit(bg_img2, [1600-x, 0])
            screen.blit(bg_img, [3200-x, 0])
        else:  # ボスが出現したらストップ
             screen.blit(bg_img, [0, 0])
            
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))
                
        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            if random.randint(0,100)<50:
                drops.add(Drop(emy))
       
        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            
        if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
            score.decrease_life()
            bird.change_img(8, screen) # こうかとん悲しみエフェクト
            time.sleep(1)
            if score.bird_life == 0:
                score.show_game_over(screen)
                score.update(screen)
                pg.display.update()
                return
              
        if tmr*8 == 9600:
            boss_group.add(Boss())
            
        for drop in pg.sprite.spritecollide(bird, drops, True):
            score.value += 10 
          
        boss_group.update(bird,bombs)
        boss_group.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        drops.update()
        drops.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
