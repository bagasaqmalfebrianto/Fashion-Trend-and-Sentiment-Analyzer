import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# ======================
# CSS Styling
# ======================
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
            width: 320px;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 2rem 1rem;
            background-color: #f8f9fa !important;
        }
        [data-testid="collapsedControl"] {
            visibility: visible;
        }
        div[data-testid="stAppViewContainer"] {
            background-color: #ffffff;
        }
        .metric-card {
            background: linear-gradient(180deg, #1E88E5 0%, #42A5F5 50%, #FFFFFF 100%) !important;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: left;
            color: #FFFFFF;
        }
        .metric-title {
            font-size: 16px;
            color: rgba(255,255,255,0.9);
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 4px;
            line-height: 1.1;
        }
        .metric-title-transparant {
            font-size: 14px;
            color: rgba(255,255,255,0.0);
        }
        .stRadio > div {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            gap: 0;
        }
    </style>
""", unsafe_allow_html=True)

# ======================
# Load Data
# ======================
df = pd.read_csv("dataset_1k.csv")
df['Launch_Date'] = pd.to_datetime(df['Launch_Date'])
df['Tahun'] = df['Launch_Date'].dt.year
df['Bulan'] = df['Launch_Date'].dt.to_period('M').astype(str)

# ======================
# FILTER UI (top row)
# ======================
cola1, cola2, cola3, cola4, cola5 = st.columns([3, 1, 1, 1, 1])

with cola1:
    st.markdown(
        """
        <h1 style="color:#1E88E5; font-size:55px; font-weight:700; margin-bottom:0; font-style: italic;">
            Fashion Intelligence Board
        </h1>
        """,
        unsafe_allow_html=True
    )

with cola3:
    selected_location = st.selectbox(
        "Region",
        options=["All"] + sorted(df['Location'].dropna().unique().tolist())
    )

with cola4:
    selected_category = st.selectbox(
        "Category",
        options=["All"] + sorted(df['Category'].dropna().unique().tolist())
    )

with cola5:
    selected_year = st.selectbox(
        "Year",
        options=["All"] + sorted(df['Tahun'].dropna().unique().tolist(), reverse=True)
    )

# ======================
# APPLY FIRST-STAGE FILTERS (Region, Category, Year)
# ======================

df_base = df.copy()

last_date = df_base['Launch_Date'].max()

if selected_location != "All":
    df_base = df_base[df_base['Location'] == selected_location]

if selected_category != "All":
    df_base = df_base[df_base['Category'] == selected_category]

if selected_year != "All":
    df_base = df_base[df_base['Tahun'] == selected_year]
else:
    # Jika "All" default ambil 30 hari terakhir
    start_date = last_date - pd.Timedelta(days=30)
    df_base = df_base[df_base['Launch_Date'] >= start_date]

# ======================
# Platform filter (depends on df_base)
# ======================
col_kiri, col_kanan = st.columns([3.5, 1.5])

with col_kiri:
    platform_options = ["All"] + sorted(df_base['Platform'].dropna().unique().tolist())
    selected_platform = st.radio(
        "Platform",
        platform_options,
        index=0,
        label_visibility="collapsed",
        horizontal=True
    )

# Apply platform filter
df_filtered = df_base if selected_platform == "All" else df_base[df_base['Platform'] == selected_platform]

# ======================
# Guard: empty data after filters
# ======================
if df_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
    st.stop()

# ======================
# METRIC COMPUTATIONS (always from df_filtered)
# ======================
df_top_1 = df_filtered.sort_values(by='Overall_Trend_Score', ascending=False).head(1)
product_top1_name = df_top_1['Product_Name'].iat[0] if not df_top_1.empty else "N/A"
brand_name = df_top_1['Brand'].iat[0] if not df_top_1.empty else "N/A"

if 'Brand' in df_filtered and not df_filtered['Brand'].dropna().empty:
    brand_top = (
        df_filtered.groupby('Brand')['Overall_Trend_Score']
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )
else:
    brand_top = "N/A"

# Platform metrics
if selected_platform != "All":
    top_platform_name = selected_platform
    top_platform_engagement = df_filtered['Engagement_Count'].mean()
else:
    grouped_platform = (
        df_filtered.groupby('Platform')['Engagement_Count']
        .mean()
        .sort_values(ascending=False)
    )
    top_platform_name = grouped_platform.index[0]
    top_platform_engagement = grouped_platform.iloc[0]

# DataFrames for visuals
product_top5 = df_filtered.sort_values(by='Overall_Trend_Score', ascending=False)


if selected_year == 'All':
    last_date = df_filtered['Launch_Date'].max()
    start_date = last_date - pd.Timedelta(days=30)
    trend_score = (
        df_filtered[df_filtered['Launch_Date'] >= start_date]
        .groupby('Launch_Date')['Trend_Score']
        .mean()
        .reset_index()
    )

    x_axis = 'Launch_Date'
    chart_title = '<b>📘 Daily Trend Score (Last 30 Days)</b>'
else:
    trend_score = (
    df_filtered.groupby('Bulan')['Trend_Score']
    .mean()
    .reset_index()
    )


# Gender (aman)
df_gender = (
    df_filtered.groupby('Gender')
    .size()
    .reset_index(name='Jumlah')
)

# Age group (aman)
df_kelompok_usia = (
    df_filtered.groupby('Age_Group')
    .size()
    .reset_index(name='Jumlah')
    .rename(columns={'Age_Group': 'Kelompok_Usia'})
)

# Brand Top 5
brand_top5 = (
    df_filtered.groupby('Brand')
    .agg({'Overall_Trend_Score': 'mean', 'Emerging_Trend_Flag': 'sum'})
    .sort_values(by='Overall_Trend_Score', ascending=False)
    .head(5)
    .reset_index()
)

# Top Sales
top10_sales = (
    df_filtered.sort_values(by='Purchase_Frequency', ascending=False)
    .drop_duplicates(subset=['Purchase_Frequency'])
    .head(5)
    .reset_index(drop=True)
)

# Heatmap data
heatmap_material = (
    df_filtered.groupby('Material', as_index=False)['Sustainability_Score']
    .mean()
)

# Influencers
top_influencers = df_filtered['Influencer_ID'].value_counts().head(10).index
influencer_df_purcFreq = df_filtered[df_filtered['Influencer_ID'].isin(top_influencers)]

influencer_df_eng = (
    df_filtered.groupby('Influencer_ID')
    .agg({'Influencer_Score': 'mean', 'Engagement_Count': 'mean'})
    .sort_values(by='Engagement_Count', ascending=False)
    .head(5)
    .reset_index()
)

# Top Engagement
top_eng = (
    df_filtered.sort_values(by='Engagement_Count', ascending=False)
    .drop_duplicates(subset=['Engagement_Count'])
    .head(5)
    .reset_index()
)

# WordCloud text (optional)
hashtags_text = " ".join(
    [" ".join(h) if isinstance(h, list) else str(h) for h in df_filtered['Hashtags']]
)

# ======================
# LAYOUT: Cards + Tabs
# ======================
with col_kiri:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🏆 Top Produk #1</div>
                <div class="metric-value">{product_top1_name}</div>
                <div class="metric-title">Brand: {brand_name}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📊 Top Brand</div>
                <div class="metric-value">{brand_top}</div>
                <div class="metric-title-transparant">-</div>
            </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📱 Platform Teratas</div>
                <div class="metric-value">{top_platform_name}</div>
                <div class="metric-title-transparant">-</div>
            </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🔥 Top Engagement</div>
                <div class="metric-value">{top_platform_engagement:,.2f}</div>
                <div class="metric-title-transparant">-</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(" ")

    tab1, tab2 = st.tabs(["Overview", "Trend Insights"])

    # ---------------- Overview ----------------
    with tab1:
        col5, col6 = st.columns([3,4])

        with col5:
            fig = px.bar(
                top10_sales,
                x='Product_Name',
                y='Purchase_Frequency',
                title='<b>📘 Sales ' \
                'Trend</b>',
            )
            fig.update_layout(height=350, xaxis_title='Product Name', yaxis_title='Purchase Frequency')
            st.plotly_chart(fig, use_container_width=True)

        with col6:
            fig = px.line(
                trend_score,
                x=x_axis,
                y='Trend_Score',
                title='<b>📘 Monthly Trend Score</b>',
                labels={x_axis: 'Tanggal' if x_axis == 'Launch_Date' else 'Bulan (YYYY-MM)', 
                'Trend_Score': 'Rata-rata Trend Score'},
                markers=True
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=350,
                xaxis_title='Date' if x_axis == 'Launch_Date' else 'Month',
                yaxis_title='Trend Score'
            )
            st.plotly_chart(fig, use_container_width=True)

        col7, col8, col9 = st.columns(3)

        with col7:
            fig = px.bar(
                top_eng,
                x='Engagement_Count',
                y='Product_Name',
                title='<b>📘 Top Engaged Products</b>'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col8:
            fig = px.scatter(
                top_eng,  # gunakan data top_eng biar konsisten (atau sample_15)
                x='Trend_Longevity',
                y='Trend_Score',
                size='Engagement_Count',
                title='<b>📘 Trend Longevity vs Trend Score</b>',
                labels={'Trend_Longevity': 'Trend Longevity (Day)', 'Trend_Score': 'Trend Score'},
                hover_data=['Product_Name', 'Brand']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col9:
            fig = px.bar(
                df_kelompok_usia,
                x='Kelompok_Usia',
                y='Jumlah',
                title='<b>📘 Distribution by Age Group</b>',
                color='Jumlah',
                text='Jumlah'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- Trend Insights ----------------
    with tab2:
        col10, col11, col12 = st.columns(3)

        with col10:
            fig = px.treemap(
                heatmap_material,
                path=['Material'], 
                values='Sustainability_Score',
                color='Sustainability_Score',
                color_continuous_scale='YlGnBu',
                title="<b>📘 Sustainability Score by Material</b>"
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col11:
            fig = px.box(
                influencer_df_purcFreq,
                x='Influencer_ID',
                y='Purchase_Frequency',
                points='outliers',
                title='<b>📘 Purchase Frequency per Influencer</b>',
                labels={'Influencer_ID': 'Influencer', 'Purchase_Frequency': 'Purchase Frequency'}
            )
            fig.update_layout(height=350, xaxis_title='Influencer ID', yaxis_title='Frequency')
            st.plotly_chart(fig, use_container_width=True)

        with col12:
            fig = px.bar(
                influencer_df_eng,
                x='Influencer_ID',
                y='Engagement_Count',
                title='<b>📘 Top Influencer by Engagement</b>'
            )
            fig.update_layout(height=350, xaxis_title='Influencer ID', yaxis_title='Engagement Count')
            st.plotly_chart(fig, use_container_width=True)

        col13, col14, col15 = st.columns(3)

        with col13:
            fig = px.pie(
                df_gender,
                values='Jumlah',
                names='Gender',
                title='<b>📘 Gender Distribution</b>'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # col14/col15 reserved

# ======================
# Sidebar column (kanan)
# ======================
with col_kanan:
    fig = px.pie(
        brand_top5,
        names='Brand',
        values='Emerging_Trend_Flag',
        title='<b>📘 Top 5 Brand by Overall Trend Score</b>',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📘 Product Trend Details")
    st.dataframe(
        product_top5[['Product_Name', 'Category', 'Brand', 'Material', 'Trend_Longevity']],
        use_container_width=True,
        hide_index=True
    )
