# KPIForge - Manufacturing & Supply Chain KPI Dashboard SaaS

**Full End-to-End Interactive KPI Dashboard** built with Streamlit, Plotly, and Pandas.

## Features
- **Excel/CSV Import & Export**: Upload your data or use sample manufacturing dataset. Export processed data, KPI summaries, or full reports to Excel.
- **Interactive Visualizations**: Dozens of chart types with Plotly (line, bar, scatter, pie, heatmap, box, gauge, treemap, etc.). Fully interactive with zoom, hover, filters.
- **Pre-built & Custom KPIs**: Manufacturing-specific metrics (OEE, Yield, On-Time Delivery, Inventory Turns, etc.) calculated automatically. Build your own.
- **Fancy Data Viz Studio**: Drag-and-drop style chart builder, multiple dashboards, date filters, category selectors.
- **AI-Powered Insights**: Get automated analysis and recommendations.
- **SaaS-Ready**: Multi-tenant simulation, user sessions, upgrade prompts. Easy to extend with real auth (Supabase/Firebase) and payments (Stripe).
- **Professional UI**: Clean industrial theme, responsive, KPI cards, dark mode option.

## Quick Start (Local Run)
1. Install Python 3.10+
2. `cd kpiforge`
3. `pip install -r requirements.txt`
4. `streamlit run app.py`
5. Open browser at http://localhost:8501

## Deploy as SaaS (Free Tier)
- Push to GitHub
- Deploy to **Streamlit Community Cloud** (free): Connect repo → Deploy
- Or use Render, Railway, or add custom domain later.
- For production SaaS: Add Supabase for DB/auth, Stripe for billing.

## Sample Data
Includes realistic manufacturing/supply chain data for Huntsville, AL style businesses (production lines, defects, inventory, orders, suppliers).

## Customization
- Edit `app.py` to add more KPIs, charts, or integrate real backend.
- Use with AI tools like Cursor/Claude to extend (e.g., add forecasting, real-time, multi-user DB).

## Architecture (MVP → Production)
- Frontend: Streamlit (Python)
- Data: Pandas + in-memory (session_state)
- Viz: Plotly Express + Graph Objects
- Export: openpyxl / xlsxwriter
- Future: FastAPI backend, PostgreSQL, React frontend, embedded analytics.

Built as your full MVP. Launch, get users, iterate!

For questions or enhancements, provide feedback.
