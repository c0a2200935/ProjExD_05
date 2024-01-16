
# シューティングゲーム
# こかんとんスマッシャー

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
横スクロールするステージで戦うゲーム
シューティングゲーム
戦闘機はビームで、敵は爆弾で攻撃する
* 矢印キーで戦闘機を操作
* SPACEキーで向いている方向にビームを発射
* クリア条件：Bossの撃破
## ゲームの実装
###共通基本機能
* 主人公キャラクターに関するクラス(Bird)
* 敵の爆弾に関するクラス(Bomb)
* 主人公キャラクターのビームに関するクラス(Beam)
* 敵が死んだときの爆発クラスに関するクラス(Explosion)
* 敵の生成に関するクラス(Enemy)
* スコア計算に関するクラス(Score)
* 背景、戦闘機、敵の描画
### 担当追加機能
* ドロップ（担当：杉本）:敵を倒した際に低確率で武器がドロップする機能
* 残機の表示,GAMEOVER（担当：植森）：敵からの攻撃が当たると画面左下にある３つの残機が減り0になるとゲームが終了する。また残機がなくなったらゲームオーバーメッセージを表示する。
* Bossを生成(担当：石井)：ゲームが一定時間進とボスを表示する
* ビームの種類の追加(担当：田中)：テンキーでビームを切り替える
* 横スクロール,敵の出現位置(担当：相田)：横スクロールで敵が右から出現するようにする。


### ToDo
- キーによるビームの切り替え実装
- [ ] BossのHPバーの生成
- [ ] Bossを倒した際にExplosionクラスの呼び出し
- [ ] ゲームに適した画像を探す
- [ ] ビームや爆弾が当たったときに音を出す
### メモ
* 1キー:縦長なビーム、2キー:横長なビーム、0キー:デフォルトのビーム　に切り替わります。
* 条件として、縦長ビームはスコア50以上、横長ビームはスコア100以上で発動可能です。（デフォルトビームは無条件で発動可能）
* 横スクロールの停止時間する時間をマージ後にボスの出現時間と合わせる
* zanki:class Birdとclass Scoreとdef main():この三つの中を改良した

