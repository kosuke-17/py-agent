# py-agent

uv init # pyproject.toml 等を作成（既存 repo でも OK）
uv python pin 3.12 # ← この repo は 3.12 系に固定したい、など
uv python install 3.12 ← 必要なら Python を入れる

```bash
# 実行
uv run python main.py
```

1. リポジトリで初期化（pyproject + .python-version）
   cd your-repo
   uv init # pyproject.toml 等を作成（既存 repo でも OK）
   uv python pin 3.12 # ← この repo は 3.12 系に固定したい、など

uv init は pyproject.toml, .python-version, .gitignore などを作ってくれます。
Astral Docs

uv python pin 3.12 はカレントディレクトリに .python-version を書いて プロジェクト単位で Python を固定。
GitHub

（必要なら Python を入れる）

uv python install 3.12

Astral Docs
+1

2. 仮想環境と依存の同期
   uv venv # .venv/ を作成（後続は自動で検出して使う）
   uv add ruff httpx # 依存追加（pyproject に書かれる）
   uv sync # lock して .venv に反映

uv はデフォで .venv を見つけて使います。
Astral Docs

依存は pyproject.toml に宣言、解決結果は uv.lock に保存されます（ロック&同期の概念）。
Astral Docs

3. 実行系（python/スクリプト/ツール）
   uv run python -V # プロジェクト環境で実行
   uv run python main.py
   uvx ruff check . # ツールを一時環境で実行（pipx 相当の別名）

uv run は実行前に環境を最新化してくれる。
Astral Docs

uvx はツールをインストール不要で即時実行（uv tool run のエイリアス）。
Astral Docs
+1
