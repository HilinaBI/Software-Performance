import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import expon, kstest
import re

# Load the log file
log_file = "service_time.log"
pattern = re.compile(r"\[TOTAL SERVICE TIME\] ([\d.]+)s")

timestamps = []
service_times = []

# Parse log
with open(log_file, "r") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            service_times.append(float(match.group(1)))
            timestamps.append(pd.to_datetime(line[:23].replace(",", ".")))  # use timestamp prefix for arrival time

# Convert to numpy array
service_times = np.array(service_times)
interarrival_times = np.diff(np.array(timestamps)).astype('timedelta64[ms]').astype(float) / 1000 if len(timestamps) > 1 else []

# Plot histograms
sns.histplot(service_times, bins=30, kde=True, color='skyblue')
plt.title("Histogram of Service Times")
plt.xlabel("Service Time (seconds)")
plt.show()

if len(interarrival_times) > 0:
    sns.histplot(interarrival_times, bins=30, kde=True, color='lightgreen')
    plt.title("Histogram of Interarrival Times")
    plt.xlabel("Interarrival Time (seconds)")
    plt.show()

# Run K-S test for exponential fit
if len(interarrival_times) > 0:
    loc, scale = expon.fit(interarrival_times)
    ks_result = kstest(interarrival_times, 'expon', args=(loc, scale))
    print("K-S test for exponential fit to interarrival times:")
    print(f"Statistic: {ks_result.statistic:.4f}, p-value: {ks_result.pvalue:.4f}")
else:
    print("Not enough interarrival data to test exponential fit.")

# Print summary stats
print(f"Service time: mean = {service_times.mean():.6f}, std = {service_times.std():.6f}")
if len(interarrival_times) > 0:
    print(f"Interarrival time: mean = {interarrival_times.mean():.6f}, std = {interarrival_times.std():.6f}")