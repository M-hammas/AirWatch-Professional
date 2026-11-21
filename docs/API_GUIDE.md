# API guide

Base URL: `http://127.0.0.1:8000/api`

Protected routes require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Sign in |
| GET | `/auth/me` | Current user |
| GET | `/cities/search?q=Lahore` | Search cities |
| POST | `/cities/monitor` | Save a city/monitoring location |
| GET | `/cities/saved` | List saved locations |
| DELETE | `/cities/saved/{saved_id}` | Remove saved location |
| POST | `/readings/refresh/{location_id}` | Fetch and store current measurements |
| GET | `/readings/latest/{location_id}` | Get latest stored reading |
| GET | `/readings/history/{location_id}?days=7` | Get historical readings |
| GET | `/readings/analytics/{location_id}?days=7` | Average and maximum pollutant values |
| GET | `/readings/compare` | Compare latest stored readings across saved cities |
| GET | `/alerts` | List alert rules |
| POST | `/alerts` | Create threshold rule |
| DELETE | `/alerts/{alert_id}` | Delete threshold rule |

Use `/docs` to explore and test the API interactively.
