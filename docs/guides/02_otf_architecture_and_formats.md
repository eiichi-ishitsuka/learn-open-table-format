# 第2章：OTFの基本構造・カタログ概念・主要フォーマット比較

[第1章へ戻る](./01_background_and_dwh_challenges.md) | [目次](./00_index.md) | [第3章へ進む](./03_architecture_and_roadmap.md)

---

## 2.1 OTFの3層アーキテクチャ

OTFは以下の3層構造によって従来の課題を解決し、データレイクハウス（Data Lakehouse）の中核を担う。

1. **カタログ層（Catalog）**: Unity CatalogやBigLake、Iceberg REST Catalogなどが担う層である。最新メタデータファイルの場所（ポインタ）を記録し、アトミックな更新（CAS: Compare-And-Swap等）を保証する。
2. **メタデータ層（Metadata）**: テーブルのスキーマ、パーティション情報、有効なデータファイル一覧、各ファイルの統計情報（最小値・最大値・NULL数・レコード数など）をJSONやAvro形式で保持する層である。
3. **データ層（Data）**: 実際のレコードが保存されるParquetやORCなどのイミュータブルなカラムナファイル群である。

データを更新する際は、既存のParquetファイルを直接書き換えない。新しいParquetファイル（または差分ファイル）を追加し、「どのファイルが有効か」を示すメタデータのポインタをアトミックに切り替える（スナップショット分離）。

---

## 2.2 「Icebergにおける技術カタログ」と「ビジネス上のデータカタログ」の違いと統合

同じ「カタログ」という名称でも、以下の2つは本来異なるレイヤーの概念である。

1. **Icebergにおける技術カタログ（Technical / Metastore Catalog）**
   - **対象**: クエリエンジン（BigQuery、Spark、Trino、DuckDB等）向け。
   - **役割**: テーブル名に対して「現在どの `metadata.json` が最新のスナップショットか」というファイルポインタを管理する。複数エンジンからの同時書き込み時にアトミックなロック制御（CAS）を行ってACIDトランザクションを保証する仕組みである（例：Iceberg REST Catalog、BigLake Metastore、AWS Glue、Project Nessie）。
2. **ビジネス上のデータカタログ（Business Data Catalog）**
   - **対象**: 人間（アナリスト・開発者）およびAIエージェント向け。
   - **役割**: テーブルやカラムの論理名・ビジネス定義（意味）、データオーナー、リネージ（系譜）、PIIタグやアクセスポリシーを検索・管理する辞書システムである（例：Google Cloud Dataplex、Collibra、DataHub）。
3. **統合トレンドと運用**
   - Databricks Unity Catalog や Google Cloud（BigLake ＋ Dataplex）は、1つのプラットフォーム内に「技術カタログ（メタデータポインタ管理）」と「ビジネスデータカタログ（定義・リネージ・列マスク）」の両方を統合している。
   - 実運用では、dbtの `schema.yml` に記述したカラムの `description` を `persist_docs` 設定によってBigQuery（Dataplex）やUnity Catalogへ自動同期させることで、コードベースで一元管理できる。

---

## 2.3 OTFのメリット・デメリットと高度な機能

### 基本メリット

- **ACIDトランザクション**: 複数ジョブからの同時書き込み制御、書き込み中の安全な読み込み（Snapshot Isolation）、処理失敗時のロールバックを保証する。
- **タイムトラベルと監査**: 過去のスナップショットが残っているため、任意の時点・バージョンのデータをクエリしたり、誤操作時に過去の状態へロールバックしたりできる。GCSのストレージ許容範囲で30日〜数年単位の長期保持が可能である。
- **スキーマ進化（Schema Evolution）**: カラムを名前ではなく一意のID（`field_id`）で管理する。過去Parquetファイルの再書き込みなしで、カラムの追加・削除・リネーム・型拡幅・並び替えがメタデータ操作のみで完結する。
- **パーティション進化（Partition Evolution）**: 過去データの書き直しなしで、月次パーティションから日次・時間次パーティションへ途中で分割定義を切り替えられる。特にApache IcebergのHidden Partitioningで威力を発揮する。
- **ベンダーロックインの回避（マルチエンジン・ゼロコピー共有）**: 単一のGCS上の実データに対して、BigQuery、Databricks、Spark、Trino、DuckDB、Python（Polars等）など複数のエンジンからデータを複製・移動せずに直接アクセスできる。

### 高度な運用メリット

- **多次元クラスタリング（Z-Order / Liquid Clustering）**: 単一カラムのパーティション分割による小ファイル化を防ぎつつ、複数カラム（日付＋顧客ID＋店舗コード等）でParquet内のデータを自動整列させる。これにより、統計情報（Min/Max）を用いたData Skippingを最大化する。
- **変更データキャプチャ（CDF / Incremental Read）のネイティブ出力**: スナップショット間の変更行（`INSERT` / `UPDATE` 前後 / `DELETE`）をそのまま後続パイプラインへ出力でき、Silver→Gold間の差分バッチを軽量化できる。
- **行レベル追跡（Row Lineage）**: 各レコードが「いつ・どのトランザクションで作成・更新されたか」をシステム固有の行IDとバージョン番号で自動追跡する。Delta LakeおよびIceberg v3で対応しており、障害調査や監査の追跡性を高める。
- **シャロー・クローン（Shallow Clone）**: 実データ（Parquet）をコピーせず、メタデータのみを複製して数秒で本番同等データの検証テーブルを立ち上げる。
- **組織間ゼロコピー共有（Delta Sharing等）**: 外部組織や異なるDWH・BIツールに対して、データを物理転送することなく署名付きURL経由で直接共有する。

### デメリットと運用上の注意点

- **Small File Problem（小ファイル問題）**: ストリーミングや高頻度の更新を行うと、小さなParquetファイルとメタデータが大量に生成され、読み込み時のI/O性能が劣化する。
- **定期メンテナンス運用が必須**:
  - **Compaction（`OPTIMIZE`）**: 小ファイルを適切なサイズ（数百MB〜1GB程度）に結合する処理。
  - **Vacuum / Expire Snapshots**: 保持期間を過ぎた古いスナップショットや、参照されなくなった孤立Parquetファイルを物理削除してストレージ容量を回収する処理。
- **書き込み戦略の設計コスト**: 読み込み速度重視の「Copy-on-Write (CoW)」と、書き込み・更新速度重視の「Merge-on-Read (MoR) / Deletion Vectors」をユースケースに応じて使い分ける必要がある。

---

## 2.4 主要3大フォーマットの比較と統合ロードマップ（Iceberg vs Delta Lake）

| 比較項目 | Apache Iceberg | Delta Lake | Apache Hudi |
| :--- | :--- | :--- | :--- |
| **開発元・起源** | Netflix発（Apache財団） | Databricks発（Linux財団） | Uber発（Apache財団） |
| **メタデータ構造** | ツリー構造（Metadata -> Manifest List -> Manifest File） | トランザクションログ（`_delta_log` 内のJSON + Parquet Checkpoint） | タイムラインベース + 内部インデックス |
| **強み・特徴** | エンジン中立性が高い、Hidden Partitioning、テーブル内ブランチ/タグ機能 | Spark / Databricksとの統合が強力、ログ構造が直感的で扱いやすい | プライマリキーによる高速Upsert、CDC・ストリーミング処理に特化 |
| **主な採用基盤** | BigQuery (BigLake), Snowflake, AWS (S3 Tables/Athena), Trino | Databricks, Microsoft Fabric | AWS EMR, ストリーミング基盤 |

### Delta Lake と Apache Iceberg の統合ロードマップ

DatabricksによるTabular社（Iceberg主要開発元）の買収以降、以下の3段階で統合・相互運用が進められている。

1. **メタデータの自動変換（Delta UniForm）【実用化済み】**: Delta Lakeへの書き込みコミットと同時に、裏側でIceberg用のメタデータを自動生成する仕組みである。Deltaで書き込み、Iceberg対応エンジン（BigQuery等）からRead-onlyで参照できる。
2. **カタログ層の統合（Unity Catalog × Iceberg REST API）【実用化済み】**: Unity CatalogがIceberg REST Catalog APIにネイティブ対応し、異なるエンジンからIcebergテーブルに対する双方向のRead/Writeが可能になっている。
3. **仕様の共通化とメタデータ統合（Iceberg v3 / v4 ＆ 次世代Delta）【進行中】**: Deltaが先行していた「Deletion Vectors（バイナリ削除ベクトル）」「Row Lineage」「VARIANT型（半構造化データ）」がIceberg v3仕様に取り込まれ、データ層の仕様が共通化された。将来的にメタデータ構造自体のさらなる統合が進められている。
