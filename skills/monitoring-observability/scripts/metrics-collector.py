#!/usr/bin/env python3
"""
Metrics Collector - Gather system and application metrics.
Collects CPU, memory, disk, and custom metrics for monitoring.
"""

import json
import time
import psutil
import subprocess
from typing import Dict, List
from datetime import datetime

class MetricsCollector:
    """Collect system and application metrics."""
    
    def __init__(self):
        self.timestamps = []
        self.metrics = {}
    
    def collect_cpu_metrics(self) -> Dict:
        """Collect CPU utilization metrics."""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count_logical": psutil.cpu_count(logical=True),
            "count_physical": psutil.cpu_count(logical=False),
            "freq_current": psutil.cpu_freq().current,
            "per_cpu": psutil.cpu_percent(percpu=True),
            "load_average": dict(zip(["1min", "5min", "15min"], psutil.getloadavg()))
        }
    
    def collect_memory_metrics(self) -> Dict:
        """Collect memory utilization metrics."""
        mem = psutil.virtual_memory()
        return {
            "total_mb": mem.total / (1024*1024),
            "available_mb": mem.available / (1024*1024),
            "used_mb": mem.used / (1024*1024),
            "percent": mem.percent,
            "swap_total_mb": psutil.swap_memory().total / (1024*1024),
            "swap_used_mb": psutil.swap_memory().used / (1024*1024),
            "swap_percent": psutil.swap_memory().percent
        }
    
    def collect_disk_metrics(self) -> Dict:
        """Collect disk utilization metrics."""
        partitions = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions[partition.mountpoint] = {
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                    "percent": usage.percent
                }
            except PermissionError:
                continue
        return partitions
    
    def collect_network_metrics(self) -> Dict:
        """Collect network I/O metrics."""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout,
            "dropped_in": net_io.dropin,
            "dropped_out": net_io.dropout
        }
    
    def collect_process_metrics(self) -> Dict:
        """Collect process-level metrics."""
        processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.cpu_percent() > 5 or proc.memory_percent() > 5:
                    processes[proc.pid] = {
                        "name": proc.name(),
                        "cpu_percent": proc.cpu_percent(),
                        "memory_percent": proc.memory_percent()
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def collect_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        cpu_metrics = self.collect_cpu_metrics()
        mem_metrics = self.collect_memory_metrics()
        
        prometheus_lines = [
            f"# HELP system_cpu_percent System CPU utilization percentage",
            f"# TYPE system_cpu_percent gauge",
            f"system_cpu_percent {cpu_metrics['percent']}",
            f"",
            f"# HELP system_memory_used_mb System memory used in MB",
            f"# TYPE system_memory_used_mb gauge",
            f"system_memory_used_mb {mem_metrics['used_mb']}",
            f"",
            f"# HELP system_memory_percent System memory utilization percentage",
            f"# TYPE system_memory_percent gauge",
            f"system_memory_percent {mem_metrics['percent']}",
            f"",
            f"# HELP system_memory_available_mb Available system memory in MB",
            f"# TYPE system_memory_available_mb gauge",
            f"system_memory_available_mb {mem_metrics['available_mb']}"
        ]
        
        return "\n".join(prometheus_lines)
    
    def collect_all(self) -> Dict:
        """Collect all metrics."""
        timestamp = datetime.utcnow().isoformat()
        
        return {
            "timestamp": timestamp,
            "cpu": self.collect_cpu_metrics(),
            "memory": self.collect_memory_metrics(),
            "disk": self.collect_disk_metrics(),
            "network": self.collect_network_metrics(),
            "processes": self.collect_process_metrics()
        }

def main():
    collector = MetricsCollector()
    metrics = collector.collect_all()
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
