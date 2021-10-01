import os

cpu_limit = os.environ.get("API_CPU_LIMIT")
if cpu_limit is None:
    num_avail_cpus = len(os.sched_getaffinity(0))  # type: ignore[attr-defined]
else:
    try:
        num_avail_cpus = int(cpu_limit)
    except ValueError:
        num_avail_cpus = 1

loglevel = os.environ.get("API_LOG_LEVEL", "INFO")
worker_class = "uvicorn.workers.UvicornWorker"
workers = num_avail_cpus
bind = "0.0.0.0:80"
