"""
This will run every 10 minutes
*/10 * * * * python schedule_engagement.py
"""

# for resolving file path
from pathlib import Path

import json

# for assigning cron job dates and number of likes and retweets
import random

# for getting environment variables
import os

# for checking twitter activity
import tweepy

# to assign engagment time
import datetime

# to create cron jobs
import cronjob


def getRandomAccounts(number):
    try:
        root_dir = f'{Path(__file__).resolve().parent.parent}/'
        accounts_list = json.load(open(f'{root_dir}accounts/authenticated_accounts.json', 'r'))
    except Exception as e:
        print(f"Could not open accounts file: {e}")
        exit()

    if number >= len(accounts_list):
        # add everything to our list if we don't have enough
        accounts = [k for k in accounts_list]
    else:
        # if we have enough, get ranom
        accounts = random.sample(list(accounts_list), k=number)

    return accounts


def main():
    # authenticate our twitter app
    consumer_token = os.environ.get('CONSUMER_TOKEN')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # Open the files we need and load data into dictionaries
    try:
        root_dir = f'{Path(__file__).resolve().parent.parent}/'

        # the account whose tweets we want to engage with
        accounts = json.load(open(f'{root_dir}.config/make_me_feel_famous.json', 'r'))
        # the last tweets that each account in make_me_feel famous.json published
        last_tweets = json.load(open(f'{root_dir}.config/last_tweets.json', 'r'))
    except Exception as e:
        # if any of the files fail to load, 
        # we can't proceed
        print(f"Could not load file: {e}")
        exit()

    for account in accounts:
        # check if a record exists in last_tweets for this account
        # if no record exists, since id will be None, which is still ok
        since_id = last_tweets.get(account)

        # check twitter for any new tweets by this account
        timeline = api.user_timeline(screen_name=account, since_id=since_id)

        if not timeline:
            pass  # don't do anything else
        else:
            # if there are multiple tweets (very unlikely) we will get the latest only            
            last_tweet = timeline[0].id_str

            # Assign a random number of likes and
            # get list of accounts that will like the tweet
            likers = getRandomAccounts(random.randrange(1, 13))  # 1000

            # Assign a random number of retweets and
            # get list of accounts that will retweet
            retweeters = getRandomAccounts(random.randrange(1, 21))  # 1000

            """
            Likes are usually more common than retweets, so
            if retweets are higher, interchange values
            """
            if len(likers) < len(retweeters):
                # temporary variable to hold likers
                temp = likers

                likers = retweeters
                retweeters = temp

            # create cron jobs for engagement
            for liker in likers:
                like_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=random.randrange(0, (5*24*60))  # random date and time within 5 days
                )

                command = f'python /home/mass-twitter-outh/scripts/engagement.py --like-tweet {last_tweet} {liker}'

                comment = f'like_{last_tweet}_{liker}'  # cron job identified by concatnating "like", tweet id and the liker

                cronjob.createCronJob(command, like_time, comment)

            print(f"{len(likers)} likes will be added to {last_tweet} in 5 days")

            for retweeter in retweeters:
                retweet_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=random.randrange(0, (5*24*60))  # random date and time within 5 days
                )

                command = f'python /home/mass-twitter-outh/scripts/engagement.py --retweet {last_tweet} {retweeter}'

                comment = f'retweet_{last_tweet}_{retweeter}'  # cron job identified by concatnating "retweet", tweet id and the retweeter

                cronjob.createCronJob(command, like_time, comment)

            print(f"{last_tweet} will be retweeted {len(retweeters)} times in 5 days")

            # update last_tweets.json
            last_tweets[account] = last_tweet

            with open(f'{root_dir}/.config/last_tweets.json', 'w') as f:
                f.write(json.dumps(last_tweets, indent=4))
    
    return

if __name__ == '__main__':
    main()
