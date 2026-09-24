# Network Security Lab

Et lite nettverksprosjekt i Docker som simulerer et segmentert bedriftsnettverk. Det viser praktisk hvordan man deler opp et nettverk i soner, styrer trafikken mellom dem med en brannmur, og overvåker hva som skjer, akkurat det en nettverksingeniør eller IT-supportmedarbeider jobber med i praksis.

Et frivillig sideprosjekt jeg har bygget på egen hånd, uavhengig av studiet.

## Hva prosjektet gjør

Det er satt opp tre soner med Docker, som fungerer på samme måte som VLAN på en ekte svitsj:

- **vlan10_corp** (`172.20.10.0/24`) — vanlige arbeidsstasjoner og servere
- **vlan20_guest** (`172.20.20.0/24`) — et isolert gjestenettverk
- **vlan99_mgmt** (`172.20.99.0/24`) — nettverk for administrasjon og overvåking

En brannmur-container styrer trafikken mellom sonene med **nftables**. Reglene er enkle: administrasjonssonen kan nå de andre to sonene, arbeidsstasjonene kan sende logger til overvåkingsserveren, men gjestenettverket er fullstendig isolert og kommer ikke inn til noen av de andre sonene. Alt som blir stoppet logges også. Se selve reglene i [`firewall/nftables.conf`](firewall/nftables.conf) og et enkelt kart over nettverket i [`docs/network-diagram.md`](docs/network-diagram.md).

I administrasjonssonen står en overvåkingsserver med to små Python-verktøy jeg har skrevet selv:

- **`port_scanner.py`** — sjekker hvilke porter som faktisk er åpne på en maskin eller et helt nettverk. Brukes til å bekrefte at isoleringen fungerer, altså at gjestenettverket faktisk ikke kommer inn til arbeidsstasjonene.
- **`traffic_logger.py`** — lytter på nettverkstrafikk og logger hva som skjer (avsender, mottaker og port), litt som en enkel overvåkingssensor.

Det ligger også med et eksempel på **WireGuard**-oppsett (`wireguard/`), som viser hvordan man kan sette opp sikker fjerntilgang inn til administrasjonssonen.

## Slik kjører du det

Du trenger Docker og Docker Compose installert.

```bash
docker compose up --build -d
```

Test deretter at isoleringen fungerer:

```bash
docker compose exec monitor python3 port_scanner.py 172.20.10.0/24
docker compose exec guest-host nc -zv 172.20.10.10 22   # skal feile, gjest er isolert
docker compose exec corp-host nc -zv 172.20.10.20 80    # skal fungere, samme sone
```

Følg med på trafikk og blokkerte forsøk live:

```bash
docker compose logs -f firewall
docker compose exec monitor python3 traffic_logger.py --count 50
```

## Hvorfor jeg laget dette

Jeg bygget dette prosjektet fordi jeg ønsket å vise frem denne siden av meg, den praktiske og nysgjerrige interessen min for nettverk og sikkerhet. Det har vært nyttig å få vist denne kompetansen på en måte som både er interessant som hobbyprosjekt og gjennomført på et profesjonelt nivå, med reell segmentering, brannmurregler jeg kan forklare i detalj, og egne overvåkingsverktøy.

## Verktøy brukt

Docker og Docker Compose, nftables, Python 3 (scapy, socket), WireGuard.
