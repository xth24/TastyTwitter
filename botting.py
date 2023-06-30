import time
from concurrent.futures import ThreadPoolExecutor

import colorama

import twitter

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

print("Sessions OK")

threadpool = ThreadPoolExecutor(50)


def actions(i):
    try:
        if i.check_if_locked():
            print(f"{colorama.Fore.RED}[LOCKED] > {i.data.email}{colorama.Fore.RESET}")
            exit()
        else:
            print(f"{colorama.Fore.GREEN}[UNLOCKED] > {i.data.email}{colorama.Fore.RESET}")
        i.like_tweet("1673826684779233283")
        print(f"{i.data.email}{colorama.Fore.LIGHTBLUE_EX} Success{colorama.Fore.RESET}")
    except Exception as e:
        print(e)


for i in sessions:
    threadpool.submit(actions, i)

threadpool.shutdown(wait=True)

print("Done!")
