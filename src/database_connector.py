import pandas as pd
from sqlalchemy import create_engine

def get_db_connection():
    DB_USER = "postgres"
    
    DB_PASSWORD = "1234"  
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "ecommerce_analytics"
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    return engine

def extract_transactional_data():
    engine = get_db_connection()
    query = """
        SELECT 
            c.customer_unique_id,
            o.order_id,
            o.order_status,
            o.order_purchase_timestamp,
            i.price,
            i.freight_value
        FROM staging_orders o
        JOIN staging_customers c ON o.customer_id = c.customer_id
        JOIN staging_order_items i ON o.order_id = i.order_id
        WHERE o.order_status = 'delivered';
    """
    print("Extracting relational records from the active SQL warehouse database...")
    df = pd.read_sql(query, engine)
    return df

if __name__ == "__main__":
    try:
        df = extract_transactional_data()
        print(f"Data verification successful! Retrieved row count shape: {df.shape}")
    except Exception as e:
        print(f"Database connection error: {e}")