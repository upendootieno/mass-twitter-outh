import tweepy
import json

import os
from pathlib import Path

import random

root_dir = f'{Path(__file__).resolve().parent.parent}/'


# We can authenticate either a specific account or choose a random one
# setting select_random to True will make the function ignore the account arg silently
def authenticate(account=None, select_random=False):
    auth_accounts = json.load(open(f'{root_dir}accounts/authenticated_accounts.json', 'r'))

    if select_random is False and account is not None:
        pass
    elif select_random is True:
        account = random.choice(list(auth_accounts.keys()))
    else:
        print('Specify account or set select_random to True')
        exit()

    tokens = auth_accounts[account]['tokens']

    # Get consumer keys from env
    consumer_token = os.environ.get("CONSUMER_TOKEN")
    consumer_secret = os.environ.get("CONSUMER_SECRET")

    # Get access keys from accounts file
    access_token = tokens['access_token']
    access_token_secret = tokens['access_secret']

    # AUTHENTICATE TWITTER
    try:
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    except tweepy.TweepError as e:
        print(f'Could not authenticate: {e}')
        exit()

    return (account, api)  # Returns (the account's twitter handle, api object)


def follow(account_to_follow, follower):
    # Get authentication keys for the follower
    api = authenticate(follower)[1]

    # follow the account
    try:
        api.create_friendship(account_to_follow)
        print(f'@{follower} followed @{account_to_follow}')
    except Exception as e:
        print(f"Could not follow @{account_to_follow}: {e}")
        exit()

    # update all_accounts.json to mark that the authenticated account is
    # following the account specified
    try:
        accounts_file = f'{root_dir}accounts/all_accounts.json'
        all_accounts = json.load(open(accounts_file, 'r'))
        following = all_accounts[follower].get('following')

        if following is None:
            # create a new list if it doesn't exist
            all_accounts[follower]['following'] = [account_to_follow]
        else:
            # add to existing items
            all_accounts[follower]['following'].append(account_to_follow)

        with open(accounts_file, 'w') as f:
            f.write(json.dumps(all_accounts, indent=4))

    except Exception as e:
        print(f"Failed to update accounts file : {e}")

    return


def addTweet():
    # open the tweets file and put all the tweets in a list
    with open(f'{root_dir}/.config/tweets.txt', 'r') as tweets_file:
        tweets = tweets_file.read().split('\n')

    # select a random tweet from the list
    tweet = random.choice(tweets)

    # authenticate a random account
    api = authenticate(account='TechniCollins')

    # publish the tweet
    api[1].update_status(tweet)

    print(f'@{api[0]} tweeted \'{tweet}\'')
    return


# def likeTweet():
#     create_favorite(id)
#     return


# def retweet():
#     retweet(id)
#     return


# def reply():
#     update_status(status, in_reply_to_status_id)
#     return


# def unfollow():
#     destroy_friendship(screen_name)
#     return


"""
TO DO

1. Randomize number of likes/retweets
3. Comment from a random pool of comments
"""