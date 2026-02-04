import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Promo Performance Dashboard",
    page_icon="📊",
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

# Custom CSS - Dark Theme dengan kontras tinggi
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
        text-shadow: 0 0 30px rgba(0,212,255,0.3);
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
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
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
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    
    .stSelectbox label, .stMultiSelect label, .stRadio label {
        font-weight: 500;
        color: #ffffff !important;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #ffffff;
    }
    
    .stExpander {
        background: linear-gradient(145deg, #1e2a4a 0%, #252f4a 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load Data Function
@st.cache_data
def load_data(file_path):
    xlsx = pd.ExcelFile(file_path)
    
    data = {
        'all_year': pd.read_excel(xlsx, sheet_name='Summary All (Year)'),
        'all_month': pd.read_excel(xlsx, sheet_name='Summary All (Month)'),
        'non_cig_year': pd.read_excel(xlsx, sheet_name='Summary Non Cigarette (Year)'),
        'non_cig_month': pd.read_excel(xlsx, sheet_name='Summary Non Cigarette (Month)')
    }
    
    for key in ['all_year', 'non_cig_year']:
        if 'Jumlah Promo' in data[key].columns:
            data[key] = data[key].rename(columns={'Jumlah Promo': 'Qty Promo'})
    
    month_order = [
        'January 2025', 'February 2025', 'March 2025', 'April 2025',
        'May 2025', 'June 2025', 'July 2025', 'August 2025',
        'September 2025', 'October 2025', 'November 2025', 'December 2025'
    ]
    
    for key in ['all_month', 'non_cig_month']:
        data[key]['Month'] = pd.Categorical(data[key]['Month'], categories=month_order, ordered=True)
        data[key] = data[key].sort_values(['Category', 'Month'])
    
    return data

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

def format_number(value):
    if value >= 1e6:
        return f"{value/1e6:.2f} Jt"
    elif value >= 1e3:
        return f"{value/1e3:.1f} K"
    else:
        return f"{value:,.0f}"

def format_short_rupiah(value):
    if value >= 1e12:
        return f"{value/1e12:.1f}T"
    elif value >= 1e9:
        return f"{value/1e9:.1f}M"
    elif value >= 1e6:
        return f"{value/1e6:.0f}Jt"
    else:
        return f"{value:,.0f}"

# Color palette
CATEGORY_COLORS_LIST = ['#00d4ff', '#9b5de5', '#f15bb5', '#00f5d4', '#fee440', '#ff6b6b', '#00bbf9']

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Promo Performance Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analisis Performa Promosi dan Kontribusi terhadap Net Sales</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        data = load_data('all_summary.xlsx')
    except FileNotFoundError:
        st.error("⚠️ File 'all_summary.xlsx' tidak ditemukan. Pastikan file berada di direktori yang sama dengan app.py")
        st.stop()
    
    # Sidebar Filters
    with st.sidebar:
        st.markdown("## 🎛️ Filter Data")
        st.markdown("---")
        
        dataset_option = st.radio(
            "📁 Pilih Dataset",
            options=['Summary All', 'Summary Non Cigarette'],
            index=0,
            help="Pilih antara data keseluruhan atau data tanpa rokok"
        )
        
        st.markdown("---")
        
        view_option = st.radio(
            "📅 Pilih Tampilan",
            options=['Yearly', 'Monthly'],
            index=1,
            help="Pilih tampilan data tahunan atau bulanan"
        )
        
        st.markdown("---")
        
        if dataset_option == 'Summary All':
            df_year = data['all_year']
            df_month = data['all_month']
        else:
            df_year = data['non_cig_year']
            df_month = data['non_cig_month']
        
        current_df = df_month if view_option == 'Monthly' else df_year
        
        all_categories = sorted(current_df['Category'].unique())
        selected_categories = st.multiselect(
            "🏷️ Filter Category",
            options=all_categories,
            default=all_categories,
            help="Pilih kategori yang ingin ditampilkan"
        )
        
        if view_option == 'Monthly':
            st.markdown("---")
            all_months = current_df['Month'].cat.categories.tolist()
            selected_months = st.multiselect(
                "📆 Filter Bulan",
                options=all_months,
                default=all_months,
                help="Pilih bulan yang ingin ditampilkan"
            )
        
        st.markdown("---")
        st.markdown("### 📌 Info")
        st.info(f"**Dataset:** {dataset_option}\n\n**View:** {view_option}\n\n**Categories:** {len(selected_categories)}")
    
    # Filter data
    if view_option == 'Monthly':
        filtered_df = current_df[
            (current_df['Category'].isin(selected_categories)) & 
            (current_df['Month'].isin(selected_months))
        ].copy()
    else:
        filtered_df = current_df[current_df['Category'].isin(selected_categories)].copy()
    
    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter. Silakan ubah filter Anda.")
        st.stop()
    
    kontribusi_col = 'Kontribusi Promo pada Net Sales' if 'Kontribusi Promo pada Net Sales' in filtered_df.columns else 'Kontribusi Sales'
    
    # Calculate KPIs
    total_sales = filtered_df['Sales Amount'].sum()
    total_noc = filtered_df['NOC'].sum()
    total_qty_promo = filtered_df['Qty Promo'].sum()
    avg_kontribusi = filtered_df[kontribusi_col].mean() * 100
    total_net_sales = filtered_df['Net Sales (by Group Category)'].sum()
    
    # KPI Cards
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            <div class="metric-value">{format_number(total_noc)}</div>
            <div class="metric-label">👥 Total NOC</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_qty_promo:,}</div>
            <div class="metric-label">🎯 Total Qty Promo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_kontribusi:.2f}%</div>
            <div class="metric-label">📊 Avg Kontribusi</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{format_rupiah(total_net_sales)}</div>
            <div class="metric-label">💎 Total Net Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== CHART 1: Sales Amount + Kontribusi ====================
    st.markdown('<p class="section-title">📊 Sales Amount & Kontribusi Promo terhadap Net Sales</p>', unsafe_allow_html=True)
    
    if view_option == 'Monthly':
        chart1_data = filtered_df.groupby('Month', observed=True).agg({
            'Sales Amount': 'sum',
            kontribusi_col: 'mean'
        }).reset_index()
        chart1_data['X_Label'] = chart1_data['Month'].astype(str).str.replace(' 2025', '')
        x_title = 'Bulan'
    else:
        chart1_data = filtered_df.groupby('Category').agg({
            'Sales Amount': 'sum',
            kontribusi_col: 'mean'
        }).reset_index()
        chart1_data['X_Label'] = 'Cat ' + chart1_data['Category'].astype(str)
        x_title = 'Category'
    
    chart1_data['Sales_Label'] = chart1_data['Sales Amount'].apply(format_short_rupiah)
    chart1_data['Kontribusi_Pct'] = chart1_data[kontribusi_col] * 100
    chart1_data['Kontribusi_Label'] = chart1_data['Kontribusi_Pct'].apply(lambda x: f'{x:.2f}%')
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig1.add_trace(
        go.Bar(
            x=chart1_data['X_Label'],
            y=chart1_data['Sales Amount'],
            name='Sales Amount',
            marker=dict(
                color=chart1_data['Sales Amount'],
                colorscale=[[0, '#00d4ff'], [0.5, '#7b2cbf'], [1, '#ff6b6b']],
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ),
            text=chart1_data['Sales_Label'],
            textposition='outside',
            textfont=dict(color='#ffffff', size=12),
            hovertemplate='<b>%{x}</b><br>Sales: Rp %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig1.add_trace(
        go.Scatter(
            x=chart1_data['X_Label'],
            y=chart1_data['Kontribusi_Pct'],
            name='Kontribusi (%)',
            mode='lines+markers+text',
            line=dict(color='#fee440', width=4),
            marker=dict(size=14, symbol='diamond', color='#fee440', 
                       line=dict(color='#ffffff', width=2)),
            text=chart1_data['Kontribusi_Label'],
            textposition='top center',
            textfont=dict(color='#fee440', size=12),
            hovertemplate='<b>%{x}</b><br>Kontribusi: %{y:.2f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig1.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Poppins'),
        xaxis_title=x_title,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            font=dict(color='#ffffff', size=12),
            bgcolor='rgba(0,0,0,0.3)'
        ),
        hovermode='x unified',
        height=500,
        margin=dict(l=80, r=80, t=80, b=80),
        bargap=0.3
    )
    
    fig1.update_xaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#ffffff', size=12),
        title_font=dict(color='#ffffff', size=14)
    )
    fig1.update_yaxes(
        title_text="Sales Amount (Rp)", 
        secondary_y=False, 
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#00d4ff', size=11),
        title_font=dict(color='#00d4ff', size=13)
    )
    fig1.update_yaxes(
        title_text="Kontribusi (%)", 
        secondary_y=True, 
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='#fee440', size=11),
        title_font=dict(color='#fee440', size=13)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # ==================== CHART 2: NOC dan Visit Customer (SINGLE SCALE LINE CHART) ====================
    st.markdown('<p class="section-title">👥 Perbandingan NOC dan Visit Customer</p>', unsafe_allow_html=True)
    
    if view_option == 'Monthly':
        chart2_data = filtered_df.groupby('Month', observed=True).agg({
            'NOC': 'sum',
            'Visit Customer': 'mean'
        }).reset_index()
        chart2_data['X_Label'] = chart2_data['Month'].astype(str).str.replace(' 2025', '')
    else:
        chart2_data = filtered_df.groupby('Category').agg({
            'NOC': 'sum',
            'Visit Customer': 'mean'
        }).reset_index()
        chart2_data['X_Label'] = 'Cat ' + chart2_data['Category'].astype(str)
    
    chart2_data['NOC_Label'] = chart2_data['NOC'].apply(format_number)
    chart2_data['Visit_Label'] = chart2_data['Visit Customer'].apply(format_number)
    chart2_data['Conversion_Rate'] = (chart2_data['NOC'] / chart2_data['Visit Customer'] * 100)
    chart2_data['Conversion_Label'] = chart2_data['Conversion_Rate'].apply(lambda x: f'{x:.2f}%')
    
    # Single Line Chart dengan satu skala
    fig2 = go.Figure()
    
    # Line NOC
    fig2.add_trace(
        go.Scatter(
            x=chart2_data['X_Label'],
            y=chart2_data['NOC'],
            name='NOC',
            mode='lines+markers+text',
            line=dict(color='#00f5d4', width=4),
            marker=dict(size=12, color='#00f5d4', symbol='circle',
                       line=dict(color='#ffffff', width=2)),
            text=chart2_data['NOC_Label'],
            textposition='top center',
            textfont=dict(color='#00f5d4', size=11),
            hovertemplate='<b>%{x}</b><br>NOC: %{y:,.0f}<extra></extra>'
        )
    )
    
    # Line Visit Customer
    fig2.add_trace(
        go.Scatter(
            x=chart2_data['X_Label'],
            y=chart2_data['Visit Customer'],
            name='Visit Customer',
            mode='lines+markers+text',
            line=dict(color='#f15bb5', width=4),
            marker=dict(size=12, color='#f15bb5', symbol='diamond',
                       line=dict(color='#ffffff', width=2)),
            text=chart2_data['Visit_Label'],
            textposition='top center',
            textfont=dict(color='#f15bb5', size=11),
            hovertemplate='<b>%{x}</b><br>Visit: %{y:,.0f}<extra></extra>'
        )
    )
    
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Poppins'),
        xaxis_title=x_title,
        yaxis_title='Jumlah',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            font=dict(color='#ffffff', size=12),
            bgcolor='rgba(0,0,0,0.3)'
        ),
        hovermode='x unified',
        height=450,
        margin=dict(l=80, r=40, t=80, b=80)
    )
    
    fig2.update_xaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#ffffff', size=11),
        title_font=dict(color='#ffffff', size=13)
    )
    fig2.update_yaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#ffffff', size=11),
        title_font=dict(color='#ffffff', size=13)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # ==================== CHART 3: CONVERSION RATE (NOC / Visit Customer) ====================
    st.markdown('<p class="section-title">🎯 Conversion Rate (NOC / Visit Customer)</p>', unsafe_allow_html=True)
    
    fig_conversion = go.Figure()
    
    # Area chart untuk conversion rate
    fig_conversion.add_trace(
        go.Scatter(
            x=chart2_data['X_Label'],
            y=chart2_data['Conversion_Rate'],
            name='Conversion Rate',
            mode='lines+markers+text',
            fill='tozeroy',
            fillcolor='rgba(254, 228, 64, 0.2)',
            line=dict(color='#fee440', width=4),
            marker=dict(size=14, color='#fee440', line=dict(color='#ffffff', width=2)),
            text=chart2_data['Conversion_Label'],
            textposition='top center',
            textfont=dict(color='#fee440', size=12, family='Poppins'),
            hovertemplate='<b>%{x}</b><br>Conversion Rate: %{y:.2f}%<extra></extra>'
        )
    )
    
    # Add average line
    avg_conversion = chart2_data['Conversion_Rate'].mean()
    fig_conversion.add_hline(
        y=avg_conversion, 
        line_dash="dash", 
        line_color="#ff6b6b",
        annotation_text=f"Avg: {avg_conversion:.2f}%",
        annotation_position="right",
        annotation_font=dict(color='#ff6b6b', size=12)
    )
    
    fig_conversion.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Poppins'),
        xaxis_title=x_title,
        yaxis_title='Conversion Rate (%)',
        height=400,
        margin=dict(l=80, r=80, t=40, b=80),
        showlegend=False
    )
    
    fig_conversion.update_xaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#ffffff', size=12),
        title_font=dict(color='#ffffff', size=14)
    )
    fig_conversion.update_yaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#fee440', size=11),
        title_font=dict(color='#fee440', size=13)
    )
    
    st.plotly_chart(fig_conversion, use_container_width=True)
    
    # Info box untuk Conversion Rate
    avg_conv = chart2_data['Conversion_Rate'].mean()
    max_conv = chart2_data['Conversion_Rate'].max()
    min_conv = chart2_data['Conversion_Rate'].min()
    max_period = chart2_data.loc[chart2_data['Conversion_Rate'].idxmax(), 'X_Label']
    min_period = chart2_data.loc[chart2_data['Conversion_Rate'].idxmin(), 'X_Label']
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 4px solid #fee440;">
            <div class="metric-value" style="font-size: 1.5rem;">{avg_conv:.2f}%</div>
            <div class="metric-label">📊 Rata-rata Conversion</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 4px solid #00f5d4;">
            <div class="metric-value" style="font-size: 1.5rem;">{max_conv:.2f}%</div>
            <div class="metric-label">🔝 Tertinggi ({max_period})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 4px solid #ff6b6b;">
            <div class="metric-value" style="font-size: 1.5rem;">{min_conv:.2f}%</div>
            <div class="metric-label">🔻 Terendah ({min_period})</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== ROW: Pie + Bar Charts ====================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<p class="section-title">🥧 Distribusi Sales Amount per Category</p>', unsafe_allow_html=True)
        
        pie_data = filtered_df.groupby('Category')['Sales Amount'].sum().reset_index()
        pie_data['Category_Label'] = 'Category ' + pie_data['Category'].astype(str)
        pie_data['Percentage'] = (pie_data['Sales Amount'] / pie_data['Sales Amount'].sum() * 100).round(2)
        
        fig3 = go.Figure(data=[go.Pie(
            labels=pie_data['Category_Label'],
            values=pie_data['Sales Amount'],
            hole=0.5,
            marker=dict(
                colors=CATEGORY_COLORS_LIST[:len(pie_data)],
                line=dict(color='#1a1a2e', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(color='#ffffff', size=11),
            hovertemplate='<b>%{label}</b><br>Sales: Rp %{value:,.0f}<br>Persentase: %{percent}<extra></extra>',
            pull=[0.02] * len(pie_data)
        )])
        
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            showlegend=True,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.15, 
                xanchor="center", 
                x=0.5,
                font=dict(color='#ffffff', size=10)
            ),
            height=450,
            margin=dict(l=20, r=20, t=20, b=80),
            annotations=[dict(
                text=f'<b>Total</b><br>{format_short_rupiah(pie_data["Sales Amount"].sum())}',
                x=0.5, y=0.5,
                font=dict(size=14, color='#ffffff', family='Poppins'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_right:
        st.markdown('<p class="section-title">📦 Jumlah Promo per Category</p>', unsafe_allow_html=True)
        
        promo_data = filtered_df.groupby('Category')['Qty Promo'].sum().reset_index()
        promo_data = promo_data.sort_values('Qty Promo', ascending=True)
        promo_data['Category_Label'] = 'Category ' + promo_data['Category'].astype(str)
        
        fig4 = go.Figure(data=[go.Bar(
            x=promo_data['Qty Promo'],
            y=promo_data['Category_Label'],
            orientation='h',
            marker=dict(
                color=promo_data['Qty Promo'],
                colorscale=[[0, '#00d4ff'], [0.5, '#9b5de5'], [1, '#f15bb5']],
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ),
            text=promo_data['Qty Promo'],
            textposition='outside',
            textfont=dict(color='#ffffff', size=12),
            hovertemplate='<b>%{y}</b><br>Qty Promo: %{x}<extra></extra>'
        )])
        
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            xaxis_title='Jumlah Promo',
            yaxis_title='',
            height=450,
            margin=dict(l=100, r=60, t=20, b=60)
        )
        
        fig4.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
        fig4.update_yaxes(tickfont=dict(color='#ffffff', size=12))
        
        st.plotly_chart(fig4, use_container_width=True)
    
    # ==================== CHART 5: Heatmap (Monthly only) ====================
    if view_option == 'Monthly':
        st.markdown('<p class="section-title">🗓️ Heatmap: Sales Amount per Category per Bulan</p>', unsafe_allow_html=True)
        
        heatmap_data = filtered_df.pivot_table(
            values='Sales Amount',
            index='Category',
            columns='Month',
            aggfunc='sum'
        )
        
        month_order = [m for m in [
            'January 2025', 'February 2025', 'March 2025', 'April 2025',
            'May 2025', 'June 2025', 'July 2025', 'August 2025',
            'September 2025', 'October 2025', 'November 2025', 'December 2025'
        ] if m in heatmap_data.columns]
        
        heatmap_data = heatmap_data[month_order]
        
        short_months = [m.replace(' 2025', '').replace('January', 'Jan').replace('February', 'Feb')
                       .replace('March', 'Mar').replace('April', 'Apr')
                       .replace('June', 'Jun').replace('July', 'Jul').replace('August', 'Aug')
                       .replace('September', 'Sep').replace('October', 'Oct').replace('November', 'Nov')
                       .replace('December', 'Dec') for m in month_order]
        
        text_annotations = [[format_short_rupiah(val) if not pd.isna(val) else '' for val in row] for row in heatmap_data.values]
        
        fig5 = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=short_months,
            y=['Cat ' + str(c) for c in heatmap_data.index],
            colorscale=[[0, '#1a1a2e'], [0.25, '#00d4ff'], [0.5, '#9b5de5'], [0.75, '#f15bb5'], [1, '#ff6b6b']],
            text=text_annotations,
            texttemplate='%{text}',
            textfont=dict(color='#ffffff', size=10),
            hovertemplate='Category: %{y}<br>Bulan: %{x}<br>Sales: Rp %{z:,.0f}<extra></extra>',
            colorbar=dict(
                title=dict(text='Sales', font=dict(color='#ffffff')),
                tickfont=dict(color='#ffffff')
            )
        ))
        
        fig5.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            xaxis_title='Bulan',
            yaxis_title='Category',
            height=400,
            margin=dict(l=80, r=20, t=20, b=80)
        )
        
        fig5.update_xaxes(tickfont=dict(color='#ffffff', size=11), side='bottom')
        fig5.update_yaxes(tickfont=dict(color='#ffffff', size=12))
        
        st.plotly_chart(fig5, use_container_width=True)
    
    # ==================== CHART 6: Top Performers ====================
    st.markdown('<p class="section-title">🏆 Top Category Performance</p>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        top_sales = filtered_df.groupby('Category')['Sales Amount'].sum().sort_values(ascending=False).head(3).reset_index()
        top_sales['Category_Label'] = 'Cat ' + top_sales['Category'].astype(str)
        
        fig6a = go.Figure(data=[go.Bar(
            x=top_sales['Category_Label'],
            y=top_sales['Sales Amount'],
            marker=dict(color=['#ffd700', '#c0c0c0', '#cd7f32']),
            text=[format_short_rupiah(v) for v in top_sales['Sales Amount']],
            textposition='outside',
            textfont=dict(color='#ffffff', size=12)
        )])
        
        fig6a.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            title=dict(text='🥇 Top 3 Sales Amount', font=dict(size=14, color='#ffffff')),
            height=350,
            margin=dict(l=40, r=40, t=60, b=40),
            yaxis_title='Sales Amount'
        )
        fig6a.update_xaxes(tickfont=dict(color='#ffffff'))
        fig6a.update_yaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
        
        st.plotly_chart(fig6a, use_container_width=True)
    
    with col_b:
        top_noc = filtered_df.groupby('Category')['NOC'].sum().sort_values(ascending=False).head(3).reset_index()
        top_noc['Category_Label'] = 'Cat ' + top_noc['Category'].astype(str)
        
        fig6b = go.Figure(data=[go.Bar(
            x=top_noc['Category_Label'],
            y=top_noc['NOC'],
            marker=dict(color=['#ffd700', '#c0c0c0', '#cd7f32']),
            text=[format_number(v) for v in top_noc['NOC']],
            textposition='outside',
            textfont=dict(color='#ffffff', size=12)
        )])
        
        fig6b.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            title=dict(text='🥇 Top 3 NOC', font=dict(size=14, color='#ffffff')),
            height=350,
            margin=dict(l=40, r=40, t=60, b=40),
            yaxis_title='NOC'
        )
        fig6b.update_xaxes(tickfont=dict(color='#ffffff'))
        fig6b.update_yaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
        
        st.plotly_chart(fig6b, use_container_width=True)
    
    with col_c:
        top_kontribusi = filtered_df.groupby('Category')[kontribusi_col].mean().sort_values(ascending=False).head(3).reset_index()
        top_kontribusi['Category_Label'] = 'Cat ' + top_kontribusi['Category'].astype(str)
        top_kontribusi['Kontribusi_Pct'] = top_kontribusi[kontribusi_col] * 100
        
        fig6c = go.Figure(data=[go.Bar(
            x=top_kontribusi['Category_Label'],
            y=top_kontribusi['Kontribusi_Pct'],
            marker=dict(color=['#ffd700', '#c0c0c0', '#cd7f32']),
            text=[f'{v:.2f}%' for v in top_kontribusi['Kontribusi_Pct']],
            textposition='outside',
            textfont=dict(color='#ffffff', size=12)
        )])
        
        fig6c.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', family='Poppins'),
            title=dict(text='🥇 Top 3 Kontribusi', font=dict(size=14, color='#ffffff')),
            height=350,
            margin=dict(l=40, r=40, t=60, b=40),
            yaxis_title='Kontribusi (%)'
        )
        fig6c.update_xaxes(tickfont=dict(color='#ffffff'))
        fig6c.update_yaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff'))
        
        st.plotly_chart(fig6c, use_container_width=True)
    
    # ==================== Data Table ====================
    st.markdown('<p class="section-title">📋 Data Table</p>', unsafe_allow_html=True)
    
    with st.expander("🔍 Lihat Detail Data", expanded=False):
        display_df = filtered_df.copy()
        display_df['Sales Amount (Formatted)'] = display_df['Sales Amount'].apply(format_rupiah)
        display_df['NOC (Formatted)'] = display_df['NOC'].apply(format_number)
        display_df['Kontribusi (%)'] = (display_df[kontribusi_col] * 100).round(2).astype(str) + '%'
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f"promo_data_{dataset_option.lower().replace(' ', '_')}_{view_option.lower()}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6b7280; padding: 1rem;'>
            <p style='color: #a0aec0;'>📊 Promo Performance Dashboard | Built with ❤️ using Streamlit & Plotly</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
