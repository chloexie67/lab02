# This creates the page for displaying data visualizations.

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visuals",
    page_icon="📈",
)

# PAGE TITLE
st.title("Data Visualizations 📈")


# PART 1: GRAPHS FROM data.json
# --- YOUR CODE GOES HERE ---
st.header("Part 1: Premier League 2024-25")

with open("data.json", "r") as file:
    league = json.load(file)

teams = pd.DataFrame(league["data_points"])

st.subheader("Attack vs. defense")
scatter = px.scatter(
    teams,
    x="goals_for",
    y="goals_against",
    text="label",
    size="value",
    color="value",
    title=league["chart_title"] + ": Goals Scored vs. Goals Conceded",
    labels={"goals_for": "Goals Scored", "goals_against": "Goals Conceded", "value": "Points"},
)
scatter.update_traces(textposition="top center", textfont_size=9)
scatter.update_yaxes(autorange="reversed")
st.plotly_chart(scatter, width="stretch")
st.caption("Top right is the best place to be: lots of goals scored, few conceded. Bigger dots = more points.")

st.subheader("Compare teams by one stat")

STAT_LABELS = {
    "value": "Points",
    "wins": "Wins",
    "goals_for": "Goals Scored",
    "goals_against": "Goals Conceded",
}

st.radio(
    "Stat to show",
    options=list(STAT_LABELS.keys()),
    format_func=lambda key: STAT_LABELS[key],
    horizontal=True,
    key="json_stat",
)
st.slider("Show the top N teams in the final table", 3, 20, 10, key="json_top_n")

stat = st.session_state["json_stat"]
top_n = st.session_state["json_top_n"]

top_teams = teams.sort_values("position").head(top_n)
st.bar_chart(top_teams.set_index("label")[stat], x_label="Team", y_label=STAT_LABELS[stat])

mean_now = top_teams[stat].mean()
median_now = top_teams[stat].median()
prev_mean = st.session_state.get("json_prev_mean")
prev_median = st.session_state.get("json_prev_median")
prev_stat = st.session_state.get("json_prev_stat")

show_delta = prev_stat == stat and prev_mean is not None
col1, col2 = st.columns(2)
col1.metric(f"Mean {STAT_LABELS[stat]}", f"{mean_now:.1f}",
            delta=f"{mean_now - prev_mean:.1f}" if show_delta else None)
col2.metric(f"Median {STAT_LABELS[stat]}", f"{median_now:.1f}",
            delta=f"{median_now - prev_median:.1f}" if show_delta else None)

st.session_state["json_prev_mean"] = mean_now
st.session_state["json_prev_median"] = median_now
st.session_state["json_prev_stat"] = stat


# PART 2: GRAPHS FROM data.csv
# --- YOUR CODE GOES HERE ---
st.divider()
st.header("Part 2: Sports Watching Survey")

if os.path.exists("data.csv") and os.path.getsize("data.csv") > 0:
    survey = pd.read_csv("data.csv")
else:
    survey = pd.DataFrame(columns=["Category", "Value"])

if survey.empty:
    st.info("No survey responses yet. Fill out the Survey page to see these charts.")
else:
    st.write(f"{len(survey)} responses so far.")

    st.subheader("Favorite sports")
    counts = survey["Category"].value_counts().reset_index()
    counts.columns = ["Sport", "Responses"]
    pie = px.pie(
        counts,
        names="Sport",
        values="Responses",
        title="Favorite Sport to Watch (share of responses)",
    )
    pie.update_traces(textinfo="label+percent")
    st.plotly_chart(pie, width="stretch")

    st.subheader("Hours watched per week")
    sport_options = ["All sports"] + sorted(survey["Category"].unique().tolist())
    st.selectbox("Filter by favorite sport", sport_options, key="csv_sport")
    st.slider("Number of bars", 2, 15, 6, key="csv_bins")

    chosen = st.session_state["csv_sport"]
    bins = st.session_state["csv_bins"]
    if chosen == "All sports":
        filtered = survey
    else:
        filtered = survey[survey["Category"] == chosen]

    hist = px.histogram(
        filtered,
        x="Value",
        nbins=bins,
        title=f"Hours of Sports Watched per Week ({chosen})",
        labels={"Value": "Hours per Week"},
    )
    hist.update_layout(yaxis_title="Number of People")
    st.plotly_chart(hist, width="stretch")

    mean_now = filtered["Value"].mean()
    median_now = filtered["Value"].median()
    prev_mean = st.session_state.get("csv_prev_mean")
    prev_median = st.session_state.get("csv_prev_median")

    col3, col4 = st.columns(2)
    col3.metric("Mean hours/week", f"{mean_now:.1f}",
                delta=f"{mean_now - prev_mean:.1f}" if prev_mean is not None else None)
    col4.metric("Median hours/week", f"{median_now:.1f}",
                delta=f"{median_now - prev_median:.1f}" if prev_median is not None else None)

    st.session_state["csv_prev_mean"] = mean_now
    st.session_state["csv_prev_median"] = median_now
