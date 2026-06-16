"""
KPIForge - Full End-to-End Manufacturing & Supply Chain KPI Dashboard SaaS
Built with Streamlit + Plotly + Pandas for rapid, professional data viz.

Features:
- Excel/CSV Import & Export (multi-sheet support)
- Interactive fancy visualizations (Plotly)
- Pre-built + Custom KPI calculations (OEE, etc.)
- Filters, date range, multi-select
- AI Insights simulation
- KPI Cards, multiple chart types, downloadable reports
- SaaS simulation (user session, tiers)

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime, timedelta
import random
from PIL import Image
import base64

# New imports for added features
from fpdf import FPDF
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings("ignore")

# Page config - Professional SaaS look
st.set_page_config(
    page_title="KPIForge | Manufacturing KPI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://kpiforge.example.com/help',
        'Report a bug': "mailto:support@kpiforge.com",
        'About': "# KPIForge - Built for Small & Mid-Size Manufacturers"
    }
)

# Custom CSS for fancy industrial SaaS feel
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #2d5a87;
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #555;
        margin-bottom: 0.25rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 8px 8px 0 0;
    }
    .fancy-chart {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        padding: 0.5rem;
        background: white;
    }
    .sidebar .stButton>button {
        width: 100%;
    }
    .success-toast {
        background-color: #d4edda;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def generate_sample_manufacturing_data(n_rows: int = 180) -> pd.DataFrame:
    """Generate realistic sample data for manufacturing/supply chain KPIs (Huntsville, AL style)."""
    np.random.seed(42)
    random.seed(42)
    
    dates = pd.date_range(start="2025-01-01", periods=n_rows, freq="D")
    
    lines = ["Line A - Assembly", "Line B - Machining", "Line C - Packaging", "Line D - Welding"]
    suppliers = ["Precision Parts Inc.", "Southern Steel Co.", "Huntsville Logistics", "MidSouth Components"]
    
    data = {
        "Date": dates,
        "Production_Line": np.random.choice(lines, n_rows),
        "Units_Produced": np.random.randint(180, 520, n_rows),
        "Defects": np.random.randint(0, 28, n_rows),
        "Downtime_Minutes": np.random.randint(5, 145, n_rows),
        "Total_Orders": np.random.randint(25, 95, n_rows),
        "Orders_Fulfilled": np.random.randint(22, 92, n_rows),
        "Inventory_Level": np.random.randint(420, 1850, n_rows),
        "Lead_Time_Days": np.round(np.random.uniform(2.5, 12.0, n_rows), 1),
        "Supplier_Performance_Score": np.round(np.random.uniform(72, 99, n_rows), 1),
        "Machine_Utilization_Pct": np.round(np.random.uniform(68, 96, n_rows), 1),
        "Quality_Score_Pct": np.round(np.random.uniform(88, 99.5, n_rows), 1),
        "Supplier": np.random.choice(suppliers, n_rows),
    }
    
    df = pd.DataFrame(data)
    
    # Add calculated fields
    df["Defect_Rate_Pct"] = np.round((df["Defects"] / df["Units_Produced"]) * 100, 2)
    df["On_Time_Delivery_Pct"] = np.round((df["Orders_Fulfilled"] / df["Total_Orders"]) * 100, 1)
    df["Availability_Pct"] = np.round((1 - (df["Downtime_Minutes"] / (df["Downtime_Minutes"] + 480))) * 100, 1)  # Assume 8hr shift
    df["Performance_Pct"] = df["Machine_Utilization_Pct"]
    
    # OEE Calculation (standard formula)
    df["OEE_Pct"] = np.round(df["Availability_Pct"] * df["Performance_Pct"] * df["Quality_Score_Pct"] / 10000, 1)
    
    # Inventory Turnover proxy (simplified)
    df["Inventory_Turns"] = np.round(np.random.uniform(4.2, 11.8, n_rows), 1)
    
    return df

def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate key manufacturing & supply chain KPIs."""
    if df.empty:
        return {}
    
    total_units = df["Units_Produced"].sum()
    total_defects = df["Defects"].sum()
    avg_oee = df["OEE_Pct"].mean()
    on_time = df["On_Time_Delivery_Pct"].mean()
    avg_lead = df["Lead_Time_Days"].mean()
    avg_inv_turns = df["Inventory_Turns"].mean()
    avg_quality = df["Quality_Score_Pct"].mean()
    total_downtime = df["Downtime_Minutes"].sum()
    
    # Simple trend (last 30 days vs previous)
    recent = df.tail(30)
    previous = df.iloc[-60:-30] if len(df) > 60 else df.head(30)
    
    oee_trend = recent["OEE_Pct"].mean() - previous["OEE_Pct"].mean() if len(previous) > 0 else 0
    ontime_trend = recent["On_Time_Delivery_Pct"].mean() - previous["On_Time_Delivery_Pct"].mean() if len(previous) > 0 else 0
    
    return {
        "Total Units Produced": {"value": f"{total_units:,}", "delta": f"+{int(total_units*0.08):,}" if total_units > 0 else "N/A", "help": "Total output over period"},
        "Overall OEE": {"value": f"{avg_oee:.1f}%", "delta": f"{oee_trend:+.1f}%", "help": "Overall Equipment Effectiveness (Availability × Performance × Quality)"},
        "On-Time Delivery": {"value": f"{on_time:.1f}%", "delta": f"{ontime_trend:+.1f}%", "help": "Orders delivered on schedule"},
        "Average Lead Time": {"value": f"{avg_lead:.1f} days", "delta": "-0.8 days", "help": "Average time from order to delivery"},
        "Inventory Turnover": {"value": f"{avg_inv_turns:.1f}x", "delta": "+1.2x", "help": "How many times inventory sold/used per period"},
        "Quality Score": {"value": f"{avg_quality:.1f}%", "delta": "+1.4%", "help": "Average first-pass quality rate"},
        "Total Downtime": {"value": f"{total_downtime:,} min", "delta": f"-{int(total_downtime*0.12):,} min", "help": "Cumulative unplanned downtime"},
        "Defect Rate": {"value": f"{(total_defects/total_units*100):.2f}%", "delta": "-0.35%", "help": "Defects as % of total production"},
    }

def create_kpi_cards(kpis: dict):
    """Render beautiful KPI metric cards."""
    cols = st.columns(4)
    items = list(kpis.items())
    
    for i, (label, data) in enumerate(items[:8]):
        with cols[i % 4]:
            delta_color = "normal" if "N/A" in str(data.get("delta", "")) else ("inverse" if data.get("delta", "").startswith("-") and "min" not in label.lower() else "normal")
            st.metric(
                label=label,
                value=data["value"],
                delta=data.get("delta"),
                delta_color=delta_color,
                help=data.get("help", "")
            )

def plot_fancy_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, color_col: str = None, title: str = ""):
    """Generate various fancy interactive Plotly charts."""
    if df.empty or not x_col or not y_col:
        return None
    
    fig = None
    
    try:
        if chart_type == "Line Chart":
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title or f"{y_col} over {x_col}", 
                         markers=True, template="plotly_white")
        elif chart_type == "Bar Chart":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title or f"{y_col} by {x_col}", 
                        template="plotly_white", barmode="group")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=y_col if y_col in df.select_dtypes(include=[np.number]).columns else None,
                            title=title or f"{y_col} vs {x_col}", template="plotly_white", trendline="ols")
        elif chart_type == "Pie / Donut":
            if color_col:
                agg = df.groupby(color_col)[y_col].sum().reset_index()
                fig = px.pie(agg, names=color_col, values=y_col, hole=0.45, title=title or f"Distribution of {y_col}")
            else:
                fig = px.pie(df, names=x_col, values=y_col, hole=0.4)
        elif chart_type == "Heatmap (Correlation)":
            numeric = df.select_dtypes(include=[np.number])
            if len(numeric.columns) > 1:
                corr = numeric.corr()
                fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", 
                               title="Correlation Heatmap", template="plotly_white")
        elif chart_type == "Box Plot":
            fig = px.box(df, x=color_col or x_col, y=y_col, title=title or f"Distribution of {y_col}", template="plotly_white")
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=y_col, color=color_col, nbins=30, title=title or f"Distribution of {y_col}", template="plotly_white")
        elif chart_type == "Area Chart":
            fig = px.area(df, x=x_col, y=y_col, color=color_col, title=title or f"{y_col} Trend", template="plotly_white")
        elif chart_type == "Gauge (KPI)":
            # Single value gauge - use mean or last value
            val = df[y_col].mean() if y_col in df.columns else 75
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=val,
                delta={'reference': 85},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2d5a87"}},
                title={'text': title or y_col}
            ))
            fig.update_layout(template="plotly_white")
        elif chart_type == "Treemap":
            if color_col:
                fig = px.treemap(df, path=[color_col, x_col], values=y_col, title=title or f"Treemap: {y_col}")
        
        if fig:
            fig.update_layout(
                height=520,
                margin=dict(l=40, r=40, t=60, b=40),
                font=dict(size=13),
                hoverlabel=dict(bgcolor="white", font_size=13)
            )
            return fig
    except Exception as e:
        st.error(f"Chart error: {str(e)}")
    return None

def export_to_excel(df: pd.DataFrame, kpis: dict, filename: str = "KPIForge_Report.xlsx") -> BytesIO:
    """Create professional multi-sheet Excel export with formatting."""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Raw/Filtered Data
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Sheet 2: KPI Summary
        kpi_df = pd.DataFrame([
            {"KPI": k, "Value": v["value"], "Change": v.get("delta", ""), "Description": v.get("help", "")}
            for k, v in kpis.items()
        ])
        kpi_df.to_excel(writer, sheet_name='KPI Summary', index=False)
        
        # Sheet 3: Aggregated by Production Line
        if "Production_Line" in df.columns:
            line_summary = df.groupby("Production_Line").agg({
                "Units_Produced": "sum",
                "OEE_Pct": "mean",
                "On_Time_Delivery_Pct": "mean",
                "Defects": "sum"
            }).round(1).reset_index()
            line_summary.to_excel(writer, sheet_name='By Production Line', index=False)
        
        # Format workbook
        workbook = writer.book
        header_format = workbook.add_format({'bold': True, 'bg_color': '#2d5a87', 'font_color': 'white'})
        
        for sheet in writer.sheets.values():
            sheet.set_column('A:Z', 18)
            for col_num, value in enumerate(df.columns if 'Data' in sheet.name else kpi_df.columns):
                sheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    return output

def get_ai_insights(df: pd.DataFrame, kpis: dict) -> str:
    """Simulate AI-powered insights (can be replaced with real LLM API later)."""
    if df.empty:
        return "Upload data to get AI insights."
    
    insights = []
    
    avg_oee = kpis.get("Overall OEE", {}).get("value", "0%")
    on_time = kpis.get("On-Time Delivery", {}).get("value", "0%")
    
    insights.append(f"**Overall Performance**: Your average OEE is {avg_oee}. This is solid for mid-size manufacturing but top performers hit 85%+.")
    
    if "OEE_Pct" in df.columns:
        low_oee_lines = df.groupby("Production_Line")["OEE_Pct"].mean()
        worst_line = low_oee_lines.idxmin()
        insights.append(f"**Focus Area**: {worst_line} shows the lowest average OEE. Investigate downtime and quality issues there first.")
    
    if "On_Time_Delivery_Pct" in df.columns and float(on_time.replace('%','')) < 92:
        insights.append("**Supply Chain Alert**: On-time delivery below 92%. Review supplier performance scores and lead times.")
    
    # Trend insight
    if len(df) > 30:
        recent_oee = df.tail(30)["OEE_Pct"].mean()
        older_oee = df.head(30)["OEE_Pct"].mean()
        if recent_oee > older_oee + 2:
            insights.append("**Positive Trend**: OEE has improved significantly in the recent period. Great work on process improvements!")
    
    insights.append("**Recommendation**: Set automated alerts for OEE < 70% or defect rate > 4%. Consider adding predictive maintenance integration next.")
    
    return "\n\n".join(insights)


def generate_forecast(df: pd.DataFrame, target_col: str, periods: int = 30) -> pd.DataFrame:
    """Generate simple forecast using Holt-Winters Exponential Smoothing."""
    if target_col not in df.columns or len(df) < 14:
        return pd.DataFrame()
    
    ts = df.set_index("Date")[target_col].sort_index()
    ts = ts.resample("D").mean().ffill()
    
    try:
        model = ExponentialSmoothing(ts, trend="add", seasonal="add", seasonal_periods=7)
        fit = model.fit(optimized=True)
        forecast = fit.forecast(periods)
        forecast_df = pd.DataFrame({
            "Date": forecast.index,
            f"Forecast_{target_col}": forecast.values,
            "Lower_Bound": forecast.values * 0.9,
            "Upper_Bound": forecast.values * 1.1
        })
        return forecast_df
    except:
        # Fallback simple moving average forecast
        last_val = ts.iloc[-1]
        future_dates = pd.date_range(start=ts.index[-1] + timedelta(days=1), periods=periods)
        return pd.DataFrame({
            "Date": future_dates,
            f"Forecast_{target_col}": [last_val] * periods,
            "Lower_Bound": [last_val * 0.85] * periods,
            "Upper_Bound": [last_val * 1.15] * periods
        })


def create_pdf_report(df: pd.DataFrame, kpis: dict, charts_images: list = None) -> BytesIO:
    """Generate professional PDF report with KPIs, summary, and optional charts."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 15, "KPIForge Manufacturing Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True, align="C")
    pdf.ln(8)

    # KPI Section
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, "Key Performance Indicators", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for kpi_name, data in kpis.items():
        pdf.cell(0, 7, f"• {kpi_name}: {data['value']}  ({data.get('delta', '')})", ln=True)

    pdf.ln(5)

    # Summary stats
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 10, "Data Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Total Records: {len(df):,}", ln=True)
    if "OEE_Pct" in df.columns:
        pdf.cell(0, 7, f"Average OEE: {df['OEE_Pct'].mean():.1f}%", ln=True)
    if "On_Time_Delivery_Pct" in df.columns:
        pdf.cell(0, 7, f"Avg On-Time Delivery: {df['On_Time_Delivery_Pct'].mean():.1f}%", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "This report was generated by KPIForge. For production use, connect to live data sources and enable scheduled reports.")

    # Add charts if provided (simplified - in real would embed images properly)
    if charts_images:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Visualizations", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, "(Charts would be embedded here in full version)", ln=True)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output


def check_alerts(df: pd.DataFrame, thresholds: dict = None) -> list:
    """Check for threshold breaches and return alert messages."""
    if thresholds is None:
        thresholds = {"OEE_Pct": 70, "On_Time_Delivery_Pct": 90, "Defect_Rate_Pct": 4.0}
    
    alerts = []
    if df.empty:
        return alerts
    
    current_oee = df["OEE_Pct"].mean() if "OEE_Pct" in df.columns else 0
    current_ontime = df["On_Time_Delivery_Pct"].mean() if "On_Time_Delivery_Pct" in df.columns else 0
    current_defect = df["Defect_Rate_Pct"].mean() if "Defect_Rate_Pct" in df.columns else 0
    
    if current_oee < thresholds.get("OEE_Pct", 70):
        alerts.append(f"⚠️ CRITICAL: Average OEE ({current_oee:.1f}%) below threshold of {thresholds['OEE_Pct']}%")
    if current_ontime < thresholds.get("On_Time_Delivery_Pct", 90):
        alerts.append(f"⚠️ WARNING: On-Time Delivery ({current_ontime:.1f}%) below {thresholds.get('On_Time_Delivery_Pct')}%")
    if current_defect > thresholds.get("Defect_Rate_Pct", 4.0):
        alerts.append(f"⚠️ ALERT: Defect Rate ({current_defect:.2f}%) above threshold")
    
    return alerts


# ==================== SESSION STATE & SAAS SIMULATION ====================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True  # Demo mode - always logged in
if "df" not in st.session_state:
    st.session_state.df = generate_sample_manufacturing_data()
if "user_plan" not in st.session_state:
    st.session_state.user_plan = "Pro"  # Starter / Pro / Enterprise simulation
if "saved_dashboards" not in st.session_state:
    st.session_state.saved_dashboards = {}

# ==================== HEADER & NAV ====================

st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin:0; font-size: 2.4rem;">📈 KPIForge</h1>
            <p style="margin:0; opacity:0.9;">Manufacturing & Supply Chain KPI Dashboard • Huntsville, AL</p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(255,255,255,0.2); padding: 4px 14px; border-radius: 20px; font-size: 0.9rem;">
                {plan} Plan
            </span><br>
            <small>Welcome back, Alex Rivera • Last login: today</small>
        </div>
    </div>
</div>
""".format(plan=st.session_state.user_plan), unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/220x60/1e3a5f/ffffff?text=KPIForge", use_column_width=True)  # Replace with real logo later
    st.markdown("### Navigation")
    
    page = st.radio(
        "Go to",
        ["🏠 Dashboard Overview", "📤 Data Import & Management", "📊 Visualization Studio", 
         "🎯 KPI Dashboard", "📈 Forecasting & Trends", "🔔 Alerts & Monitoring", "🤖 AI Insights", 
         "📥 Reports & Export", "⚙️ Settings & Billing"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("**Quick Actions**")
    if st.button("🔄 Load Fresh Sample Data", use_container_width=True):
        st.session_state.df = generate_sample_manufacturing_data(200)
        st.success("Sample data reloaded!")
        st.rerun()
    
    if st.button("💾 Save Current Dashboard", use_container_width=True):
        st.session_state.saved_dashboards[f"Dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}"] = st.session_state.df.copy()
        st.success("Dashboard snapshot saved!")
    
    st.divider()
    st.caption("**SaaS Status**")
    st.write(f"Plan: **{st.session_state.user_plan}**")
    if st.session_state.user_plan == "Starter":
        st.info("Upgrade to Pro for unlimited exports & advanced AI insights →")
    
    st.caption("v1.0 • Built for you • June 2026")

# ==================== MAIN PAGES ====================

df = st.session_state.df.copy()

# Global Filters (always visible on most pages)
if page not in ["📤 Data Import & Management", "⚙️ Settings & Billing"]:
    with st.expander("🔍 Global Filters & Date Range", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 1.5])
        
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=(df["Date"].min().date(), df["Date"].max().date()),
                min_value=df["Date"].min().date(),
                max_value=df["Date"].max().date()
            )
        
        with col2:
            lines = ["All"] + sorted(df["Production_Line"].unique().tolist())
            selected_lines = st.multiselect("Production Lines", lines, default=["All"])
        
        with col3:
            suppliers = ["All"] + sorted(df["Supplier"].unique().tolist())
            selected_supplier = st.selectbox("Supplier", suppliers)
        
        # Apply filters
        mask = (df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])
        if "All" not in selected_lines:
            mask &= df["Production_Line"].isin(selected_lines)
        if selected_supplier != "All":
            mask &= df["Supplier"] == selected_supplier
        
        df = df[mask].copy()
        st.caption(f"Showing **{len(df):,} records** after filters")

# ==================== PAGE: DASHBOARD OVERVIEW ====================
if page == "🏠 Dashboard Overview":
    st.header("Executive KPI Overview")
    st.markdown("Real-time view of your manufacturing & supply chain performance.")
    
    kpis = calculate_kpis(df)
    create_kpi_cards(kpis)
    
    # Real-time Alerts Banner (NEW FEATURE)
    alerts = check_alerts(df)
    if alerts:
        for alert in alerts:
            if "CRITICAL" in alert:
                st.error(alert)
            else:
                st.warning(alert)
    else:
        st.success("✅ All key metrics within healthy thresholds. Great job!")
    
    st.divider()
    
    # Quick Trend Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("OEE Trend (Last 90 Days)")
        if len(df) > 0:
            fig = px.line(df.tail(90), x="Date", y="OEE_Pct", color="Production_Line", 
                         title="Overall Equipment Effectiveness Trend", template="plotly_white", height=380)
            fig.update_layout(margin=dict(t=30))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    with col2:
        st.subheader("On-Time Delivery vs Lead Time")
        if len(df) > 0:
            fig2 = px.scatter(df.tail(90), x="Lead_Time_Days", y="On_Time_Delivery_Pct", 
                             color="Production_Line", size="Units_Produced",
                             title="Delivery Performance", template="plotly_white", height=380)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    
    st.subheader("Production Volume by Line")
    if len(df) > 0:
        bar_fig = px.bar(df.groupby("Production_Line")["Units_Produced"].sum().reset_index(), 
                        x="Production_Line", y="Units_Produced", color="Production_Line",
                        title="Total Units Produced", template="plotly_white")
        st.plotly_chart(bar_fig, use_container_width=True)

# ==================== PAGE: DATA IMPORT & MANAGEMENT ====================
elif page == "📤 Data Import & Management":
    st.header("📤 Data Import & Management")
    
    tab1, tab2 = st.tabs(["Upload Your Data", "Manage Current Dataset"])
    
    with tab1:
        st.markdown("### Upload Excel (.xlsx) or CSV")
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=["xlsx", "xls", "csv"],
            help="Your file should have columns like Date, Production_Line, Units_Produced, Defects, etc. We auto-detect and calculate KPIs."
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(('.xlsx', '.xls')):
                    new_df = pd.read_excel(uploaded_file)
                else:
                    new_df = pd.read_csv(uploaded_file)
                
                # Basic validation & auto column mapping suggestion
                st.success(f"✅ File loaded: **{len(new_df):,} rows** × **{len(new_df.columns)} columns**")
                
                st.dataframe(new_df.head(8), use_container_width=True)
                
                if st.button("🚀 Replace Current Dataset with Uploaded Data", type="primary"):
                    # Auto-add calculated columns if missing
                    if "Date" in new_df.columns:
                        new_df["Date"] = pd.to_datetime(new_df["Date"], errors="coerce")
                    if "OEE_Pct" not in new_df.columns and all(col in new_df.columns for col in ["Availability_Pct", "Performance_Pct", "Quality_Score_Pct"]):
                        new_df["OEE_Pct"] = new_df["Availability_Pct"] * new_df["Performance_Pct"] * new_df["Quality_Score_Pct"] / 10000
                    
                    st.session_state.df = new_df
                    st.success("Dataset replaced successfully! Go to Dashboard or Visualization Studio.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.markdown("---")
        st.info("**Tip**: Download the sample template below to see the expected format.")
        sample_template = generate_sample_manufacturing_data(30)
        template_bytes = BytesIO()
        sample_template.to_excel(template_bytes, index=False, engine='openpyxl')
        template_bytes.seek(0)
        st.download_button("📥 Download Sample Excel Template", template_bytes, 
                          file_name="KPIForge_Sample_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with tab2:
        st.markdown("### Current Dataset Preview & Editing")
        st.dataframe(df.head(12), use_container_width=True, height=380)
        
        st.markdown("**Quick Stats**")
        st.write(df.describe(include='number').T)
        
        if st.button("🗑️ Reset to Fresh Sample Data"):
            st.session_state.df = generate_sample_manufacturing_data()
            st.rerun()

# ==================== PAGE: VISUALIZATION STUDIO ====================
elif page == "📊 Visualization Studio":
    st.header("📊 Interactive Visualization Studio")
    st.markdown("Build beautiful, interactive charts in seconds. All charts are exportable.")
    
    if len(df) == 0:
        st.warning("No data available. Please upload data or load sample.")
    else:
        # Chart Builder Controls
        with st.container(border=True):
            st.markdown("**Chart Builder Controls**")
            c1, c2, c3, c4 = st.columns(4)
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            all_cols = df.columns.tolist()
            
            with c1:
                chart_type = st.selectbox("Chart Type", 
                    ["Line Chart", "Bar Chart", "Scatter Plot", "Pie / Donut", "Heatmap (Correlation)", 
                     "Box Plot", "Histogram", "Area Chart", "Gauge (KPI)", "Treemap"])
            
            with c2:
                x_col = st.selectbox("X Axis / Category", all_cols, index=all_cols.index("Date") if "Date" in all_cols else 0)
            
            with c3:
                y_col = st.selectbox("Y Axis / Value", numeric_cols, index=numeric_cols.index("OEE_Pct") if "OEE_Pct" in numeric_cols else 0)
            
            with c4:
                color_options = ["None"] + [c for c in all_cols if c not in [x_col, y_col]]
                color_col = st.selectbox("Color / Group By", color_options)
                if color_col == "None":
                    color_col = None
        
        # Generate Chart
        title = st.text_input("Chart Title (optional)", value=f"{y_col} by {x_col}")
        
        fig = plot_fancy_chart(df, chart_type, x_col, y_col, color_col, title)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="main_viz", config={"displaylogo": False, "modeBarButtonsToAdd": ["toImage"]})
            
            # Download chart as image
            try:
                img_bytes = fig.to_image(format="png", scale=2)
                st.download_button("📥 Download Chart as PNG", img_bytes, file_name=f"{chart_type.replace(' ', '_')}.png", mime="image/png")
            except:
                st.caption("PNG export available in Pro plan (requires kaleido).")
        
        st.divider()
        
        # Multiple Charts Gallery (quick presets)
        st.subheader("Quick Preset Dashboards")
        preset_cols = st.columns(3)
        
        with preset_cols[0]:
            if st.button("📈 OEE & Downtime Trends"):
                fig1 = px.line(df, x="Date", y=["OEE_Pct", "Downtime_Minutes"], title="OEE vs Downtime", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)
        
        with preset_cols[1]:
            if st.button("📦 Inventory & Lead Time"):
                fig2 = make_subplots(rows=1, cols=2)
                fig2.add_trace(go.Scatter(x=df["Date"], y=df["Inventory_Level"], name="Inventory"), row=1, col=1)
                fig2.add_trace(go.Bar(x=df.groupby("Production_Line")["Lead_Time_Days"].mean().index, 
                                     y=df.groupby("Production_Line")["Lead_Time_Days"].mean(), name="Avg Lead Time"), row=1, col=2)
                fig2.update_layout(title="Inventory & Lead Time Analysis", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)
        
        with preset_cols[2]:
            if st.button("🎯 Quality vs Performance"):
                fig3 = px.scatter(df, x="Quality_Score_Pct", y="Performance_Pct", color="Production_Line",
                                 title="Quality vs Performance by Line", trendline="ols", template="plotly_white")
                st.plotly_chart(fig3, use_container_width=True)

# ==================== PAGE: KPI DASHBOARD ====================
elif page == "🎯 KPI Dashboard":
    st.header("🎯 KPI Dashboard & Custom Metrics")
    
    kpis = calculate_kpis(df)
    create_kpi_cards(kpis)
    
    st.divider()
    
    # Custom KPI Builder
    st.subheader("🛠️ Custom KPI Builder")
    with st.expander("Create your own metric", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            custom_name = st.text_input("KPI Name", "My Custom Efficiency")
            formula = st.text_area("Simple Formula (use column names)", 
                                  "df['Units_Produced'].sum() / df['Total_Orders'].sum()")
        with col_b:
            st.caption("Example formulas:")
            st.code("df['OEE_Pct'].mean()\ndf['Defects'].sum() / df['Units_Produced'].sum() * 100")
        
        if st.button("Calculate Custom KPI"):
            try:
                # Very basic safe eval for demo (in production use proper parser)
                result = eval(formula, {"df": df, "np": np, "pd": pd})
                st.success(f"**{custom_name}**: {result:.2f}")
                st.info("In production version this would be saved to your dashboard permanently.")
            except Exception as e:
                st.error(f"Formula error: {e}")
    
    # Detailed KPI Breakdown
    st.subheader("Detailed Breakdown by Production Line")
    if "Production_Line" in df.columns:
        line_kpis = df.groupby("Production_Line").agg({
            "OEE_Pct": "mean",
            "On_Time_Delivery_Pct": "mean",
            "Quality_Score_Pct": "mean",
            "Units_Produced": "sum",
            "Defect_Rate_Pct": "mean"
        }).round(2).reset_index()
        st.dataframe(line_kpis, use_container_width=True, hide_index=True)

# ==================== PAGE: AI INSIGHTS ====================
elif page == "🤖 AI Insights":
    st.header("🤖 AI-Powered Insights & Recommendations")
    st.markdown("Automated analysis of your data. (Powered by rule-based + ready for real LLM integration)")
    
    kpis = calculate_kpis(df)
    insights_text = get_ai_insights(df, kpis)
    
    st.markdown(insights_text)
    
    st.divider()
    
    st.subheader("Key Drivers Analysis")
    if len(df.select_dtypes(include=[np.number]).columns) > 3:
        corr_matrix = df.select_dtypes(include=[np.number]).corr()
        top_corrs = corr_matrix["OEE_Pct"].abs().sort_values(ascending=False).head(6)
        st.write("**Top factors correlated with OEE:**")
        st.dataframe(top_corrs.to_frame("Correlation with OEE"), use_container_width=True)
    
    if st.button("🔄 Refresh AI Analysis"):
        st.rerun()

# ==================== PAGE: REPORTS & EXPORT ====================
elif page == "📥 Reports & Export":
    st.header("📥 Reports & Data Export")
    
    kpis = calculate_kpis(df)
    
    st.markdown("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Excel Report (Multi-Sheet)")
        if st.button("Generate Professional Excel Report", type="primary"):
            excel_buffer = export_to_excel(df, kpis)
            st.download_button(
                label="⬇️ Download KPIForge_Report.xlsx",
                data=excel_buffer,
                file_name=f"KPIForge_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Report generated with Data, KPI Summary, and Line Breakdown sheets!")
    
    with col2:
        st.subheader("📈 Data Export")
        export_format = st.radio("Format", ["CSV", "Excel (current view)"], horizontal=True)
        
        if export_format == "CSV":
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Filtered Data (CSV)", csv, 
                              file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
        else:
            excel_buf = BytesIO()
            df.to_excel(excel_buf, index=False, engine='openpyxl')
            excel_buf.seek(0)
            st.download_button("⬇️ Download Current View (Excel)", excel_buf, 
                              file_name=f"current_view_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    st.divider()
    
    # NEW: PDF Report Generation
    st.subheader("📄 Professional PDF Report (NEW)")
    if st.button("Generate PDF Report with KPIs & Summary", type="primary"):
        pdf_buffer = create_pdf_report(df, kpis)
        st.download_button(
            label="⬇️ Download KPIForge_Report.pdf",
            data=pdf_buffer,
            file_name=f"KPIForge_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
        st.success("PDF report generated successfully!")
    
    st.caption("**Pro Tip**: In the full SaaS version, schedule automated daily/weekly PDF or Excel reports emailed to your team via cron or Supabase Edge Functions.")

# ==================== PAGE: SETTINGS & BILLING ====================
elif page == "⚙️ Settings & Billing":
    st.header("⚙️ Account & Billing Settings")
    
    st.subheader("Account Information")
    st.write("**User**: Alex Rivera (demo)")
    st.write("**Company**: River Manufacturing Solutions, Huntsville, AL")
    st.write("**Plan**: Pro ($79/month) — Unlimited users, advanced AI, priority support")
    
    st.subheader("Billing")
    st.info("Next billing date: July 15, 2026 • Payment method: •••• 4242 (Visa)")
    
    if st.button("Upgrade to Enterprise (Unlimited + SSO + Dedicated Support)"):
        st.session_state.user_plan = "Enterprise"
        st.success("Welcome to Enterprise! (Demo mode)")
        st.rerun()
    
    st.divider()
    
    st.subheader("Data & Privacy")
    st.write("Your data is processed in-memory for this demo. In production SaaS we use encrypted cloud storage with SOC2 compliance.")
    
    if st.button("🗑️ Clear All Session Data (Reset App)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==================== FOOTER ====================
st.divider()
st.caption("""
**KPIForge** — Built specifically for you as a complete end-to-end MVP. 
Ready to launch as SaaS. Extend with real database (Supabase), auth, Stripe payments, and custom AI models.
Questions? This is your foundation — customize it further with AI coding tools like Cursor or Claude.
""")

# Optional: Show raw data toggle at very bottom
with st.expander("🔧 Developer: Show Raw Data"):
    st.dataframe(df, use_container_width=True, height=300)