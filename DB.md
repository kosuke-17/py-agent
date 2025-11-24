DockerのPostgreSQLに接続するコマンドと、docsテーブルを表示するSQLです。

## Dockerコンテナに入るコマンド

**方法1: docker-composeを使用（推奨）**
```bash
docker-compose exec postgres psql -U langchain -d langchain
```

**方法2: dockerコマンドを直接使用**
```bash
docker exec -it langchain-postgres psql -U langchain -d langchain
```

## docsテーブルを表示するSQL

PostgreSQLに接続後、以下のSQLを実行してください：

**テーブル構造を確認**
```sql
\d docs
```

**全データを表示**
```sql
SELECT * FROM docs;
```

**レコード数を確認**
```sql
SELECT COUNT(*) FROM docs;
```

**特定のカラムのみ表示（カラム名が分かっている場合）**
```sql
SELECT id, content FROM docs LIMIT 10;
```

**ワンライナーで実行する場合**
```bash
docker-compose exec postgres psql -U langchain -d langchain -c "SELECT * FROM docs;"
```

または

```bash
docker-compose exec postgres psql -U langchain -d langchain -c "\d docs"
```

`\d docs`でテーブル構造を確認してから、必要なカラムを指定してSELECTしてください。
