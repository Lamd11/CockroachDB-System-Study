"""
generate_graphs.py
Creates dual-axis plots for TPS and Latency from test CSVs.
Updates: specific Y-axis scaling (0 to max + padding).
"""
import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_data(filename, title):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return

    # Create the figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # --- LEFT Y-AXIS (TPS) ---
    color = 'tab:blue'
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('TPS (Transactions/Sec)', color=color, fontweight='bold')
    ax1.plot(df['time_elapsed'], df['tps'], color=color, linewidth=2, label='TPS')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # FIX 1: Set TPS Axis from 0 to Max + 10 (or 20% buffer)
    tps_max = df['tps'].max()
    # If max is 0 (e.g. errors), default to 10 so graph doesn't break
    top_limit = tps_max + 10 if tps_max > 0 else 10
    ax1.set_ylim(bottom=0, top=top_limit)

    # --- RIGHT Y-AXIS (Latency) ---
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Latency (ms)', color=color, fontweight='bold')
    ax2.plot(df['time_elapsed'], df['p99_latency'], color=color, linestyle='--', label='p99 Latency')
    ax2.plot(df['time_elapsed'], df['p95_latency'], color='orange', linestyle=':', label='p95 Latency')
    ax2.tick_params(axis='y', labelcolor=color)

    # FIX 2: Set Latency Axis from 0 to Max + 20% buffer (keeps spikes visible but grounded)
    lat_max = max(df['p99_latency'].max(), df['p95_latency'].max())
    # Default to 100ms if empty/zero to keep shape
    lat_top_limit = (lat_max * 1.2) if lat_max > 0 else 100
    ax2.set_ylim(bottom=0, top=lat_top_limit)

    # --- TITLE & SAVING ---
    plt.title(f"CockroachDB System Study: {title}", fontsize=14, pad=20)
    
    # Combined Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)

    fig.tight_layout()
    
    output_file = filename.replace('.csv', '.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved to {output_file} (Y-axis fixed to start at 0)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_graphs.py <file.csv> <Title String>")
    else:
        plot_data(sys.argv[1], sys.argv[2])