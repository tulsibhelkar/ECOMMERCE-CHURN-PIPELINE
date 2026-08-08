import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sqlalchemy import create_engine  # Added for PostgreSQL connection
import os

def train_pipeline():
    feature_path = 'Data/Processed/customer_features.csv'
    if not os.path.exists(feature_path):
        print("Feature matrix not discovered locally. Initializing feature calculations...")
        import feature_engineering
        feature_engineering.build_features()
        
    df = pd.read_csv(feature_path)
    
    # Extract structural calculation parameters
    X = df.drop(columns=['customer_unique_id', 'is_churned', 'historic_ltv', 'monetary_value'])
    y = df['is_churned']
    
    # Stratified target division mapping
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\nTraining predictive machine learning engine (XGBoost)...")
    model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    print("\n==================== PIPELINE EVALUATION METRICS ====================")
    print(classification_report(y_test, preds))
    print(f"ROC-AUC Performance Score: {roc_auc_score(y_test, probs):.4f}")
    print("=====================================================================\n")
    
    # Generate predictions
    print("Generating advanced customer risk tiers...")
    df['churn_probability'] = model.predict_proba(X)[:, 1]
    df['is_churned'] = model.predict(X)
    
    # 1. Create Tenure Tiers matching the design layout
    def categorize_tenure(days):
        if days <= 30: return '0-1 Month'
        elif days <= 180: return '2-6 Months'
        elif days <= 365: return '1 Year'
        else: return '2+ Years'
    df['Tenure_Cohort'] = df['customer_lifespan_days'].apply(categorize_tenure)
    
    # 2. Create Corporate Value Segments based on average order spend
    def categorize_value(val):
        if val <= 50: return 'Bronze (Low Spend)'
        elif val <= 150: return 'Silver (Mid Spend)'
        else: return 'Gold (VIP High Spend)'
    df['Customer_Value_Segment'] = df['avg_order_value'].apply(categorize_value)
    
    # 3. Create Shipping Risk Factor based on the correct 'avg_freight' column name
    df['Shipping_Cost_Impact'] = df['avg_freight'].apply(lambda x: 'High Cost' if x > 25 else 'Standard Cost')
    
    # =====================================================================
    # NEW DATABASE EXPORT LAYER FOR POWER BI LIVE CONNECTION
    # =====================================================================
    print("\n🔌 Establishing direct export bridge to PostgreSQL database...")
    
    # 🛑 CRITICAL: Change "YOUR_PASSWORD_HERE" to your actual local PostgreSQL password!
    DB_USER = "postgres"
    DB_PASS = "1234"  
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "ecommerce_analytics"
    
    try:
        # Create the database connection engine string
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        print("Writing master predictions matrix straight to 'final_customer_predictions' table...")
        # Writes directly to PostgreSQL database table. Replaces it if it already exists.
        df.to_sql('final_customer_predictions', engine, if_exists='replace', index=False)
        print("🎉 Database export successful! Your live table is ready inside PostgreSQL.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print("⚠️ Falling back to saving a standard local CSV file...")
        output_path = os.path.join("Data", "processed", "final_predictions.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved fallback CSV file instead to: {output_path}")

if __name__ == "__main__":
    train_pipeline()