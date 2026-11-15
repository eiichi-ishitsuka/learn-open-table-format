# Open Table Formats (Apache Iceberg) 設計ガイド・実践ハンズオン

このリポジトリは、Open Table Formats（OTF）の標準フォーマットである Apache Iceberg について、アーキテクチャ設計・移行戦略を解説する「読み物（実践設計・移行ガイド）」と、ローカルの Python ノートブックで3層メタデータ構造・ガバナンス・運用保守を検証する「ハンズオン教材」をまとめたものです。

学習の進め方や環境構築の手順は `docs/` 配下に整理しています。目的に応じて以下のドキュメントを参照してください。

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

### 2. ハンズオン（ローカル完結・Jupyter ノートブック）

読み物の各章と連動し、`pyiceberg`・`deltalake`・`polars`・`duckdb` を用いて架空企業「Usagi Craft & Cafe」のデータを題材に OTF の内部動作・ガバナンス・ディメンショナルモデリングを検証する全 7 冊のノートブックです。ノートブックは未実行の状態で格納しているため、手元の環境で `00` から順に実行して動作を確認できます。

- [学習手順・環境構築: OTF 実践ハンズオン](./docs/handson/00_learning_plan.md)
- [架空ビジネスとデータ仕様（Usagi Craft & Cafe）](./docs/handson/01_business_and_data_spec.md)
  - [00: 環境初期化とサンプルデータ生成](./notebooks/00_setup_and_data_generation.ipynb)
  - [01: OTF の 3 層構造とメタデータ解剖（Iceberg / Delta Lake）](./notebooks/01_otf_anatomy_and_3layers.ipynb)
  - [02: 日次全件スナップショットの最適化（Upsert と SCD Type 2）](./notebooks/02_snapshot_upsert_and_scd2.ipynb)
  - [03: スキーマ進化（Schema Evolution）とドリフト耐性](./notebooks/03_schema_drift_and_evolution.ipynb)
  - [04: PII 保護・遡及削除（GDPR/CCPA）とタイムトラベル](./notebooks/04_pii_governance_and_time_travel.ipynb)
  - [05: ディメンショナルモデリング（Gold 層）と WAP パターン](./notebooks/05_wap_and_dimensional_modeling.ipynb)
  - [06: メンテナンス（Compaction）と GCP / Airflow 実践リファレンス](./notebooks/06_maintenance_and_gcp_airflow_guide.ipynb)
