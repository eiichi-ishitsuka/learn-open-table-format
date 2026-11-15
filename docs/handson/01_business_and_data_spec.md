# 架空ビジネスとデータ仕様（Usagi Craft & Cafe）

このドキュメントでは、ハンズオンで使用する架空企業「Usagi Craft & Cafe」のビジネス背景、4 つのソースデータ（Day 1〜Day 3）、ストレージ構成、および Gold 層のディメンショナルモデルを説明します。

## 1. ビジネス背景

**Usagi Craft & Cafe** は、全国の主要都市にカフェと雑貨店を複数展開し、アプリ会員向けのポイントサービスや EC サイトも運営する BtoC 小売企業です。

- **店舗網**: 北海道・関東・中部・関西・九州の 9 実店舗に加え、EC オンラインストア 1 拠点（計 10 拠点）を展開しています。
- **取り扱い商品**: ドリンク（珈琲・ラテ等）、フード（ケーキ・クッキー等）、雑貨（マグカップ・トートバッグ等）、物販（珈琲豆・ドリップバッグ等）の 4 カテゴリを扱います。
- **会員制度**: アプリ会員には `BRONZE`、`SILVER`、`GOLD` の 3 段階の会員ランク（`membership_tier`）と、利用状況を表すステータス（`ACTIVE` / `WITHDRAWN`）があります。

## 2. ストレージ構成（ローカル 2 バケット再現）

クラウド環境における連携用バケット（DMZ）とレイクハウス本体バケットの分離を、ローカルの 2 ディレクトリで再現しています。

| ローカルパス | クラウド上の対応 | 役割 |
| :--- | :--- | :--- |
| `storage/data-landing/` | 連携用バケット（Landing / DMZ） | 上流システムから出力される生データ（CSV / JSONL）の受け入れ先 |
| `storage/lakehouse-main/bronze/` | レイクハウス本体（Bronze 層） | 生データを OTF 形式で取り込んだ元データ層 |
| `storage/lakehouse-main/silver/` | レイクハウス本体（Silver 層） | クレンジング・重複排除・SCD 履歴管理を行った統合データ層 |
| `storage/lakehouse-main/gold/` | レイクハウス本体（Gold 層） | 分析・BI 向けにスタースキーマへ整形したデータマート層 |
| `storage/lakehouse-main/pii_vault/` | レイクハウス本体（PII 隔離領域） | 氏名・メール・電話番号などの個人情報を分離保管する保護領域 |

## 3. ソースデータ仕様（Landing 層へ出力される生データ）

`src/data_generator.py` により、**Day 1（初期状態）**、**Day 2（差分・スキーマ変化・退会発生）**、**Day 3（異常値混入）** の 3 日分のタイムスライスが `storage/data-landing/day1/` 〜 `day3/` に生成されます。

### 3.1 `crm_customers.csv`（会員 DB ダンプ / 日次全件スナップショット）

- **出力形式**: CSV（毎日全件が出力されるが、前日からの変更は数%のみ）
- **件数推移**: Day 1: 500 件 → Day 2: 515 件（新規 15 件、ランク昇格 15 件、退会 `WITHDRAWN` 10 件） → Day 3: 525 件（新規 10 件、ランク昇格 5 件）
- **主なカラム**: `customer_id`, `name`, `email`, `phone`, `birth_date`, `membership_tier`, `status`, `updated_at`
- **学習テーマ**: 日次全件積み上げの回避（`upsert` による差分反映）、SCD Type 2（履歴保持）、PII 分離と GDPR 遡及マスク・物理削除

### 3.2 `pos_transactions.jsonl`（店舗 POS 売上トランザクション / 日次差分）

- **出力形式**: JSON Lines（各日 300 件の差分イベント）
- **Day 1 カラム**: `transaction_id`, `store_id`, `customer_id`, `product_id`, `quantity`, `unit_price`, `total_amount`, `purchased_at`
- **Day 2 の変化（Schema Drift）**: レジ改修により `payment_method`（文字列）と `discount_amount`（整数）が予告なく追加されます。また、10 件のレコードで `quantity` に `"two"` などの文字列が混入します。
- **Day 3 の変化（データ品質異常）**: 上流バグにより、`total_amount` がマイナス値または NULL となる異常レコードが約 20%（60 件）混入します。
- **学習テーマ**: Schema Merge、`SAFE_CAST` と `_rescued_data` による救済、WAP（Write-Audit-Publish）による異常データ遮断

### 3.3 `erp_products.csv`（商品マスタ）

- **出力形式**: CSV（Day 1: 24 商品、Day 2〜3: 26 商品）
- **Day 1 カラム**: `product_id`, `product_name`, `category`, `price`, `cost`, `launched_at`
- **Day 2 の変化**: `price` カラムが `unit_price` にリネームされ、新商品 2 件（`PRD-025`, `PRD-026`）が追加されます。
- **学習テーマ**: `field-id` ベースのカラム管理によるゼロコピー・カラムリネーム

### 3.4 `store_master.csv`（店舗マスタ）

- **出力形式**: CSV（全期間共通 10 拠点）
- **カラム**: `store_id`, `store_name`, `region`, `prefecture`, `opened_date`
- **学習テーマ**: スキーマ固定の小規模マスタと OTF テーブルの混在 JOIN

## 4. Gold 層のディメンショナルモデル（スタースキーマ）

Notebook 05 では、上記データから分析用のスタースキーマを `gold` 名前空間に構築します。

- **`fct_sales`（売上ファクトテーブル / 注文明細粒度）**
  - `sale_id`, `date_key`, `customer_key`, `product_key`, `store_key`, `payment_method`, `quantity`, `gross_amount`, `discount_amount`, `net_amount`, `purchased_at`
- **`dim_customers`（顧客ディメンション / SCD Type 2 対応）**
  - `customer_key`（サロゲートキー）, `customer_id`, `email_masked`, `membership_tier`, `status`, `valid_from`, `valid_to`, `is_current`
- **`dim_products`（商品ディメンション）**
  - `product_key`, `product_id`, `product_name`, `category`, `unit_price`, `cost`
- **`dim_stores`（店舗ディメンション）**
  - `store_key`, `store_id`, `store_name`, `region`, `prefecture`, `opened_date`
- **`dim_date`（日付ディメンション）**
  - `date_key`（`YYYYMMDD`）, `date`, `day_of_week`, `is_weekend`, `month`, `quarter`, `year`
