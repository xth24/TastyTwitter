import json


class Data:
    payloads = json.load(open("twitter/data/data.json"))
    config = json.load(open("config.json"))

    def __init__(self):
        # Account Data
        self.email = None
        self.username = None
        self.at_username = None
        self.account_id = None
        self.location = None
        self.description = None
        self.password = None

        # Account state
        self.scraped = False
        self.locked = None  # is a bool
        self.birthday_info = None  # is a dict

        # Account cookies
        self.csrf = None
        self.auth_token = None

        # Requests data
        self.flow_token_payload = self.payloads['flow_token'].copy()
        self.verify_email_code_payload = self.payloads['verify_email'].copy()
        self.bearer = self.payloads['bearer']

        # Config data
        self.solver_key = self.config['solver_key']
        self.captcha_public_key = self.config['captcha_public_key']
        self.captcha_url = self.config['captcha_url']
        self.email_domain = self.config['email_domain']
