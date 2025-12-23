import pandas as pd

def run_one_week_with_snapshots(seed=2025):
    sim = SimulationOneWeek(seed)
    res = sim.run()
    snap_df = pd.DataFrame(res.get("snapshots", []))
    return res, snap_df

def run_replications(num_reps=50, seed0=2025):
    Ab_sum = np.zeros(24)
    sys_all = {"fault": [], "train": [], "join": [], "disconnect": []}
    idle_hour_sum = np.zeros(24)
    idle_group_sum = np.zeros(3)

    for i in range(num_reps):
        sim = SimulationOneWeek(seed0 + i)
        res = sim.run()
        Ab_sum += res["Abandon_hour_avg_per_day"]
        for k in sys_all:
            sys_all[k].extend(res["system_time"][k])
        idle_hour_sum += res["idle_pct_by_hour"]
        idle_group_sum += res["idle_pct_by_group"]

    return {
        "num_reps": num_reps,
        "Abandon_hour_avg_per_day": Ab_sum / num_reps,
        "system_time_all": sys_all,
        "idle_hour_avg": idle_hour_sum / num_reps,
        "idle_group_avg": idle_group_sum / num_reps
    }
