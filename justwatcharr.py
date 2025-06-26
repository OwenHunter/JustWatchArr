import os
import requests
from simplejustwatchapi import justwatch as jw
from datetime import datetime, timezone


class Radarr:
    def __init__(self):
        self.api_key = os.environ.get("RADARR_API_KEY")
        self.url = os.environ.get("RADARR_URL")
        self.header = {"X-Api-Key": self.api_key}

    def _get_tag_info(self, id):
        response = requests.get(f"{self.url}/api/v3/tag/{id}", headers=self.header)
        response.raise_for_status()
        return response.json()

    def get_movies(self):
        response = requests.get(f"{self.url}/api/v3/movie", headers=self.header)
        response.raise_for_status()
        return response.json()

    def get_movie_tags(self, movie):
        response = requests.get(
            f"{self.url}/api/v3/movie/{movie['id']}", headers=self.header
        )
        response.raise_for_status()
        tags_json = response.json()["tags"]
        tags = []
        for tag in tags_json:
            tags.append(self._get_tag_info(tag)["label"])

        return tags

    def unmonitor_movie(self, movie):
        movie["monitored"] = False
        response = requests.put(
            f"{self.url}/api/v3/movie/{movie['id']}", headers=self.header, json=movie
        )
        response.raise_for_status()
        return response.json()

    def monitor_movie(self, movie):
        movie["monitored"] = True
        response = requests.put(
            f"{self.url}/api/v3/movie/{movie['id']}", headers=self.header, json=movie
        )
        response.raise_for_status()
        return response.json()

    def get_movie_files(self, movie):
        response = requests.get(
            f"{self.url}/api/v3/moviefile?movieId={movie['id']}", headers=self.header
        )
        response.raise_for_status()
        return response.json()

    def delete_movie_files(self, files):
        for file in files:
            response = requests.delete(
                f"{self.url}/api/v3/moviefile/{file['id']}", headers=self.header
            )
            response.raise_for_status()


class Sonarr:
    def __init__(self):
        self.api_key = os.environ.get("SONARR_API_KEY")
        self.url = os.environ.get("SONARR_URL")
        self.header = {"X-Api-Key": self.api_key}

    def _get_tag_info(self, id):
        response = requests.get(f"{self.url}/api/v3/tag/{id}", headers=self.header)
        response.raise_for_status()
        return response.json()

    def get_series(self):
        response = requests.get(f"{self.url}/api/v3/series", headers=self.header)
        response.raise_for_status()
        return response.json()

    def get_series_tags(self, series):
        response = requests.get(
            f"{self.url}/api/v3/series/{series['id']}", headers=self.header
        )
        response.raise_for_status()
        tags_json = response.json()["tags"]
        tags = []
        for tag in tags_json:
            tags.append(self._get_tag_info(tag)["label"])

        return tags

    def monitor_series(self, series):
        series["monitored"] = True
        response = requests.put(
            f"{self.url}/api/v3/series/{series['id']}", headers=self.header, json=series
        )
        response.raise_for_status()
        return response.json()

    def unmonitor_series(self, series):
        series["monitored"] = False
        response = requests.put(
            f"{self.url}/api/v3/series/{series['id']}", headers=self.header, json=series
        )
        response.raise_for_status()
        return response.json()

    def delete_series_files(self, series):
        response = requests.get(
            f"{self.url}/api/v3/episodefile?seriesId={series['id']}",
            headers=self.header,
        )
        response.raise_for_status()
        for episode in response.json():
            response = requests.delete(
                f"{self.url}/api/v3/episodefile/{episode['id']}", headers=self.header
            )


def main():
    jw_providers = [
        p.strip() for p in os.environ.get("JUSTWATCH_PROVIDERS").split(",") if p.strip()
    ]
    jw_content_types = [
        p.strip()
        for p in os.environ.get("JUSTWATCH_CONTENT_TYPES", "FREE,FLATRATE").split(",")
        if p.strip()
    ]
    jw_region = os.environ.get("JUSTWATCH_REGION", "US")

    print("Checking Radarr...")
    radarr = Radarr()
    movies = radarr.get_movies()
    for movie in movies:
        if movie["status"] == "released" and "jw-exclude" not in radarr.get_movie_tags(
            movie
        ):
            if movie["monitored"] or radarr.get_movie_files(movie):
                offers = None
                try:
                    jw_result = jw.search(movie["title"], jw_region, "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type == "FLATRATE"
                            and offer.package.name in jw_providers
                        ):
                            offers.append(offer)
                except Exception:
                    pass

                if offers:
                    print(f"{movie['title']}: Available on {', '.join(offers)}")
                    print(f"{movie['title']}: Unmonitoring")
                    radarr.unmonitor_movie(movie)
                    print(f"{movie['title']}: Deleting Local Files")
                    radarr.delete_movie_files(radarr.get_movie_files(movie))
            else:
                grab = True
                try:
                    jw_result = jw.search(movie["title"], "GB", "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type in jw_content_types
                            and offer.package.name in jw_providers
                        ):
                            grab = False
                except Exception:
                    pass

                if grab:
                    print(f"{movie['title']}: Not available, monitoring")
                    radarr.monitor_movie(movie)

    print("Checking Sonarr...")
    sonarr = Sonarr()
    all_series = sonarr.get_series()
    for series in all_series:
        series["seasons"] = [
            s for s in series.get("seasons", []) if s.get("seasonNumber") != 0
        ]

        if datetime.fromisoformat(
            series["firstAired"].replace("Z", "+00:00")
        ) <= datetime.now(timezone.utc) and "jw-exclude" not in sonarr.get_series_tags(
            series
        ):
            if series["monitored"] or series["statistics"]["episodeFileCount"] > 0:
                offers = None
                try:
                    jw_result = jw.search(series["title"], jw_region, "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type in jw_content_types
                            and offer.package.name in jw_providers
                            and offer.element_count == len(series["seasons"])
                        ):
                            offers.append(offer)
                except Exception:
                    pass

                if offers:
                    print(f"{series['title']}: Available on {', '.join(offers)}")
                    print(f"{series['title']}: Unmonitoring")
                    sonarr.unmonitor_series(series)
                    print(f"{series['title']}: Deleting Local Files")
                    sonarr.delete_series_files(series)
            else:
                grab = True
                try:
                    jw_result = jw.search(series["title"], jw_region, "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type in jw_content_types
                            and offer.package.name in jw_providers
                            and offer.element_count == len(series["seasons"])
                        ):
                            grab = False
                except Exception:
                    pass

                if grab:
                    print(f"{series['title']}: Not available, monitoring")
                    sonarr.monitor_series(series)


if __name__ == "__main__":
    main()
