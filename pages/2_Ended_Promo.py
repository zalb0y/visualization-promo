import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="Ended Promo Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide sidebar navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS - Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 50%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #a0aec0;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    
    .metric-container {
        background: linear-gradient(145deg, #1e2a4a 0%, #2d3a5a 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,212,255,0.2);
        border-color: rgba(0,212,255,0.3);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 0.5rem;
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #00d4ff;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #ffffff;
    }
    
    .stSelectbox label, .stMultiSelect label, .stRadio label {
        font-weight: 500;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: #ffffff;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
    }
</style>
""", unsafe_allow_html=True)

# Load Data Function
@st.cache_data
def load_data(file_path):
    xlsx = pd.ExcelFile(file_path)
    
    df_sales = pd.read_excel(xlsx, sheet_name='Sales')
    df_sales = df_sales.dropna(how='all')
    df_sales = df_sales.dropna(subset=['Category'])
    
    df_qty = pd.read_excel(xlsx, sheet_name='Qty')
    df_qty = df_qty.dropna(how='all')
    df_qty = df_qty.dropna(subset=['Cat'])
    
    return df_sales, df_qty

# Format functions
def format_rupiah(value):
    if value >= 1e12:
        return f"Rp {value/1e12:.2f} T"
    elif value >= 1e9:
        return f"Rp {value/1e9:.2f} M"
    elif value >= 1e6:
        return f"Rp {value/1e6:.2f} Jt"
    else:
        return f"Rp {value:,.0f}"

def format_short_rupiah(value):
    if value >= 1e12:
        return f"{value/1e12:.1f}T"
    elif value >= 1e9:
        return f"{value/1e9:.2f}M"
    elif value >= 1e6:
        return f"{value/1e6:.1f}Jt"
    else:
        return f"{value:,.0f}"

def format_percent(value):
    return f"{value*100:.2f}%"

# Aggregate function for Category view
def aggregate_sales_by_category(df):
    agg_df = df.groupby('Category').agg({
        'Promo Name': 'count',
        'Total Count': 'sum',
        'Total Claim': 'sum',
        'NOC': 'first',
        'Sales Amount': 'sum',
        'Net Sales (by Category)': 'first',
        'Contribution Sales': 'sum'
    }).reset_index()
    
    agg_df = agg_df.rename(columns={'Promo Name': 'Jumlah Promo'})
    agg_df['Conversion Rate (Claim/Count)'] = agg_df['Total Claim'] / agg_df['Total Count']
    agg_df['Conversion Rate (Count/NOC)'] = agg_df['Total Count'] / agg_df['NOC']
    agg_df['Category'] = 'Category ' + agg_df['Category'].astype(int).astype(str)
    
    return agg_df

def aggregate_qty_by_category(df):
    agg_df = df.groupby('Cat').agg({
        'Nama Promo': 'count',
        'Total Count': 'sum',
        'Total Claim': 'sum',
        'NOC': 'first'
    }).reset_index()
    
    agg_df = agg_df.rename(columns={'Nama Promo': 'Jumlah Promo', 'Cat': 'Category'})
    agg_df['Conversion Rate(Claim/Count)'] = agg_df['Total Claim'] / agg_df['Total Count']
    agg_df['Conversion Rate(Count/NOC)'] = agg_df['Total Count'] / agg_df['NOC']
    agg_df['Category'] = 'Category ' + agg_df['Category'].astype(int).astype(str)
    
    return agg_df

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Ended Promo Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Summary Promo yang Berakhir - January 2026</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        df_sales, df_qty = load_data('Final_Summary_Ended_Promo_Jan_2026.xlsx')
    except FileNotFoundError:
        st.error("⚠️ File 'Final_Summary_Ended_Promo_Jan_2026.xlsx' tidak ditemukan.")
        st.stop()
    
    # Sidebar
    # Sidebar
    with st.sidebar:
        # Tombol kembali ke Home
        if st.button("🏠 Kembali ke Home", use_container_width=True):
            st.switch_page("app.py")
        
        st.markdown("---")
        st.markdown("## 🎛️ Filter & View")
        
        view_option = st.radio(
            "📊 Pilih Tampilan",
            options=['Per Promo', 'Per Category'],
            index=0,
            help="Pilih tampilan per promo atau per kategori"
        )
        
        st.markdown("---")
        
        # Category filter for Sales
        all_categories_sales = sorted(df_sales['Category'].unique())
        selected_categories_sales = st.multiselect(
            "🏷️ Filter Category (Sales)",
            options=all_categories_sales,
            default=all_categories_sales,
            format_func=lambda x: f"Category {int(x)}"
        )
        
        st.markdown("---")
        
        # Category filter for Qty
        all_categories_qty = sorted(df_qty['Cat'].unique())
        selected_categories_qty = st.multiselect(
            "🏷️ Filter Category (Qty)",
            options=all_categories_qty,
            default=all_categories_qty,
            format_func=lambda x: f"Category {int(x)}"
        )
        
        st.markdown("---")
        st.markdown("### 📌 Info")
        st.info(f"**View:** {view_option}")
    
    # Filter data
    filtered_sales = df_sales[df_sales['Category'].isin(selected_categories_sales)].copy()
    filtered_qty = df_qty[df_qty['Cat'].isin(selected_categories_qty)].copy()
    
    if filtered_sales.empty and filtered_qty.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter.")
        st.stop()
    
    # Tabs
    tab_sales, tab_qty = st.tabs(["💰 SALES", "📦 QTY"])
    
    # ==================== TAB SALES ====================
    with tab_sales:
        if filtered_sales.empty:
            st.warning("⚠️ Tidak ada data Sales untuk kategori yang dipilih.")
        else:
            # Prepare data based on view
            if view_option == 'Per Promo':
                display_df = filtered_sales.copy()
                display_df['Label'] = display_df['Promo Name']
                name_col = 'Promo Name'
                conv_claim_col = 'Conversion Rate (Claim/Count)'
                conv_noc_col = 'Conversion Rate (Count/NOC)'
            else:
                display_df = aggregate_sales_by_category(filtered_sales)
                display_df['Label'] = display_df['Category']
                name_col = 'Category'
                conv_claim_col = 'Conversion Rate (Claim/Count)'
                conv_noc_col = 'Conversion Rate (Count/NOC)'
            
            # KPI Cards
            st.markdown("### 📈 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales = display_df['Sales Amount'].sum()
            total_promo = len(filtered_sales) if view_option == 'Per Promo' else display_df['Jumlah Promo'].sum()
            avg_conv_claim = display_df[conv_claim_col].mean()
            avg_conv_noc = display_df[conv_noc_col].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_rupiah(total_sales)}</div>
                    <div class="metric-label">💰 Total Sales Amount</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{int(total_promo)}</div>
                    <div class="metric-label">🎯 Jumlah Promo</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_percent(avg_conv_claim)}</div>
                    <div class="metric-label">📊 Avg Conv. (Claim/Count)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_percent(avg_conv_noc)}</div>
                    <div class="metric-label">👥 Avg Conv. (Count/NOC)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart 1: Sales Amount Ranking
            st.markdown('<p class="section-title">💰 Ranking Sales Amount</p>', unsafe_allow_html=True)
            
            sales_sorted = display_df.sort_values('Sales Amount', ascending=True)
            sales_sorted['Sales_Label'] = sales_sorted['Sales Amount'].apply(format_short_rupiah)
            
            fig1 = go.Figure(data=[go.Bar(
                x=sales_sorted['Sales Amount'],
                y=sales_sorted['Label'],
                orientation='h',
                marker=dict(
                    color=sales_sorted['Sales Amount'],
                    colorscale=[[0, '#00d4ff'], [0.5, '#7b2cbf'], [1, '#ff6b6b']],
                    line=dict(color='rgba(255,255,255,0.3)', width=1)
                ),
                text=sales_sorted['Sales_Label'],
                textposition='outside',
                textfont=dict(color='#ffffff', size=11),
                hovertemplate='<b>%{y}</b><br>Sales: Rp %{x:,.0f}<extra></extra>'
            )])
            
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', family='Poppins'),
                xaxis_title='Sales Amount (Rp)',
                yaxis_title='',
                height=400 if view_option == 'Per Category' else 500,
                margin=dict(l=250 if view_option == 'Per Promo' else 120, r=80, t=20, b=60)
            )
            fig1.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
            fig1.update_yaxes(tickfont=dict(color='#ffffff', size=11))
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Chart 2: Kontribusi Sales (Treemap for Per Promo, Donut for Per Category)
            st.markdown('<p class="section-title">📊 Kontribusi terhadap Net Sales</p>', unsafe_allow_html=True)
            
            contrib_df = display_df.copy()
            contrib_df['Contribution_Pct'] = contrib_df['Contribution Sales'] * 100
            contrib_df['Contrib_Label'] = contrib_df['Contribution_Pct'].apply(lambda x: f'{x:.2f}%')
            
            if view_option == 'Per Promo':
                # Treemap for Per Promo
                fig2 = px.treemap(
                    contrib_df,
                    path=['Label'],
                    values='Contribution Sales',
                    color='Contribution_Pct',
                    color_continuous_scale=[[0, '#00d4ff'], [0.5, '#7b2cbf'], [1, '#ff6b6b']],
                    hover_data={'Contribution_Pct': ':.2f'}
                )
                fig2.update_traces(
                    textinfo='label+percent root',
                    textfont=dict(color='#ffffff', size=12),
                    hovertemplate='<b>%{label}</b><br>Kontribusi: %{value:.4f}<br>Persentase: %{percentRoot:.2%}<extra></extra>'
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    height=450,
                    margin=dict(l=20, r=20, t=20, b=20),
                    coloraxis_showscale=False
                )
            else:
                # Donut for Per Category
                fig2 = go.Figure(data=[go.Pie(
                    labels=contrib_df['Label'],
                    values=contrib_df['Contribution Sales'],
                    hole=0.5,
                    marker=dict(
                        colors=['#00d4ff', '#9b5de5', '#f15bb5', '#00f5d4', '#fee440', '#ff6b6b', '#00bbf9'],
                        line=dict(color='#1a1a2e', width=3)
                    ),
                    textinfo='label+percent',
                    textfont=dict(color='#ffffff', size=12),
                    hovertemplate='<b>%{label}</b><br>Kontribusi: %{value:.4f}<br>Persentase: %{percent}<extra></extra>'
                )])
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=True,
                    legend=dict(font=dict(color='#ffffff'))
                )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Chart 3 & 4: Conversion Rates (Side by Side)
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown('<p class="section-title">🔄 Conversion Rate (Claim/Count)</p>', unsafe_allow_html=True)
                
                conv1_df = display_df.sort_values(conv_claim_col, ascending=True).copy()
                conv1_df['Conv_Label'] = conv1_df[conv_claim_col].apply(lambda x: f'{x*100:.2f}%')
                
                fig3 = go.Figure(data=[go.Bar(
                    x=conv1_df[conv_claim_col] * 100,
                    y=conv1_df['Label'],
                    orientation='h',
                    marker=dict(
                        color=conv1_df[conv_claim_col],
                        colorscale=[[0, '#ff6b6b'], [0.5, '#fee440'], [1, '#00f5d4']],
                        line=dict(color='rgba(255,255,255,0.3)', width=1)
                    ),
                    text=conv1_df['Conv_Label'],
                    textposition='outside',
                    textfont=dict(color='#ffffff', size=10),
                    hovertemplate='<b>%{y}</b><br>Conversion: %{x:.2f}%<extra></extra>'
                )])
                
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    xaxis_title='Conversion Rate (%)',
                    yaxis_title='',
                    height=400 if view_option == 'Per Category' else 500,
                    margin=dict(l=200 if view_option == 'Per Promo' else 100, r=60, t=20, b=60)
                )
                fig3.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
                fig3.update_yaxes(tickfont=dict(color='#ffffff', size=10))
                
                st.plotly_chart(fig3, use_container_width=True)
            
            with col_right:
                st.markdown('<p class="section-title">👥 Conversion Rate (Count/NOC)</p>', unsafe_allow_html=True)
                
                conv2_df = display_df.sort_values(conv_noc_col, ascending=True).copy()
                conv2_df['Conv_Label'] = conv2_df[conv_noc_col].apply(lambda x: f'{x*100:.4f}%')
                
                fig4 = go.Figure(data=[go.Bar(
                    x=conv2_df[conv_noc_col] * 100,
                    y=conv2_df['Label'],
                    orientation='h',
                    marker=dict(
                        color=conv2_df[conv_noc_col],
                        colorscale=[[0, '#ff6b6b'], [0.5, '#fee440'], [1, '#00f5d4']],
                        line=dict(color='rgba(255,255,255,0.3)', width=1)
                    ),
                    text=conv2_df['Conv_Label'],
                    textposition='outside',
                    textfont=dict(color='#ffffff', size=10),
                    hovertemplate='<b>%{y}</b><br>Conversion: %{x:.4f}%<extra></extra>'
                )])
                
                fig4.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    xaxis_title='Conversion Rate (%)',
                    yaxis_title='',
                    height=400 if view_option == 'Per Category' else 500,
                    margin=dict(l=200 if view_option == 'Per Promo' else 100, r=60, t=20, b=60)
                )
                fig4.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
                fig4.update_yaxes(tickfont=dict(color='#ffffff', size=10))
                
                st.plotly_chart(fig4, use_container_width=True)
            
            # Data Table
            st.markdown('<p class="section-title">📋 Data Table</p>', unsafe_allow_html=True)
            
            with st.expander("🔍 Lihat Detail Data", expanded=False):
                st.dataframe(display_df, use_container_width=True, height=300)
    
    # ==================== TAB QTY ====================
    with tab_qty:
        if filtered_qty.empty:
            st.warning("⚠️ Tidak ada data Qty untuk kategori yang dipilih.")
        else:
            # Prepare data based on view
            if view_option == 'Per Promo':
                display_qty = filtered_qty.copy()
                display_qty['Label'] = display_qty['Nama Promo']
                conv_claim_col_qty = 'Conversion Rate(Claim/Count)'
                conv_noc_col_qty = 'Conversion Rate(Count/NOC)'
            else:
                display_qty = aggregate_qty_by_category(filtered_qty)
                display_qty['Label'] = display_qty['Category']
                conv_claim_col_qty = 'Conversion Rate(Claim/Count)'
                conv_noc_col_qty = 'Conversion Rate(Count/NOC)'
            
            # KPI Cards
            st.markdown("### 📈 Key Performance Indicators")
            
            col1, col2, col3 = st.columns(3)
            
            total_promo_qty = len(filtered_qty) if view_option == 'Per Promo' else display_qty['Jumlah Promo'].sum()
            avg_conv_claim_qty = display_qty[conv_claim_col_qty].mean()
            avg_conv_noc_qty = display_qty[conv_noc_col_qty].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{int(total_promo_qty)}</div>
                    <div class="metric-label">🎯 Jumlah Promo</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_percent(avg_conv_claim_qty)}</div>
                    <div class="metric-label">📊 Avg Conv. (Claim/Count)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_percent(avg_conv_noc_qty)}</div>
                    <div class="metric-label">👥 Avg Conv. (Count/NOC)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart 3 & 4: Conversion Rates (Side by Side)
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown('<p class="section-title">🔄 Conversion Rate (Claim/Count)</p>', unsafe_allow_html=True)
                
                conv1_qty = display_qty.sort_values(conv_claim_col_qty, ascending=True).copy()
                conv1_qty['Conv_Label'] = conv1_qty[conv_claim_col_qty].apply(lambda x: f'{x*100:.2f}%')
                
                fig5 = go.Figure(data=[go.Bar(
                    x=conv1_qty[conv_claim_col_qty] * 100,
                    y=conv1_qty['Label'],
                    orientation='h',
                    marker=dict(
                        color=conv1_qty[conv_claim_col_qty],
                        colorscale=[[0, '#ff6b6b'], [0.5, '#fee440'], [1, '#00f5d4']],
                        line=dict(color='rgba(255,255,255,0.3)', width=1)
                    ),
                    text=conv1_qty['Conv_Label'],
                    textposition='outside',
                    textfont=dict(color='#ffffff', size=11),
                    hovertemplate='<b>%{y}</b><br>Conversion: %{x:.2f}%<extra></extra>'
                )])
                
                fig5.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    xaxis_title='Conversion Rate (%)',
                    yaxis_title='',
                    height=400 if view_option == 'Per Category' else 450,
                    margin=dict(l=280 if view_option == 'Per Promo' else 100, r=60, t=20, b=60)
                )
                fig5.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
                fig5.update_yaxes(tickfont=dict(color='#ffffff', size=10))
                
                st.plotly_chart(fig5, use_container_width=True)
            
            with col_right:
                st.markdown('<p class="section-title">👥 Conversion Rate (Count/NOC)</p>', unsafe_allow_html=True)
                
                conv2_qty = display_qty.sort_values(conv_noc_col_qty, ascending=True).copy()
                conv2_qty['Conv_Label'] = conv2_qty[conv_noc_col_qty].apply(lambda x: f'{x*100:.4f}%')
                
                fig6 = go.Figure(data=[go.Bar(
                    x=conv2_qty[conv_noc_col_qty] * 100,
                    y=conv2_qty['Label'],
                    orientation='h',
                    marker=dict(
                        color=conv2_qty[conv_noc_col_qty],
                        colorscale=[[0, '#ff6b6b'], [0.5, '#fee440'], [1, '#00f5d4']],
                        line=dict(color='rgba(255,255,255,0.3)', width=1)
                    ),
                    text=conv2_qty['Conv_Label'],
                    textposition='outside',
                    textfont=dict(color='#ffffff', size=11),
                    hovertemplate='<b>%{y}</b><br>Conversion: %{x:.4f}%<extra></extra>'
                )])
                
                fig6.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', family='Poppins'),
                    xaxis_title='Conversion Rate (%)',
                    yaxis_title='',
                    height=400 if view_option == 'Per Category' else 450,
                    margin=dict(l=280 if view_option == 'Per Promo' else 100, r=60, t=20, b=60)
                )
                fig6.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
                fig6.update_yaxes(tickfont=dict(color='#ffffff', size=10))
                
                st.plotly_chart(fig6, use_container_width=True)
            
            # Data Table
            st.markdown('<p class="section-title">📋 Data Table</p>', unsafe_allow_html=True)
            
            with st.expander("🔍 Lihat Detail Data", expanded=False):
                st.dataframe(display_qty, use_container_width=True, height=300)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #a0aec0; padding: 1rem;'>
            <p>📈 Ended Promo Dashboard - January 2026 | Built with ❤️ using Streamlit & Plotly</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
