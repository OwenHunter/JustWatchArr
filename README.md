# JustWatchArr

Removes local files and unmonitors movies and series from Radarr and Sonarr that are available in your selected providers.

## Options

See the example [docker-compose.yml](docker-compose.yml).

 - `RADARR_API_KEY`
 - `RADARR_URL`
 - `SONARR_API_KEY`
 - `SONARR_URL`
 - `JUSTWATCH_PROVIDERS` - Comma separated list. Hover over the logos of providers on [JustWatch](https://www.justwatch.com) to find the names required.
 - `JUSTWATCH_CONTENT_TYPES` - Comma separated list. `buy`, `rent`, `flatrate` (subscription), `free`
 - `JUSTWATCH_REGION` - ISO2 country code.
 - `RUNPERIOD` - `Daily`, `Weekly`, `Monthly`, `Quarterly`, `Yearly`
