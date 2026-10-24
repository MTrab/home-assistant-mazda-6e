# Manglende og delvise MQTT-mappings

Kontrolleret mod `normalize_status()` i `mqtt.py`, commit `e214c75`, 18. oktober 2026.
Listen beskriver, hvad integrationen anvender. Et felt kan godt være modtaget
fra MQTT uden at være oversat til en entity.

## Uden MQTT-mapping

| Tilstand | Internt felt | Hvad mangler |
| --- | --- | --- |
| Hastighed | `vehicleStatus.speed` | Oversættelse af kildefelt og enhed |
| Bilens online-status | `vehicleStatus.connectStatus` | `connectStatus` anvendes ikke; rene forbindelsesbeskeder må ikke gøre telemetrien nyere |
| Samlet ladestrøm | `charge.chargeCurrent` | Valg af kildefelt og skalering; observeret `totalCurrent=10` svarede til HTTPS-værdien 0 |
| Varme og ventilation på bagsæderne | `seat.leftBack.*`, `seat.rightBack.*` | Koder og niveauer; MQTT-værdien 6 må ikke uden videre fortolkes som høj varme |
| Cockpit-temperatur | `hvac.consTempCockpit` | Intet fastslået MQTT-kildefelt; `constantTempCabinStatus` er ikke dokumenteret som en temperatur |
| Position | `location` | Koordinatoversættelse, gyldighed og koordinatsystem; en brugbar position er heller ikke observeret i EU HTTPS-svarene |
| Vinduernes åbningsgrad | `window.openDegree` | Oversættelse af grader/procenter og rækkefølge |
| Batteriforvarmningsplan: aktiveret og tidspunkt | `battery_preheating_plan` | Ingen MQTT-mapping; planen hentes særskilt via HTTPS |

## Kun delvist oversat

| Tilstand | Det MQTT kan opdatere nu | Det der stadig mangler |
| --- | --- | --- |
| Ratvarme | Rå kode 1 til slukket | Tændt og øvrige koder |
| Forsædernes varme og ventilation | Rå kode 0 til slukket | Aktive niveauer; samlet sædetilstand sættes kun til slukket, når begge felter er 0 i samme besked |
| Lys og blinklys | Rå kode 0 til slukket | Tændt og øvrige koder |
| Dækalarm | Rå kode 0 til status 0 | Advarselskoder; selve dæktrykket er allerede mappet |
| Ladestatus | Rå `chargeStatus=3` til ikke ladende | Lader, færdig, pause og øvrige koder |
| Ladestik | DC frakoblet ved rå kode 0; samlet frakoblet, når både AC og DC er 0 | Tilsluttet og øvrige koder; AC=0 alene afgør ikke samlet stikstatus |
| Førerdørens og passagerdørens lås | Rå kode 0 til låst | Ulåst og øvrige koder; bagdørenes låsekoder anvendes ikke |
| Bilens kørselsstatus | Rå `carStatus=2` til parkeret | Kører og øvrige koder |
| Strømstatus | Rå `powerStatusFeedBack=0/2` til intern 0/2 | Kode 1 og øvrige koder |
| AC/DC-ladestrøm | Felterne `BattACChrgInCurr` / `BattDCChrgInCurr` og deres aliaser | Ingen oversættelse fra `obcChrgInpAcI`, `chargeCurrentVal` eller `totalCurrent` |

Vinduernes åbne/lukkede værdier er mappet, men rækkefølgen mellem MQTT og EU
HTTPS er ikke verificeret ved forskellige tilstande på de enkelte vinduer.
Forrudeafrimning har både tændt og slukket oversat; modstridende eller ukendte
koder ignoreres.

## Betydning i EU og Asia

Begge regioner bruger samme MQTT-oversættelse. EU får fortsat en HTTPS-status
hvert 15. minut, som kan opdatere de manglende felter, hvis de findes i svaret.
Asia læser sin fulde status via MQTT og samme parser: et nyt snapshot giver
derfor ikke i sig selv adgang til felter eller koder, som parseren ikke mapper.
Batteriforvarmningsplanen har sit særskilte HTTPS-kald.

Ukendte koder i delvise beskeder bevarer den eksisterende værdi. En mappet værdi
er ikke en garanti for, at bilen sender en spontan besked ved hver ændring.
De lokale observationer er fra EU. Brugeren har den 24. oktober 2026 bekræftet,
at Asia er afprøvet og fungerer. Det fastslår ikke i sig selv betydningen af
de manglende statuskoder ovenfor.
