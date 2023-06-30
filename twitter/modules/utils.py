from .data import Data
from .. import exceptions
from .. import helpers


class Utils:
    def __init__(self, session, data: Data) -> None:
        self.data = data
        self.session = session

    def get_user_id(self, username: str) -> str:
        data = self.session.get(
            f'https://twitter.com/i/api/graphql/oUZZZ8Oddwxs8Cd3iW3UEA/UserByScreenName?variables=%7B%22screen_name%22%3A%22{username}%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22hidden_profile_likes_enabled%22%3Afalse%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            })
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        data = data.json()['data']['user']['result']
        if not data.get("rest_id"):
            raise exceptions.TwitterInvalidUser(f"Could not fetch ID of {username}")
        return data['rest_id']
