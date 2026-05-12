# Test fixtures

## Provenance & privacy

All `getReadings*.json` files in this directory are **captures from the
vendor-owned public demo controller at <https://demo.myviolet.de/>**, which
Pooldigital provides specifically as a reference deployment for developers
and prospective customers.

This means:

- The hardware identifiers in the fixture (e.g. `onewire*_rcode` values,
  `HW_SERIAL_CARRIER`) belong to vendor demo hardware — **not** to any
  customer site.
- The timestamps in the fixture reflect when the snapshot was captured
  against the vendor demo and carry no private information.
- No sanitisation is required before committing additional captures from
  the same demo system.

If you ever need to add a fixture from a **different** controller (your own
pool, a customer site, etc.), sanitise it first:

- Replace `onewire*_rcode` with `"0000000000000000"`.
- Replace `HW_SERIAL_CARRIER` with `"0"`.
- Normalise all Unix-epoch timestamps (`*_LAST_ON`, `*_LAST_OFF`,
  `CURRENT_TIME_UNIX`, `BACKWASH_LAST_*`, etc.) to a fixed reference such
  as `1700000000`.
- Drop any keys that obviously identify the deployment
  (e.g. user-set names, configured WiFi SSID, geolocation).

## How fixtures are used

- `getReadings_seed.json` is the canonical `?ALL,DOSAGE,RUNTIMES` snapshot.
  It seeds both the unit-test fixtures (`tests/conftest.py`) and the mock
  service (`tools.myviolet_mock`).
- `getReadings_selective.json` is an example of a key-selected response
  (`?pH_value,PUMP,COVER_STATE`), used to demonstrate the selective-fetch
  code path.

To regenerate from the live demo:

```bash
curl -sSL 'https://demo.myviolet.de/getReadings?ALL,DOSAGE,RUNTIMES' \
    > tests/fixtures/getReadings_seed.json
curl -sSL 'https://demo.myviolet.de/getReadings?pH_value,PUMP,COVER_STATE' \
    > tests/fixtures/getReadings_selective.json
```
