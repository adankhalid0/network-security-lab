# Penetrasjonstest og sikkerhetsherding av headless CMS-applikasjon

Bacheloroppgave i sikkerhetstesting (Høyskolen Kristiania, våren 2026, karakter B) — en grey-box penetrasjonstest av en produksjonslignende headless CMS-webapplikasjon, etterfulgt av en full defensiv herding og uavhengig re-testing av resultatene.

> **Om anonymisering:** Dette oppdraget ble utført for en reell norsk kunde gjennom en autorisert avtale knyttet til bacheloroppgaven. Kundenavn, domener, IP-adresser, tokens og innloggingsopplysninger er fjernet eller erstattet med generiske plassholdere. Det som deles her er kun metodikk, sårbarhetstyper, tiltak og resultater.

## Kontekst

Et norsk programvareselskap (kundenavn anonymisert) stilte en "baseline"-versjon av et av sine headless CMS-produkter til rådighet som testobjekt for bacheloroppgaven vår. Målet var å identifisere sikkerhetssvakheter i en realistisk, moderne arkitektur, deretter designe og implementere tiltak, og til slutt verifisere at tiltakene faktisk fungerte.

**Arkitekturen som ble testet:**

```
┌──────────────┐        HTTPS / JSON        ┌────────────────────┐
│   React SPA   │ ───────────────────────▶  │  WordPress REST API │
│  (frontend)   │ ◀───────────────────────  │     (backend)        │
└──────────────┘      JWT-basert autentisering └────────────────────┘
```

En React-basert frontend kommuniserer med en WordPress-backend utelukkende gjennom REST API-et, med autentisering via JSON Web Tokens (JWT) — et vanlig mønster for "headless CMS"-løsninger.

## Min rolle

Jeg hadde hovedansvaret for dokumentasjon, sårbarhetsrapportering, risikovurdering og koordinering med oppdragsgiver og akademiske krav — jeg skrev opp hvert funn med bevis (proof of concept), alvorlighetsgrad og konsekvens, og strukturerte den endelige rapporten etter OWASP-standarder. Medstudenten min hadde hovedansvaret for å implementere tiltakene i den herdede versjonen.

## Metodikk

- **Tilnærming:** Grey-box penetrasjonstest — begrenset innsikt på forhånd (en vanlig brukerkonto), ingen tilgang til kildekode, som simulerer en realistisk angriper med noe legitim tilgang.
- **Standard:** OWASP Web Security Testing Guide (WSTG), funnene klassifisert mot OWASP Top 10 / OWASP API Security Top 10.
- **Faser:** Kartlegging → Sårbarhetsanalyse → Utnyttelse (Proof of Concept) → Rapportering → Utbedring → Re-testing.
- **Verktøy:** Burp Suite, OWASP ZAP, Nmap, Nikto, nettleserens utviklerverktøy (nettverksanalyse, JS/konsoll-analyse).

Hvert funn ble dokumentert med et reproduserbart proof of concept før det ble rapportert — dette var bevisst, for å unngå falske positiver og gi oppdragsgiver et objektivt grunnlag for å prioritere tiltak, fremfor en liste med teoretiske bekymringer.

## Oppsummering av funn (offensiv fase)

| ID | Sårbarhet | OWASP-kategori | Alvorlighet |
|----|------------|------------------|-------------|
| V1 | Hardkodede administrative innloggingsopplysninger i klientsidens JavaScript | Sensitive Data Exposure | Kritisk |
| V2 | Autentiseringslogikk (inkl. token-generering) håndtert på klientsiden i stedet for server-side | Broken Authentication | Kritisk |
| V3 | JWT-token lagret i nettleserens `localStorage`, tilgjengelig for ethvert klientsideskript | Insecure Storage | Høy |
| V4 | REST API-et returnerte for mye brukerdata (ID, e-post, interne felter) til enhver autentisert forespørsel | Information Disclosure / Excessive Data Exposure | Medium |
| V5 | Manglende `X-Frame-Options` / CSP `frame-ancestors`-header, som muliggjorde clickjacking | Security Misconfiguration | Medium |

De to kritiske funnene (V1, V2) hadde samme rotårsak: sikkerhetskritisk logikk — innloggingsopplysninger og token-utstedelse — lå i frontend i stedet for backend, noe som per definisjon er fullt kontrollerbart for en angriper så snart det når nettleseren.

## Utbedring (defensiv fase)

Hvert funn ble adressert med et målrettet, prinsippstyrt tiltak fremfor en enkeltstående lapp:

- **Fjernet alle hardkodede hemmeligheter** fra klientkoden; sensitiv konfigurasjon flyttet til server-side miljøvariabler.
- **Flyttet autentisering til serversiden.** Klienten sender nå kun inn innloggingsopplysninger; serveren validerer dem og utsteder/verifiserer tokens — noe som eliminerer angrepsflaten på klientsiden fullstendig.
- **Flyttet JWT-lagring fra `localStorage` til `HttpOnly`-cookies**, som gjør tokenet utilgjengelig for klientsidens JavaScript og lukker muligheten for sesjonskapring via XSS.
- **Implementerte rollebasert tilgangskontroll** på API-endepunkter, slik at kun autoriserte brukere kan hente ut sensitive felter.
- **Innførte server-side inputvalidering og sanitering** på tvers av registrering, innlegg og kontaktskjema, som lukker både reflekterte og lagrede XSS- og injeksjonsvektorer.
- **Innførte rate limiting** på autentiseringsendepunkter for å redusere effekten av brute-force- og credential-stuffing-forsøk.
- **La til sikkerhetsheadere** — `X-Frame-Options`, `Content-Security-Policy: frame-ancestors`, `X-Content-Type-Options` — for å herde klienten mot clickjacking og MIME-sniffing.

Styrende prinsipper: **Secure by Design**, **Defense in Depth**, **Least Privilege** — målet var aldri å lappe enkeltfeil isolert, men å fjerne hele risikoklasser ved å rette opp hvor tillitsgrensene i arkitekturen lå.

## Validering

Tiltakene ble ikke tatt på tro — alt ble re-testet med identisk metodikk og verktøy som i den opprinnelige analysen, slik at resultatene var direkte sammenlignbare:

- Alle kritiske og høye funn (V1–V3) ble **fullstendig løst**: ingen eksponerte innloggingsopplysninger i klienten, JWT-tokenet utilgjengelig for klientsideskript, og forfalskede autentiseringsforespørsler mot API-et ble korrekt avvist av serveren.
- API-responser for de mellomstore funnene (V4, V5) ble re-verifisert for å bekrefte at tilgangen nå var begrenset til autoriserte roller, og at sikkerhetsheaderne mot clickjacking var til stede på alle responser.
- Vi gjennomførte også en **brukertest med 12 deltakere** (blandet teknisk bakgrunn) for å bekrefte at herdingen ikke hadde ødelagt brukeropplevelsen:
  - Opplevd brukervennlighet: **4.1 → 4.4 av 5**
  - Opplevd tillit til applikasjonen: **3.6 → 4.5 av 5**, hvor 11 av 12 deltakere rapporterte full tillit (5/5) etter herdingen.

Dette var viktig for meg — en sikkerhetsløsning som stille ødelegger produktet er ikke egentlig en løsning folk vil beholde. Å bekrefte at brukervennligheten holdt seg oppe sammen med sikkerhetsforbedringene var en del av å behandle dette som et reelt oppdrag, ikke bare en akademisk øvelse.

## Viktigste læringspunkter

- Arkitektonisk plassering av sikkerhetskritisk logikk betyr mer enn noen enkelt kontroll — begge de kritiske funnene eksisterte fordi autentiseringslogikken lå i feil lag, ikke fordi det manglet "ekstra" beskyttelse.
- Automatiserte skannere (Nmap, Nikto, ZAP) fanget opp konfigurasjonsfeilene pålitelig (V5), men de mest alvorlige funnene (V1–V4) krevde manuell analyse av hvordan frontend og API faktisk kommuniserte.
- Sikkerhet og brukervennlighet står ikke nødvendigvis i konflikt — den herdede versjonen scoret *høyere* på både tillit og brukervennlighet enn den opprinnelige baseline-versjonen.

## Teknologi og verktøy

`React` · `WordPress REST API` · `JWT` · `Burp Suite` · `OWASP ZAP` · `Nmap` · `Nikto` · OWASP WSTG / OWASP Top 10 / OWASP API Security Top 10

---
*Bacheloroppgave, BAO304, Høyskolen Kristiania, våren 2026. Gjennomført sammen med en medstudent under et autorisert kundeoppdrag. Karakter: B.*
