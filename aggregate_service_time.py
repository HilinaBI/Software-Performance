import re
import statistics

from starlette.middleware.base import BaseHTTPMiddleware

# Path to your log file
log_file = "service_time.log"

# Regex to extract the individual service time
service_pattern = re.compile(r"\[SERVICE TIME\] ([\d.]+)s")
render_pattern = re.compile(r"\[RENDER TIME\] ([\d.]+)s")
tot_req_pattern = re.compile(r"\[TOTAL REQUEST TIME\] ([\d.]+)s")

service_times = []
render_times = []
tot_req_times = []

# Read and extract all service time values
with open(log_file, "r") as f:
    for line in f:
        service_match = service_pattern.search(line)
        render_match = render_pattern.search(line)
        tot_req_match = tot_req_pattern.search(line)
        if service_match:
            service_times.append(float(service_match.group(1)))
        elif render_match:
            render_times.append(float(render_match.group(1)))
        elif tot_req_match:
            tot_req_times.append(float(tot_req_match.group(1)))


# Compute final average
if service_times:
    avg_service_time = sum(service_times) / len(service_times)
    print(f"Final average service time: {avg_service_time:.10f} seconds over {len(service_times)} requests")
    
    # mean and variance of service time (to calculate PK-formula)
    var_s = statistics.variance(service_times)
    print(f"Variance of service times: {var_s:.10f}")
else:
    print("No service times found.")
    
if render_times:
    avg_render_time = sum(render_times) / len(render_times)
    print(f"Final average render time: {avg_render_time:.10f} seconds over {len(render_times)} requests")
else:
    print("No render times found.")
    
if tot_req_times:
    avg_tot_req_time = sum(tot_req_times) / len(tot_req_times)
    print(f"Final average total request time: {avg_tot_req_time:.10f} seconds over {len(tot_req_times)} requests")
else:
    print("No total request times found.")
    
    
