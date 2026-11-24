"""Build a Tableau-ready order-level retention mart from the Olist public dataset.

Input: a checkout of https://github.com/infobarbosa/dataset-olist (gzip CSV files)
Output: data/ecommerce_retention_tableau.csv

The output grain is one delivered order. Customer-level retention fields are repeated
on each order deliberately so Tableau Public can analyze cohorts without data blending.
"""
from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT.parent / "olist-source" / "data"
OUTPUT = PROJECT / "data" / "ecommerce_retention_tableau.csv"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def rows(filename: str):
    # One source file has a UTF-8 BOM in its header; utf-8-sig handles both cases.
    with gzip.open(SOURCE / filename, "rt", encoding="utf-8-sig", newline="") as file:
        yield from csv.DictReader(file)


def as_date(value: str) -> datetime:
    return datetime.strptime(value, DATE_FORMAT)


def month_start(value: datetime) -> str:
    return value.strftime("%Y-%m-01")


def months_between(start: datetime, end: datetime) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def main() -> None:
    translations = {
        row["product_category_name"]: row["product_category_name_english"]
        for row in rows("product_category_name_translation.csv.gz")
    }
    products = {row["product_id"]: row["product_category_name"] for row in rows("olist_products_dataset.csv.gz")}
    customers = {
        row["customer_id"]: row
        for row in rows("olist_customers_dataset.csv.gz")
    }

    order_items: dict[str, dict] = defaultdict(lambda: {
        "items": 0, "revenue": 0.0, "freight": 0.0, "sellers": set(), "categories": defaultdict(float),
    })
    for row in rows("olist_order_items_dataset.csv.gz"):
        bucket = order_items[row["order_id"]]
        price = float(row["price"])
        bucket["items"] += 1
        bucket["revenue"] += price
        bucket["freight"] += float(row["freight_value"])
        bucket["sellers"].add(row["seller_id"])
        source_category = products.get(row["product_id"])
        category = translations.get(source_category, source_category or "Uncategorized")
        bucket["categories"][category] += price

    payments: dict[str, dict] = defaultdict(lambda: {"value": 0.0, "max_value": -1.0, "type": "Unknown", "installments": 0})
    for row in rows("olist_order_payments_dataset.csv.gz"):
        bucket = payments[row["order_id"]]
        value = float(row["payment_value"])
        bucket["value"] += value
        bucket["installments"] = max(bucket["installments"], int(row["payment_installments"]))
        if value > bucket["max_value"]:
            bucket["max_value"] = value
            bucket["type"] = row["payment_type"]

    reviews: dict[str, list[int]] = defaultdict(list)
    for row in rows("olist_order_reviews_dataset.csv.gz"):
        reviews[row["order_id"]].append(int(row["review_score"]))

    delivered_orders: list[dict] = []
    for row in rows("olist_orders_dataset.csv.gz"):
        if row["order_status"] != "delivered" or not row["order_delivered_customer_date"]:
            continue
        customer = customers[row["customer_id"]]
        purchase = as_date(row["order_purchase_timestamp"])
        delivered = as_date(row["order_delivered_customer_date"])
        estimated = as_date(row["order_estimated_delivery_date"])
        item = order_items[row["order_id"]]
        primary_category = max(item["categories"], key=item["categories"].get, default="Uncategorized")
        score_values = reviews.get(row["order_id"], [])
        delivered_orders.append({
            "order_id": row["order_id"],
            "purchase": purchase,
            "delivered": delivered,
            "estimated": estimated,
            "customer": customer["customer_unique_id"],
            "city": customer["customer_city"].title(),
            "state": customer["customer_state"].upper(),
            "items": item["items"],
            "sellers": len(item["sellers"]),
            "revenue": item["revenue"],
            "freight": item["freight"],
            "payment": payments[row["order_id"]],
            "review": round(sum(score_values) / len(score_values), 2) if score_values else None,
            "category": primary_category,
        })

    by_customer: dict[str, list[dict]] = defaultdict(list)
    for order in delivered_orders:
        by_customer[order["customer"]].append(order)
    for customer_orders in by_customer.values():
        customer_orders.sort(key=lambda order: (order["purchase"], order["order_id"]))
        first_purchase = customer_orders[0]["purchase"]
        lifetime_orders = len(customer_orders)
        for sequence, order in enumerate(customer_orders, start=1):
            order["first_purchase"] = first_purchase
            order["sequence"] = sequence
            order["lifetime_orders"] = lifetime_orders

    headers = [
        "Order ID", "Purchase Date", "Purchase Month", "Customer ID", "Customer City", "Customer State",
        "Primary Category", "Item Count", "Seller Count", "Item Revenue BRL", "Freight BRL", "Payment Value BRL",
        "Primary Payment Type", "Max Installments", "Average Review Score", "Review Sentiment", "Delivery Days",
        "Delivery vs Estimate Days", "Delivery Performance", "First Purchase Date", "Customer Cohort Month",
        "Customer Order Number", "Customer Lifetime Orders", "Customer Type", "Retention Cycle", "Months Since First Purchase",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for order in sorted(delivered_orders, key=lambda order: order["purchase"]):
            review = order["review"]
            if review is None:
                sentiment = "No review"
            elif review >= 5:
                sentiment = "Promoter (5)"
            elif review >= 3:
                sentiment = "Passive (3-4)"
            else:
                sentiment = "Detractor (1-2)"
            delivery_delta = (order["delivered"].date() - order["estimated"].date()).days
            writer.writerow({
                "Order ID": order["order_id"],
                "Purchase Date": order["purchase"].strftime("%Y-%m-%d"),
                "Purchase Month": month_start(order["purchase"]),
                "Customer ID": order["customer"],
                "Customer City": order["city"],
                "Customer State": order["state"],
                "Primary Category": order["category"],
                "Item Count": order["items"],
                "Seller Count": order["sellers"],
                "Item Revenue BRL": f"{order['revenue']:.2f}",
                "Freight BRL": f"{order['freight']:.2f}",
                "Payment Value BRL": f"{order['payment']['value']:.2f}",
                "Primary Payment Type": order["payment"]["type"],
                "Max Installments": order["payment"]["installments"],
                "Average Review Score": "" if review is None else review,
                "Review Sentiment": sentiment,
                "Delivery Days": (order["delivered"].date() - order["purchase"].date()).days,
                "Delivery vs Estimate Days": delivery_delta,
                "Delivery Performance": "Late" if delivery_delta > 0 else "On / early",
                "First Purchase Date": order["first_purchase"].strftime("%Y-%m-%d"),
                "Customer Cohort Month": month_start(order["first_purchase"]),
                "Customer Order Number": order["sequence"],
                "Customer Lifetime Orders": order["lifetime_orders"],
                "Customer Type": "Returning customer" if order["lifetime_orders"] > 1 else "One-time customer",
                "Retention Cycle": "Repeat purchase" if order["sequence"] > 1 else "First purchase",
                "Months Since First Purchase": months_between(order["first_purchase"], order["purchase"]),
            })
    total_revenue = sum(order["payment"]["value"] for order in delivered_orders)
    retained_customers = sum(1 for orders in by_customer.values() if len(orders) > 1)
    print(f"Wrote {len(delivered_orders):,} delivered orders for {len(by_customer):,} customers.")
    print(f"Payment value: R$ {total_revenue:,.2f}; returning customers: {retained_customers:,}.")


if __name__ == "__main__":
    main()
