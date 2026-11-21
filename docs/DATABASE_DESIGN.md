# AirWatch database design

## Tables and purpose
1. **Users** — account identity and password hash.
2. **Cities** — city name, country, coordinates and timezone.
3. **MonitoringLocations** — a monitored coordinate belonging to a city.
4. **Pollutants** — pollutant catalogue (PM2.5, PM10, CO, NO2, SO2, O3).
5. **AirQualityReadings** — timestamped data collection event for one monitoring location.
6. **PollutantValues** — measured value for one pollutant in one reading.
7. **Alerts** — user-defined pollutant thresholds.
8. **SavedLocations** — many-to-many association between users and monitoring locations.

## Relationships
- Cities 1 → many MonitoringLocations.
- MonitoringLocations 1 → many AirQualityReadings.
- AirQualityReadings 1 → many PollutantValues.
- Pollutants 1 → many PollutantValues.
- Users many ↔ many MonitoringLocations through SavedLocations.
- Users 1 → many Alerts.

## Normalization notes
The pollutant catalogue is stored separately from values. This avoids repeating pollutant names and units in every measurement. Each PollutantValue references one reading and one pollutant. The unique constraint on `(reading_id, pollutant_id)` prevents duplicate pollutant entries for the same reading. SavedLocations also has a unique `(user_id, location_id)` constraint.
