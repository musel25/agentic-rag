# OpenConfig Interfaces Telemetry Reference

## Interface counters via OpenConfig
vendor: multi
nos: multi
signal: interface_statistics
signal_aliases: interface_counters, interface_metrics
source_type: openconfig-doc

Canonical OpenConfig path candidate:
- /interfaces/interface[name=<interface-name>]/state/counters

Notes:
- Use as a vendor-neutral candidate when native support is unknown.
- Final implementation still depends on device support and model mapping.

---

## Interface operational state via OpenConfig
vendor: multi
nos: multi
signal: interface_oper_state
signal_aliases: link_state, admin_state
source_type: openconfig-doc

Canonical OpenConfig path candidate:
- /interfaces/interface[name=<interface-name>]/state