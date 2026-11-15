# 第3章：アーキテクチャ全体像とフォーマット選定ロードマップ（BigQuery × Databricks）

[第2章へ戻る](./02_otf_architecture_and_formats.md) | [目次](./00_index.md) | [第4章へ進む](./04_gcs_design_and_security.md)

---

## 3.1 東京リージョン（`asia-northeast1`）での対応状況と前提条件

- **GCS上のOTF参照・書き込み**: BigLake外部テーブル（`DELTA_LAKE` / `ICEBERG`）およびBigLake Managed Tables for Apache Icebergは、東京リージョン（`asia-northeast1`）で利用できる。GCSバケット、BigLake Cloud Resource Connection、BigQueryデータセットの3つを `asia-northeast1` で揃えて構築する。
- **フォーマット制約の注意点**: BigQueryがネイティブに書き込み（`INSERT` / `UPDATE` / `MERGE` / dbtでのテーブル作成）をサポートしているOTFは Apache Iceberg のみであり、Delta LakeはBigQueryからは読み込み専用（Read-only）となる。

---

## 3.2 パイプライン設計の2パターン

- **パターンA：マート層（Gold）のみOTF化する構成**
  - ソース（Bronze）や中間層（Silver）は既存の「BigQueryネイティブストレージ ＋ dbt」のまま維持し、最終的なマート層（Gold）のdbtモデルの出力設定だけを `table_type='iceberg'`（BigLake Managed Tables）に変更してGCSへ出力する。
  - **メリット**: 既存のBigQuery＋dbtパイプラインを壊さず、EXPORT/IMPORTバッチなしでDatabricks（AI / BI）から最新マートをゼロコピーで直接参照できる。
- **パターンB：ソース層（Bronze）からOTF化する構成（Zero-ETL / Tのみ実行）**
  - 連携元・CDCツールが直接GCSにOTF出力するか、ELパイプラインでLandingバケットからBronze OTFを作成する。
  - **メリット**: 加工前のローデータ（Bronze）とマート（Gold）の両方に、BigQuery（dbt）とDatabricks（Python / ML）の双方からゼロコピーでアクセスできる。さらに、[第5章](./05_governance_schema_pii_wap.md)で述べるスキーマ変化耐性やPII遡及マスクの恩恵をソース層から受けられる。

---

## 3.3 現在BigQueryメイン・将来Databricks移行を見据えた選定ロードマップ

- **Phase 1（現在：BigQuery＋dbtがメイン）**: BigQueryから直接書き込みが可能な Apache Iceberg を採用し、GCS上に出力してDatabricksから参照する。
- **Phase 2（過渡期：加工処理を徐々にDatabricksへ移行）**: Unity CatalogのIcebergサポートを活用し、既存のIcebergテーブルへDatabricks側から書き込みを引き継ぐ。
- **Phase 3（将来：Databricksがメイン）**: 新規・主要テーブルを Delta Lake（Delta UniForm有効化）で作成する。Databricks固有の最適化機能（Liquid Clustering等）を活用しつつ、UniFormのIcebergメタデータ経由でBigQueryからの後方互換参照も維持する。既存のIcebergテーブルをDelta Lakeへ移行する際も、`CONVERT TO DELTA` によるメタデータのIn-place変換のみでデータコピーなしに移行できる。
