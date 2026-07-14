import sys
import os
import pygame


# 実行ファイルのディレクトリにカレントディレクトリを変更（素材やスコアファイルの読み込みエラー防止）
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 各自のモジュールをインポートする準備（後ほど合流） ---
# import player    # B君: プレイヤー（カゴ）担当
# import item      # C君: 落ちてくる物体（アイテム）担当
# import judge     # D君: 当たり判定＆スコア担当
# import ui        # E君: UI（文字表示）＆BGM担当
# import assets    # F君: グラフィック（素材・演出）担当
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

FONT_FILE = "PixelMplus12-Regular.ttf" #追加G　使用するドットフォントのファイル名
HIGHSCORE_FILE = "highscore.txt"

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
        pass  # 初期化処理（必要に応じて拡張可能）

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
        global current_score  # メインループのスコア変数を更新するためにグローバル宣言

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

        return remaining_items



def main():
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("落ち物キャッチゲーム")
    clock = pygame.time.Clock()

    # ゲームの状態管理用変数
    # "TITLE": タイトル画面, "PLAY": ゲーム中, "GAMEOVER": ゲームオーバー（リザルト）画面
    game_state = "TITLE"
    
    # --- [D君・G君合流用変数] スコア管理の土台 ---
    current_score = 0  # 今回のスコア（D君がゲーム中に加算する）
    high_score = 0     # 最高スコア（G君がファイルから読み込む）
    high_score =load_highscore() #ゲーム機同時に最高スコアを読み込む
    score_manager = ScoreManager() #class のインスタンス化

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
    #追加G　タイマー用の変数準備
    start_ticks = 0
    time_left = 30
    
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
                        game_state = "PLAY"

                elif game_state == "PLAY":
                    # ［B君の合流ポイント①］
                    # ゲーム中のキー入力（左右の移動など）は主にB君のモジュールに引き渡す
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
            # ［C君의 合流ポイント①: アイテムの落下更新］
            
            # ［D君の合流ポイント①: 当たり判定の計算とスコアの加減算］
            # ※ 'player_rect' と 'active_items' は他のメンバーの変数名に合わせて調整してください
            # active_items = score_manager.check_collisions(player_rect, active_items)
            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000 #追加G　残り時間の計算
            time_left = 30 - elapsed_seconds
            
            #　追加G　タイムオーバー判定
            if time_left <= 0: 
                time_left = 0
                high_score = check_and_save_highscore(current_score, high_score) #ハイスコアを判定して保存
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
            #タイトル画面を（ドット風、中央揃え）
            title_text = large_font.render("FALLING CATCH GAME", True, ORANGE)  
            start_text = font.render("Press SPACE to Start", True, WHITE)  
            
            title_rect=title_text.get_rect(center=(SCREEN_WIDTH//2,200))   #スタートタイトルの位置設定（画面中央ｘ＝400、y＝200）
            start_rect=start_text.get_rect(center=(SCREEN_WIDTH//2,400)) #スタート文字の位置設定（画面中央X＝400、ｙ＝400)
           
           # 画面に描画
            screen.blit(title_text, title_rect)
            screen.blit(start_text, start_rect)

        elif game_state == "PLAY":
            # ［F君・B君の合流ポイント: プレイヤー（カゴ）の描画］
            # ［F君・C君の合流ポイント: アイテム（果物・爆弾）の描画］
            # ［E君の合流ポイント①: 画面上部への「現在のスコア」や「残り時間」の文字描画］
            time_text = font.render(f"TIME: {int(time_left)}",True, WHITE)#追加G　残り時間の表示
            screen.blit(time_text, (20,20))

            # MVP確認用の暫定表示
            play_text = font.render("Playing... [Enter:Finish]", True, WHITE)
            play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            screen.blit(play_text, play_rect)

        elif game_state == "GAMEOVER":
            # ［G君の合流ポイント③: リザルト画面の描画（A君の画面を乗っ取る）］
            over_text = font.render("TIME OVER",True,RED)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(over_text, over_rect)
            # G君が作成した文字配置や、F君が作ったリザルト背景などをここで描画する
            
            # スコアとハイスコアの表示（G君の担当箇所）
            score_text = small_font.render(f"YOUR SCORE: {current_score}", True, WHITE)
            highscore_text = small_font.render(f"HI-SCORE: {high_score}", True, YELLOW)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
            highscore_rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
            screen.blit(score_text, score_rect)
            screen.blit(highscore_text, highscore_rect)
            
            
            retry_text = small_font.render("Press SPACE to Title", True, WHITE)
            screen.blit(retry_text, (260, 450))

        # 画面の更新
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":

    main()
