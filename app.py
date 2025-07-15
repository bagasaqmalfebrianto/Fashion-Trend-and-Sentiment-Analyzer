import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Trend Fashion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        .container-flex {
            display: flex;
            flex-direction: row;
            gap: 20px;
            margin-top: 20px;
        }
        .left-column {
            flex: 3;
        }
        .right-column {
            flex: 2;
        } 
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            text-align: left;
        }
        .metric-title {
            font-size: 16px;
            color: #888;
        }
        .metric-value {
            font-size: 22px;
            font-weight: bold;
            color: #222;
        }
        .metric-title-transparant {
            background-color: rgba(255, 255, 255, 0.0);
            color: rgba(255, 255, 255, 0.0);
            font-size: 16px;
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
# Load and Filter Data
# ======================
@st.cache_data
def load_data():
    return pd.read_csv("dataset_1k.csv")

df = load_data()
df['Launch_Date'] = pd.to_datetime(df['Launch_Date'])
df['Tahun'] = df['Launch_Date'].dt.year
df['Bulan'] = df['Launch_Date'].dt.to_period('M').astype(str)


# ======================
# Analytics Query
# ======================
df_top_1 = df.sort_values(by='Overall_Trend_Score', ascending=False).head(1)
product_top1_name = df_top_1['Product_Name'].values[0]
brand_name = df_top_1['Brand'].values[0]

brand_top = df.groupby('Brand')['Overall_Trend_Score'].mean().sort_values(ascending=False).index[0]
top_platform_name = df.groupby('Platform')['Engagement_Count'].mean().sort_values(ascending=False).index[0]
top_platform_engagement = df.groupby('Platform')['Engagement_Count'].mean().sort_values(ascending=False).iloc[0]

product_top5 = df.sort_values(by='Overall_Trend_Score', ascending=False)
df['Bulan'] = df['Launch_Date'].dt.to_period('M').astype(str)
trend_score = df.groupby('Bulan')['Trend_Score'].mean().reset_index()
df_gender = df['Gender'].value_counts().reset_index()
df_gender.columns = ['Gender', 'Jumlah']
brand_top5 = df.groupby(by='Brand').agg({
    'Overall_Trend_Score': 'mean',
    'Emerging_Trend_Flag': 'sum'
}).sort_values(by='Overall_Trend_Score', ascending=False).head(5).reset_index()

# Age Group
df_kelompok_usia = df['Age_Group'].value_counts().reset_index()
df_kelompok_usia.columns = ['Kelompok_Usia', 'Jumlah']

# Trend Score
df['Launch_Date'] = pd.to_datetime(df['Launch_Date'])
df['Bulan'] = df['Launch_Date'].dt.to_period('M').astype(str)
trend_score = df.groupby('Bulan')['Trend_Score'].mean().reset_index()

#Gender
df_gender = df['Gender'].value_counts().reset_index()
df_gender.columns = ['Gender', 'Jumlah']

# Trend score by Longevity
sample_15 = df.sort_values(by='Overall_Trend_Score').head(15)

#Top 10 Sales
top10_sales = df.sort_values(by='Purchase_Frequency',ascending=False).drop_duplicates(subset=['Purchase_Frequency']).head(5).reset_index()

#Heatmap
heatmap_material = df.groupby('Material', as_index=False)['Sustainability_Score'].mean()

#Influencer by Purchase Freq
top_influencers = df['Influencer_ID'].value_counts().head(10).index
influencer_df_purcFreq = df[df['Influencer_ID'].isin(top_influencers)]

#Influencer by Engagement
influencer_df_eng = df.groupby('Influencer_ID').agg({
    'Influencer_Score': 'mean',
    'Engagement_Count' : 'mean'
}).sort_values(by='Engagement_Count', ascending=False).head(5).reset_index()

#Product Top Engagement
top_eng = df.sort_values(by='Engagement_Count',ascending=False).drop_duplicates(subset=['Engagement_Count']).head(5).reset_index()

# WordCloud
hastags_series = df['Hashtags']

hashtags_text = " ".join([" ".join(h) if isinstance(h, list) else h for h in hastags_series])



cola1, cola2, cola3, cola4, cola5 = st.columns([3, 1, 1, 1, 1])

with cola1:
    st.markdown("# Fashion Intelligence Board")

with cola3:
    selected_location = st.selectbox("Region", options=df['Location'].unique())

with cola4:
   selected_category = st.selectbox("Category", options=df['Category'].unique())

with cola5:
    selected_year = st.selectbox("Year", sorted(df['Tahun'].unique(), reverse=True), index=1)

if selected_location:
    df = df[df['Location'] == selected_location]

if selected_year:
    df = df[df['Tahun'] == selected_year]

if selected_category:
    df = df[df['Category'] == selected_category]



col_kiri, col_kanan = st.columns([3.5, 1.5])
with col_kiri:
    selected_platform = st.radio(
        "Platform", ["All", "TikTok", "Instagram", "Twiter"],
            index=0, label_visibility="collapsed", horizontal=True
        )
    if selected_platform != "All":
        df = df[df['Platform'] == selected_platform]


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
                <div class="metric-title">🔥Top Engagement</div>
                <div class="metric-value">{top_platform_engagement:,.2f}</div>
                <div class="metric-title-transparant">-</div>
            </div>""", unsafe_allow_html=True)
    st.markdown(" ")

    tab1, tab2 = st.tabs(["Overview", "Trend Insights"])
    with tab1:        
        col5, col6 = st.columns([3,4])
        with col5:

            fig = px.bar(top10_sales, x='Product_Name', y='Purchase_Frequency',
                         title='📈 Sales Trend',)
            fig.update_layout(height=350, xaxis_title='Product Name', yaxis_title='Purchase Frequency')

            st.plotly_chart(fig)
        
        with col6:
            # st.write('📈 Perkembangan Trend Score per Bulan')
            fig = px.line(
            trend_score,
            x='Bulan',
            y='Trend_Score',
            title='📈 Monthly Trend Score',
            labels={'Bulan': 'Bulan (YYYY-MM)', 'Trend_Score': 'Rata-rata Trend Score'},
            markers=True
            )

            fig.update_layout(xaxis_tickangle=-45, height=350, xaxis_title='Product Name', yaxis_title='Engagement Count')

            st.plotly_chart(fig)

        col7, col8, col9 = st.columns(3)
        with col7:
            fig = px.bar(top_eng, x='Engagement_Count', y='Product_Name',
                         title='Top Engaged Products')
            fig.update_layout(height=350)

            st.plotly_chart(fig)
            # fig = px.pie(
            #     df_gender,
            #     values='Jumlah',
            #     names='Gender',
            #     title='Distribusi Gender'
            # )
            # fig.update_layout(height=350)
            # st.plotly_chart(fig)

        with col8:
            fig = px.scatter(
            sample_15,
            x='Trend_Longevity',
            y='Trend_Score',
            # color='Category',
            size='Engagement_Count',
            title='Trend Longevity vs Trend Score',
            labels={'Trend_Longevity': 'Trend Longevity (Day)', 'Trend_Score': 'Trend Score'},
            hover_data=['Product_Name', 'Brand']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig)

        with col9:
            
            fig = px.bar(
            df_kelompok_usia,
            x='Kelompok_Usia',
            y='Jumlah',
            title='Distribution by Age Group',
            color='Jumlah',  
            text='Jumlah'
            )

            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_title='Age Group', yaxis_title='Frequency', height=350)

            # Tampilkan di Streamlit
            st.plotly_chart(fig)

    with tab2:
        col10, col11, col12 = st.columns(3)

        with col10:
            fig = px.treemap(
            heatmap_material,
            path=['Material'], 
            values='Sustainability_Score',
            color='Sustainability_Score',
            color_continuous_scale='YlGnBu',
            title="Sustainability Score by Material"
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col11:
            fig = px.box(
            influencer_df_purcFreq,
            x='Influencer_ID',
            y='Purchase_Frequency',
            points='outliers',
            title='Purchase Frequency per Influencer',
            labels={'Influencer_ID': 'Influencer', 'Purchase_Frequency': 'Purchase Frequency'}
            )
            # fig.update_layout(xaxis_tickangle=-45)
            fig.update_layout(height=350, xaxis_title='Influencer ID', yaxis_title='Frequency')
            st.plotly_chart(fig)

        with col12:
            fig = px.bar(
            influencer_df_eng,
            x='Influencer_ID',
            y='Engagement_Count',
            title='Top Influencer by Engagement'
            )
            fig.update_layout(height=350, xaxis_title='Influencer ID', yaxis_title='Engagement Count')
            st.plotly_chart(fig)

        col13, col14, col15 = st.columns(3)

        with col13:
            fig = px.pie(
                df_gender,
                values='Jumlah',
                names='Gender',
                title='Gender Distribution'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig)
        
        # with col14:
        #     fig = px.scatter(
        #         df,
        #         x='Price',
        #         y='Trend_Score',
        #         color='Category',  # Optional: bisa dihapus jika ingin polos
        #         size='Engagement_Count',  # Optional: menambahkan dimensi
        #         title='💸 Trend Score vs Price',
        #         labels={
        #             'Price': 'Harga Produk',
        #             'Trend_Score': 'Skor Trend'
        #         },
        #         hover_data=['Product_Name', 'Brand']
        #     )
        #     fig.update_layout(height=350)
        #     st.plotly_chart(fig, use_container_width=True)
        
        # with col15:
        #     wordcloud = WordCloud(
        #         width=800, 
        #         height=400, 
        #         background_color='white', 
        #         colormap='tab10', 
        #         max_words=100
        #     ).generate(hashtags_text)

        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.imshow(wordcloud, interpolation='bilinear')
        #     ax.axis('off')
        #     fig.update_layout(height=350)
        #     st.pyplot(fig)
        

with col_kanan:
    fig = px.pie(brand_top5,
                 names='Brand',
                 values='Emerging_Trend_Flag',
                 title='Top 5 Brand by Overall Trend Score',
                 hole=0.4)
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📦 Product Trend Details")
    st.dataframe(
            product_top5[['Product_Name', 'Category', 'Brand','Material', 'Trend_Longevity']],
            use_container_width=True,
            hide_index=True
        )
