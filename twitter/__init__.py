import random
from datetime import datetime

import colorama
import tls_client as requests

from . import exceptions
from . import helpers
from .modules.account import Account
from .modules.actions import Actions
from .modules.auth import Auth
from .modules.data import Data
from .modules.utils import Utils


class _Twitter:
    """
    Private class to manage modules
    """

    def __init__(self, account: str = None) -> None:
        self.proxy = helpers.get_proxy()
        _session = requests.Session(client_identifier="chrome_110", random_tls_extension_order=True)
        _session.proxies = {
            "http": f"http://{self.proxy}",
            "https": f"http://{self.proxy}"
        }
        self.data = Data()
        self._account = Account(_session, self.data)
        self._actions = Actions(_session, self.data)
        self._auth = Auth(_session, self.data)
        self._utils = Utils(_session, self.data)

        if account:
            self._parse_account(account)
            _session.cookies.set(name="auth_token", path="/", domain=".twitter.com", value=self.data.auth_token)
            _session.cookies.set(name="ct0", path="/", domain=".twitter.com", value=self.data.csrf)

    def _parse_account(self, account: str) -> None:
        parts = account.split(':')

        self.data.email = parts[0]
        self.data.password = parts[1]
        self.data.auth_token = parts[2]
        self.data.csrf = parts[3]


class Session(_Twitter):
    """
    Main class of the wrapper, extends _Twitter class
    """

    def __init__(self, account: str = None, debug: bool = False) -> None:
        self._session_id = random.randint(1000, 9999)
        self._debug = debug

        super().__init__(account)

        self.log(f"Using proxy {self.proxy}")

    def log(self, content: str) -> None:
        """
        Log using Session
        """
        if self._debug:
            print(
                f'(thread-{self._session_id}) {colorama.Fore.LIGHTYELLOW_EX}(Debug) - {datetime.now().strftime("%H:%M:%S")} {colorama.Fore.RESET}{content}')

    def create_account(
            self,
            username: str = None,
            password: str = None,
            save: bool = True
    ) -> None:
        """
        :param username: Account username
        :param password: Account password
        :param save: Save account information in file
        """

        if not password:
            password = helpers.random_string(16)  # Generate random password if not given
        if not username:
            username = helpers.random_string(16)  # Generate random username if not given

        email = helpers.Email()  # We get an email by creating Email object

        self._auth.get_guest_token()  # Get guest token
        self._auth.get_flow_token()  # Get flow token
        self.log(f"Verifying email")
        self._auth.get_email_code(  # Start signup by verifying email
            email=email.email,
            username=username
        )
        code = email.get_code()  # Wait for code
        self.log(f"Received code {code}")
        captcha_key = helpers.FunCaptchaTask(  # Solve captcha and get captcha token
            api_key=self.data.solver_key,
            public_key=self.data.captcha_public_key,
            url=self.data.captcha_url
        ).captcha_token
        self.log(f"Solved Captcha {captcha_key.split('|')[0]}")
        self._auth.verify_email_code(code=code, captcha_key=captcha_key)  # Verify code
        self.log(f"Verified email")
        self._auth.set_password(password=password)  # Set account password
        self._auth.end_signup()  # Skip end signup steps

        self._account.fetch_account_data()

        if save:
            with open("twitter/data/accounts.txt", "a+") as f:
                f.write(f"{self.data.email}:{self.data.password}:{self.data.auth_token}:{self.data.csrf}\n")

    def like_tweet(self, tweet_id: str) -> None:
        """
        Method to like a specific tweet,
        :param tweet_id: tweet ID to like
        """

        return self._actions.like_tweet(tweet_id=tweet_id)

    def retweet(self, tweet_id: str) -> None:
        """
        Retweet a specific tweet,
        :param tweet_id: tweet ID to like
        """

        return self._actions.retweet(tweet_id=tweet_id)

    def tweet(self, content: str, reply_tweet_id: str = None) -> None:
        """
        Tweet a message,
        :param content: Tweet content
        :param reply_tweet_id: Reply to tweet id
        """

        return self._actions.tweet(content=content, reply_tweet_id=reply_tweet_id)

    def follow(self, user_id: str = None, username: str = None) -> None:
        """
        Follow a user,
        :param user_id: User ID
        :param username: Username
        """

        if user_id is None and username is None:
            raise exceptions.MissingArguments()

        if username:
            user_id = self._utils.get_user_id(username=username)

        return self._actions.follow(user_id=user_id)

    def unfollow(self, user_id: str, username: str = None) -> None:
        """
        Stop following someone,
        :param user_id: User ID
        :param username: Username
        """

        if user_id is None and username is None:
            raise exceptions.MissingArguments()

        if username:
            user_id = self._utils.get_user_id(username=username)

        return self._actions.unfollow(user_id=user_id)

    def upload_media(self, media_path: str) -> str:
        """
        Upload media
        :param media_path: Path to the JPEG file
        :returns string: Media ID
        """

        return self._actions.upload_media(media_path=media_path, proxy=self.proxy)

    def fetch_timeline(self) -> list:
        """
        Fetch timeline
        :returns list: Tweet IDs
        """

        return self._actions.fetch_timeline()

    def fetch_connect_timeline(self) -> list:
        """
        Fetch connect timeline
        returns list: Tweet IDs
        """

        return self._actions.fetch_connect_timeline()

    def fetch_topics_picker(self) -> list:
        """
        Fetch topics picker
        returns list: Tweet IDs
        """

        return self._actions.fetch_topics_picker()

    def set_profile_picture(self, media_id: str = None, media_path: str = None) -> None:
        """
        Set a profile picture
        :param media_path: Path to the JPEG file
        :param media_id: Media ID to set as profile picture
        """

        if media_id is None and media_path is None:
            raise exceptions.MissingArguments()

        if not media_id:
            media_id = self.upload_media(media_path=media_path)

        return self._account.set_profile_picture(media_id=media_id)

    def follow_topic(self, topic_id: str) -> None:
        """
        Follow a topic,
        :param topic_id: User ID
        """

        return self._actions.follow_topic(topic_id=topic_id)

    def check_if_locked(self) -> bool:
        """
        :returns a bool: True if locked, False if unlocked
        """

        return self._account.check_if_locked()

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
        """
        Edit profile information
        :param dob_day: DOB day
        :param dob_month: DOB month
        :param dob_year: DOB year
        :param dob_visibility: DOB visibility for public
        :param dob_year_visibility: DOB year visibility for public
        :param username: Screen name (aka username)
        :param description: Profile description
        :param location: Profile location
        """

        return self._account.edit_profile(
            dob_day=dob_day,
            dob_month=dob_month,
            dob_year=dob_year,
            dob_visibility=dob_visibility,
            dob_year_visibility=dob_year_visibility,
            username=username,
            description=description,
            location=location
        )
