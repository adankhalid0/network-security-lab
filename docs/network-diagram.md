# Network topology

```
                         ┌─────────────────────────┐
                         │      firewall            │
                         │  (nftables, routes all   │
                         │   traffic between zones) │
                         └────┬───────┬──────────┬──┘
                              │       │          │
              172.20.10.1     │       │          │ 172.20.99.1
                              │       │          │
        ┌─────────────────┐  │       │  ┌───────────────────┐
        │  vlan10_corp     │◄─┘       └─►│  vlan99_mgmt       │
        │  172.20.10.0/24  │             │  172.20.99.0/24    │
        │                  │             │                    │
        │  corp-host  .10  │             │  monitor      .10  │
        │  corp-server .20 │             │  (scanner +        │
        └──────────────────┘             │   traffic logger)  │
                                          └────────────────────┘
                              172.20.20.1
                                   │
                        ┌──────────────────┐
                        │  vlan20_guest     │
                        │  172.20.20.0/24   │
                        │                   │
                        │  guest-host  .10  │
                        └───────────────────┘
```

## Zones

| Zone        | Subnet            | Purpose                                   |
|-------------|-------------------|--------------------------------------------|
| vlan10_corp | 172.20.10.0/24    | Corporate workstation and server segment    |
| vlan20_guest| 172.20.20.0/24    | Isolated guest network                      |
| vlan99_mgmt | 172.20.99.0/24    | Management/monitoring segment               |

## Traffic policy

| From \ To | corp | guest | mgmt |
|-----------|------|-------|------|
| corp      | -    | deny  | syslog only (udp/514) |
| guest     | deny | -     | deny |
| mgmt      | allow| allow | -    |

This mirrors how VLANs are segmented on a real managed switch: each
zone is its own broadcast domain, and an L3 device (here, the
`firewall` container) enforces which zones may talk to which, using
the same deny-by-default logic as `firewall/nftables.conf`.
