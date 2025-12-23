import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Shuv-Tikshuv | Simulation Dashboard",
    layout="wide"
)

st.title("📊 Shuv-Tikshuv – Simulation Control Room")
st.markdown(
    "אנימציה אינטראקטיבית המדגימה את התפתחות מערכת השירות לאורך זמן "
    "(Playback, Heatmap, Sankey, מדדים דינמיים)"
)

# ===============================
# DATA GENERATION (SELF CONTAINED)
# ===============================
@st.cache_data
def generate_data():
    np.random.seed(42)
    T = 300
    t = np.arange(T)

    peak1 = np.exp(-0.5 * ((t - 80) / 20) ** 2)
    peak2 = np.exp(-0.5 * ((t - 200) / 30) ** 2)
    load = 0.5 + 1.8 * peak1 + 1.4 * peak2

    q_fault = np.maximum(0, (20 * load + np.random.randn(T) * 2)).astype(int)
    q_train = np.maximum(0, (14 * load + np.random.randn(T) * 1.5)).astype(int)
    q_senior = np.maximum(0, (8 * load + np.random.randn(T))).astype(int)

    abandon = np.cumsum((np.random.rand(T) < 0.01 * load).astype(int))

    df = pd.DataFrame({
        "t": t,
        "fault": q_fault,
        "train": q_train,
        "senior": q_senior,
        "total": q_fault + q_train + q_senior,
        "abandon": abandon
    })
    return df

df = generate_data()

# ===============================
# CONTROLS
# ===============================
play = st.toggle("▶ Play animation", value=False)
speed = st.slider("Speed", 0.02, 0.2, 0.08)

if "frame" not in st.session_state:
    st.session_state.frame = 0

if play:
    st.session_state.frame = (st.session_state.frame + 1) % len(df)
    time.sleep(speed)
    st.rerun()

row = df.iloc[st.session_state.frame]

# ===============================
# KPI METRICS
# ===============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Queue", int(row.total))
c2.metric("Fault Queue", int(row.fault))
c3.metric("Train / Join Queue", int(row.train))
c4.metric("Abandonments (cum)", int(row.abandon))

# ===============================
# LINE + STACKED GRAPH
# ===============================
left, right = st.columns(2)

with left:
    st.subheader("Total Queue Over Time")
    fig, ax = plt.subplots()
    ax.plot(df["t"], df["total"])
    ax.axvline(row.t, linestyle="--")
    ax.set_xlabel("Time")
    ax.set_ylabel("Requests")
    st.pyplot(fig)

with right:
    st.subheader("Queue Composition")
    fig, ax = plt.subplots()
    ax.stackplot(
        df["t"],
        df["fault"],
        df["train"],
        df["senior"],
        labels=["Fault", "Train", "Senior"]
    )
    ax.axvline(row.t, linestyle="--")
    ax.legend()
    st.pyplot(fig)

# ===============================
# HEATMAP
# ===============================
st.subheader("Abandonments Heatmap (conceptual)")
heat = np.random.rand(5, 24)
fig, ax = plt.subplots()
im = ax.imshow(heat, aspect="auto")
ax.set_xlabel("Hour")
ax.set_ylabel("Day")
fig.colorbar(im, ax=ax)
st.pyplot(fig)

# ===============================
# SANKEY (WOW EFFECT)
# ===============================
st.subheader("System Flow – Sankey Diagram")

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        label=["Arrivals", "Fault", "Train", "Senior", "Served", "Abandoned"]
    ),
    link=dict(
        source=[0,0,0,1,2,3],
        target=[1,2,3,4,4,5],
        value=[50,30,20,40,30,10]
    )
)])
st.plotly_chart(fig, use_container_width=True)
