# 第6章：既存パイプラインからの移行ガイド（Airflow 2系・dbt・クロスプロジェクト）

[第5章へ戻る](./05_governance_schema_pii_wap.md) | [目次](./00_index.md) | [ハンズオンへ進む](../handson/00_learning_plan.md)

---

## 6.1 既存フォーマットからの変換アプローチ（In-place vs CTAS）

既存のテーブルやファイルをOTFへ移行する際は、用途に応じて以下の2つのアプローチを使い分ける。

- **In-place変換（メタデータ生成のみ）**: 既存のParquetファイルやIcebergテーブルのデータファイルをコピーせず、メタデータのみを生成・変換する方式（[3.3節](./03_architecture_and_roadmap.md)の `CONVERT TO DELTA` など）。
- **CTAS / MERGE による変換**: SQLの `CREATE OR REPLACE TABLE ... AS SELECT` や `MERGE` によって、新しいOTFテーブルとしてGCSへ書き出す方式（6.2節・6.3節）。

---

## 6.2 Apache Airflow 2系におけるCSV / APIデータ連携のIceberg移行手順

Airflowワーカー自体のメモリ不足（OOM）を防ぐため、Parquet変換やメタデータ生成のコンピュートはBigQuery（BigLake）にオフロードする。Airflowはオーケストレーションに徹する構成を基本とする。

1. **Extract（Landingバケットへの配置）**: 既存のAPI取得処理やCSV配置処理は変更せず、`gs://{env}-data-landing/` への生ファイル出力をそのまま維持する。
2. **Load & Transform（IcebergへのUpsert）**: 従来の `GCSToBigQueryOperator`（`bq load`）を `BigQueryInsertJobOperator`（またはdbt `incremental` モデル）に置き換える。SQL内でLandingの生ファイルを一時外部テーブル（`CREATE TEMP EXTERNAL TABLE`、型は文字列等で定義する）として定義し、`SAFE_CAST` やPIIマスクを施しながら `gs://{env}-lakehouse-main/bronze/` 上のBigLake Icebergテーブルへ `MERGE`（または `INSERT`）する。
3. **小〜中規模データの直接書き込み（代替パターン）**: BigQueryのコンピュート課金を避けたい小規模データについては、AirflowのPythonタスク内で `Polars` ＋ `PyIceberg` / `deltalake` を用い、`schema_mode="merge"` を指定して直接GCSへOTF出力する方式も選択できる。ただし、同一テーブルへのBigQueryと外部Pythonからの同時書き込みは避ける。

---

## 6.3 別プロジェクトのBigQueryネイティブテーブルからのIceberg取り込み

他部署や外部システムが別GCPプロジェクトのBigQueryネイティブテーブルとしてデータを提供している場合、中間ファイルのエクスポートを介さず、自プロジェクト側のSQL（またはdbt）1本で直接自プロジェクトのGCSバケットへIcebergとして取り込める。

- **必要なIAM権限**
  - 自プロジェクトのパイプライン実行用サービスアカウントに対し、相手プロジェクトの対象テーブルへの `roles/bigquery.dataViewer` を付与する。
  - 自プロジェクトのBigLake Connectionのサービスアカウントに対し、自プロジェクトのGCSバケットへの `roles/storage.objectAdmin` を付与する。双方のデータセットとGCSバケットのリージョンは `asia-northeast1` で統一する。
- **dbt（`dbt-bigquery`）での実装例**
  - `sources.yml` の `database` に相手プロジェクトIDを指定し、自プロジェクトのモデル設定で `table_type='iceberg'` と `storage_uri='gs://my-lakehouse-main/bronze/...'` を指定して `CREATE OR REPLACE TABLE ... AS SELECT`（または `incremental` での `MERGE`）を実行する。

---

## 6.4 日次全件スナップショット連携のストレージ最適化（パーティション積み上げからの脱却）

- **従来の課題**: アプリケーションDBの全件スナップショットを毎日BigQueryの日付パーティションとして積み上げると、未変更の99%のレコードまで毎日重複保存され、ストレージコストが線形に肥大化する。
- **Icebergでの最適化**: 日付パーティションへの全件追加をやめ、主キーベースの `MERGE`（Upsert）によって「最新状態（SCD Type 1）」または「変更履歴のみ（SCD Type 2）」を更新する運用へ切り替える。
- **Deletion VectorsとSnapshot管理の組み合わせ**: `MERGE` 時のファイル書き換え負荷はDeletion Vectorsで最小化し、不要になった過去スナップショットのParquetファイルは `expire_snapshots` / `VACUUM`（例：7日間保持）で物理削除する。月末時点などの重要スナップショットのみIcebergの `TAG` 機能で保護することで、ストレージコストを圧縮しつつ過去参照要件も満たせる。

---

## 6.5 IcebergソースとBigQueryネイティブソースの混在運用と段階的移行基準

- **テーブル単位での混在は問題なし**: BigQuery上ではIcebergテーブルとネイティブテーブルを意識せず同一SQL内で `JOIN` や `UNION ALL` が可能であり、dbtのSilver層で両者を統合できる（1つのテーブル内部での混在は不可）。
- **段階的移行の優先順位**:
  - **優先度・高（Iceberg化推奨）**: スキーマ変更が頻繁なログ・SaaSデータ、PIIの遡及マスク・削除が必要なデータ、日次全件スナップショットでストレージが肥大化しているデータ、Databricksからも直接参照したいデータ。
  - **優先度・低（ネイティブ維持可）**: スキーマ固定の小規模マスタや、BigQuery内のみで完結し遡及更新も発生しないデータ。
