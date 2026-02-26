# SR Linux Native Telemetry Reference

## Interface statistics on SR Linux
vendor: nokia
nos: sr-linux
signal: interface_statistics
signal_aliases: interface_counters, port_stats, interface_metrics
source_type: native-doc

Use this when the user wants telemetry for interface counters, packet statistics, octets, errors, or discards.

Common native path candidate:
- /interface[name=<interface-name>]/statistics

Example for management interface:
- /interface[name=mgmt0]/statistics

Notes:
- This path is intended for interface-level counters and statistics.
- If the user asks for the management interface, prefer mgmt0 when explicitly confirmed.
- If the interface name is not known, keep it unresolved instead of inventing one.

---

## Subinterface statistics on SR Linux
vendor: nokia
nos: sr-linux
signal: subinterface_statistics
signal_aliases: subif_stats, logical_interface_stats
source_type: native-doc

Common native path candidate:
- /interface[name=<interface-name>]/subinterface[index=<subif-index>]/statistics

Notes:
- Use only when the user explicitly asks for subinterface or logical interface statistics.

---

## BGP neighbor telemetry on SR Linux
vendor: nokia
nos: sr-linux
signal: bgp_neighbors
signal_aliases: bgp_sessions, bgp_peer_state
source_type: native-doc

Common native path candidate:
- /network-instance[name=<ni-name>]/protocols/bgp/neighbor[peer-address=<peer-ip>]

Notes:
- Use when the user wants neighbor state, received prefixes, session status, or peer counters.
- Requires network-instance and neighbor identity for exact targeting.

---

## CPU usage on SR Linux
vendor: nokia
nos: sr-linux
signal: cpu_usage
signal_aliases: cpu, system_cpu
source_type: native-doc

Common native path candidate:
- /platform/control[slot=<slot-id>]/cpu

Notes:
- Exact native path may vary by platform/release.
- If slot is missing, keep unresolved.

---

## Memory usage on SR Linux
vendor: nokia
nos: sr-linux
signal: memory_usage
signal_aliases: ram, memory, system_memory
source_type: native-doc

Common native path candidate:
- /platform/control[slot=<slot-id>]/memory

Notes:
- Exact native path may vary by platform/release.
- If slot is missing, keep unresolved.