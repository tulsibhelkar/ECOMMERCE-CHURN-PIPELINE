# ⚡ E-Commerce Executive Churn Management & Revenue Risk Pipeline

An end-to-end Machine Learning and Business Intelligence solution designed to analyze customer churn, quantify revenue exposure, and provide operational retention targeting for e-commerce platforms.

This repository features an automated ETL pipeline, SQL database schema configuration, an **XGBoost** predictive classification engine, and an interactive **Streamlit** executive dashboard.

---

## 🎥 Interactive Dashboard Demo

![Executive Dashboard Demo](assets/dashboard_demo.gif)

---

## 🎯 Key Features & Architecture

* **Database & Pipeline Integration:** Connects directly to **PostgreSQL** (`schema.sql`) for scalable data persistence with dynamic ETL scripts (`feature_engineering.py`).
* **Predictive ML Engine (`train_model.py`):** Trains an **XGBoost Classifier** on transactional and demographic data to output churn probability scores and risk tiers.
* **Executive KPI Ribbon:** Real-time visibility into monitored customer bases, predicted churn rates, average ticket size, and total revenue risk exposure.
* **Interactive Analytics Matrix:** Dynamic Plotly visuals breaking down churn across risk tiers, tenure cohorts, customer value segments (Gold/Silver/Bronze), and shipping overhead.
* **Model Explainability (SHAP):** Global feature importance visualizer highlighting key behavioral drivers behind customer churn spikes.
* **Actionable Watchlist & CSV Export:** Filterable target list displaying high-risk user IDs with single-click CSV export capabilities for automated win-back campaigns.

---

## 📂 Repository Structure

```text
ECOMMERCE-CHURN-PIPELINE/
├── assets/
│   └── dashboard_demo.gif               # Dashboard demo video / GIF
├── Data/
│   ├── Processed/
│   │   ├── customer_features.csv        # Feature-engineered dataset
│   │   └── final_predictions.csv        # Output predictions with churn risk scores
│   └── Raw/
│       ├── olist_customers_dataset.csv  # Olist customer demographic records
│       ├── olist_order_items_dataset.csv# Transactional order data
│       └── olist_orders_dataset.csv     # Delivery and order status data
├── Sql/
│   └── schema.sql                       # PostgreSQL database table schemas
├── src/
│   ├── database_connector.py            # PostgreSQL connection manager
│   ├── feature_engineering.py           # Feature extraction & cohort generation
│   ├── train_model.py                   # XGBoost model training & evaluation pipeline
│   └── app.py                           # Interactive Streamlit Executive Hub
├── .gitignore                           # Files excluded from source control
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation