import pandas as pd
import numpy as np
import os
from database_connector import extract_transactional_data

def build_features():
    # 1. Fetch raw transaction variables
    df = extract_transactional_data()
    
    # 2. Synchronize date column data types
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    print("Transforming transactional purchase histories into customer metric rows...")
    # 3. Aggregate transaction frequencies to unique user IDs
    customer_matrix = df.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary_value=('price', 'sum'),
        avg_freight=('freight_value', 'mean'),
        first_purchase=('order_purchase_timestamp', 'min'),
        last_purchase=('order_purchase_timestamp', 'max')
    ).reset_index()
    
    # 4. Feature Mathematics
    customer_matrix['customer_lifespan_days'] = (customer_matrix['last_purchase'] - customer_matrix['first_purchase']).dt.days
    customer_matrix['avg_order_value'] = customer_matrix['monetary_value'] / customer_matrix['frequency']
    
    # 5. Model Targets (90 Days No-Purchase window classifies Churn)
    customer_matrix['is_churned'] = (customer_matrix['recency'] > 90).astype(int)
    customer_matrix['historic_ltv'] = customer_matrix['monetary_value']
    
    final_features = customer_matrix.drop(columns=['first_purchase', 'last_purchase'])
    
    # 6. Save data frame out to your data subfolder
    os.makedirs('Data/Processed', exist_ok=True)
    output_path = 'Data/Processed/customer_features.csv'
    final_features.to_csv(output_path, index=False)
    print(f"Feature matrix construction successful! Output saved here: {output_path}")

if __name__ == "__main__":
    build_features()