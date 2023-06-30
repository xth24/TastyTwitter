import ctypes
import hashlib
import os
import random
import re
import string
import time
from pathlib import Path
from urllib.parse import quote_plus

import kopeechka
import requests

from . import exceptions

# Globals
_LIBRARY = ctypes.CDLL("twitter/libraries/library.so")
_KOPEECHKA = kopeechka.MailActivations(token="146649b83ecbca8a2c0d2016db90bde7")
_PROXIES = open("proxies.txt", errors="ignore").read().splitlines()
_BIOS = open("twitter/data/bio.txt", encoding="UTF-8").read().splitlines()
_USERNAMES = open("twitter/data/usernames.txt", encoding="UTF-8").read().splitlines()
_COOL_EMOJIS = "😀😁😂🤣😃😅😆😗🥰😘😍😎😋😊😉😙😚☺🙂🤗🤩🤔🤨😮😥😣😏🙄😶😑😐🤐😯😪😫🥱😴😌😛🙃😕😔😓😒🤤😝😜🤑😲☹😖🙁😞😟😤😬🤯😩😨😧😦😭😢😰😱🥵🥶😳🤪😵🥴🤮🤢🤕🤒😷🤬😡😠🤧😇🧐🤭🤓🥳🥺😈👿🤠👹👺🤥💀🤫"


class Email:
    def __init__(self):
        self.email = None

        self._get_email()

    def _get_email(self):
        self.email = requests.get('http://46.30.189.19:8080/generate/plus?length=6').json()['email']

    def get_code(self):
        retries = 0
        while retries < 15:
            try:
                data = requests.get(f'http://46.30.189.19:8080/get?mail={quote_plus(self.email)}').json()
                while data['pending']:
                    time.sleep(1)
                    data = requests.get(f'http://46.30.189.19:8080/get?mail={quote_plus(self.email)}').json()
                return re.findall(r'\b\d{6}\b', data['body'])[-1]
            except Exception:
                retries += 1
                time.sleep(2)
        raise exceptions.EmailTimeoutException("Couldn't get the code after 15 retries")


class KopeechkaEmail:
    def __init__(self, domain: str = "outlook.com"):
        self.domain = domain
        self.email_data = None
        self.tracking_link = None

        self._get_mail()

    def _get_mail(self):
        self.email_data = _KOPEECHKA.mailbox_get_email(site="twitter.com", mail_type=self.domain)

    def _get_letter(self) -> kopeechka.types_kopeechka.mailboxGetMessage:
        try:
            letter = _KOPEECHKA.mailbox_get_message(full=1, id=self.email_data.id)
        except kopeechka.errors.WAIT_LINK:
            letter = False
        return letter

    def get_code(self):
        retries = 0
        letter = None

        while retries <= 30:
            letter = self._get_letter()
            if letter:
                break
            retries += 1
            time.sleep(2)

        if not letter:
            raise kopeechka.errors.WAIT_LINK("Could not find code")

        self.tracking_link = letter.fullmessage.split('height="1" src="')[1].split('"')[0]

        return letter.value

    def request_tracking_link(self):
        requests.get(self.tracking_link)


class FunCaptchaTask:
    def __init__(self, public_key: str, url: str, api_key: str) -> None:
        self._public_key = public_key
        self._api_key = api_key
        self._url = url

        self._task_id = None
        self._create_task()

        self.captcha_token = self._join_result()

    def _create_task(self):
        data = requests.get(
            f'https://api.nonecaptcha.com/funcaptchatokentask?apikey={self._api_key}&sitekey={self._public_key}&siteurl={self._url}')
        body = data.json()
        if body['Code'] != 0:
            raise exceptions.FunCaptchaException(f"Failed to create task, message: {body['Message']}")
        self._task_id = data.json()['TaskId']

    def _join_result(self):
        url = f'https://api.nonecaptcha.com/getresult?apikey={self._api_key}&taskid={self._task_id}'
        data = requests.get(url)
        while data.json()['Status'] in ("PENDING", "PROCESSING"):
            time.sleep(0.25)
            data = requests.get(url)
        if data.json()['Code'] != 0:
            raise exceptions.FunCaptchaException(f"Failed to create task, message: {data.json()['Message']}")
        return data.json()['Data']['Token']


def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def solve_instrumentation(data: str) -> str:
    _LIBRARY.parseScript.argtypes = [ctypes.c_char_p]
    _LIBRARY.parseScript.restype = ctypes.c_char_p

    data = data.encode("utf-8")
    response = _LIBRARY.parseScript(data)

    return response.decode()


def get_proxy() -> str:
    return random.choice(_PROXIES).replace('sessionid', random_string(8))


def headers(custom: dict = None) -> dict:
    var = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://twitter.com/",
        "Origin": "https://twitter.com",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

    # var = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Referer": "https://twitter.com/",
    #     "Origin": "https://twitter.com",
    #     "Connection": "keep-alive",
    #     "Sec-Ch-Ua-Platform": "\"Windows\"",
    #     "Sec-Ch-Ua-Mobile": "?0",
    #     "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    #     "Sec-Fetch-Dest": "empty",
    #     "Sec-Fetch-Mode": "cors",
    #     "Sec-Fetch-Site": "same-origin",
    #     "Sec-Fetch-User": "?1"
    # }

    if custom:
        for i in custom:
            var[i] = custom[i]

    return var


def generate_sentence() -> str:
    return requests.get('http://metaphorpsum.com/paragraphs/1').text.split('.')[0]


def get_file_size(path: str) -> int:
    return Path(path).stat().st_size


def file_as_bytes(file):
    with file:
        return file.read()


def get_file_checksum(path: str) -> str:
    return hashlib.md5(file_as_bytes(open(path, 'rb'))).hexdigest()


def generate_random_city() -> str:
    return requests.get('https://api.3geonames.org/?randomland=yes').text.split('<city>')[1].split('<')[0]


def get_random_bio() -> str:
    bio = random.choice(_BIOS)
    bio = "".join(ch for ch in bio if ch.isalnum())
    return bio


def get_random_username() -> str:
    username = random.choice(_USERNAMES)
    username = "".join(ch for ch in username if ch.isalnum())
    return username


def get_random_pfp() -> str:
    return "twitter/data/images/" + random.choice(os.listdir('twitter/data/images/'))


def get_random_emojis(length: int) -> str:
    return ''.join(random.choice(_COOL_EMOJIS) for _ in range(length))
