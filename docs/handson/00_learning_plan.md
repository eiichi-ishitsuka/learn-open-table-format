# ハンズオン学習プラン（Usagi Craft & Cafe）

架空の BtoC 複数店舗運営企業「Usagi Craft & Cafe」の Day 1〜Day 3 データを用い、ローカル環境だけで Apache Iceberg と Delta Lake の仕組み・ガバナンス・ディメンショナルモデリングを段階的に体験します。

ビジネス設定およびソースデータ・スタースキーマの詳細仕様は [架空ビジネスとデータ仕様（Usagi Craft & Cafe）](./01_business_and_data_spec.md) を参照してください。

## 事前準備

1. **推奨拡張機能のインストール**: VS Code または Antigravity でこのリポジトリを開くと、[.vscode/extensions.json](../../.vscode/extensions.json "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") に記載された `ms-toolsai.jupyter` と `ms-python.python` のインストールが推奨されます。ノートブックを実行するため、両方をインストールしてください。
2. **Python 環境の構築**: リポジトリルートで `uv sync` を実行し、`.venv` 仮想環境を作成します。
3. **カーネルの選択と実行**: 各ノートブックは未実行（出力クリア済み）の状態で保存されています。`notebooks/` 配下の `.ipynb` ファイルを `00` から順に開き、右上の「Select Kernel」から `.venv`（`Python 3`）を選択して上から順にセルを実行してください。

> メンテナンス手順（開発者向け）: ノートブックを編集した際は、`uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb` で全セルの動作を検証したあと、`uv run jupyter nbconvert --clear-output --inplace notebooks/*.ipynb` で出力をクリアし、一時ディレクトリ `storage/` を削除してからコミットします。

## ストレージ構成（ローカル 2 バケット再現）

- `storage/data-landing/`: 連携用バケット（DMZ）の再現。外部システムから出力される生データ（CSV / JSONL）を配置します。
- `storage/lakehouse-main/`: レイクハウス本体バケットの再現。`bronze/`, `silver/`, `gold/`, `pii_vault/` のレイヤーを持ちます。

## ノートブック一覧

| 順序 | ノートブック | 主なテーマ |
| --- | --- | --- |
| 0 | [00\_setup\_and\_data\_generation.ipynb](../../notebooks/00_setup_and_data_generation.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | ストレージ初期化と Day 1〜Day 3 生データの生成・確認 |
| 1 | [01\_otf\_anatomy\_and\_3layers.ipynb](../../notebooks/01_otf_anatomy_and_3layers.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | OTF の 3 層構造、Iceberg / Delta ログ解剖、Data Skipping |
| 2 | [02\_snapshot\_upsert\_and\_scd2.ipynb](../../notebooks/02_snapshot_upsert_and_scd2.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | 日次全件連携のアンチパターン比較、Upsert（SCD Type 1）、SCD Type 2 |
| 3 | [03\_schema\_drift\_and\_evolution.ipynb](../../notebooks/03_schema_drift_and_evolution.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | Schema Merge、`_rescued_data` 救済、ゼロコピー・カラムリネーム |
| 4 | [04\_pii\_governance\_and\_time\_travel.ipynb](../../notebooks/04_pii_governance_and_time_travel.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | PII Vault 分離、GDPR 遡及マスク、`expire_snapshots` / `vacuum` による物理抹消 |
| 5 | [05\_wap\_and\_dimensional\_modeling.ipynb](../../notebooks/05_wap_and_dimensional_modeling.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | Gold 層スタースキーマ構築、DuckDB 分析、WAP パターンとタグ付与 |
| 6 | [06\_maintenance\_and\_gcp\_airflow\_guide.ipynb](../../notebooks/06_maintenance_and_gcp_airflow_guide.ipynb "Ctrl+クリック (Mac: Cmd+クリック) でリンク先を開く") | Small File Problem と Compaction、GCP（BigLake × Databricks × Airflow 2 系）設計リファレンス |
