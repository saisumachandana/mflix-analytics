# 🎬 MFlix Movie Insights Dashboard — Advanced Layout & Visual Variety
# Author: Sai Suma Chandana Bolla
# Database: Azure Cosmos DB (MongoDB API)
# Purpose: Interactive storytelling dashboard for film analytics

import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------------
# 🌐 Streamlit Page Setup
# -------------------------------------
st.set_page_config(page_title="🎥 MFlix Cloud Insights", layout="wide")
st.title("🎬 **MFlix Global Movie Analytics Dashboard**")
st.caption("📊 *Author: Sai Suma Chandana Bolla* | Database: Azure CosmosDB (MongoDB API)")
st.markdown("---")

# -------------------------------------
# 🔗 Connect to MongoDB
# -------------------------------------
uri = "mongodb+srv://suma:Bigdata%40123@mflix-cluster.mongocluster.cosmos.azure.com/sample_mflix?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false"
client = MongoClient(uri)
db = client["sample_mflix"]

# -------------------------------------
# 🧠 Data Extraction
# -------------------------------------
movies_df = pd.DataFrame(list(db.movies.find(
    {}, {"title": 1, "year": 1, "genres": 1, "countries": 1, "imdb.rating": 1, "imdb.votes": 1, "_id": 0}
)))
comments_df = pd.DataFrame(list(db.comments.find({}, {"email": 1, "_id": 0})))

# Data Cleaning
movies_df = movies_df.dropna(subset=["imdb"])
movies_df["rating"] = movies_df["imdb"].apply(lambda x: x.get("rating"))
movies_df["votes"] = movies_df["imdb"].apply(lambda x: x.get("votes"))
movies_df.drop(columns=["imdb"], inplace=True)
movies_df = movies_df.dropna(subset=["rating", "votes", "year"])
movies_df = movies_df[movies_df["year"].apply(lambda x: isinstance(x, int))]

# -------------------------------------
# 🎯 KPI Metrics
# -------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Total Movies", f"{len(movies_df):,}")
col2.metric("⭐ Avg IMDb Rating", f"{movies_df['rating'].mean():.2f}")
col3.metric("🗣️ Total Comments", f"{len(comments_df):,}")

st.markdown("---")

# ====================================================
# SECTION 1 — GENRE INSIGHTS
# ====================================================
st.subheader("🎭 **Genre Insights — Quality & Popularity**")

genre_rating = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"avg_rating": -1}}, {"$limit": 10}
])))
genre_rating.rename(columns={"_id": "Genre"}, inplace=True)
fig1 = px.bar(genre_rating, x="avg_rating", y="Genre", orientation="h",
              color="avg_rating", color_continuous_scale="Tealgrn",
              title="🎬 Top 10 Genres by Average IMDb Rating")
st.plotly_chart(fig1, use_container_width=True)

# Popularity by Votes
genre_votes = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.votes": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_votes": {"$avg": "$imdb.votes"}}},
    {"$sort": {"avg_votes": -1}}, {"$limit": 10}
])))
genre_votes.rename(columns={"_id": "Genre"}, inplace=True)
fig2 = px.treemap(genre_votes, path=["Genre"], values="avg_votes",
                  color="avg_votes", color_continuous_scale="Sunset",
                  title="🔥 Genre Popularity by IMDb Votes (Treemap)")
st.plotly_chart(fig2, use_container_width=True)

st.info("🎯 Film-Noir and Documentary excel in quality, while Action and Adventure dominate engagement.")

# ====================================================
# SECTION 2 — USER ENGAGEMENT
# ====================================================
st.subheader("💬 **Top Commenters — Audience Engagement**")

users_df = pd.DataFrame(list(db.comments.aggregate([
    {"$group": {"_id": "$email", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit": 10}
])))
users_df.rename(columns={"_id": "User", "count": "Comments"}, inplace=True)
fig3 = px.scatter(users_df, x="Comments", y="User", size="Comments", color="Comments",
                  color_continuous_scale="Purp", title="🗣️ Top 10 Active Commenters")
st.plotly_chart(fig3, use_container_width=True)
st.info("💡 Frequent commenters represent the most engaged community segment — vital for marketing decisions.")

# ====================================================
# SECTION 3 — TEMPORAL TRENDS
# ====================================================
st.subheader("📆 **Film Production Trends Over Time**")

# Movies per Decade
year_df = pd.to_numeric(movies_df["year"], errors="coerce").dropna()
decades = (year_df // 10 * 10).value_counts().sort_index()
decade_df = pd.DataFrame({"Decade": decades.index, "Movies": decades.values})
fig4 = px.area(decade_df, x="Decade", y="Movies", color_discrete_sequence=["#F39C12"],
               title="📈 Movies Released per Decade")
st.plotly_chart(fig4, use_container_width=True)

# Rating trend per year
rating_trend = pd.DataFrame(list(db.movies.aggregate([
    {"$match": {"year": {"$type": "number"}, "imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$year", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"_id": 1}}
])))
rating_trend.rename(columns={"_id": "Year"}, inplace=True)
fig5 = px.line(rating_trend, x="Year", y="avg_rating", markers=True,
               color_discrete_sequence=["#1ABC9C"], title="⭐ Average IMDb Rating by Year")
st.plotly_chart(fig5, use_container_width=True)
st.info("📊 Ratings remain relatively stable, suggesting consistent viewer expectations over time.")

# ====================================================
# SECTION 4 — COUNTRY INSIGHTS
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
                     title="🌏 Top 10 Countries by Number of Movies")
st.plotly_chart(fig6, use_container_width=True)
st.info("🇺🇸 USA leads production, followed by UK, France, and India — indicating dominant global influence.")

# ====================================================
# SECTION 5 — CORRELATION & DIRECTORS
# ====================================================
st.subheader("🧩 **Ratings, Votes & Direction Quality**")

# Hexbin: Votes vs Ratings
fig7, ax = plt.subplots(figsize=(7, 5))
hb = ax.hexbin(movies_df["votes"], movies_df["rating"], gridsize=40, cmap="viridis", mincnt=1)
ax.set_xscale("log")
ax.set_xlabel("IMDb Votes (log scale)")
ax.set_ylabel("IMDb Rating")
ax.set_title("Votes vs Ratings — Popularity vs Quality")
cb = fig7.colorbar(hb, ax=ax)
cb.set_label("Number of Movies")
st.pyplot(fig7, use_container_width=True)

# Correlation Heatmap
corr = movies_df[["rating", "votes", "year"]].corr()
fig8, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
st.pyplot(fig8, use_container_width=True)

# Top Directors
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
              title="🏆 Top 10 Directors by Average IMDb Rating")
st.plotly_chart(fig9, use_container_width=True)

st.success("✅ Dashboard successfully loaded with all visuals and insights from Azure MongoDB.")
