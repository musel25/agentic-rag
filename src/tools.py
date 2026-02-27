# src/tools.py
import yaml
import subprocess
import logging
from typing import List, Dict

# Import the schema from your existing src/schema.py
from schema import IntentSkeleton

logger = logging.getLogger(__name__)

# --- Constants & Defaults ---
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "NokiaSrl1!"
DEFAULT_CONTAINER_NAME = "clab-telemetry-lab-gnmic"
DEFAULT_CONFIG_PATH = "../containerlab/gnmic.yaml"

YANG_PATH_MAP: Dict[str, List[str]] = {
    "system_cpu": ["/platform/control/cpu"],
    "system_memory": ["/platform/control/memory"],
    "bgp": ["/network-instance/protocols/bgp"],
    "environmental": ["/platform/fan-tray", "/platform/chassis/thermal"],
}

def resolve_paths_from_intent(intent: IntentSkeleton) -> List[str]:
    paths = []
    for goal in intent.telemetry_goal:
        if goal in YANG_PATH_MAP:
            paths.extend(YANG_PATH_MAP[goal])
    
    if "interfaces" in intent.telemetry_goal:
        if not intent.target_interfaces:
            paths.append("/interface/statistics")
        else:
            for iface in intent.target_interfaces:
                paths.append(f"/interface[name={iface}]/statistics")
                
    if intent.path_requirements:
        paths.extend(intent.path_requirements)
        
    return list(set(paths)) 

def generate_gnmic_config(intent: IntentSkeleton, resolved_paths: List[str], 
                          username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> str:
    target_name = intent.target_router.address
    target_port = intent.target_router.port or 57400
    
    gnmic_config = {
        "targets": {
            target_name: {
                "address": f"{target_name}:{target_port}",
                "username": username,
                "password": password,
                "skip-verify": True
            }
        },
        "subscriptions": {
            f"sub-{target_name}": {
                "paths": resolved_paths,
                "sample-interval": f"{intent.sample_interval_ms or 10000}ms",
                "encoding": intent.encoding or "json_ietf"
            }
        },
        "outputs": {
            "prom-output": {
                "type": "prometheus",
                "listen": f":{intent.collector.port or 9804}"
            }
        }
    }
    return yaml.dump(gnmic_config, sort_keys=False, default_flow_style=False)

def write_config(config_yaml: str, file_path: str) -> None:
    with open(file_path, "w") as f:
        f.write(config_yaml)

def restart_docker_container(container_name: str) -> None:
    subprocess.run(
        ["docker", "restart", container_name], 
        check=True, 
        capture_output=True, 
        text=True
    )

def deploy_telemetry(intent: IntentSkeleton, config_path: str = DEFAULT_CONFIG_PATH, 
                     container_name: str = DEFAULT_CONTAINER_NAME) -> str:
    """Main tool execution function for the LLM."""
    try:
        paths = resolve_paths_from_intent(intent)
        if not paths:
            return "Error: No valid YANG paths could be resolved from the intent goals."

        yaml_output = generate_gnmic_config(intent, paths)
        write_config(yaml_output, config_path)
        restart_docker_container(container_name)
        
        return f"Success: Telemetry deployed. Generated config with {len(paths)} paths and restarted '{container_name}'."
        
    except subprocess.CalledProcessError as e:
        return f"System Error: Failed to restart container '{container_name}'. Docker output: {e.stderr}"
    except Exception as e:
        return f"Application Error: An unexpected error occurred during execution: {str(e)}"