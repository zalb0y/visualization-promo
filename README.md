# 📊 Promo Performance Dashboard

Dashboard interaktif untuk menganalisis performa promosi dan kontribusinya terhadap Net Sales.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🎯 Fitur

### Visualisasi Utama
- **Combo Chart**: Sales Amount (Bar) + Kontribusi Promo (Line) dengan dual Y-axis
- **Line Chart**: Perbandingan NOC vs Visit Customer
- **Donut Chart**: Distribusi Sales Amount per Category
- **Horizontal Bar Chart**: Jumlah Promo per Category
- **Heatmap**: Sales Amount per Category per Bulan (tampilan Monthly)

### Filter Interaktif
- Pilihan Dataset: Summary All / Summary Non Cigarette
- Pilihan View: Yearly / Monthly
- Multi-select Category
- Multi-select Bulan (untuk view Monthly)

### KPI Cards
- Total Sales Amount
- Total NOC (Number of Customer)
- Visit Customer
- Average Kontribusi Promo

### Fitur Tambahan
- Data Table dengan ekspansi
- Download data ke CSV
- Responsive design

## 📁 Struktur File

```
promo-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── all_summary.xlsx       # Data file (perlu ditambahkan)
├── README.md             # Documentation
├── .gitignore            # Git ignore file
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

## 🚀 Cara Menjalankan

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/username/promo-dashboard.git
   cd promo-dashboard
   ```

2. **Buat virtual environment (opsional tapi disarankan)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Tambahkan file data**
   
   Pastikan file `all_summary.xlsx` berada di folder yang sama dengan `app.py`.
   
   File Excel harus memiliki sheet berikut:
   - Summary All (Year)
   - Summary All (Month)
   - Summary Non Cigarette (Year)
   - Summary Non Cigarette (Month)

5. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

6. **Buka browser**
   
   Aplikasi akan otomatis terbuka di `http://localhost:8501`

## 📊 Struktur Data

### Sheet: Summary All/Non Cigarette (Year)
| Kolom | Deskripsi |
|-------|-----------|
| Category | Kode kategori (11, 14, 17, 19, 21, 26, 27) |
| Qty Promo | Jumlah promo |
| NOC | Number of Customer |
| Visit Customer | Jumlah kunjungan customer |
| Sales Amount | Nilai penjualan dari promo |
| Net Sales (by Group Category) | Total net sales per kategori |
| Kontribusi Promo pada Net Sales | Persentase kontribusi |

### Sheet: Summary All/Non Cigarette (Month)
Sama seperti di atas, dengan tambahan kolom:
| Kolom | Deskripsi |
|-------|-----------|
| Month | Bulan (January 2025 - December 2025) |

## 🎨 Kustomisasi

### Mengubah Warna
Edit dictionary `CATEGORY_COLORS` di `app.py`:
```python
CATEGORY_COLORS = {
    11: '#667eea',
    14: '#764ba2', 
    17: '#f093fb',
    19: '#10b981',
    21: '#f59e0b',
    26: '#ef4444',
    27: '#3b82f6'
}
```

### Mengubah Theme
Edit file `.streamlit/config.toml` untuk mengubah tema aplikasi.

## 🌐 Deployment

### Deploy ke Streamlit Cloud

1. Push kode ke GitHub repository
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Pilih branch dan file `app.py`
5. Klik Deploy

### Deploy ke Server Sendiri

```bash
# Install dependencies
pip install -r requirements.txt

# Run dengan port tertentu
streamlit run app.py --server.port 8080

# Run di background
nohup streamlit run app.py --server.port 8080 &
```

## 📝 License

MIT License - Silakan gunakan dan modifikasi sesuai kebutuhan.

## 🤝 Contributing

Kontribusi selalu diterima! Silakan buat Pull Request atau buka Issue untuk saran dan perbaikan.

---

Made with ❤️ using Streamlit
