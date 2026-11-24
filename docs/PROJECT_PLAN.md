# E-Commerce Customer Retention Lab — Project Plan

## Purpose

Build a Tableau Public portfolio project that explains how customers purchase, return, and rate their marketplace experience. The work will use the Olist Brazilian E-Commerce Public Dataset (2016–2018), an anonymized multi-table marketplace dataset with orders, customers, payments, delivery, product, and review information.

## Primary stakeholder questions

1. How are revenue, customers, and order volume evolving month to month?
2. What share of customers return, and how long does their next purchase take?
3. Which categories, regions, payment methods, and delivery experiences are associated with stronger or weaker customer outcomes?
4. Where should a retention or operations team investigate first?

## Tableau dashboard design

| Zone | Visual | Interaction |
| --- | --- | --- |
| Executive strip | Revenue, orders, customers, repeat-customer rate, average review score | Global date/category/state filters |
| Customer pulse | Monthly revenue and orders trend | Hover tooltips and range selection |
| Retention lab | Cohort month by months-since-first-purchase | Cohort/retention filter |
| Experience drivers | Delivery performance vs. review sentiment | Click a segment to filter the dashboard |
| Commercial mix | Category revenue and customer-state map | Click-to-filter drill-down |

## Deliverables

- Tableau Public workbook with interactive filters and a polished executive layout.
- Reproducible order-level Tableau data mart.
- GitHub repository with a data dictionary, methodology, documented insights, and a GitHub Pages landing page that embeds the Tableau workbook.

## Quality standards

- Use `COUNTD([Order ID])` for orders and `COUNTD([Customer ID])` for customers.
- Use `SUM([Payment Value BRL])` for marketplace payment value; do not use a raw row count for revenue.
- Label the data as an anonymized historical marketplace dataset, not a live Olist performance feed.
- Attribute the Kaggle/Olist source and preserve its CC BY-NC-SA 4.0 license context.
