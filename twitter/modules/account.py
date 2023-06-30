import json

from .data import Data
from .. import exceptions
from .. import helpers


class Account:
    def __init__(self, session, data: Data) -> None:
        self.data = data
        self.session = session

    def set_profile_picture(self, media_id: str) -> None:
        data = self.session.post(
            f'https://api.twitter.com/1.1/account/update_profile_image.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            data={
                "include_profile_interstitial_type": "1",
                "include_blocking": "1",
                "include_blocked_by": "1",
                "include_followed_by": "1",
                "include_want_retweets": "1",
                "include_mute_edge": "1",
                "include_can_dm": "1",
                "include_can_media_tag": "1",
                "include_ext_has_nft_avatar": "1",
                "include_ext_is_blue_verified": "1",
                "include_ext_verified_type": "1",
                "include_ext_profile_image_shape": "1",
                "skip_status": "1",
                "return_user": True,
                "media_id": media_id,
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")

    def fetch_account_data(self) -> None:
        data = self.session.get(
            f'https://twitter.com/',
            headers=helpers.headers({
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            })
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")

        data = json.loads(data.text.split('window.__INITIAL_STATE__=')[1].split(';')[0])

        key = next(iter(data['entities']['users']['entities'].keys()))
        user_data = data['entities']['users']['entities'][key]

        self.data.at_username = user_data['screen_name']
        self.data.birthday_info = user_data['birthdate']
        self.data.account_id = user_data['id_str']
        self.data.description = user_data['description']
        self.data.location = user_data['location']

    def edit_profile(
            self,
            dob_day: str = None,
            dob_month: str = None,
            dob_year: str = None,
            dob_visibility: str = None,
            dob_year_visibility: str = None,
            username: str = None,
            description: str = None,
            location: str = None,
    ) -> None:
        if not self.data.scraped:
            self.fetch_account_data()

        if not dob_day:
            dob_day = self.data.birthday_info['day']
            dob_month = self.data.birthday_info['month']
            dob_year = self.data.birthday_info['year']

        if not dob_visibility:
            dob_visibility = self.data.birthday_info['visibility']
            dob_year_visibility = self.data.birthday_info['year_visibility']

        if not username:
            username = self.data.username

        if not description:
            description = self.data.description

        if not location:
            location = self.data.location

        data = self.session.post(
            f'https://api.twitter.com/1.1/account/update_profile.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            data={
                "birthdate_day": dob_day,
                "birthdate_month": dob_month,
                "birthdate_year": dob_year,
                "birthdate_visibility": dob_visibility,
                "birthdate_year_visibility": dob_year_visibility,
                "displayNameMaxLength": "50",
                "name": username,
                "description": description,
                "location": location,
            }
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code} ({data.text})")
        if data.json().get("errors"):
            err = data.json()['errors'][0]
            raise exceptions.TwitterHTTPException(f"Server refused request: {err['message']} (/{err['path'][0]})")

    def check_if_locked(self):
        data = self.session.head(
            'https://twitter.com/account/access',
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            }
        )
        if data.status_code == 200:
            self.data.locked = True
            return True
        else:
            self.data.locked = False
            return False
