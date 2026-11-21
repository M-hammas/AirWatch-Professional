# Project demonstration guide

## Suggested 5–7 minute presentation
1. **Problem and purpose (30 sec):** Explain why monitoring air pollution and comparing locations is useful.
2. **Architecture (45 sec):** React is the presentation layer, FastAPI handles application logic and API integration, MySQL stores relational data.
3. **Database (60 sec):** Show the eight tables and explain primary keys, foreign keys, one-to-many and many-to-many relationships.
4. **Live workflow (2 min):** Register, search for a city, save it, refresh Open-Meteo data and show pollutant values.
5. **Historical data (45 sec):** Explain that each refresh stores a timestamped reading and history uses those stored records.
6. **Alerts (30 sec):** Create a pollutant threshold and show it persisted in MySQL.
7. **Conclusion (30 sec):** Summarize API integration, CRUD operations, relational design and future improvements.

## Important viva questions
- **Why MySQL?** It is a relational DBMS with constraints and foreign keys suited to structured, related records.
- **Why a separate Pollutants table?** It avoids repeating pollutant metadata and supports normalized pollutant values.
- **Why a junction table SavedLocations?** A user can save many locations and a location can be saved by many users.
- **What is a foreign key?** A constraint linking a row to a valid row in another table.
- **What is an API?** A defined interface through which software systems exchange data.
- **What does FastAPI do?** It exposes backend endpoints, validates requests and coordinates database and external API operations.
- **Does the app create historical data automatically?** Each explicit refresh stores a timestamped snapshot. Historical charts show saved snapshots, not invented values.
- **What is normalization?** Organizing relational data to reduce duplication and update anomalies.
