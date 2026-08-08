import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Executive Churn Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM ENTERPRISE STYLING & HIGH-CONTRAST CSS
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Main App Background & Default Text */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1a252f !important;
    }
    
    /* Global Typography Force Dark */
    p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #1a252f !important;
    }
    
    /* Main Page Headings */
    .main-title {
        color: #1a252f !important;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #4a5568 !important;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    /* Executive Metric Card Fixes */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 18px 22px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
    }
    
    div[data-testid="stMetricLabel"] * {
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetricValue"] * {
        color: #0f172a !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    
    /* Sidebar Styling Override */
    section[data-testid="stSidebar"] {
        background-color: #1a252f !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Tab Navigation Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        font-weight: 700;
        color: #1a252f !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MOCK DATA GENERATOR (Replace with PostgreSQL Query)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 1000
    
    segments = np.random.choice(['Gold (VIP High Spend)', 'Silver (Mid Spend)', 'Bronze (Low Spend)'], n, p=[0.2, 0.5, 0.3])
    shipping = np.random.choice(['Standard Cost', 'High Cost'], n, p=[0.7, 0.3])
    tenure_cohorts = np.random.choice(['0-1 Month', '2-6 Months', '1 Year', '2+ Years'], n, p=[0.4, 0.3, 0.2, 0.1])
    
    lifespan = np.random.randint(1, 730, n)
    avg_order = np.round(np.random.uniform(15.0, 350.0, n), 2)
    churn_prob = np.round(np.random.uniform(0.1, 1.0, n), 2)
    
    df = pd.DataFrame({
        'customer_unique_id': [f"CUST-{i:05d}-{np.random.randint(1000, 9999)}" for i in range(n)],
        'Customer_Value_Segment': segments,
        'Shipping_Cost_Impact': shipping,
        'Tenure_Cohort': tenure_cohorts,
        'customer_lifespan_days': lifespan,
        'avg_order_value': avg_order,
        'churn_probability': churn_prob
    })
    
    # Risk Tiers
    df['Risk_Tier'] = pd.cut(
        df['churn_probability'], 
        bins=[0, 0.4, 0.7, 1.0], 
        labels=['Low Risk (0-40%)', 'Medium Risk (40-70%)', 'High Risk (70-100%)']
    )
    
    df['revenue_at_risk'] = np.where(df['churn_probability'] > 0.7, df['avg_order_value'] * 3, 0)
    return df

df_raw = load_data()

# -----------------------------------------------------------------------------
# 4. SIDEBAR ENTERPRISE FILTERS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/analytics.png", width=64)
st.sidebar.title("Executive Control")
st.sidebar.markdown("---")

selected_segment = st.sidebar.multiselect(
    "Filter Account Segment",
    options=df_raw['Customer_Value_Segment'].unique(),
    default=df_raw['Customer_Value_Segment'].unique()
)

selected_shipping = st.sidebar.multiselect(
    "Filter Logistics Impact",
    options=df_raw['Shipping_Cost_Impact'].unique(),
    default=df_raw['Shipping_Cost_Impact'].unique()
)

risk_threshold = st.sidebar.slider(
    "Minimum Churn Probability Filter",
    min_value=0.0, max_value=1.0, value=0.0, step=0.05
)

# Filter Dataframe
filtered_df = df_raw[
    (df_raw['Customer_Value_Segment'].isin(selected_segment)) &
    (df_raw['Shipping_Cost_Impact'].isin(selected_shipping)) &
    (df_raw['churn_probability'] >= risk_threshold)
]

# -----------------------------------------------------------------------------
# 5. DASHBOARD HEADER & EXECUTIVE KPI RIBBON
# -----------------------------------------------------------------------------
st.markdown("<h1 class='main-title'>⚡ E-Commerce Executive Churn Management Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Operational Business Intelligence Loop powered by XGBoost & PostgreSQL Engine</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

total_monitored = len(filtered_df)
avg_churn = filtered_df['churn_probability'].mean() * 100 if total_monitored > 0 else 0
avg_ticket = filtered_df['avg_order_value'].mean() if total_monitored > 0 else 0
total_revenue_risk = filtered_df['revenue_at_risk'].sum()

col1.metric("Monitored Base", f"{total_monitored:,}", delta="-1.2% MoM")
col2.metric("Predicted Churn Rate", f"{avg_churn:.1f}%", delta="+2.4% vs Target", delta_color="inverse")
col3.metric("Average Ticket Size", f"${avg_ticket:.2f}", delta="+$4.10 MoM")
col4.metric("Revenue at Risk", f"${total_revenue_risk:,.2f}", delta="High Priority", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# Helper function to enforce dark axis text on transparent chart cards
def apply_chart_style(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#1a252f", family="Inter, sans-serif", size=13),
        xaxis=dict(
            title_font=dict(color="#1a252f", size=14, family="Inter, sans-serif"),
            tickfont=dict(color="#1a252f", size=12, family="Inter, sans-serif"),
            gridcolor="#e2e8f0"
        ),
        yaxis=dict(
            title_font=dict(color="#1a252f", size=14, family="Inter, sans-serif"),
            tickfont=dict(color="#1a252f", size=12, family="Inter, sans-serif"),
            gridcolor="#e2e8f0"
        ),
        template="plotly_white",
        margin=dict(l=30, r=30, t=30, b=30)
    )
    return fig

# -----------------------------------------------------------------------------
# 6. TABBED INTERACTIVE ANALYTICS MATRIX
# -----------------------------------------------------------------------------
tab_overview, tab_drivers, tab_watchlist = st.tabs([
    "📊 Executive Overview Matrix", 
    "🔍 Risk Drivers & Model Insights", 
    "🎯 Targeted Retention Watchlist"
])

# TAB 1: EXECUTIVE OVERVIEW MATRIX
with tab_overview:
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("### Churn Spread by Model Risk Tier")
        risk_counts = filtered_df['Risk_Tier'].value_counts().reset_index()
        risk_counts.columns = ['Risk_Tier', 'Count']
        
        fig_risk = px.bar(
            risk_counts, x='Risk_Tier', y='Count', 
            color='Risk_Tier',
            color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c'],
            text_auto=True
        )
        fig_risk.update_layout(showlegend=False, height=330)
        st.plotly_chart(apply_chart_style(fig_risk), use_container_width=True)
        st.info("💡 **Insight:** Focus automated retention messaging on the **High Risk (70-100%)** cohort.")

    with row1_col2:
        st.markdown("### Churn Incidents by Tenure Cohorts")
        tenure_df = filtered_df.groupby('Tenure_Cohort')['churn_probability'].mean().reset_index()
        
        fig_tenure = px.line(
            tenure_df, x='Tenure_Cohort', y='churn_probability', 
            markers=True, line_shape='spline',
            color_discrete_sequence=['#8e44ad']
        )
        fig_tenure.update_layout(height=330, yaxis_tickformat='.0%')
        st.plotly_chart(apply_chart_style(fig_tenure), use_container_width=True)
        st.info("💡 **Insight:** Drop-off peaks heavily during the **0-1 Month** onboarding window.")

    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("### Account Volume across Value Segments")
        fig_segment = px.pie(
            filtered_df, names='Customer_Value_Segment', 
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_segment.update_layout(height=330)
        st.plotly_chart(apply_chart_style(fig_segment), use_container_width=True)

    with row2_col2:
        st.markdown("### Logistics Overhead Impact vs. Churn Risk")
        fig_logistics = px.box(
            filtered_df, x='Shipping_Cost_Impact', y='churn_probability',
            color='Shipping_Cost_Impact',
            color_discrete_sequence=['#2c3e50', '#d35400']
        )
        fig_logistics.update_layout(showlegend=False, height=330)
        st.plotly_chart(apply_chart_style(fig_logistics), use_container_width=True)

# TAB 2: MODEL INSIGHTS & DRIVERS
with tab_drivers:
    st.markdown("### 🤖 XGBoost Feature Importance (Global Risk Drivers)")
    st.markdown("<p style='color: #334155 !important;'>Calculated global SHAP impact scores indicating primary behavioral drivers causing churn prediction spikes:</p>", unsafe_allow_html=True)
    
    feature_importance = pd.DataFrame({
        'Feature': ['Freight_Cost_Ratio', 'Order_Frequency_30D', 'Support_Tickets_Opened', 'Days_Since_Last_Order', 'App_Session_Duration'],
        'Importance': [0.38, 0.27, 0.18, 0.11, 0.06]
    }).sort_values(by='Importance', ascending=True)
    
    fig_shap = px.bar(
        feature_importance, x='Importance', y='Feature', orientation='h',
        color='Importance', color_continuous_scale='Blues'
    )
    fig_shap.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(apply_chart_style(fig_shap), use_container_width=True)

# TAB 3: ACTIONABLE RETENTION WATCHLIST
with tab_watchlist:
    st.markdown("### 🎯 Priority High-Risk Target Watchlist")
    
    high_risk_df = filtered_df[filtered_df['churn_probability'] >= 0.70].sort_values(
        by='churn_probability', ascending=False
    )
    
    st.markdown(f"<p style='color: #334155 !important;'>Displaying <b>{len(high_risk_df)}</b> flagged customer accounts requiring immediate win-back campaigns:</p>", unsafe_allow_html=True)
    
    st.dataframe(
        high_risk_df[[
            'customer_unique_id', 'Customer_Value_Segment', 
            'customer_lifespan_days', 'avg_order_value', 
            'churn_probability', 'revenue_at_risk'
        ]],
        column_config={
            "customer_unique_id": "Customer Account ID",
            "Customer_Value_Segment": "Segment",
            "customer_lifespan_days": st.column_config.NumberColumn("Tenure (Days)"),
            "avg_order_value": st.column_config.NumberColumn("Avg Ticket", format="$%.2f"),
            "churn_probability": st.column_config.ProgressColumn(
                "Churn Risk Score", format="%.2f", min_value=0.0, max_value=1.0
            ),
            "revenue_at_risk": st.column_config.NumberColumn("Revenue Exposure", format="$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # CSV Export Button
    st.download_button(
        label="📥 Export Target Watchlist to CSV",
        data=high_risk_df.to_csv(index=False),
        file_name="High_Risk_Retention_Watchlist.csv",
        mime="text/csv"
    )