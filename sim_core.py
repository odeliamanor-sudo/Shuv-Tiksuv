import pandas as pd

def run_one_week_with_snapshots(seed=2025):
    sim = SimulationOneWeek(seed)
    res = sim.run()
    snap_df = pd.DataFrame(res["snapshots"])
    return res, snap_df
