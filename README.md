# E-Commerce Customer Retention Lab

An interactive Tableau portfolio project that turns the historical **Olist Brazilian e-commerce marketplace** dataset into a customer-retention and experience-monitoring dashboard.

## Explore the dashboard

**[Open the interactive Tableau Public dashboard](https://public.tableau.com/app/profile/perumal.marimuthu3867/viz/E-CommerceCustomerRetentionLabOlistMarketplace/RetentionCommandCenter)**

The dashboard is designed for an e-commerce retention or operations team. Click any month, delivery/review cell, or product category to cross-filter the other views; hover for precise values and use the category ranking's sort control to explore the commercial mix.

## Business questions

- How did marketplace payment value evolve month by month?
- Which delivery experiences are associated with promoter, passive, and detractor reviews?
- Which product categories contribute the most marketplace payment value?
- Where should a retention or operations team investigate first?

## Dashboard highlights

| View | What it answers | Interaction |
| --- | --- | --- |
| Monthly Customer Pulse | Revenue momentum across the marketplace's 2016–2018 history | Select a period to filter the dashboard |
| Delivery & Review Matrix | The relationship between delivery performance and customer sentiment | Select a cell to focus the analysis |
| Category Revenue Ranking | Payment value by primary product category | Sort or select a category to filter the other views |

The visual design uses a deliberate **purple–orange–teal** palette: purple for time-series momentum, orange for delivery/review experience, and teal for commercial mix.

## Data and methodology

The project uses the public, anonymized [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), covering orders placed from 2016 to 2018. The Tableau mart is at one delivered-order per row and contains customer, payment, delivery, product-category, and review fields.

Key metric definitions:

- **Revenue:** `SUM([Payment Value BRL])`
- **Orders:** `COUNTD([Order ID])`
- **Customers:** `COUNTD([Customer ID])`
- **Returning customer:** a customer with more than one delivered order in the available historical data
- **Delivery performance:** `Late` when delivery occurred after the estimated date; otherwise `On / early`
- **Review sentiment:** Detractor (1–2), Passive (3–4), Promoter (5), or No review

> This is a historical portfolio analysis of anonymized public data—not a live Olist performance feed. The source data's CC BY-NC-SA 4.0 licensing context should be respected.

## Repository structure

```text
.
├── data/
│   └── ecommerce_retention_tableau.csv   # Tableau-ready delivered-order mart
├── docs/
│   └── PROJECT_PLAN.md                   # stakeholder questions and design plan
├── scripts/
│   └── build_retention_mart.py           # reproducible mart builder
└── README.md
```

## Reproducing the data mart

1. Obtain the Olist source CSV files and place the gzip files under `../olist-source/data/` relative to this repository.
2. Run:

   ```bash
   python scripts/build_retention_mart.py
   ```

3. Connect Tableau Public to `data/ecommerce_retention_tableau.csv`.

## Portfolio takeaway

This project demonstrates an end-to-end analytics workflow: data preparation in Python, documented metric logic, stakeholder-focused dashboard design, and an interactive Tableau Public delivery.
