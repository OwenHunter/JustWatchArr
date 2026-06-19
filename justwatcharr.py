import os
import requests
import time
import schedule
from simplejustwatchapi import justwatch as jw
from datetime import datetime, timezone


class Telegram:
    def _check_token(self):
        requestURL = f"{self.url}/getUpdates"
        try:
            response = requests.post(requestURL)
        except requests.exceptions.ConnectionError:
            print("Telegram", f"{str(datetime.now())} - Error contacting {requestURL}")
            return False

        response = response.json()
        if response["ok"]:
            return True
        else:
            return False

    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        self.url = f"https://api.telegram.org/bot{self.token}"

        if not self._check_token():
            print(f"Error contacting Telegram with the token {self.token}")

    def clean_text(self, text):
        reserved_chars = [
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        ]

        for char in reserved_chars:
            text = text.replace(char, rf"\{char}")

        return text

    def send_message(self, heading, content):
        requestURL = f"{self.url}/sendMessage"
        message = f"*JustWatchArr*\n_{heading}_\n{content}"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "MarkdownV2"}

        try:
            message_sent = False
            while not message_sent:
                response = requests.post(requestURL, payload)
                try:
                    response.raise_for_status()
                    message_sent = True
                except requests.exceptions.HTTPError as e:
                    if "Too Many Requests" in e.response.json()["description"]:
                        time.sleep(e.response.json()["parameters"]["retry_after"])
                        continue
                    else:
                        raise e
        except requests.exceptions.ConnectionError:
            print(f"{str(datetime.now())} - Error contacting {requestURL}")
        except requests.exceptions.HTTPError as e:
            print(f"{str(datetime.now())} - {e.request.url} - {e} - {e.response.text}")


telegram = Telegram()


class Radarr:
    def __init__(self):
        self.api_key = os.environ.get("RADARR_API_KEY")
        self.url = os.environ.get("RADARR_URL")
        self.header = {"X-Api-Key": self.api_key}

    def _get_tag_info(self, id):
        requestURL = f"{self.url}/api/v3/tag/{id}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return None

    def get_movies(self):
        requestURL = f"{self.url}/api/v3/movie"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return {}

    def get_movie_tags(self, movie):
        requestURL = f"{self.url}/api/v3/movie/{movie['id']}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()
            tags_json = response.json()["tags"]
            tags = []
            for tag in tags_json:
                tag_info = self._get_tag_info(tag)["label"]
                if tag_info:
                    tags.append(tag_info)

            return tags
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return []

    def unmonitor_movie(self, movie):
        movie["monitored"] = False

        requestURL = f"{self.url}/api/v3/movie/{movie['id']}"
        try:
            response = requests.put(requestURL, headers=self.header, json=movie)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")

    def monitor_movie(self, movie):
        movie["monitored"] = True

        requestURL = f"{self.url}/api/v3/movie/{movie['id']}"
        try:
            response = requests.put(requestURL, headers=self.header, json=movie)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")

    def search_movie(self, movie):
        requestURL = f"{self.url}/api/v3/command"
        payload = {"name": "MoviesSearch", "movieIds": [movie["id"]]}
        try:
            response = requests.post(requestURL, headers=self.header, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"{str(datetime.now())} - Error contacting {requestURL}")

    def get_movie_files(self, movie):
        requestURL = f"{self.url}/api/v3/moviefile?movieId={movie['id']}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.ConnectionError:
            output("Radarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return None

    def delete_movie_files(self, files):
        for file in files:
            requestURL = f"{self.url}/api/v3/moviefile/{file['id']}"
            try:
                response = requests.delete(requestURL, headers=self.header)
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                output(
                    "Radarr", f"{str(datetime.now())} - Error contacting {requestURL}"
                )


class Sonarr:
    def __init__(self):
        self.api_key = os.environ.get("SONARR_API_KEY")
        self.url = os.environ.get("SONARR_URL")
        self.header = {"X-Api-Key": self.api_key}

    def _get_tag_info(self, id):
        requestURL = f"{self.url}/api/v3/tag/{id}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return None

    def get_series(self):
        requestURL = f"{self.url}/api/v3/series"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return {}

    def get_series_tags(self, series):
        requestURL = f"{self.url}/api/v3/series/{series['id']}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()
            tags_json = response.json()["tags"]
            tags = []
            for tag in tags_json:
                tag_info = self._get_tag_info(tag)["label"]
                if tag_info:
                    tags.append(tag_info)

            return tags
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")
            return []

    def monitor_series(self, series):
        series["monitored"] = True

        requestURL = f"{self.url}/api/v3/series/{series['id']}"
        try:
            response = requests.put(requestURL, headers=self.header, json=series)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")

    def search_series(self, series):
        requestURL = f"{self.url}/api/v3/command"
        payload = {"name": "SeriesSearch", "seriesId": series["id"]}
        try:
            response = requests.post(requestURL, headers=self.header, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"{str(datetime.now())} - Error contacting {requestURL}")

    def unmonitor_series(self, series):
        series["monitored"] = False

        requestURL = f"{self.url}/api/v3/series/{series['id']}"
        try:
            response = requests.put(requestURL, headers=self.header, json=series)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")

    def delete_series_files(self, series):
        requestURL = f"{self.url}/api/v3/episodefile?seriesId={series['id']}"
        try:
            response = requests.get(requestURL, headers=self.header)
            response.raise_for_status()
            for episode in response.json():
                requestURL = f"{self.url}/api/v3/episodefile/{episode['id']}"
                try:
                    response = requests.delete(requestURL, headers=self.header)
                except requests.exceptions.ConnectionError:
                    output(
                        "Sonarr",
                        f"{str(datetime.now())} - Error contacting {requestURL}",
                    )
        except requests.exceptions.ConnectionError:
            output("Sonarr", f"{str(datetime.now())} - Error contacting {requestURL}")


def output(origin, content):
    print(f"{str(datetime.now())} - {origin}: {content}")
    telegram.send_message(origin, telegram.clean_text(content))


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

    print(f"{str(datetime.now())} - Checking Radarr...")
    radarr = Radarr()
    movies = radarr.get_movies()
    for movie in movies:
        movie_files = radarr.get_movie_files(movie)
        if movie["status"] == "released" and "jw-exclude" not in radarr.get_movie_tags(
            movie
        ):
            if movie.get("monitored", True) or movie_files:
                offers = []
                try:
                    jw_result = jw.search(movie["title"], jw_region, "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type in jw_content_types
                            and offer.package.name in jw_providers
                        ):
                            offers.append(offer)
                except Exception:
                    pass

                if offers:
                    output(
                        "Radarr",
                        f"{movie['title']}: Available on {', '.join([offer.package.name for offer in offers])}",
                    )
                    if movie.get("monitored", True):
                        radarr.unmonitor_movie(movie)
                        output("Radarr", f"{movie['title']}: Unmonitoring")
                    if movie_files:
                        radarr.delete_movie_files(movie_files)
                        output("Radarr", f"{movie['title']}: Deleting Local Files")

            else:
                grab = True
                try:
                    jw_result = jw.search(movie["title"], jw_region, "en", 1, True)[0]
                    for offer in jw_result.offers:
                        if (
                            offer.monetization_type in jw_content_types
                            and offer.package.name in jw_providers
                        ):
                            grab = False
                except Exception:
                    pass

                if grab:
                    radarr.monitor_movie(movie)
                    radarr.search_movie(movie)
                    output("Radarr", f"{movie['title']}: Not available, monitoring")

    print(f"{str(datetime.now())} - Radarr checks complete")

    print(f"{str(datetime.now())} - Checking Sonarr...")
    sonarr = Sonarr()
    all_series = sonarr.get_series()
    for series in all_series:
        series["seasons"] = [
            s for s in series.get("seasons", []) if s.get("seasonNumber") != 0
        ]
        episode_file_count = series.get("statistics", {}).get("episodeFileCount", 0)

        if datetime.fromisoformat(
            series["firstAired"].replace("Z", "+00:00")
        ) <= datetime.now(timezone.utc) and "jw-exclude" not in sonarr.get_series_tags(
            series
        ):
            if series.get("monitored", True) or episode_file_count > 0:
                offers = []
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
                    output(
                        "Sonarr",
                        f"{series['title']}: Available on {', '.join([offer.package.name for offer in offers])}",
                    )
                    if series.get("monitored", True):
                        sonarr.unmonitor_series(series)
                        output("Sonarr", f"{series['title']}: Unmonitoring")
                    if episode_file_count > 0:
                        sonarr.delete_series_files(series)
                        output("Sonarr", f"{series['title']}: Deleting Local Files")

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
                    sonarr.monitor_series(series)
                    sonarr.search_series(series)
                    output("Sonarr", f"{series['title']}: Not available, monitoring")

    print(f"{str(datetime.now())} - Sonarr checks complete")


def schedule_runs():
    """Set up the scheduler based on RUNPERIOD environment variable"""
    run_period = os.environ.get("RUNPERIOD", "Daily").lower()

    if run_period == "daily":
        schedule.every().day.at("03:00").do(main)
    elif run_period == "weekly":
        schedule.every().monday.at("03:00").do(main)
    elif run_period == "monthly":
        # Run on the 1st of each month at 03:00
        schedule.every().day.at("03:00").do(lambda: _run_if_monthly())
    elif run_period == "quarterly":
        # Run on the 1st of months 1, 4, 7, 10 at 03:00
        schedule.every().day.at("03:00").do(lambda: _run_if_quarterly())
    elif run_period == "yearly":
        # Run on Jan 1st at 03:00
        schedule.every().day.at("03:00").do(lambda: _run_if_yearly())
    else:
        # Default to daily
        schedule.every().day.at("03:00").do(main)


def _run_if_monthly():
    """Helper to run only on monthly schedule (1st of each month)"""
    now = datetime.now()
    if now.day == 1:
        main()


def _run_if_quarterly():
    """Helper to run only on quarterly schedule (1st of months 1, 4, 7, 10)"""
    now = datetime.now()
    if now.day == 1 and now.month in [1, 4, 7, 10]:
        main()


def _run_if_yearly():
    """Helper to run only on yearly schedule (Jan 1st)"""
    now = datetime.now()
    if now.day == 1 and now.month == 1:
        main()


if __name__ == "__main__":
    print(f"{str(datetime.now())} - Starting initial run...")
    # Run immediately on startup
    main()

    print(f"{str(datetime.now())} - Enabling schedule...")
    # Set up the scheduler
    schedule_runs()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(300)  # Check schedule every 5 minutes
