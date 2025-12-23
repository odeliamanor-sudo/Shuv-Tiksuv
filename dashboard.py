import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from sim_core import run_replications, run_one_week_with_snapshots

st.set_page_config(page_title="Shuv-Tikshuv | Control Room", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#0b1020,#08162f); color: #e8eefc;}
.block-container{padding-top:1rem;}
.card{border:1px solid rgba(255,255,255,.12); border-radius:16px; padding:12px 14px;
background: rgba(255,255,255,.06); backdrop-filter: blur(10px);}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='card'><h1>🛰 Shuv-Tikshuv Control Room</h1><div>Playback + סטטיסטיקות מתוך הסימולציה שלכם</div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Run")
    seed = st.number_input("Seed", 1, 999999, 2025)
    reps = st.slider("Replications", 10, 80, 40)
    play = st.toggle("▶ Play", value=False)
    speed = st.slider("Speed", 0.02, 0.25, 0.08)

@st.cache_data
def cached_replications(reps, seed):
    return run_replications(reps, seed0=seed)

@st.cache_data
def cached_one(seed):
    res, snap = run_one_week_with_snapshots(seed=seed)
    return res, snap

agg = cached_replications(reps, seed)
res1, snap = cached_one(seed)

# Playback frame
if "i" not in st.session_state:
    st.session_state.i = 0
if play:
    st.session_state.i = (st.session_state.i + 1) % len(snap)
    time.sleep(speed)
    st.rerun()

row = snap.iloc[st.session_state.i]

# KPI cards
c1,c2,c3,c4 = st.columns(4)
for col, title, val in [
    (c1,"Total Queue", int(row.q_fault + row.q_train_join + row.q_senior)),
    (c2,"Active Agents", int(row.active_agents)),
    (c3,"Idle Total", int(row.idle_total)),
    (c4,"Abandoned (cum)", int(row.aband_cum)),
]:
    col.markdown(f"<div class='card'><h3>{title}</h3><h2>{val}</h2></div>", unsafe_allow_html=True)

# Timeline with current marker
st.markdown("<div class='card'>", unsafe_allow_html=True)
fig = go.Figure()
fig.add_trace(go.Scatter(x=snap["t"], y=snap["q_fault"], mode="lines", name="Fault Q"))
fig.add_trace(go.Scatter(x=snap["t"], y=snap["q_train_join"], mode="lines", name="Train/Join Q"))
fig.add_trace(go.Scatter(x=snap["t"], y=snap["q_senior"], mode="lines", name="Senior Q"))
fig.add_vline(x=float(row.t), line_width=2, line_dash="dash")
fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10),
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Heatmap abandon by hour (from replications result)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🔥 Abandonments per hour (avg per day)")
ab = agg["Abandon_hour_avg_per_day"]
fig2 = px.bar(x=list(range(24)), y=ab, labels={"x":"Hour","y":"Avg/day"})
fig2.update_layout(height=300, margin=dict(l=10,r=10,t=30,b=10),
                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Time in system distribution (replications)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("⏱ Time in system (distribution)")
order = ["fault","train","join","disconnect"]
df_box = []
for k in order:
    for v in agg["system_time_all"][k]:
        df_box.append({"type": k, "minutes": v})
df_box = pd.DataFrame(df_box)
fig3 = px.violin(df_box, x="type", y="minutes", box=True, points=False)
fig3.update_layout(height=320, margin=dict(l=10,r=10,t=30,b=10),
                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig3, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
