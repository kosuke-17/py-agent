# py-agent

@see: https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview

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

## 1. Docker コンテナが実行中か確認

docker ps | grep pgvector

## 2. コンテナの詳細情報を確認

docker inspect pgvector-db

## 3. コンテナのログを確認

docker logs pgvector-db

## 4. ポート マッピングの確認（-p で表示される）

docker port pgvector-db

## 5. コンテナ内から直接接続してみる

docker exec -it pgvector-db psql -U langchain -d langchain

## 6.テーブルを確認

```sql
SELECT
column_name,
data_type,
is_nullable,
column_default
FROM information_schema.columns
WHERE table_name = 'langchain_pg_embedding'
ORDER BY ordinal_position;
```

セーフガード

```propmt
作業時間が10分超える場合は作業を中断して、10分ごとのタスクに分割して、Issueとして実行するためのPromptを作成してください。
それぞれのPromptを`work/service-implementsation-issue-prompt-<番号>.md`に日本語で追記してください。
```

日本語ではなく英語で行う方が正確に動く
プロンプトは選択する。ただプロンプトを投げないで影響範囲を絞り込む
