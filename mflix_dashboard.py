# 🎬 MFlix Movie Analytics Dashboard — Distinct Visuals for Each EDA
# Author: Sai Suma Chandana Bolla
# Source: Azure Cosmos DB (MongoDB API)
# Purpose: Full-page dashboard showing varied movie analytics visuals

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🎥 MFlix Analytics Dashboard", layout="wide")
sns.set_style("whitegrid")

# -------------------------------
# 🔗 Connect to MongoDB on Azure
# -------------------------------
uri = "mongodb+srv://suma:Bigdata%40123@mflix-cluster.mongocluster.cosmos.azure.com/sample_mflix?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false"
client = MongoClient(uri)
db = client["sample_mflix"]

st.title("🎬 MFlix Cloud Movie Analytics Dashboard")
st.caption("**Author:** Sai Suma Chandana Bolla | **Database:** Azure MongoDB (CosmosDB API)")
st.markdown("---")

# ---------------------------------------------------------
# 1️⃣ Top 10 Movie Genres by Average IMDb Rating — Horizontal Bar (Clean)
# ---------------------------------------------------------
st.subheader("🎭 Top 10 Movie Genres by Average IMDb Rating")

genres_df = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"avg_rating": -1}}, {"$limit": 10}
])))
genres_df.rename(columns={"_id": "Genre"}, inplace=True)
fig = px.bar(genres_df, x="avg_rating", y="Genre", orientation="h",
             color="avg_rating", color_continuous_scale="Viridis",
             title="Top Genres by Average Rating")
st.plotly_chart(fig, use_container_width=True)
st.info("🎯 *Drama* and *Documentary* consistently achieve higher ratings than commercial genres.")

# ---------------------------------------------------------
# 2️⃣ Top 10 Active Users by Comment Count — Bubble Chart
# ---------------------------------------------------------
st.subheader("💬 Top 10 Active Users by Comment Count")

users_df = pd.DataFrame(list(db.comments.aggregate([
    {"$group": {"_id": "$email", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit": 10}
])))
users_df.rename(columns={"_id": "User", "count": "Comments"}, inplace=True)
fig = px.scatter(users_df, x="Comments", y="User", size="Comments", color="Comments",
                 color_continuous_scale="Magenta", title="Most Active Commenters")
st.plotly_chart(fig, use_container_width=True)
st.info("🗣️ High-comment users are the most engaged community members — valuable for targeted marketing.")

# ---------------------------------------------------------
# 3️⃣ Movies Released per Decade — Line Chart with Area Fill
# ---------------------------------------------------------
st.subheader("📆 Movies Released per Decade")

year_df = pd.DataFrame(list(db.movies.find({}, {"year": 1, "_id": 0})))
year_df["year"] = pd.to_numeric(year_df["year"], errors="coerce")
year_df.dropna(inplace=True)
year_df["decade"] = (year_df["year"] // 10) * 10
decade_df = year_df["decade"].value_counts().sort_index().reset_index()
decade_df.columns = ["Decade", "Movies"]

fig = px.area(decade_df, x="Decade", y="Movies", color_discrete_sequence=["#66c2a5"],
              title="Movies Released per Decade (Trend of Film Production)")
st.plotly_chart(fig, use_container_width=True)
st.info("🎞️ A sharp increase after the 1980s marks globalization and streaming revolution.")

# ---------------------------------------------------------
# 4️⃣ Average IMDb Rating Trend by Year — Smoothed Line + Scatter
# ---------------------------------------------------------
st.subheader("📈 Average IMDb Rating Trend by Year")

rating_trend = pd.DataFrame(list(db.movies.aggregate([
    {"$match": {"year": {"$type": "number"}, "imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$year", "avg_rating": {"$avg": "$imdb.rating"}}},
    {"$sort": {"_id": 1}}
])))
rating_trend.rename(columns={"_id": "Year"}, inplace=True)
fig = px.line(rating_trend, x="Year", y="avg_rating", markers=True, color_discrete_sequence=["#2ca02c"],
              title="Average IMDb Rating by Year")
st.plotly_chart(fig, use_container_width=True)
st.info("📊 Ratings remain stable across years — indicating consistent audience expectations.")

# ---------------------------------------------------------
# 5️⃣ Top 10 Countries by Movie Count — Choropleth Map
# ---------------------------------------------------------
st.subheader("🌍 Top 10 Countries by Movie Count")

country_df = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$countries"},
    {"$group": {"_id": "$countries", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit": 10}
])))
country_df.rename(columns={"_id": "Country", "count": "Movies"}, inplace=True)
fig = px.choropleth(country_df, locations="Country", locationmode="country names",
                    color="Movies", color_continuous_scale="Blues",
                    title="Top 10 Countries by Number of Movies")
st.plotly_chart(fig, use_container_width=True)
st.info("🇺🇸 The U.S. leads in production volume, followed by UK, France, and India.")

# ---------------------------------------------------------
# 6️⃣ IMDb Votes vs Rating Correlation — Hexbin Density Plot
# ---------------------------------------------------------
st.subheader("⭐ IMDb Votes vs Rating Correlation")

vote_df = pd.DataFrame(list(db.movies.find(
    {"imdb.rating": {"$type": "number"}, "imdb.votes": {"$type": "number"}},
    {"imdb.rating": 1, "imdb.votes": 1, "_id": 0}
)))
vote_df["rating"] = vote_df["imdb"].apply(lambda x: x["rating"])
vote_df["votes"] = vote_df["imdb"].apply(lambda x: x["votes"])
vote_df.drop(columns=["imdb"], inplace=True)

fig, ax = plt.subplots(figsize=(7, 5))
hb = ax.hexbin(vote_df["votes"], vote_df["rating"], gridsize=40, cmap="plasma", mincnt=1)
ax.set_xscale("log")
ax.set_xlabel("IMDb Votes (log scale)")
ax.set_ylabel("IMDb Rating")
ax.set_title("Popularity vs Quality (Votes vs Ratings)")
cb = fig.colorbar(hb, ax=ax)
cb.set_label("Density of Movies")
st.pyplot(fig)
st.info("📈 Dense clusters near mid-range ratings (6–7) show majority audience sentiment concentration.")

# ---------------------------------------------------------
# 7️⃣ Genre Popularity vs IMDb Votes — Horizontal Lollipop Chart
# ---------------------------------------------------------
st.subheader("🎬 Genre Popularity vs IMDb Votes")

genre_votes = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$genres"},
    {"$match": {"imdb.votes": {"$type": "number"}}},
    {"$group": {"_id": "$genres", "avg_votes": {"$avg": "$imdb.votes"}}},
    {"$sort": {"avg_votes": -1}}, {"$limit": 10}
])))
genre_votes.rename(columns={"_id": "Genre"}, inplace=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hlines(y=genre_votes["Genre"], xmin=0, xmax=genre_votes["avg_votes"], color="skyblue", lw=3)
ax.plot(genre_votes["avg_votes"], genre_votes["Genre"], "o", color="steelblue")
ax.set_xscale("log")
ax.set_xlabel("Average IMDb Votes (log scale)")
st.pyplot(fig)
st.info("🎥 Action and Adventure genres show strong audience engagement (high votes).")

# ---------------------------------------------------------
# 8️⃣ Correlation Heatmap (Ratings, Votes, Year)
# ---------------------------------------------------------
st.subheader("📊 Correlation Heatmap — Ratings, Votes, and Year")

corr_df = pd.DataFrame(list(db.movies.find({}, {"imdb.rating": 1, "imdb.votes": 1, "year": 1, "_id": 0})))
corr_df["imdb_rating"] = pd.to_numeric(corr_df["imdb"].apply(lambda x: x.get("rating") if x else None), errors="coerce")
corr_df["imdb_votes"] = pd.to_numeric(corr_df["imdb"].apply(lambda x: x.get("votes") if x else None), errors="coerce")
corr_df["year"] = pd.to_numeric(corr_df["year"], errors="coerce")
corr_df.drop(columns=["imdb"], inplace=True)
corr = corr_df[["imdb_rating", "imdb_votes", "year"]].dropna().corr()

fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
st.pyplot(fig)
st.info("🧩 Weak correlation between ratings and votes — indicating that popularity ≠ quality.")

# ---------------------------------------------------------
# 9️⃣ Top 10 Directors by Average IMDb Rating — Horizontal Bar with Color
# ---------------------------------------------------------
st.subheader("🎥 Top 10 Directors by Average IMDb Rating")

dir_df = pd.DataFrame(list(db.movies.aggregate([
    {"$unwind": "$directors"},
    {"$match": {"imdb.rating": {"$type": "number"}}},
    {"$group": {"_id": "$directors", "avg_rating": {"$avg": "$imdb.rating"}, "count": {"$sum": 1}}},
    {"$match": {"count": {"$gte": 3}}},
    {"$sort": {"avg_rating": -1}}, {"$limit": 10}
])))
dir_df.rename(columns={"_id": "Director"}, inplace=True)
fig = px.bar(dir_df, x="avg_rating", y="Director", orientation="h",
             color="avg_rating", color_continuous_scale="Inferno",
             title="Top Directors by Consistent High Ratings")
st.plotly_chart(fig, use_container_width=True)
st.info("🏆 Directors with consistently high-rated films show creative longevity and audience trust.")

st.success("✅ All visuals successfully loaded from Azure MongoDB!")
