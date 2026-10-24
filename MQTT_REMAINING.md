# Missing and partial MQTT mappings

Checked against the local `normalize_status()` in `mqtt.py` on October 24, 2026.
This list describes what the integration applies to entities. Receiving a field
in an MQTT message does not mean that the field has a usable mapping.

## Fields without an MQTT mapping

| State | Internal field | What is missing |
| --- | --- | --- |
| Speed | `vehicleStatus.speed` | Source field conversion and units |
| Vehicle online status | `vehicleStatus.connectStatus` | `connectStatus` is not applied; connection-only reports must not make vehicle telemetry appear newer |
| Total charging current | `charge.chargeCurrent` | Source field and scaling; an observed `totalCurrent=10` corresponded to HTTPS `chargeCurrent=0` |
| Rear-seat heating and ventilation | `seat.leftBack.*`, `seat.rightBack.*` | Codes and levels; MQTT value 6 must not be assumed to mean high heat |
| Cockpit temperature | `hvac.consTempCockpit` | No established MQTT source; `constantTempCabinStatus` is not documented as a temperature |
| Location | `location` | Coordinate conversion, validity and coordinate system; usable coordinates have not been observed in the EU HTTPS responses either |
| Window opening percentage | `window.openDegree` | Units, scaling and position order |
| Battery-preheating plan: enabled state and time | `battery_preheating_plan` | No MQTT mapping; the plan is fetched through a separate HTTPS request |

## Partially mapped states

| State | What MQTT can update | What remains unresolved |
| --- | --- | --- |
| Lamps and turn signals | Raw code 0 maps to off | On and other codes |
| Tire warnings | Raw code 0 maps to status 0 | Warning codes; tire pressure itself is already mapped |
| Charging status | Raw `chargeStatus=3` maps to not charging | Charging, completed, paused and other codes |
| Charge connection | Raw DC code 0 maps to disconnected; overall disconnected requires both AC and DC to be 0 | Connected and other codes; AC=0 alone does not establish overall connection status |
| Driver and passenger door locks | Raw code 0 maps to locked | Unlocked and other codes; rear-door lock codes are not applied |
| Vehicle driving status | Raw `carStatus=2` maps to parked | Driving and other codes |
| Power status | Raw `powerStatusFeedBack=0/2` maps to internal 0/2 | Code 1 and other codes |
| AC/DC charging current | `BattACChrgInCurr` / `BattDCChrgInCurr` and their aliases | No conversion from `obcChrgInpAcI`, `chargeCurrentVal` or `totalCurrent` |

Window open/closed values are mapped, but the position order between MQTT and EU
HTTPS has not been verified with different states on individual windows.
Front defrost supports both off and on. Conflicting or unknown codes are ignored.
Steering-wheel heating maps raw code 1 to off and raw code 2 to on.

Front-seat heating and ventilation use levels 0-3 directly on both sides. Seat
mode is heating when heat is active and ventilation when ventilation is active.
If both are active in the same report, their levels update without choosing a
combined mode. Setting the combined mode to off requires both heat and
ventilation to be 0 in the report. Unknown codes, including 6, are ignored.

## EU and Asia

Both regions use the same MQTT normalizer. EU still receives a full HTTPS status
every 15 minutes, which can update missing fields when the endpoint supplies
them. Asia reads its full status through MQTT and the same parser: a new
snapshot does not add support for fields or codes that the parser does not map.
The battery-preheating plan retains its separate HTTPS request.

Unknown codes in partial reports preserve the existing value. A supported
mapping does not guarantee that the vehicle sends a spontaneous report for
every change. Local MQTT/HTTPS comparisons are from EU. The user confirmed on
October 24, 2026 that Asia has been tested and works; that does not establish
the meaning of the unresolved status codes listed above.
