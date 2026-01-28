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

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .stSelectbox label, .stMultiSelect label {
        font-weight: 500;
        color: #374151;
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
    
    # Standardize column names
    for key in ['all_year', 'non_cig_year']:
        if 'Jumlah Promo' in data[key].columns:
            data[key] = data[key].rename(columns={'Jumlah Promo': 'Qty Promo'})
    
    # Define month order
    month_order = [
        'January 2025', 'February 2025', 'March 2025', 'April 2025',
        'May 2025', 'June 2025', 'July 2025', 'August 2025',
        'September 2025', 'October 2025', 'November 2025', 'December 2025'
    ]
    
    # Sort monthly data
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

# Color palette
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f093fb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6'
}

CATEGORY_COLORS = {
    11: '#667eea',
    14: '#764ba2', 
    17: '#f093fb',
    19: '#10b981',
    21: '#f59e0b',
    26: '#ef4444',
    27: '#3b82f6'
}

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
        
        # Dataset selection
        dataset_option = st.radio(
            "📁 Pilih Dataset",
            options=['Summary All', 'Summary Non Cigarette'],
            index=0,
            help="Pilih antara data keseluruhan atau data tanpa rokok"
        )
        
        st.markdown("---")
        
        # View selection
        view_option = st.radio(
            "📅 Pilih Tampilan",
            options=['Yearly', 'Monthly'],
            index=1,
            help="Pilih tampilan data tahunan atau bulanan"
        )
        
        st.markdown("---")
        
        # Get current dataframe based on selection
        if dataset_option == 'Summary All':
            df_year = data['all_year']
            df_month = data['all_month']
        else:
            df_year = data['non_cig_year']
            df_month = data['non_cig_month']
        
        current_df = df_month if view_option == 'Monthly' else df_year
        
        # Category filter
        all_categories = sorted(current_df['Category'].unique())
        selected_categories = st.multiselect(
            "🏷️ Filter Category",
            options=all_categories,
            default=all_categories,
            help="Pilih kategori yang ingin ditampilkan"
        )
        
        # Month filter (only for monthly view)
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
        st.info(f"Dataset: **{dataset_option}**\nView: **{view_option}**\nCategories: **{len(selected_categories)}**")
    
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
    
    # KPI Cards
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = filtered_df['Sales Amount'].sum()
    total_noc = filtered_df['NOC'].sum()
    total_visit = filtered_df['Visit Customer'].mean() if view_option == 'Yearly' else filtered_df['Visit Customer'].iloc[-1] if len(filtered_df) > 0 else 0
    avg_kontribusi = filtered_df['Kontribusi Promo pada Net Sales'].mean() if 'Kontribusi Promo pada Net Sales' in filtered_df.columns else filtered_df['Kontribusi Sales'].mean()
    
    with col1:
        st.metric(
            label="💰 Total Sales Amount",
            value=format_rupiah(total_sales),
            delta=None
        )
    
    with col2:
        st.metric(
            label="👥 Total NOC",
            value=format_number(total_noc),
            delta=None
        )
    
    with col3:
        st.metric(
            label="🏪 Visit Customer",
            value=format_number(total_visit),
            delta=None
        )
    
    with col4:
        st.metric(
            label="📊 Avg Kontribusi Promo",
            value=f"{avg_kontribusi*100:.2f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Chart 1: Sales Amount (Bar) + Kontribusi (Line) - Combo Chart
    st.markdown("### 📊 Sales Amount & Kontribusi Promo terhadap Net Sales")
    
    kontribusi_col = 'Kontribusi Promo pada Net Sales' if 'Kontribusi Promo pada Net Sales' in filtered_df.columns else 'Kontribusi Sales'
    
    if view_option == 'Monthly':
        # Aggregate by month
        chart1_data = filtered_df.groupby('Month', observed=True).agg({
            'Sales Amount': 'sum',
            kontribusi_col: 'mean'
        }).reset_index()
        x_axis = 'Month'
        x_title = 'Bulan'
    else:
        chart1_data = filtered_df.groupby('Category').agg({
            'Sales Amount': 'sum',
            kontribusi_col: 'mean'
        }).reset_index()
        chart1_data['Category'] = chart1_data['Category'].astype(str)
        x_axis = 'Category'
        x_title = 'Category'
    
    # Create combo chart
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Bar chart for Sales Amount
    fig1.add_trace(
        go.Bar(
            x=chart1_data[x_axis],
            y=chart1_data['Sales Amount'],
            name='Sales Amount',
            marker_color='#667eea',
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>Sales: Rp %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Line chart for Kontribusi
    fig1.add_trace(
        go.Scatter(
            x=chart1_data[x_axis],
            y=chart1_data[kontribusi_col] * 100,
            name='Kontribusi (%)',
            mode='lines+markers',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=10, symbol='diamond'),
            hovertemplate='<b>%{x}</b><br>Kontribusi: %{y:.2f}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig1.update_layout(
        title=dict(text='', font=dict(size=16)),
        xaxis_title=x_title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(l=60, r=60, t=40, b=60)
    )
    
    fig1.update_yaxes(title_text="Sales Amount (Rp)", secondary_y=False, gridcolor='#f0f0f0')
    fig1.update_yaxes(title_text="Kontribusi (%)", secondary_y=True, gridcolor='#f0f0f0')
    fig1.update_xaxes(gridcolor='#f0f0f0')
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: NOC vs Visit Customer
    st.markdown("### 👥 Perbandingan NOC vs Visit Customer")
    
    if view_option == 'Monthly':
        chart2_data = filtered_df.groupby('Month', observed=True).agg({
            'NOC': 'sum',
            'Visit Customer': 'mean'
        }).reset_index()
        x_axis2 = 'Month'
    else:
        chart2_data = filtered_df.groupby('Category').agg({
            'NOC': 'sum',
            'Visit Customer': 'mean'
        }).reset_index()
        chart2_data['Category'] = chart2_data['Category'].astype(str)
        x_axis2 = 'Category'
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(
        go.Scatter(
            x=chart2_data[x_axis2],
            y=chart2_data['NOC'],
            name='NOC',
            mode='lines+markers',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>NOC: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig2.add_trace(
        go.Scatter(
            x=chart2_data[x_axis2],
            y=chart2_data['Visit Customer'],
            name='Visit Customer',
            mode='lines+markers',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Visit: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig2.update_layout(
        title=dict(text='', font=dict(size=16)),
        xaxis_title=x_title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=60, r=60, t=40, b=60)
    )
    
    fig2.update_yaxes(title_text="NOC", secondary_y=False, gridcolor='#f0f0f0')
    fig2.update_yaxes(title_text="Visit Customer", secondary_y=True, gridcolor='#f0f0f0')
    fig2.update_xaxes(gridcolor='#f0f0f0')
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Additional Charts Row
    col_left, col_right = st.columns(2)
    
    # Chart 3: Pie Chart - Distribusi Sales Amount per Category
    with col_left:
        st.markdown("### 🥧 Distribusi Sales Amount per Category")
        
        pie_data = filtered_df.groupby('Category')['Sales Amount'].sum().reset_index()
        pie_data['Category'] = pie_data['Category'].astype(str)
        
        fig3 = px.pie(
            pie_data,
            values='Sales Amount',
            names='Category',
            color='Category',
            color_discrete_map={str(k): v for k, v in CATEGORY_COLORS.items()},
            hole=0.4
        )
        
        fig3.update_traces(
            textposition='outside',
            textinfo='percent+label',
            hovertemplate='<b>Category %{label}</b><br>Sales: Rp %{value:,.0f}<br>Persentase: %{percent}<extra></extra>'
        )
        
        fig3.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=400,
            margin=dict(l=20, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Chart 4: Bar Chart - Qty Promo per Category
    with col_right:
        st.markdown("### 📦 Jumlah Promo per Category")
        
        promo_data = filtered_df.groupby('Category')['Qty Promo'].sum().reset_index()
        promo_data['Category'] = promo_data['Category'].astype(str)
        promo_data = promo_data.sort_values('Qty Promo', ascending=True)
        
        fig4 = px.bar(
            promo_data,
            x='Qty Promo',
            y='Category',
            orientation='h',
            color='Category',
            color_discrete_map={str(k): v for k, v in CATEGORY_COLORS.items()}
        )
        
        fig4.update_traces(
            hovertemplate='<b>Category %{y}</b><br>Qty Promo: %{x}<extra></extra>'
        )
        
        fig4.update_layout(
            showlegend=False,
            xaxis_title='Jumlah Promo',
            yaxis_title='Category',
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            margin=dict(l=60, r=20, t=20, b=60)
        )
        
        fig4.update_xaxes(gridcolor='#f0f0f0')
        
        st.plotly_chart(fig4, use_container_width=True)
    
    # Chart 5: Heatmap - Sales Amount per Category per Month (only for monthly view)
    if view_option == 'Monthly':
        st.markdown("### 🗓️ Heatmap: Sales Amount per Category per Bulan")
        
        heatmap_data = filtered_df.pivot_table(
            values='Sales Amount',
            index='Category',
            columns='Month',
            aggfunc='sum'
        )
        
        # Reorder columns by month
        month_order = [m for m in [
            'January 2025', 'February 2025', 'March 2025', 'April 2025',
            'May 2025', 'June 2025', 'July 2025', 'August 2025',
            'September 2025', 'October 2025', 'November 2025', 'December 2025'
        ] if m in heatmap_data.columns]
        
        heatmap_data = heatmap_data[month_order]
        
        # Shorten month names for display
        short_months = [m.replace(' 2025', '').replace('January', 'Jan').replace('February', 'Feb')
                       .replace('March', 'Mar').replace('April', 'Apr').replace('May', 'May')
                       .replace('June', 'Jun').replace('July', 'Jul').replace('August', 'Aug')
                       .replace('September', 'Sep').replace('October', 'Oct').replace('November', 'Nov')
                       .replace('December', 'Dec') for m in month_order]
        
        fig5 = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=short_months,
            y=[str(c) for c in heatmap_data.index],
            colorscale='Viridis',
            hovertemplate='Category: %{y}<br>Bulan: %{x}<br>Sales: Rp %{z:,.0f}<extra></extra>'
        ))
        
        fig5.update_layout(
            xaxis_title='Bulan',
            yaxis_title='Category',
            height=350,
            margin=dict(l=60, r=20, t=20, b=60)
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    
    # Data Table
    st.markdown("### 📋 Data Table")
    
    with st.expander("🔍 Lihat Detail Data", expanded=False):
        display_df = filtered_df.copy()
        
        # Format columns for display
        display_df['Sales Amount (Formatted)'] = display_df['Sales Amount'].apply(format_rupiah)
        display_df['NOC (Formatted)'] = display_df['NOC'].apply(format_number)
        
        if kontribusi_col in display_df.columns:
            display_df['Kontribusi (%)'] = (display_df[kontribusi_col] * 100).round(2).astype(str) + '%'
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
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
            <p>📊 Promo Performance Dashboard | Built with Streamlit & Plotly</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
