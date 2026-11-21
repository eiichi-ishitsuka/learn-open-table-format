# Open Table Formats (Apache Iceberg) 設計ガイド・実践ハンズオン

このリポジトリは、Open Table Formats（OTF）の標準フォーマットである Apache Iceberg について、アーキテクチャ設計・移行戦略を解説する「読み物（実践設計・移行ガイド）」と、Google Cloud（GCS / BigLake Metastore / BigQuery）× PyIceberg で自動スキーマ進化と Upsert を体験する「GCP 実機ハンズオン」をまとめたものです。

## ドキュメント構成

### 1. 読み物（実践設計・移行ガイド）

データウェアハウス（DWH）の課題背景から、Apache Iceberg / Delta Lake / Apache Hudi の比較、メダリオンアーキテクチャ、ストレージ設計、データガバナンス（スキーマ進化・PII 消去・WAP）、段階的移行・運用設計までを章別に解説しています。

- [目次: Open Table Formats (OTF) 実践設計・移行ガイド](./docs/guides/00_index.md)
  - [第1章: 背景と従来型 DWH の構造的課題](./docs/guides/01_background_and_dwh_challenges.md)
  - [第2章: OTF の内部構造と主要3フォーマットの比較](./docs/guides/02_otf_architecture_and_formats.md)
  - [第3章: 実践アーキテクチャと導入ロードマップ](./docs/guides/03_architecture_and_roadmap.md)
  - [第4章: Google Cloud Storage のバケット設計とセキュリティ](./docs/guides/04_gcs_design_and_security.md)
  - [第5章: データガバナンス実装（スキーマ進化・PII 消去・WAP）](./docs/guides/05_governance_schema_pii_wap.md)
  - [第6章: 段階的移行（Strangler Fig）と運用・FinOps](./docs/guides/06_migration_and_operations.md)

### 2. ハンズオン（GCP 実機: Apache Iceberg × BigQuery）

実際の Google Cloud（GCS / BigLake Metastore / BigQuery）上で、CSV からの自動スキーマ進化（3 列目へのカラム追加）・列欠損時の `NULL` 補完・Upsert・タイムトラベルをコード変更なしで体験する実践ハンズオンです。

- **01: PyIceberg × BigLake Metastore（Iceberg REST Catalog）版**（軽量・マルチエンジン向け）
  - [手順書 01](./docs/handson/01_gcp_pyiceberg_biglake_handson.md)
  - [01: PyIceberg × BigLake Metastore × BigQuery ハンズオン](./notebooks/01_gcp_pyiceberg_biglake_schema_evolution.ipynb)
- **02: BigQuery 管理 Iceberg テーブル版**（大規模 CSV 分散ロード・`MERGE` 向け）
  - [手順書 02](./docs/handson/02_gcp_bigquery_managed_iceberg_handson.md)
  - [02: BigQuery 管理 Iceberg テーブル ハンズオン](./notebooks/02_gcp_bigquery_managed_iceberg_schema_evolution.ipynb)
