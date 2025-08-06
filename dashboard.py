#!/usr/bin/env python
"""
Simple Streamlit dashboard to visualize ingested articles.

Run with:

    streamlit run dashboard.py

It will display a table of stored articles and a bar chart of publication dates.
"""

import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, url, title, publication_date, fetched_at FROM articles",
        conn,
    )
    conn.close()
    return df


def main():
    st.title("Structured Notes Research Dashboard")
    df = load_data()
    st.subheader("Ingested Articles")
    st.dataframe(df)

    st.subheader("Articles by Publication Date")
    if not df.empty:
        # Convert publication_date to datetime for plotting
        df["publication_date"] = pd.to_datetime(df["publication_date"])
        counts = df.groupby(df["publication_date"].dt.date).size()
        st.bar_chart(counts)
    else:
        st.info("No articles have been ingested yet.")


if __name__ == "__main__":
    main()