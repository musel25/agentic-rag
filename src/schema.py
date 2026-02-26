
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class DeviceHints(BaseModel):
    vendor: Optional[str] = Field(None, description="The hardware vendor, e.g., 'cisco', 'arista', 'nokia'.")
    nos: Optional[str] = Field(None, description="The network operating system, e.g., 'ios-xr', 'eos', 'sr-linux'.")
    version: Optional[str] = Field(None, description="The OS version, if explicitly stated.")

class ConnectionTarget(BaseModel):
    address: Optional[str] = Field(
        None, 
        description="The IP address or hostname. MUST NOT contain the port. If input is 'leaf-01:6030', address is 'leaf-01'."
    )
    port: Optional[int] = Field(
        None, 
        description="The connection port. Extract this if appended to the address with a colon."
    )

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

# ... (Keep DeviceHints and ConnectionTarget as they are) ...

class IntentSkeleton(BaseModel):
    device_hints: DeviceHints
    target_router: ConnectionTarget
    collector: ConnectionTarget
    
    telemetry_goal: List[Literal[
        "interfaces", 
        "bgp", 
        "system_cpu", 
        "system_memory", 
        "environmental", 
        "other"
    ]] = Field(default_factory=list)
    
    target_interfaces: List[str] = Field(default_factory=list)
    sample_interval_ms: Optional[int] = Field(None)
    
    encoding: Optional[Literal["gpb", "kv-gpb", "json", "xml"]] = Field(
        None, description="The encoding format. Prefer 'gpb' or 'json'."
    )
    protocol: Optional[Literal["grpc", "tcp", "udp"]] = Field(
        None, description="The transport protocol. Usually 'grpc'."
    )
    telemetry_mode: Optional[Literal["dial-out", "dial-in"]] = Field(
        "dial-out", description="MDT connection mode. Defaults to dial-out."
    )
    
    path_requirements: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    unresolved: List[str] = Field(default_factory=list)

    # THE FIX: Intercept dirty LLM strings before they enter your app
    @field_validator("encoding", "protocol", "telemetry_mode", mode="before")
    @classmethod
    def wipe_null_strings(cls, value):
        if isinstance(value, str) and value.strip().lower() == "null":
            return None # Convert literal string "null" to actual None type
        return value