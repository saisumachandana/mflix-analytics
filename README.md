# 🎬 MFlix Cloud Movie Analytics Dashboard

### Author: Sai Suma Chandana Bolla  
**Database:** Azure Cosmos DB (MongoDB API)  
**Visualization Tool:** Streamlit  
**Project Type:** Cloud Data Analytics and Visualization  

---

## 📊 Project Overview
This project connects an **Azure-hosted MongoDB (Cosmos DB)** database containing movie-related data (`sample_mflix` dataset).  
It analyzes and visualizes movie metrics such as ratings, user activity, and production trends through an interactive Streamlit dashboard.

---

## ⚙️ Key Visuals
1. **Top 10 Movie Genres by Average IMDb Rating** – Horizontal bar (category ranking)  
2. **Top 10 Active Users by Comment Count** – Bubble chart (engagement visualization)  
3. **Movies Released per Decade** – Area chart (temporal trend)  
4. **Average IMDb Rating by Year** – Line chart (quality consistency)  
5. **Top 10 Countries by Movie Count** – Choropleth map (geographic distribution)  
6. **IMDb Votes vs Rating** – Hexbin plot (popularity vs quality)  
7. **Genre Popularity vs IMDb Votes** – Log-scaled bar (engagement level)  
8. **Correlation Heatmap** – Numerical insights (ratings, votes, years)  
9. **Top 10 Directors by Average IMDb Rating** – Horizontal bar (creative excellence)

---

## 🧠 Analytical Value
This dashboard helps streaming platforms, producers, and marketing teams:
- Understand **which genres and directors consistently perform best**.  
- Identify **viewer engagement patterns** (votes/comments).  
- Track **historical film production trends** over time.  
- Use data-driven insights for **content strategy and audience targeting**.

---

## ☁️ Deployment Notes
1. Data is hosted on **Azure Cosmos DB (MongoDB API)**.  
2. Dashboard built using **Streamlit**, connected through **PyMongo**.  
3. App deployed via **Streamlit Cloud** with secure `MONGO_URI` in Secrets.

---

## 🧩 Run Locally
To run the app locally:
```bash
pip install -r requirements.txt
streamlit run mflix_dashboard_final_visuals.py
