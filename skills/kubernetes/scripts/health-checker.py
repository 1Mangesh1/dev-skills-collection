#!/usr/bin/env python3
"""Kubernetes Health Check Tool"""

import subprocess
import json
import sys

def check_cluster_health():
    """Check overall cluster health"""
    try:
        # Check nodes
        result = subprocess.run(
            ['kubectl', 'get', 'nodes', '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        nodes = json.loads(result.stdout)['items']
        ready_nodes = sum(
            1 for node in nodes
            if any(cond['type'] == 'Ready' and cond['status'] == 'True'
                   for cond in node['status']['conditions'])
        )
        
        print(f"✓ Nodes: {ready_nodes}/{len(nodes)} ready")
        
        # Check pods
        result = subprocess.run(
            ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        pods = json.loads(result.stdout)['items']
        running_pods = sum(
            1 for pod in pods
            if pod['status']['phase'] == 'Running'
        )
        
        print(f"✓ Pods: {running_pods}/{len(pods)} running")
        
        return ready_nodes == len(nodes) and running_pods == len(pods)
        
    except Exception as e:
        print(f"❌ Error checking cluster health: {e}")
        return False

if __name__ == "__main__":
    is_healthy = check_cluster_health()
    sys.exit(0 if is_healthy else 1)
