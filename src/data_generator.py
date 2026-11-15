"""Synthetic data generator for 'Usagi Craft & Cafe' (Day 1 - Day 3)."""

from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from faker import Faker


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _build_stores() -> list[dict[str, Any]]:
    return [
        {"store_id": "STR-001", "store_name": "Usagi 札幌大通店", "region": "北海道", "prefecture": "北海道", "opened_date": "2021-04-01"},
        {"store_id": "STR-002", "store_name": "Usagi 渋谷神南店", "region": "関東", "prefecture": "東京都", "opened_date": "2020-07-15"},
        {"store_id": "STR-003", "store_name": "Usagi 吉祥寺店", "region": "関東", "prefecture": "東京都", "opened_date": "2021-10-01"},
        {"store_id": "STR-004", "store_name": "Usagi 横浜元町店", "region": "関東", "prefecture": "神奈川県", "opened_date": "2022-03-12"},
        {"store_id": "STR-005", "store_name": "Usagi 名古屋栄店", "region": "中部", "prefecture": "愛知県", "opened_date": "2022-09-20"},
        {"store_id": "STR-006", "store_name": "Usagi 金沢香林坊店", "region": "中部", "prefecture": "石川県", "opened_date": "2023-04-05"},
        {"store_id": "STR-007", "store_name": "Usagi 京都烏丸店", "region": "関西", "prefecture": "京都府", "opened_date": "2021-06-18"},
        {"store_id": "STR-008", "store_name": "Usagi 大阪梅田店", "region": "関西", "prefecture": "大阪府", "opened_date": "2020-11-03"},
        {"store_id": "STR-009", "store_name": "Usagi 福岡天神店", "region": "九州", "prefecture": "福岡県", "opened_date": "2023-08-10"},
        {"store_id": "STR-010", "store_name": "Usagi ECオンライン", "region": "オンライン", "prefecture": "全国", "opened_date": "2020-04-01"},
    ]


def _build_products() -> list[dict[str, Any]]:
    items = [
        ("PRD-001", "うさぎブレンド珈琲", "ドリンク", 550, 160, "2020-04-01"),
        ("PRD-002", "宇治抹茶ラテ", "ドリンク", 650, 210, "2020-04-01"),
        ("PRD-003", "キャラメルマキアート", "ドリンク", 620, 190, "2020-06-01"),
        ("PRD-004", "自家製レモネード", "ドリンク", 580, 150, "2021-05-01"),
        ("PRD-005", "クラフトコーラ", "ドリンク", 640, 200, "2022-07-01"),
        ("PRD-006", "アールグレイティー", "ドリンク", 520, 130, "2020-04-01"),
        ("PRD-007", "季節のフルーツソーダ", "ドリンク", 680, 220, "2023-04-01"),
        ("PRD-008", "厚焼きホットケーキ", "フード", 880, 280, "2020-04-01"),
        ("PRD-009", "バスクチーズケーキ", "フード", 720, 240, "2021-02-14"),
        ("PRD-010", "うさぎ型バタークッキー", "フード", 480, 140, "2020-04-01"),
        ("PRD-011", "クロックムッシュ", "フード", 820, 290, "2021-09-01"),
        ("PRD-012", "米粉のシフォンケーキ", "フード", 660, 210, "2022-11-01"),
        ("PRD-013", "カヌレ 2個セット", "フード", 640, 200, "2023-03-01"),
        ("PRD-014", "陶製うさぎマグカップ", "雑貨", 2200, 820, "2020-05-01"),
        ("PRD-015", "キャンバスミニトート", "雑貨", 2600, 950, "2020-08-01"),
        ("PRD-016", "木製コースター 2枚組", "雑貨", 1100, 380, "2021-03-01"),
        ("PRD-017", "ドリップバッグ 5袋入", "物販", 980, 350, "2020-04-01"),
        ("PRD-018", "珈琲豆 ハウスブレンド 200g", "物販", 1650, 620, "2020-04-01"),
        ("PRD-019", "真鍮コーヒースプーン", "雑貨", 1450, 500, "2022-01-15"),
        ("PRD-020", "刺繍ハンカチ", "雑貨", 1320, 440, "2022-06-01"),
        ("PRD-021", "ステンレスタンブラー", "雑貨", 3400, 1300, "2023-01-10"),
        ("PRD-022", "ポストカード 3枚セット", "雑貨", 660, 180, "2021-04-01"),
        ("PRD-023", "オリジナルエコバッグ", "雑貨", 1800, 610, "2022-04-01"),
        ("PRD-024", "和紅茶ティーバッグ 10袋入", "物販", 1280, 450, "2023-06-01"),
    ]
    return [
        {
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "price": price,
            "cost": cost,
            "launched_at": launched,
        }
        for pid, name, cat, price, cost, launched in items
    ]


def _make_customer(fake: Faker, rng: random.Random, idx: int, updated_at: str) -> dict[str, Any]:
    tiers = ["BRONZE", "SILVER", "GOLD"]
    weights = [0.6, 0.3, 0.1]
    return {
        "customer_id": f"CUST-{idx:04d}",
        "name": fake.name(),
        "email": f"user{idx:04d}@{fake.free_email_domain()}",
        "phone": fake.phone_number(),
        "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "membership_tier": rng.choices(tiers, weights=weights, k=1)[0],
        "status": "ACTIVE",
        "updated_at": updated_at,
    }


def generate_all_days(landing_dir: Path, seed: int = 42) -> dict[str, dict[str, int]]:
    """Generate Day 1, Day 2, and Day 3 source files under landing_dir.

    Returns a summary dict mapping day -> filename -> row count.
    """
    fake = Faker("ja_JP")
    Faker.seed(seed)
    rng = random.Random(seed)

    stores = _build_stores()
    products_d1 = _build_products()

    # --- Customers (Day 1: 500, Day 2: 515 full snapshot, Day 3: 525 full snapshot) ---
    customers_d1 = [
        _make_customer(fake, rng, i, "2026-11-01T09:00:00")
        for i in range(1, 501)
    ]

    # Day 2: copy Day 1, promote 15 tiers, mark 10 WITHDRAWN, add 15 new customers
    customers_d2 = [dict(c) for c in customers_d1]
    promote_targets = rng.sample(range(0, 450), 15)
    for idx in promote_targets:
        cur = customers_d2[idx]["membership_tier"]
        customers_d2[idx]["membership_tier"] = "SILVER" if cur == "BRONZE" else "GOLD"
        customers_d2[idx]["updated_at"] = "2026-11-02T09:00:00"

    withdraw_targets = rng.sample(range(450, 500), 10)
    for idx in withdraw_targets:
        customers_d2[idx]["status"] = "WITHDRAWN"
        customers_d2[idx]["updated_at"] = "2026-11-02T09:00:00"

    for i in range(501, 516):
        customers_d2.append(_make_customer(fake, rng, i, "2026-11-02T09:00:00"))

    # Day 3: copy Day 2, promote 5 tiers, add 10 new customers
    customers_d3 = [dict(c) for c in customers_d2]
    for idx in rng.sample(range(0, 400), 5):
        if customers_d3[idx]["status"] == "ACTIVE":
            customers_d3[idx]["membership_tier"] = "GOLD"
            customers_d3[idx]["updated_at"] = "2026-11-03T09:00:00"
    for i in range(516, 526):
        customers_d3.append(_make_customer(fake, rng, i, "2026-11-03T09:00:00"))

    # --- Products (Day 2 renames price -> unit_price and adds 2 items) ---
    products_d2 = [
        {
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "category": p["category"],
            "unit_price": p["price"],
            "cost": p["cost"],
            "launched_at": p["launched_at"],
        }
        for p in products_d1
    ] + [
        {"product_id": "PRD-025", "product_name": "季節限定モンブラン", "category": "フード", "unit_price": 780, "cost": 260, "launched_at": "2026-11-02"},
        {"product_id": "PRD-026", "product_name": "うさぎアクリルキーホルダー", "category": "雑貨", "unit_price": 880, "cost": 240, "launched_at": "2026-11-02"},
    ]
    products_d3 = [dict(p) for p in products_d2]

    # --- POS Transactions ---
    store_ids = [s["store_id"] for s in stores]
    product_price_map = {p["product_id"]: p["price"] for p in products_d1}
    product_price_map.update({"PRD-025": 780, "PRD-026": 880})

    def _gen_pos(
        start_tx: int,
        count: int,
        tx_date: date,
        active_cust_max: int,
        prod_ids: list[str],
        include_drift_cols: bool,
        bad_qty_indices: set[int] | None = None,
        bad_amt_indices: set[int] | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        pay_methods = ["CREDIT_CARD", "QR_PAY", "CASH", "IC_CARD"]
        discounts = [0, 0, 0, 100, 200, 500]
        for offset in range(count):
            tx_num = start_tx + offset
            pid = rng.choice(prod_ids)
            qty = rng.randint(1, 4)
            uprice = product_price_map[pid]
            disc = rng.choice(discounts) if include_drift_cols else 0
            total = max(qty * uprice - disc, 0)
            ts = datetime(tx_date.year, tx_date.month, tx_date.day, rng.randint(9, 20), rng.randint(0, 59), rng.randint(0, 59))

            row: dict[str, Any] = {
                "transaction_id": f"TX-{tx_num:06d}",
                "store_id": rng.choice(store_ids),
                "customer_id": f"CUST-{rng.randint(1, active_cust_max):04d}",
                "product_id": pid,
                "quantity": qty,
                "unit_price": uprice,
                "total_amount": total,
                "purchased_at": ts.isoformat(),
            }
            if include_drift_cols:
                row["payment_method"] = rng.choice(pay_methods)
                row["discount_amount"] = disc

            if bad_qty_indices and offset in bad_qty_indices:
                row["quantity"] = rng.choice(["two", "three", "N/A"])
            if bad_amt_indices and offset in bad_amt_indices:
                row["total_amount"] = None if offset % 2 == 0 else -abs(total or 500)

            rows.append(row)
        return rows

    d1_prod_ids = [p["product_id"] for p in products_d1]
    d2_prod_ids = [p["product_id"] for p in products_d2]

    pos_d1 = _gen_pos(1, 300, date(2026, 11, 1), 500, d1_prod_ids, include_drift_cols=False)
    pos_d2 = _gen_pos(
        301,
        300,
        date(2026, 11, 2),
        515,
        d2_prod_ids,
        include_drift_cols=True,
        bad_qty_indices=set(rng.sample(range(300), 10)),
    )
    pos_d3 = _gen_pos(
        601,
        300,
        date(2026, 11, 3),
        525,
        d2_prod_ids,
        include_drift_cols=True,
        bad_amt_indices=set(rng.sample(range(300), 60)),  # 20% anomalous total_amount
    )

    # Write all files
    cust_cols = ["customer_id", "name", "email", "phone", "birth_date", "membership_tier", "status", "updated_at"]
    store_cols = ["store_id", "store_name", "region", "prefecture", "opened_date"]
    prod_d1_cols = ["product_id", "product_name", "category", "price", "cost", "launched_at"]
    prod_d2_cols = ["product_id", "product_name", "category", "unit_price", "cost", "launched_at"]

    day_specs = {
        "day1": {
            "crm_customers.csv": ("csv", cust_cols, customers_d1),
            "pos_transactions.jsonl": ("jsonl", [], pos_d1),
            "erp_products.csv": ("csv", prod_d1_cols, products_d1),
            "store_master.csv": ("csv", store_cols, stores),
        },
        "day2": {
            "crm_customers.csv": ("csv", cust_cols, customers_d2),
            "pos_transactions.jsonl": ("jsonl", [], pos_d2),
            "erp_products.csv": ("csv", prod_d2_cols, products_d2),
            "store_master.csv": ("csv", store_cols, stores),
        },
        "day3": {
            "crm_customers.csv": ("csv", cust_cols, customers_d3),
            "pos_transactions.jsonl": ("jsonl", [], pos_d3),
            "erp_products.csv": ("csv", prod_d2_cols, products_d3),
            "store_master.csv": ("csv", store_cols, stores),
        },
    }

    summary: dict[str, dict[str, int]] = {}
    for day, files in day_specs.items():
        summary[day] = {}
        for fname, (fmt, cols, rows) in files.items():
            target = landing_dir / day / fname
            if fmt == "csv":
                _write_csv(target, cols, rows)
            else:
                _write_jsonl(target, rows)
            summary[day][fname] = len(rows)
    return summary
