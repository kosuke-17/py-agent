# PGVector ガイド

## PGVector とは

**pgvector** は、PostgreSQL の拡張機能で、ベクトルデータの保存と高速な類似度検索を実現します。特に、RAG（Retrieval-Augmented Generation）や機械学習アプリケーションで活用されています。

## 主な機能

### 1. ベクトルデータ型

- PostgreSQL ネイティブのベクトルデータ型をサポート
- 数値ベクトル（浮動小数点数の配列）を効率的に保存

### 2. ベクトル関数

- ベクトル間の演算に対応
- 複数の距離計算方式をサポート

### 3. 近似最近傍探索（ANN）インデックス

- 高速な類似度検索を実現
- 大規模データセットでも効率的

## 距離計算方式

pgvector では以下の距離計算方法が利用できます：

| 計算方式             | 説明                     | 用途                         |
| -------------------- | ------------------------ | ---------------------------- |
| **コサイン距離**     | ベクトル間の角度の類似度 | テキスト埋め込みの類似度検索 |
| **ユークリッド距離** | ベクトル間の直線距離     | 幾何学的な距離計算           |
| **内積**             | ベクトルの内積           | 方向性のある類似度           |
| **マンハッタン距離** | 座標軸に沿った距離       | グリッドベースの計算         |

## 導入と適用シーン

### 導入の容易さ

- 既存の PostgreSQL 環境に追加するだけで利用可能
- 比較的容易な実装プロセス

### 適用に適したスケール

- **データ量が 1,000 万件以下** の小～中規模システム
- **社内エンジニアが少人数** の場合に最適
- スタートアップやプロトタイプ段階のプロジェクト

## LangChain との連携

### LangChain での活用メリット

LangChain と pgvector を組み合わせることで、以下の処理を簡単に実装できます：

1. **ドキュメントのベクトル化**

   - テキストを埋め込みモデル（OpenAI など）でベクトル化

2. **データベースへの格納**

   - ベクトルデータを PostgreSQL に効率的に保存

3. **類似度検索**
   - ユーザーのクエリに対して最も関連性のある情報を高速に検索

### 実装例

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector

# 埋め込みモデルの初期化
model = OpenAIEmbeddings(model="text-embedding-3-small")

# ドキュメントをベクトル化して保存
db = PGVector.from_documents(
    documents=chunked_documents,
    embedding=model,
    connection_string="postgresql+psycopg://user:password@localhost:5432/dbname"
)

# 類似度検索（k=3で最も似た3件を取得）
results = db.similarity_search("検索クエリ", k=3)
```

## RAG（Retrieval-Augmented Generation）での活用

### RAG とは

LLM に外部のナレッジベースから取得した情報を提供することで、より正確で最新の回答を生成するアプローチ

### pgvector でのメリット

| 従来の方法                 | pgvector の方法        |
| -------------------------- | ---------------------- |
| キーワードベースの全文検索 | 意味的な類似度検索     |
| キーワードに依存           | キーワードに依存しない |
| 検索精度が限定的           | 高い検索精度           |

### 実現できること

- **テキストの意味理解**：キーワード検索ではなく、テキストの意味を理解した検索
- **柔軟な検索**：ユーザーの質問の意図を捉えた関連情報の取得
- **精度の向上**：より正確で関連性の高い情報の提供

## データベーススキーマの基本

pgvector では以下のような CRUD 操作が可能です：

- **Create（作成）**：ベクトルデータをテーブルに挿入
- **Read（読み取り）**：類似度検索によるデータ取得
- **Update（更新）**：既存のベクトルデータを更新
- **Delete（削除）**：不要なベクトルデータを削除

## 注意点

### メタデータ形式の非推奨警告

LangChain 最新版では、メタデータストレージ形式が **JSON から JSONB** へ変更されました：

- 新規環境の場合：自動的に JSONB 形式で保存（対応不要）
- 既存環境の場合：DB マイグレーションが必要な場合がある
- フィルタリング演算子が `$` プレフィックス付きに変更

## 参考資料

- [pgvector - GitHub](https://github.com/pgvector/pgvector)
- [LangChain PGVector ドキュメント](https://python.langchain.com/docs/integrations/vectorstores/pgvector)
- QIITA: pgvector の活用
- Zenn: pgvector 解説記事
  - https://zenn.dev/msmtec/articles/af78a002128240

## まとめ

pgvector は、以下の特徴を備えた強力なベクトル検索ソリューションです：

✅ 導入が容易（既存 PostgreSQL への追加）
✅ 中規模データセットに最適（～ 1000 万件）
✅ LangChain との統合が簡単
✅ RAG アプリケーションに特に有効
✅ 複数の距離計算方式に対応

これにより、従来のキーワード検索では実現できなかった、より自然で精度の高い情報検索が可能になります。
