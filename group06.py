import sys
import os
import random
import pygame


# 実行ファイルのディレクトリにカレントディレクトリを変更（素材やスコアファイルの読み込みエラー防止）
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 各自のモジュールをインポートする準備（後ほど合流） ---
# import player    # B君: プレイヤー（カゴ）担当
# import item      # C君: 落ちてくる物体（アイテム）担当
# import judge     # D君: 当たり判定＆スコア担当
# import ui        # E君: UI（文字表示）＆BGM担当
# # import assets    # F君: グラフィック（素材・演出）担当
# import ranking   # G君: リザルト画面（スコア記録・ランキング）担当

# 定数定義（最初の1時間で全員で決める内容の例）
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色の定義（RGB値）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 120, 0) #追加
CYAN = (255, 122, 0) #追加

# 落ちてくるアイテム
ITEM_DEFINITIONS = [
    {"file": "img/apple.png", "type": "good"},
    {"file": "img/banana.png", "type": "good"},
    {"file": "img/peach.png", "type": "good"},
    {"file": "img/strawberry.png", "type": "good"},
    {"file": "img/watermelon.png", "type": "good"},
    {"file": "img/avocado_dmg.png", "type": "bad"},  # これだけマイナスアイテム
]

FONT_FILE = "PixelMplus12-Regular.ttf" #追加G　使用するドットフォントのファイル名
HIGHSCORE_FILE = "highscore.txt"

class ScoreDisplay:
    def __init__(self):
        self.font=pygame.font.Font(None,50)
        self.color=(255, 255 , 255)
        self.rect_center=(100,SCREEN_HEIGHT-50)

    def update(self,screen:pygame.Surface,current_score:int):
        self.image = self.font.render(f"Score: {current_score}", 0,self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.rect_center
        screen.blit(self.image, self.rect)

class TimeDisplay:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.normal_color = (0, 0, 255)
        self.warning_color = (255, 0, 0)
        self.rect_center = (300, SCREEN_HEIGHT - 50)
        
    def _get_text(self, time_left: int) -> str:
        minutes = time_left // 60
        seconds = time_left % 60
        return f"Time: {minutes}:{seconds:02f}"

    def _get_color(self, time_left: int):
        if time_left <= 10:
            return self.warning_color
        else:
            return self.normal_color
        
    def update(self, screen: pygame.Surface, time_left: int):
        # self.image = self.font.render(self._get_text(time_left), 0, self._get_color(time_left))
        # self.rect = self.image.get_rect()
        # self.rect.center = self.rect_center
        # screen.blit(self.image, self.rect)
        pass
        
# ==========================================
# f君 (C0C25082) 担当箇所: が仮で入れたやつ　たぶんあとで消す
# ==========================================
# 
class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    機能ボタンを押されたら左右に動く機能
    """
    delta = {  # 押下キーと移動量の辞書
        # pg.K_UP: (0, -5),      # 上キーが押されたら Y座標を -5（上に移動）
        # pg.K_DOWN: (0, +5),    # 下キーが押されたら Y座標を +5（下に移動）
        pygame.K_LEFT: (-5, 0),
        pygame.K_RIGHT: (+5, 0),
    }
    img0 = pygame.transform.rotozoom(pygame.image.load("fig/3.png"), 0, 1) # デフォルトのこうかとん
    img = pygame.transform.flip(img0, True, False)  # 左右反転して右向きに　上下反転しない
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pygame.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pygame.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pygame.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pygame.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pygame.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pygame.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.img = pygame.image.load("img/basket.png").convert_alpha()
        self.rct: pygame.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pygame.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pygame.transform.rotozoom(pygame.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pygame.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        # if check_bound(self.rct) != (True, True):
        #     self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)

# ==========================================
# ==========================================

def load_highscore():
    """ゲーム起動時に最高スコアを読み込む関数"""
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0


def check_and_save_highscore(current_score, current_highscore):
    """今回のスコアがハイスコアを超えていたらファイルに保存する関数"""
    if current_score > current_highscore:
        current_highscore = current_score
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(current_score))
        return current_score  # 新しいハイスコアを返す
    return current_highscore  # 更新されなければ今のハイスコアをそのまま返す

# ==========================================
# D君 (C0A25136) 担当箇所: 当たり判定＆スコア処理
# ==========================================
class ScoreManager:
    """
    プレイヤーと落ちてくるアイテムの当たり判定、およびスコアの加減算を管理するクラス
    """
    def __init__(self) -> None:
        pass 

    def check_collisions(self, player_rect: pygame.Rect, item_list: list) -> list:
        """
        プレイヤーの矩形とアイテムリストの当たり判定を行うメソッド
        
        Args:
            player_rect (pygame.Rect): プレイヤー（カゴ）の判定領域
            item_list (list): 画面内にあるアクティブなアイテムのリスト
            
        Returns:
            list: 衝突しなかった（画面に残る）アイテムの新しいリスト
        """
        remaining_items: list = []
        # global current_score  # メインループのスコア変数を更新するためにグローバル宣言
        current_score = 0

        for item in item_list:
            # アイテムの判定（相手のコードが辞書型かオブジェクト型かによって調整可能）
            # ここでは一般的な辞書型（"rect"キーにpygame.Rectが入っている）と仮定
            item_rect = item["rect"] if isinstance(item, dict) else item.rect
            item_type = item["type"] if isinstance(item, dict) else item.type

            # colliderect で重なり（衝突）を判定
            if player_rect.colliderect(item_rect):
                # 衝突した場合：スコアの更新
                if item_type == "good":      # 良いアイテム（果物など）
                    current_score += 10
                elif item_type == "bad":     # 悪いアイテム（爆弾など）
                    current_score -= 20
                    if current_score < 0:    # スコアがマイナスにならないように安全処理
                        current_score = 0
                # 衝突したアイテムは remaining_items に追加しない（＝消滅させる）
            else:
                # 衝突しなかったアイテムは次のフレームも残す
                remaining_items.append(item)

        # return remaining_items
        return current_score # currentscore を返す



def main():
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("落ち物キャッチゲーム")
    clock = pygame.time.Clock()
    with open(HIGHSCORE_FILE, "w") as f:
        f.write("0")   

    #こうかとんの初期設定
    player_img = pygame.image.load("fig/9.png")  
    player_rect = player_img.get_rect() 
    player_rect.centerx = SCREEN_WIDTH // 2 
    player_rect.bottom = SCREEN_HEIGHT - 20 
    player_speed = 10
    """
    こうかとんの画像は笑顔の「9.png」を使用しています
    こうかとんはゲーム開始時画面の下側、中央のにいます

    """

    # ゲームの状態管理用変数
    # "TITLE": タイトル画面, "PLAY": ゲーム中, "GAMEOVER": ゲームオーバー（リザルト）画面
    game_state = "TITLE"
    
    # --- [D君・G君合流用変数] スコア管理の土台 ---
    current_score = 0  # 今回のスコア（D君がゲーム中に加算する）
    high_score = 0     # 最高スコア（G君がファイルから読み込む）
    time_left=30 
    high_score =load_highscore() #ゲーム機同時に最高スコアを読み込む
    score_manager = ScoreManager() #class のインスタンス化

    # score_display=ScoreDisplay()
    # time_display=TimeDisplay()


    # ［G君の合流ポイント①: ゲーム起動時に最高スコアを読み込む］
    # 例: high_score = ranking.load_highscore()

    try: #追加G
        font = pygame.font.Font(FONT_FILE, 48)            
        small_font = pygame.font.Font(FONT_FILE, 36)
        large_font = pygame.font.Font(FONT_FILE, 64)
    except Exception:
        # 万が一フォントファイルがない場合のフォールバック（エラー落ち防止）
        print(f"Warning: {FONT_FILE} が見つかりません。デフォルトフォントを使用します。")
        font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 36)
        large_font = pygame.font.SysFont(None, 64)
        
    # フォントの用意（E君・G君のUI表示用フォントが決まるまでの暫定）
    # font = pygame.font.SysFont(None, 48)
    # small_font = pygame.font.SysFont(None, 36)
    start_bg=pygame.image.load("img/start_image.jpg").convert()
    start_bg=pygame.transform.scale(start_bg,(SCREEN_WIDTH,SCREEN_HEIGHT))
    play_bg=pygame.image.load("img/play_image.jpg").convert()
    play_bg=pygame.transform.scale(play_bg,(SCREEN_WIDTH,SCREEN_HEIGHT))

    score_display=ScoreDisplay()
    time_display=TimeDisplay()

    pygame.mixer.init()
    pygame.mixer.music.load("music/start_music.mp3")
    pygame.mixer.music.set_volume(1.5)
    pygame.mixer.music.play(-1)
    get_sound = pygame.mixer.Sound("music/get_music.mp3")
    damage_sound = pygame.mixer.Sound("music/damage_music.mp3") # ダメージ音もセットで！
    #追加G　タイマー用の変数準備
    start_ticks = 0
    time_left = 30
        
    item_images = []
    for item_def in ITEM_DEFINITIONS:
        image = pygame.image.load(item_def["file"])
        item_images.append({"image": image, "type": item_def["type"]})
    # current_item = random.choice(item_images)
    # fruit_image = current_item["image"]
    # fruit_type = current_item["type"]
    # fruit_rect = fruit_image.get_rect()
    # fruit_rect.x = random.randint(0, SCREEN_WIDTH - fruit_rect.width)
    # fruit_rect.y = -fruit_rect.height
    # fruit_speed = random.randint(3, 8)

    active_items = [] 
    # フルーツ出現制御用
    last_spawn_time = 0
    spawn_interval = 500  # ミリ秒（0.5秒）
    
    LANES = [50, 200, 350, 500, 650]  # フルーツが落ちてくる5つの横位置
    last_lane_idx = -1                # 前回選んだレーンの番号を保存する変数
    running = True
    while running:
        # FPS（フレームレート）の設定
        clock.tick(FPS)

        # ==========================================
        # 1. イベント処理（キー入力や閉じるボタンの監視）
        # ==========================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # キーボードが押されたときの処理
            if event.type == pygame.KEYDOWN:
                if game_state == "TITLE":
                    if event.key == pygame.K_SPACE:
                        # タイトル画面でスペースキーを押したらゲーム開始
                        current_score = 0  # スコアをリセット
                        time_left = 30
                        start_ticks = pygame.time.get_ticks() #追加G　タイマー開始
                        active_items.clear() #（前のプレイのフルーツを全部消す）
                        player_rect.centerx = SCREEN_WIDTH // 2
                        player_rect.bottom = SCREEN_HEIGHT - 20
                        game_state = "PLAY"

                elif game_state == "PLAY":
                    # ［B君の合流ポイント①］
                    #ここの処理は［B君の合流ポイント②: プレイヤーの移動更新］と重複するので記述していません
                    pass

                elif game_state == "GAMEOVER":
                    if event.key == pygame.K_SPACE:
                        # 追加G　タイムオーバ画面でスペースキーを押したらタイトルに戻る
                        game_state = "TITLE"

        # ==========================================
        # 2. データ更新処理（ゲームロジック）
        # ==========================================
        if game_state == "TITLE":
            pass

        elif game_state == "PLAY":
            # ［B君の合流ポイント②: プレイヤーの移動更新］
            keys = pygame.key.get_pressed() 
            if keys[pygame.K_LEFT]: 
                player_rect.x -= player_speed 
            if keys[pygame.K_RIGHT]: 
                player_rect.x += player_speed 
            # 画面外に出ないようにする処理 
            if player_rect.left < 0: 
                player_rect.left = 0 
            if player_rect.right > SCREEN_WIDTH: 
                player_rect.right = SCREEN_WIDTH 
            """
            こうかとんの移動可能方向は左右のみです
            画面外には行けないようにしています
            """

            # ［C君合流ポイント①: アイテムの落下更新］
            # ［C君合流ポイント①: アイテムの落下更新］
            # 1. ランダムなタイミングで新しいアイテムを生成（例: 毎フレーム約5%の確率）
            # if random.randint(1, 100) <= 5: 
            #     new_item = random.choice(item_images)
            #     new_rect = new_item["image"].get_rect()
            #     new_rect.x = random.randint(0, SCREEN_WIDTH - new_rect.width)
            #     new_rect.y = -new_rect.height
            #     # 速度を早くする（元の3〜8から、5〜12に変更。好みで調整してください）
            #     new_speed = random.randint(3, 6) 
            # フルーツ出現制御
            now = pygame.time.get_ticks()
        # ずっと同じ頻度で「まばら」に落とす（0.8秒に1個）
            spawn_interval = 350

            if now - last_spawn_time > spawn_interval:
                last_spawn_time = now
                spawn_interval = random.randint(250, 450)
                new_item = random.choice(item_images)
                new_rect = new_item["image"].get_rect()
                # 前回落とした場所（レーン）の「お隣」に流れるように落とす
                if last_lane_idx == -1:
                    last_lane_idx = random.randint(0, len(LANES) - 1)
                else:
                    # ランダムに選ぶが、前回と「同じレーン」になったら引き直す
                    next_lane = random.randint(0, len(LANES) - 1)
                    while next_lane == last_lane_idx:
                        next_lane = random.randint(0, len(LANES) - 1)
                    last_lane_idx = next_lane
                    # 端っこにいるときは、自動的に内側のレーンに戻す（端に溜まるのを防ぐ）
                    if last_lane_idx == 0:
                        last_lane_idx = 1
                    elif last_lane_idx == len(LANES) - 1:
                        last_lane_idx = len(LANES) - 2
                    else:
                        last_lane_idx += random.choice([-1, 1]) # 必ず左右どちらかに動く
                    # step = random.choice([-1, 0, 1])  # 左隣、同じ場所、右隣
                    # last_lane_idx = max(0, min(len(LANES) - 1, last_lane_idx + step))
                # new_rect = new_item["image"].get_rect()
                # 固定されたレーン位置から、左右に「-35 〜 +35ピクセル」のランダムなズレを加えます。
                # これにより、縦にきれいに並びすぎる機械的な不自然さが消え、自然にまばらになります。
                offset = random.randint(-35, 35)
                new_rect.x = LANES[last_lane_idx] + offset #random.randint(0, SCREEN_WIDTH - new_rect.width)
                new_rect.y = -new_rect.height

                # 全て一定のスピードにする（ここでは「4」ピクセルずつ）
                new_speed = random.randint(6, 10)
 
                # リストにアイテムの情報をひとまとめにして追加
                active_items.append({
                    "image": new_item["image"],
                    "type": new_item["type"],
                    "rect": new_rect,
                    "speed": new_speed
                    })

            # 2. リスト内の全アイテムを移動させ、画面外に出たら削除する
            for item in active_items[:]: # [:]をつけてコピーをループすると削除が安全に行えます
                item["rect"].y += item["speed"]
                if item["rect"].top > SCREEN_HEIGHT:
                    active_items.remove(item)
                    # fruit_rect.y += fruit_speed
                    # if fruit_rect.top > SCREEN_HEIGHT:
                    #     current_item = random.choice(item_images)
                    #     fruit_image = current_item["image"]
                    #     fruit_type = current_item["type"]
                    #     fruit_rect = fruit_image.get_rect()
                    #     fruit_rect.x = random.randint(0, SCREEN_WIDTH - fruit_rect.width)
                    #     fruit_rect.y = -fruit_rect.height
                    #     fruit_speed = random.randint(3, 8)

            # ［D君の合流ポイント①: 当たり判定の計算とスコアの加減算］
            # ※ 'player_rect' と 'active_items' は他のメンバーの変数名に合わせて調整してください
            for item in active_items[:]:
                if player_rect.colliderect(item["rect"]):
                    if item["type"] == "good":
                        current_score += 10
                        get_sound.play()
                    elif item["type"] == "bad":
                        current_score -= 20
                        damage_sound.play()
                        if current_score < 0:
                            current_score = 0
                        # キャッチしたアイテムを画面から消す
                    active_items.remove(item)
                    
                    
            # current_item = random.choice(item_images)
            # fruit_image = current_item["image"]
            # fruit_type = current_item["type"]
            # fruit_rect = fruit_image.get_rect()
            # fruit_rect.x = random.randint(0, SCREEN_WIDTH-fruit_rect.width)
            # fruit_rect.y = -fruit_rect.height
            # fruit_speed = random.randint(3, 8)

            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000 #追加G　残り時間の計算
            time_left = 30 - elapsed_seconds
            
            #　追加G　タイムオーバー判定
            if time_left <= 0: 
                time_left = 0
                high_score = check_and_save_highscore(current_score, high_score) #ハイスコアを判定して保存
                high_score = load_highscore()
                game_state = "GAMEOVER"

            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                current_score = 150  # テスト用にスコアが入ったと仮定
                high_score = check_and_save_highscore(current_score, high_score)
                game_state = "GAMEOVER"
        
            # MVP確認用の暫定ルール（エンターキーを押したらゲーム終了・リザルトへ移動）
            # ※本番はD君の判定で「タイムアップ」や「ライフ0」になったら切り替える
                 # ［G君の合流ポイント②: ゲーム終了時にハイスコアを判定して保存］
           
        elif game_state == "GAMEOVER":
            pass

        # ==========================================
        # 3. 描画処理（画面への表示）
        # ==========================================
        screen.fill(BLACK)  # 画面を黒でクリア

        if game_state == "TITLE":

            # タイトル画面の描画（E君・F君の素材が来るまでの暫定表示）
            screen.blit(start_bg,(0,0))
            title_text = font.render("FALLING CATCH GAME", True,(255,215,0))
            start_text = font.render("Press SPACE to Start", True, WHITE)
            screen.blit(title_text, (200, 200))
            screen.blit(start_text, (230, 350))
        elif game_state == "PLAY":
            screen.blit(play_bg,(0,0))
            screen.blit(player_img, player_rect) 
            """スクリーンにこうかとんを映しています"""
            # ［F君・B君の合流ポイント: プレイヤー（カゴ）の描画］
            # ［F君・C君の合流ポイント: アイテム（果物・爆弾）の描画］
            # screen.blit(fruit_image, fruit_rect)
        # ［F君・C君の合流ポイント: アイテム（果物・爆弾）の描画］
            for item in active_items:
                screen.blit(item["image"], item["rect"])
                
            # ［E君の合流ポイント①: 画面上部への「現在のスコア」や「残り時間」の文字描画］
            time_text = font.render(f"TIME: {int(time_left)}",True, WHITE)#追加G　残り時間の表示
            screen.blit(time_text, (20,20))


            # MVP確認用の暫定表示
            score_display.update(screen,current_score)
            time_display.update(screen,time_left)

        elif game_state == "GAMEOVER":
            # ［G君の合流ポイント③: リザルト画面の描画（A君の画面を乗っ取る）］
            # プレイ画面と同じ背景
            screen.blit(play_bg, (0, 0))
            
            over_text = font.render("TIME OVER", True, ORANGE)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(over_text, over_rect)
            
            
            # スコアとハイスコアの表示（G君の担当箇所）
            score_text = small_font.render(f"YOUR SCORE: {current_score}", True, WHITE)
            highscore_text = small_font.render(f"HI-SCORE: {high_score}", True, YELLOW)

            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
            highscore_rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, 340))

            screen.blit(score_text, score_rect)
            screen.blit(highscore_text, highscore_rect)

            retry_text = small_font.render("Press SPACE to Title", True, WHITE)
            screen.blit(retry_text, (260, 450))
            # G君が作成した文字配置や、F君が作ったリザルト背景などをここで描画する
            
        # 画面の更新
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":

    main()