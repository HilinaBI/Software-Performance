import re
import statistics

from starlette.middleware.base import BaseHTTPMiddleware

# Path to your log file
log_file = "service_time.log"

# Regex to extract the individual service time
service_pattern = re.compile(r"\[TOTAL SERVICE TIME\] ([\d.]+)s")
server_pattern = re.compile(r"\[SERVER TIME\] ([\d.]+)s")
db_pattern = re.compile(r"\[DB TIME\] ([\d.]+)s")

service_times = []
server_times = []
db_times = []

# Read and extract all service time values
with open(log_file, "r") as f:
    for line in f:
        service_match = service_pattern.search(line)
        server_match = server_pattern.search(line)
        db_match = db_pattern.search(line)
        if service_match:
            service_times.append(float(service_match.group(1)))
        elif server_match:
            server_times.append(float(server_match.group(1)))
        elif db_match:
            db_times.append(float(db_match.group(1)))


# Compute final average
if service_times:
    avg_service_time = sum(service_times) / len(service_times)
    print(f"Final average service time: {avg_service_time:.10f} seconds over {len(service_times)} requests")
    
    # mean and variance of service time (to calculate PK-formula)
    var_s = statistics.variance(service_times)
    print(f"Variance of service times: {var_s:.10f}")
else:
    print("No service times found.")
    
if server_times:
    avg_server_time = sum(server_times) / len(server_times)
    print(f"Final average server time: {avg_server_time:.10f} seconds over {len(server_times)} requests")
else:
    print("No server times found.")
    
if db_times:
    avg_db_time = sum(db_times) / len(db_times)
    print(f"Final average db time: {avg_db_time:.10f} seconds over {len(db_times)} requests")
else:
    print("No db times found.")
    
    
