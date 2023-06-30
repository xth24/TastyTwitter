import random
import threading
import time

import colorama

import twitter

amount = int(input("Amount of accounts >> "))
total = 0


def customize_account(session):
    session.set_profile_picture(media_path=twitter.helpers.get_random_pfp())
    session.log(f"Set profile picture")

    session.edit_profile(
        location=twitter.helpers.generate_random_city(),
        description=twitter.helpers.get_random_bio(),
        username=twitter.helpers.get_random_username()
    )
    session.log(f"Edited profile")

    connect_timeline = iter(session.fetch_connect_timeline())
    session.log(f"Fetched Connect Timeline")
    for i in range(random.randint(5, 7)):
        session.follow(user_id=next(connect_timeline))

    topics_picker = iter(session.fetch_topics_picker())
    session.log(f"Fetched Topics Picker")
    for i in range(random.randint(3, 4)):
        session.follow_topic(topic_id=next(topics_picker))

    timeline = session.fetch_timeline()
    timeline_iter = iter(timeline)
    session.log(f"Fetched Tweets Timeline")
    for i in range(6):
        try:
            time.sleep(60)
            tweet_id = next(timeline_iter)['tweet_id']
            session.like_tweet(tweet_id)
            if random.random() > 0.70:
                session.retweet(tweet_id)
                session.log(f"Retweeted {tweet_id}")
            session.log(f"Liked {tweet_id}")
        except Exception as e:
            session.log(f"{colorama.Fore.YELLOW}[Warning] {e}{colorama.Fore.RESET}")

    for i in range(2):
        try:
            session.tweet(random.choice(timeline)['tweet_content'][:185])
            session.log(f"Tweeted [{i + 1}/2]")
            time.sleep(5)
        except Exception as e:
            session.log(f"{colorama.Fore.YELLOW}[Warning] {e}{colorama.Fore.RESET}")


def create_account():
    global amount, total
    session = twitter.Session(debug=True)
    username = twitter.helpers.get_random_username()

    try:
        session.log(f"Creating account")

        session.create_account(username=username)

        customize_account(session)

        total += 1
        session.log(f"Finished thread [{total}/{amount}]")
    except Exception as e:
        session.log(f"{colorama.Fore.RED}[Fatal] {e}{colorama.Fore.RESET}")


for _ in range(amount):
    threading.Thread(target=create_account).start()
    time.sleep(0.05)
