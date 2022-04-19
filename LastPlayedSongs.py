import datetime
import json
import requests
from requests.exceptions import HTTPError
import pandas as pd
import logging
from Refresh import Refresh


class LastPlayedSongs:

    def __init__(self, token="", limit=50, from_date=0, to_date=0):
        self._token = token
        self._limit = limit
        self._from_date = from_date
        self._to_date = to_date

    @property
    def token(self):
        return self._token

    @property
    def limit(self):
        return self._limit

    @property
    def from_date(self):
        return self._from_date

    @property
    def to_date(self):
        return self._to_date

    def _refresh_access_token(self):
        logging.info("Refreshing token")
        refresh_obj = Refresh()
        self._token = refresh_obj.refresh()

    def _set_timeframe(self):
        # get last day
        today = datetime.datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - datetime.timedelta(days=1)
        # print(yesterday)
        yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
        today_unix_timestamp = int(today.timestamp()) * 1000

        print(yesterday, today, yesterday_unix_timestamp, today_unix_timestamp)

        self._from_date = yesterday_unix_timestamp
        self._to_date = today_unix_timestamp

    def _extract_data(self, json_message: dict):

        # get basic info from last played tracks
        artists = []
        titles = []
        played_at = []
        dates = []

        for song in json_message["items"]:
            artists.append(song["track"]["artists"][0]["name"])
            titles.append(song["track"]["name"])
            played_at.append(song["played_at"])
            dates.append(song["played_at"][0:10])

        # create a dict with basic info
        song_dict = {
            "artist_name": artists,
            "song_name": titles,
            "played_at": played_at,
            "date": dates
        }

        # create pandas DataFrame
        songs_df = pd.DataFrame(song_dict, columns=["artist_name", "song_name", "played_at", "date"])
        # print(songs_df.shape)

        # validate DataFrame
        if self._validate_df(songs_df):
            print("Data is valid")
            print(songs_df)

        '''
        for i, date in enumerate(dates):
            print(f"{i+1}. date: ", date)
        '''

    @staticmethod
    def _validate_df(df: pd.DataFrame) -> bool:
        # check if df is empty
        if df.empty:
            print("No songs found. Finishing execution")
            return False

        # primary key check
        if pd.Series(df["played_at"]).is_unique:
            pass
        else:
            raise Exception("Primary key violated")

        # check for nulls
        if df.isnull().values.any():
            raise Exception("Null value found")

        return True

    def get_last_played_tracks(self):
        # set log level
        logging.basicConfig(level=logging.WARNING)

        # set timeframe
        self._set_timeframe()

        # request url
        url = f"https://api.spotify.com/v1/me/player/recently-played"

        # request params
        params = {"limit": self._limit,
                  "after": self._from_date}
        # "before": self.to_date}

        # get token
        self._refresh_access_token()

        # request headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}"
        }

        # make the request
        logging.info("Downloading list of last played tracks")
        try:
            response = requests.get(url, params=params, headers=headers)

            response.raise_for_status()

            response_json = response.json()

            # dump response_json to spot.json file
            with open('spot.json', 'w') as file:
                json.dump(response_json, file, indent=4)

            self._extract_data(response_json)

        except HTTPError as http_err:
            logging.error(f"Request failed. HTTP error: {http_err} Message: {response.text}")
            return
        except Exception as e:
            logging.error(f"Other Error: {e}", exc_info=True)
            return
        else:
            logging.info(f"Request finished successfully. "
                         f"Status code: {response.status_code} "
                         f"Reason: {response.reason}")