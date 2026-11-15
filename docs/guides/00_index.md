# オープンテーブルフォーマット（OTF）技術検証およびApache Iceberg導入・設計ガイド

Apache Icebergを軸としたデータレイクハウスを導入するにあたり、既存DWH運用の課題整理からOTFの基本構造、フォーマット選定ロードマップ、GCSインフラ・セキュリティ設計、データガバナンス、Apache Airflow 2系・dbtを用いた移行・運用手順までを章ごとに整理した設計ガイドである。

Python（`pyiceberg` + `pyarrow` / `polars` / `duckdb`）を用いたApache Icebergのローカル検証ハンズオンは、[../handson/00_learning_plan.md](../handson/00_learning_plan.md) にまとめている。

---

## 章構成

1. [第1章：エグゼクティブサマリーと導入背景](./01_background_and_dwh_challenges.md)
   - 1.1 エグゼクティブサマリー
   - 1.2 従来のデータレイク（Hive形式等）の課題
   - 1.3 通常のBigQueryネイティブテーブルへのロード（従来型DWH運用）の課題
2. [第2章：OTFの基本構造・カタログ概念・主要フォーマット比較](./02_otf_architecture_and_formats.md)
   - 2.1 OTFの3層アーキテクチャ
   - 2.2 「Icebergにおける技術カタログ」と「ビジネス上のデータカタログ」の違いと統合
   - 2.3 OTFのメリット・デメリットと高度な機能
   - 2.4 主要3大フォーマットの比較と統合ロードマップ（Iceberg vs Delta Lake）
3. [第3章：アーキテクチャ全体像とフォーマット選定ロードマップ（BigQuery × Databricks）](./03_architecture_and_roadmap.md)
   - 3.1 東京リージョン（`asia-northeast1`）での対応状況と前提条件
   - 3.2 パイプライン設計の2パターン
   - 3.3 現在BigQueryメイン・将来Databricks移行を見据えた選定ロードマップ
4. [第4章：GCSストレージ設計・パフォーマンス最適化・セキュリティ（IAM/保護）](./04_gcs_design_and_security.md)
   - 4.1 GCSバケットの分割設計
   - 4.2 GCSのオブジェクト数上限とボトルネックへの対策
   - 4.3 GCSストレージクラスの選定指針
   - 4.4 Apache Icebergにおけるスキャン量削減（プルーニングとクラスタリング）
   - 4.5 レイクハウス本体バケットのIAM権限設計
   - 4.6 単一バケット集約における保護・復旧・特権オーバーライド対策
5. [第5章：データガバナンス・スキーマ変化耐性・PII保護・ブランチ運用（WAP）](./05_governance_schema_pii_wap.md)
   - 5.1 スキーマの変化（Schema Drift）への耐性
   - 5.2 個人情報（PII）のマスキングと削除要求（GDPR等）への対応
   - 5.3 データのGit管理（ブランチ・タグ）とWAP（Write-Audit-Publish）パターン
6. [第6章：既存パイプラインからの移行ガイド（Airflow 2系・dbt・クロスプロジェクト）](./06_migration_and_operations.md)
   - 6.1 既存フォーマットからの変換アプローチ（In-place vs CTAS）
   - 6.2 Apache Airflow 2系におけるCSV / APIデータ連携のIceberg移行手順
   - 6.3 別プロジェクトのBigQueryネイティブテーブルからのIceberg取り込み
   - 6.4 日次全件スナップショット連携のストレージ最適化（パーティション積み上げからの脱却）
   - 6.5 IcebergソースとBigQueryネイティブソースの混在運用と段階的移行基準
