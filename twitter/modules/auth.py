import json
import random

from .data import Data
from .. import exceptions
from .. import helpers


class Auth:
    def __init__(self, session, data: Data) -> None:
        self.data = data
        self.session = session

        self.guest_token = None
        self.flow_token = None

    def get_guest_token(self) -> None:
        data = None
        for _ in range(2):
            data = self.session.get(
                'https://twitter.com/i/flow/signup',
                headers=helpers.headers()
            )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        self.guest_token = data.text.split('gt=')[1].split(';')[0]

    def get_flow_token(self) -> None:
        data = self.session.post(
            'https://api.twitter.com/1.1/onboarding/task.json?flow_name=signup',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-guest-token": self.guest_token,
                "x-csrf-token": helpers.random_string(8),
                "x-twitter-client-language": "en",
                "x-twitter-active-user": "yes",
            }),
            json=self.data.flow_token_payload
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        self.flow_token = data.json()['flow_token']

    def get_instrumentation(self) -> str:
        data = self.session.get(
            'https://twitter.com/i/js_inst?c_name=ui_metrics',
            headers=helpers.headers({
                "accept": "*/*",
                "Referer": "https://twitter.com/i/flow/signup",
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin"
            })
        )
        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        return data.text

    def get_email_code(self, email: str, username: str) -> None:

        self.data.email = email
        self.data.username = username

        data = self.session.post(
            'https://api.twitter.com/1.1/onboarding/begin_verification.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-guest-token": self.guest_token,
                "x-csrf-token": helpers.random_string(8),
                "x-twitter-client-language": "en",
                "x-twitter-active-user": "yes",
            }),
            json={
                "email": email,
                "display_name": username,
                "flow_token": self.flow_token
            }
        )

        if data.status_code != 204:
            raise exceptions.TwitterHTTPException(f"Expected 204, got {data.status_code} ({data.text})")

    def verify_email_code(self, code: str, captcha_key: str) -> None:
        payload = self.data.verify_email_code_payload
        instrumentation_result = helpers.solve_instrumentation(data=self.get_instrumentation())

        # Flow token
        payload['flow_token'] = self.flow_token

        # Email Part
        payload['subtask_inputs'][4]['email_verification']['code'] = code
        payload['subtask_inputs'][4]['email_verification']['email'] = self.data.email

        # Captcha part
        payload['subtask_inputs'][3]['web_modal'][
            'completion_deeplink'] = f"twitter://onboarding/web_modal/next_link?access_token={captcha_key}"

        # Account information part
        payload['subtask_inputs'][0]['sign_up']['js_instrumentation']['response'] = instrumentation_result
        payload['subtask_inputs'][0]['sign_up']['name'] = self.data.username
        payload['subtask_inputs'][0]['sign_up']['email'] = self.data.email
        payload['subtask_inputs'][0]['sign_up']['birthday']['day'] = random.randint(1, 27)
        payload['subtask_inputs'][0]['sign_up']['birthday']['month'] = random.randint(1, 12)
        payload['subtask_inputs'][0]['sign_up']['birthday']['year'] = random.randint(1990, 2000)

        data = self.session.post(
            'https://api.twitter.com/1.1/onboarding/task.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-guest-token": self.guest_token,
                "x-csrf-token": helpers.random_string(8),
                "x-twitter-client-language": "en",
                "x-twitter-active-user": "yes",
            }),
            json=payload
        )

        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        self.flow_token = data.json()['flow_token']

    def set_password(self, password: str) -> None:
        self.data.password = password

        data = self.session.post(
            'https://api.twitter.com/1.1/onboarding/task.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-guest-token": self.guest_token,
                "x-csrf-token": helpers.random_string(8),
                "x-twitter-client-language": "en",
                "x-twitter-active-user": "yes",
            }),
            json={
                "flow_token": self.flow_token,
                "subtask_inputs": [{"subtask_id": "EnterPassword",
                                    "enter_password": {"password": self.data.password, "link": "next_link"}}]}
        )

        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        self.flow_token = data.json()['flow_token']

        self.data.auth_token = data.cookies.get('auth_token')
        self.data.csrf = data.cookies.get('ct0')

    def end_signup(self):
        data = self.session.post(
            'https://api.twitter.com/1.1/onboarding/task.json',
            headers=helpers.headers({
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.data.bearer,
                "x-csrf-token": self.data.csrf,
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en"
            }),
            json={"flow_token": self.flow_token,
                  "subtask_inputs": [{"subtask_id": "SelectAvatar", "select_avatar": {"link": "skip_link"}}]}
        )

        if data.status_code != 200:
            raise exceptions.TwitterHTTPException(f"Expected 200, got {data.status_code}")

        self.flow_token = data.json()['flow_token']

        self.data.csrf = data.cookies.get('ct0')