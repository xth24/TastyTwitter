import random
import time
from concurrent.futures import ThreadPoolExecutor

import colorama

import twitter
from twitter.helpers import random_string

sessions = []

accounts = open("twitter/data/accounts.txt").read().splitlines()


def create_session(account: str):
    session = twitter.Session(
        account=account
    )

    sessions.append(session)


threadpool = ThreadPoolExecutor(50)

for i in accounts:
    threadpool.submit(create_session, i)

threadpool.shutdown(wait=True)

print("Created sessions")

threadpool = ThreadPoolExecutor(50)
locked = 0
unlocked = 0

def generate_words():
    words = ""
    for i in range(random.randint(2, 8)):
        word = random_string(random.randint(4, 8)) + " "
        words += word
    return words


def actions(i):
    try:
        global locked, unlocked
        if i.check_if_locked():
            print(f"{colorama.Fore.RED}[LOCKED]   > {i.data.email}{colorama.Fore.RESET} [HEAD: 200, true]")
            locked += 1
            exit()
        else:
            print(f"{colorama.Fore.GREEN}[UNLOCKED] > {i.data.email}{colorama.Fore.RESET} [HEAD: 403, null]")
            unlocked += 1
    except Exception as e:
        print(e)


for i in sessions:
    time.sleep(0.02)
    threadpool.submit(actions, i)

threadpool.shutdown(wait=True)

print(f"""
Locked: {locked}
Unlocked: {unlocked}
""")
