import yaml
import subprocess
from typing import List, Dict
from schema import IntentSkeleton

# --- Path Mapper ---
# This translates the "Intent Goal" into specific SR Linux YANG paths
YANG_PATH_MAP: Dict[str, List[str]] = {
    "system_cpu": ["/platform/control/cpu"],
    "system_memory": ["/platform/control/memory"],
    "bgp": ["/network-instance/protocols/bgp"],
    "environmental": ["/platform/fan-tray", "/platform/chassis/thermal"],
    # For interfaces, we can build a dynamic path below
}

def resolve_paths_from_intent(intent: IntentSkeleton) -> List[str]:
    """
    Translates the Intent goals into a flat list of YANG paths.
    """
    paths = []
    
    # 1. Map standard goals
    for goal in intent.telemetry_goal:
        if goal in YANG_PATH_MAP:
            paths.extend(YANG_PATH_MAP[goal])
    
    # 2. Handle specific interface requests
    if "interfaces" in intent.telemetry_goal:
        if not intent.target_interfaces:
            # If no specific interface is named, get all interface stats
            paths.append("/interface/statistics")
        else:
            # Get stats for the specific interfaces named in the intent
            for iface in intent.target_interfaces:
                paths.append(f"/interface[name={iface}]/statistics")
                
    # 3. Handle custom path requirements explicitly provided in intent
    if intent.path_requirements:
        paths.extend(intent.path_requirements)
        
    return list(set(paths)) # Remove duplicates

def generate_gnmic_config(intent: IntentSkeleton) -> str:
    """
    Generates gnmic.yaml based entirely on the validated IntentSkeleton.
    """
    target_name = intent.target_router.address
    target_port = intent.target_router.port or 57400
    
    # Resolve the paths dynamically
    resolved_paths = resolve_paths_from_intent(intent)
    
    if not resolved_paths:
        raise ValueError("No valid YANG paths could be resolved from the intent goals.")

    gnmic_config = {
        "targets": {
            target_name: {
                "address": f"{target_name}:{target_port}",
                "username": "admin",
                "password": "NokiaSrl1!",
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

if __name__ == "__main__":
    # In a real scenario, this would be loaded from a file or API
    # intent_json = sys.stdin.read() 
    
    intent_data = {
  "device_hints": {
    "vendor": "nokia",
    "nos": "sr-linux",
    "version": "latest"
  },
  "target_router": {
    "address": "clab-telemetry-lab-srl-router",
    "port": 57400
  },
  "collector": {
    "address": "clab-telemetry-lab-prometheus",
    "port": 9804
  },
  "telemetry_goal": [
    "system_cpu",
    "system_memory",
    "interfaces"
  ],
  "target_interfaces": [
    "mgmt0"
  ],
  "sample_interval_ms": 2000,
  "encoding": "json",
  "protocol": "grpc",
  "telemetry_mode": "dial-in",
  "path_requirements": [],
  "notes": [],
  "unresolved": [
    "Specific YANG paths for system CPU, system memory, and mgmt0 interface statistics are needed for Nokia SR Linux."
  ]
}
    
    # 1. Instantiate and Validate via Pydantic
    intent = IntentSkeleton(**intent_data)

    # 2. Generate config from intent
    try:
        yaml_output = generate_gnmic_config(intent)
        
        with open("gnmic.yaml", "w") as f:
            f.write(yaml_output)
        
        print(f"✅ Configuration generated with {len(resolve_paths_from_intent(intent))} paths.")
        
        # 3. Trigger Reload
        container_name = "clab-telemetry-lab-gnmic"
        print(f"🔄 Reloading {container_name}...")
        subprocess.run(["docker", "restart", container_name], check=True)
        print("✅ Success! Telemetry intent is now live.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")