import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 50%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
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
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 0.5rem;
    }
    
    .section-title {
        font-size: 1.3rem;
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
    
    # Load raw data
    df_sales_raw = pd.read_excel(xlsx, sheet_name='Sales', header=None)
    df_qty_raw = pd.read_excel(xlsx, sheet_name='Qty', header=None)
    
    # Extract Summary by Promo (Sales) - rows 6-22
    df_sales_promo = df_sales_raw.iloc[6:22, :11].copy()
    df_sales_promo.columns = ['Category', 'Promo Name', 'End of Period Promotion', 'Total Count',
                              'Total Claim', 'NOC', 'Conversion Rate (Count/NOC)',
                              'Conversion Rate (Claim/Count)', 'Sales Amount',
                              'Net Sales (by Category)', 'Contribution Sales']
    df_sales_promo = df_sales_promo.iloc[1:].reset_index(drop=True)
    
    # Extract Summary by Category (Sales) - rows 26-33
    df_sales_cat = df_sales_raw.iloc[26:33, :10].copy()
    df_sales_cat.columns = ['Category', 'End of Period Promotion', 'Total Count', 'Total Claim',
                            'NOC', 'Conversion Rate (Claim/Count)', 'Conversion Rate (Count/NOC)',
                            'Sales Amount', 'Net Sales (by Category)', 'Contribution Sales']
    df_sales_cat = df_sales_cat.iloc[1:].reset_index(drop=True)
    
    # Convert numeric columns - Sales Promo
    numeric_cols_promo = ['Category', 'Total Count', 'Total Claim', 'NOC',
                          'Conversion Rate (Count/NOC)', 'Conversion Rate (Claim/Count)',
                          'Sales Amount', 'Net Sales (by Category)', 'Contribution Sales']
    for col in numeric_cols_promo:
        df_sales_promo[col] = pd.to_numeric(df_sales_promo[col], errors='coerce')
    
    # Convert numeric columns - Sales Category
    numeric_cols_cat = ['Category', 'Total Count', 'Total Claim', 'NOC',
                        'Conversion Rate (Claim/Count)', 'Conversion Rate (Count/NOC)',
                        'Sales Amount', 'Net Sales (by Category)', 'Contribution Sales']
    for col in numeric_cols_cat:
        df_sales_cat[col] = pd.to_numeric(df_sales_cat[col], errors='coerce')
    
    # Extract Summary by Promo (Qty) - rows 6-16
    df_qty_promo = df_qty_raw.iloc[6:16, :8].copy()
    df_qty_promo.columns = ['Category', 'Promo Name', 'End of Period Promotion', 'Total Count',
                            'Total Claim', 'NOC', 'Conversion Rate (Claim/Count)',
                            'Conversion Rate (Count/NOC)']
    df_qty_promo = df_qty_promo.iloc[1:].reset_index(drop=True)
    
    # Extract Summary by Category (Qty) - rows 20-25
    df_qty_cat = df_qty_raw.iloc[20:25, :7].copy()
    df_qty_cat.columns = ['Category', 'End of Period Promotion', 'Total Count', 'Total Claim',
                          'NOC', 'Conversion Rate (Claim/Count)', 'Conversion Rate (Count/NOC)']
    df_qty_cat = df_qty_cat.iloc[1:].reset_index(drop=True)
    
    # Convert numeric columns - Qty
    numeric_cols_qty_promo = ['Category', 'Total Count', 'Total Claim', 'NOC',
                              'Conversion Rate (Claim/Count)', 'Conversion Rate (Count/NOC)']
    for col in numeric_cols_qty_promo:
        df_qty_promo[col] = pd.to_numeric(df_qty_promo[col], errors='coerce')
        
    numeric_cols_qty_cat = ['Category', 'Total Count', 'Total Claim', 'NOC',
                            'Conversion Rate (Claim/Count)', 'Conversion Rate (Count/NOC)']
    for col in numeric_cols_qty_cat:
        df_qty_cat[col] = pd.to_numeric(df_qty_cat[col], errors='coerce')
    
    return df_sales_promo, df_sales_cat, df_qty_promo, df_qty_cat

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

def format_billion(value):
    return f"Rp {value/1e9:.2f} B"

def format_number(value):
    return f"{value:,.0f}"

# Create horizontal bar chart
def create_bar_chart(df, x_col, y_col, title, x_label, color_scale, label_format='value', show_detail=False, detail_cols=None):
    df_sorted = df.sort_values(x_col, ascending=True).reset_index(drop=True)
    
    # Prepare colors
    values = df_sorted[x_col].values
    if color_scale == 'Blues':
        colors = [f'rgba({int(65 + 150*(1-i/len(values)))}, {int(105 + 100*(1-i/len(values)))}, {int(225)}, 0.9)' for i in range(len(values))]
    elif color_scale == 'Greens':
        colors = [f'rgba({int(50)}, {int(150 + 80*(1-i/len(values)))}, {int(80 + 80*(1-i/len(values)))}, 0.9)' for i in range(len(values))]
    elif color_scale == 'Reds':
        normalized = values / max(values) if max(values) > 0 else values
        colors = [f'rgba({int(255)}, {int(100 + 100*(1-n))}, {int(100*(1-n))}, 0.9)' for n in normalized]
    elif color_scale == 'Oranges':
        colors = [f'rgba({int(255)}, {int(180 - 80*i/len(values))}, {int(50)}, 0.9)' for i in range(len(values))]
    else:
        colors = [f'rgba(0, 212, 255, 0.8)'] * len(values)
    
    # Format labels
    if label_format == 'billion':
        text_labels = [f'Rp {v/1e9:.2f} B' for v in values]
    elif label_format == 'percent':
        text_labels = [f'{v*100:.2f}%' for v in values]
    elif label_format == 'percent_detail' and show_detail and detail_cols:
        claim_col, count_col = detail_cols
        text_labels = [f'{v*100:.1f}%  ({int(c):,} / {int(t):,})' 
                      for v, c, t in zip(values, df_sorted[claim_col], df_sorted[count_col])]
    else:
        text_labels = [f'{v:,.0f}' for v in values]
    
    fig = go.Figure(data=[go.Bar(
        x=values,
        y=df_sorted[y_col],
        orientation='h',
        marker=dict(
            color=colors[::-1],
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=text_labels,
        textposition='outside',
        textfont=dict(color='#ffffff', size=11, family='Poppins'),
        hovertemplate='<b>%{y}</b><br>' + x_label + ': %{x:,.2f}<extra></extra>'
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Poppins'),
        title=dict(text=title, font=dict(size=16, color='#ffffff'), x=0.5),
        xaxis_title=x_label,
        yaxis_title='',
        height=max(350, len(df_sorted) * 45),
        margin=dict(l=250, r=120, t=60, b=60)
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#ffffff', size=10))
    fig.update_yaxes(tickfont=dict(color='#ffffff', size=10))
    
    return fig

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Ended Promo Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Summary Promo yang Berakhir - January 2026</p>', unsafe_allow_html=True)
    
    # Load data
    try:
        df_sales_promo, df_sales_cat, df_qty_promo, df_qty_cat = load_data('Final_Summary_Ended_Promo_Jan_2026_Last.xlsx')
    except FileNotFoundError:
        st.error("⚠️ File 'Final_Summary_Ended_Promo_Jan_2026_Last.xlsx' tidak ditemukan.")
        st.stop()
    
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
        
        # Filter Category for Sales
        if view_option == 'Per Promo':
            all_cat_sales = sorted(df_sales_promo['Category'].dropna().unique())
            selected_cat_sales = st.multiselect(
                "🏷️ Filter Category (Sales)",
                options=all_cat_sales,
                default=all_cat_sales,
                format_func=lambda x: f"Category {int(x)}"
            )
            
            all_cat_qty = sorted(df_qty_promo['Category'].dropna().unique())
            selected_cat_qty = st.multiselect(
                "🏷️ Filter Category (Qty)",
                options=all_cat_qty,
                default=all_cat_qty,
                format_func=lambda x: f"Category {int(x)}"
            )
        else:
            all_cat_sales = sorted(df_sales_cat['Category'].dropna().unique())
            selected_cat_sales = st.multiselect(
                "🏷️ Filter Category (Sales)",
                options=all_cat_sales,
                default=all_cat_sales,
                format_func=lambda x: f"Category {int(x)}"
            )
            
            all_cat_qty = sorted(df_qty_cat['Category'].dropna().unique())
            selected_cat_qty = st.multiselect(
                "🏷️ Filter Category (Qty)",
                options=all_cat_qty,
                default=all_cat_qty,
                format_func=lambda x: f"Category {int(x)}"
            )
        
        st.markdown("---")
        st.markdown("### 📌 Info")
        st.info(f"**View:** {view_option}")
    
    # Filter data based on selection
    if view_option == 'Per Promo':
        df_sales = df_sales_promo[df_sales_promo['Category'].isin(selected_cat_sales)].copy()
        df_sales['Label'] = df_sales['Promo Name'].apply(lambda x: x[:35] + '...' if len(str(x)) > 35 else x)
        
        df_qty = df_qty_promo[df_qty_promo['Category'].isin(selected_cat_qty)].copy()
        df_qty['Label'] = df_qty['Promo Name'].apply(lambda x: x[:35] + '...' if len(str(x)) > 35 else x)
    else:
        df_sales = df_sales_cat[df_sales_cat['Category'].isin(selected_cat_sales)].copy()
        df_sales['Label'] = 'Category ' + df_sales['Category'].astype(int).astype(str)
        
        df_qty = df_qty_cat[df_qty_cat['Category'].isin(selected_cat_qty)].copy()
        df_qty['Label'] = 'Category ' + df_qty['Category'].astype(int).astype(str)
    
    # Tabs
    tab_sales, tab_qty = st.tabs(["💰 SALES", "📦 QTY"])
    
    # ==================== TAB SALES ====================
    with tab_sales:
        if df_sales.empty:
            st.warning("⚠️ Tidak ada data Sales untuk kategori yang dipilih.")
        else:
            # KPI Cards
            st.markdown("### 📈 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales = df_sales['Sales Amount'].sum()
            total_promo = len(df_sales)
            avg_conv_claim = df_sales['Conversion Rate (Claim/Count)'].mean()
            avg_conv_noc = df_sales['Conversion Rate (Count/NOC)'].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{format_rupiah(total_sales)}</div>
                    <div class="metric-label">💰 Total Sales</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{total_promo}</div>
                    <div class="metric-label">🎯 Jumlah {'Promo' if view_option == 'Per Promo' else 'Category'}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{avg_conv_claim*100:.2f}%</div>
                    <div class="metric-label">📊 Avg Claim/Count</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{avg_conv_noc*100:.4f}%</div>
                    <div class="metric-label">👥 Avg Count/NOC</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart 1: Sales Amount Ranking
            st.markdown(f'<p class="section-title">💰 Ranking Sales Amount (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig1 = create_bar_chart(
                df_sales, 'Sales Amount', 'Label',
                '', 'Sales Amount (Billion Rp)',
                'Blues', label_format='billion'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Chart 2: Contribution Sales Ranking
            st.markdown(f'<p class="section-title">📊 Ranking Contribution Sales (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig2 = create_bar_chart(
                df_sales, 'Contribution Sales', 'Label',
                '', 'Contribution Sales (%)',
                'Greens', label_format='percent'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Chart 3: Conversion Rate (Claim/Count)
            st.markdown(f'<p class="section-title">🔄 Conversion Rate - Claim/Count (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig3 = create_bar_chart(
                df_sales, 'Conversion Rate (Claim/Count)', 'Label',
                '', 'Conversion Rate (%)',
                'Reds', label_format='percent_detail',
                show_detail=True, detail_cols=['Total Claim', 'Total Count']
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Chart 4: Conversion Rate (Count/NOC)
            st.markdown(f'<p class="section-title">👥 Conversion Rate - Count/NOC (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig4 = create_bar_chart(
                df_sales, 'Conversion Rate (Count/NOC)', 'Label',
                '', 'Conversion Rate (%)',
                'Oranges', label_format='percent_detail',
                show_detail=True, detail_cols=['Total Count', 'NOC']
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            # Data Table
            st.markdown('<p class="section-title">📋 Data Table</p>', unsafe_allow_html=True)
            with st.expander("🔍 Lihat Detail Data", expanded=False):
                st.dataframe(df_sales, use_container_width=True, height=300)
    
    # ==================== TAB QTY ====================
    with tab_qty:
        if df_qty.empty:
            st.warning("⚠️ Tidak ada data Qty untuk kategori yang dipilih.")
        else:
            # KPI Cards
            st.markdown("### 📈 Key Performance Indicators")
            
            col1, col2, col3 = st.columns(3)
            
            total_promo_qty = len(df_qty)
            avg_conv_claim_qty = df_qty['Conversion Rate (Claim/Count)'].mean()
            avg_conv_noc_qty = df_qty['Conversion Rate (Count/NOC)'].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{total_promo_qty}</div>
                    <div class="metric-label">🎯 Jumlah {'Promo' if view_option == 'Per Promo' else 'Category'}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{avg_conv_claim_qty*100:.2f}%</div>
                    <div class="metric-label">📊 Avg Claim/Count</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{avg_conv_noc_qty*100:.4f}%</div>
                    <div class="metric-label">👥 Avg Count/NOC</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart 1: Conversion Rate (Claim/Count)
            st.markdown(f'<p class="section-title">🔄 Conversion Rate - Claim/Count (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig5 = create_bar_chart(
                df_qty, 'Conversion Rate (Claim/Count)', 'Label',
                '', 'Conversion Rate (%)',
                'Reds', label_format='percent_detail',
                show_detail=True, detail_cols=['Total Claim', 'Total Count']
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Chart 2: Conversion Rate (Count/NOC)
            st.markdown(f'<p class="section-title">👥 Conversion Rate - Count/NOC (by {view_option.replace("Per ", "")})</p>', unsafe_allow_html=True)
            
            fig6 = create_bar_chart(
                df_qty, 'Conversion Rate (Count/NOC)', 'Label',
                '', 'Conversion Rate (%)',
                'Oranges', label_format='percent_detail',
                show_detail=True, detail_cols=['Total Count', 'NOC']
            )
            st.plotly_chart(fig6, use_container_width=True)
            
            # Data Table
            st.markdown('<p class="section-title">📋 Data Table</p>', unsafe_allow_html=True)
            with st.expander("🔍 Lihat Detail Data", expanded=False):
                st.dataframe(df_qty, use_container_width=True, height=300)
    
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
