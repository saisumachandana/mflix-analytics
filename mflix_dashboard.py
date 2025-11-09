# 🎬 MFlix Movie Insights Dashboard — Clean & Compact
# Author: Sai Suma Chandana Bolla

import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------------
# 🌐 Streamlit Setup
# -------------------------------------
st.set_page_config(page_title="🎥 MFlix Cloud Insights", layout="wide")
st.title("🎬 **MFlix Global Movie Analytics Dashboard**")
st.caption("📊 *Author: Sai Suma Chandana Bolla* | Database: Azure CosmosDB (MongoDB API)")
st.markdown("---")

# -------------------------------------
# 🔗 MongoDB Connection
# -------------------------------------
uri = "mongodb+srv://suma:Bigdata%40123@mflix-cluster.mongocluster.cosmos.azure.com/sample_mflix?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false"
client = MongoClient(uri)
db = client["sample_mflix"]

# -------------------------------------
# 🧠 Load & Clean Data
# -------------------------------------
movies_df = pd.DataFrame(list(db.movies.find(
    {}, {"title": 1, "year": 1, "genres": 1, "countries": 1, "imdb.rating": 1, "imdb.votes": 1, "_id": 0}
)))
comments_df = pd.DataFrame(list(db.comments.find({}, {"email": 1, "_id": 0})))

# --- Flatten IMDb fields safely ---
movies_df = movies_df.dropna(subset=["imdb"])
movies_df["rating"] = movies_df["imdb"].apply(lambda x: x.get("rating") if isinstance(x, dict) else None)
movies_df["votes"] = movies_df["imdb"].apply(lambda x: x.get("votes") if isinstance(x, dict) else None)

# --- Convert to numeric ---
movies_df["rating"] = pd.to_numeric(movies_df["rating"], errors="coerce")
movies_df["votes"] = pd.to_numeric(movies_df["votes"], errors="coerce")
movies_df["year"] = pd.to_numeric(movies_df["year"], errors="coerce")

# --- Drop invalid entries ---
movies_df.dropna(subset=["rating", "votes", "year"], inplace=True)

if movies_df.empty:
    st.warning("⚠️ No valid movie data found in your MongoDB collection. Please check the database.")
    st.stop()

# -------------------------------------
# 🎯 KPI Cards
# -------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Total Movies", f"{len(movies_df):,}")
col2.metric("⭐ Avg IMDb Rating", f"{movies_df['rating'].mean():.2f}")
col3.metric("💬 Total Comments", f"{len(comments_df):,}")
st.markdown("---")

# ====================================================
# 🎭 SECTION 1 — Genre Insights
# ====================================================
st.subheader("🎭 **Genre Insights — Quality & Popularity**")
c1, c2 = st.columns(2)

# Average Rating by Genre
genre_rating = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"avg_rating": -1}}, {"$limit": 10}
])))
genre_rating.rename(columns={"_id": "Genre"}, inplace=True)
fig1 = px.bar(genre_rating, x="avg_rating", y="Genre", orientation="h",
              color="avg_rating", color_continuous_scale="Viridis",
              height=400, title="🎬 Top Genres by Average IMDb Rating")
c1.plotly_chart(fig1, use_container_width=True)

# Genre Popularity by Votes
genre_votes = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.votes": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_votes": {"$avg": "$imdb.votes"}}},
    {"$sort": {"avg_votes": -1}}, {"$limit": 10}
])))
genre_votes.rename(columns={"_id": "Genre"}, inplace=True)
fig2 = px.sunburst(genre_votes, path=["Genre"], values="avg_votes",
                   color="avg_votes", color_continuous_scale="Sunset",
                   height=400, title="🔥 Genre Popularity by IMDb Votes")
c2.plotly_chart(fig2, use_container_width=True)

st.info("🎯 Film-Noir and Documentary excel in quality, while Action and Adventure dominate audience engagement.")

# ====================================================
# 💬 SECTION 2 — Audience Engagement
# ====================================================
st.subheader("💬 **Top Commenters — Audience Engagement**")

users_df = pd.DataFrame(list(db.comments.aggregate([
    {"$group": {"_id": "$email", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit": 10}
])))
users_df.rename(columns={"_id": "User", "count": "Comments"}, inplace=True)
fig3 = px.scatter(users_df, x="Comments", y="User", size="Comments",
                  color="Comments", color_continuous_scale="Purp",
                  height=400, title="🗣️ Top 10 Active Commenters")
st.plotly_chart(fig3, use_container_width=True)
st.info("💡 Frequent commenters are key for building loyal audience communities and feedback loops.")

# ====================================================
# 📆 SECTION 3 — Temporal Trends
# ====================================================
st.subheader("📆 **Film Production Over Time**")
c3, c4 = st.columns(2)

# Movies per Decade
decade_df = (
    movies_df["year"].apply(lambda y: int(y // 10 * 10))
    .value_counts().sort_index().reset_index()
)
decade_df.columns = ["Decade", "Movies"]
fig4 = px.area(decade_df, x="Decade", y="Movies",
               color_discrete_sequence=["#F39C12"],
               height=400, title="📈 Movies Released per Decade")
c3.plotly_chart(fig4, use_container_width=True)

# Rating Trend by Year
rating_trend = pd.DataFrame(list(db.movies.aggregate([
    {"$match": {"year": {"$type": "number"}, "imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$year", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"_id": 1}}
])))
rating_trend.rename(columns={"_id": "Year"}, inplace=True)
fig5 = px.line(rating_trend, x="Year", y="avg_rating", markers=True,
               color_discrete_sequence=["#1ABC9C"], height=400,
               title="⭐ Average IMDb Rating by Year")
c4.plotly_chart(fig5, use_container_width=True)

# ====================================================
# 🌍 SECTION 4 — Global Film Distribution
# ====================================================
st.subheader("🌍 **Global Film Production Distribution**")

country_df = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$countries"},
    {"$group": {"_id": "$countries", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit": 10}
])))
country_df.rename(columns={"_id": "Country", "count": "Movies"}, inplace=True)
fig6 = px.choropleth(country_df, locations="Country", locationmode="country names",
                     color="Movies", color_continuous_scale="Blues",
                     height=450, title="🌏 Top 10 Countries by Number of Movies")
st.plotly_chart(fig6, use_container_width=True)

# ====================================================
# 🧩 SECTION 5 — Correlation & Directors
# ====================================================
st.subheader("🧩 **Ratings, Votes & Direction Quality**")
c5, c6 = st.columns(2)

# Hexbin Plot — Votes vs Ratings
fig7, ax = plt.subplots(figsize=(5, 4))
hb = ax.hexbin(movies_df["votes"], movies_df["rating"], gridsize=35, cmap="plasma", mincnt=1)
ax.set_xscale("log")
ax.set_xlabel("IMDb Votes (log scale)")
ax.set_ylabel("IMDb Rating")
ax.set_title("Votes vs Ratings — Popularity vs Quality")
cb = fig7.colorbar(hb, ax=ax)
cb.set_label("Number of Movies")
c5.pyplot(fig7, use_container_width=True)

# Correlation Heatmap
corr = movies_df[["rating", "votes", "year"]].corr()
fig8, ax = plt.subplots(figsize=(4.5, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
ax.set_title("Correlation Heatmap (Ratings, Votes, Year)")
c6.pyplot(fig8, use_container_width=True)

# Directors
dir_df = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$directors"},
    {"$match": {"imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$directors", "avg_rating": {"$avg": "$imdb.rating"}, "count": {"$sum": 1}}},
    {"$match": {"count": {"$gte": 3}}},
    {"$sort": {"avg_rating": -1}}, {"$limit": 10}
])))
dir_df.rename(columns={"_id": "Director"}, inplace=True)
fig9 = px.bar(dir_df, x="avg_rating", y="Director", orientation="h",
              color="avg_rating", color_continuous_scale="Inferno",
              height=400, title="🏆 Top 10 Directors by Average IMDb Rating")
st.plotly_chart(fig9, use_container_width=True)

st.success("✅ Dashboard loaded successfully with all visuals and insights from Azure MongoDB.")
