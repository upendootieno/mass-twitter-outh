"""
This will be run as a CRON job.
"""

import os
import tweepy

# for getting accounts
import json

# for resolving file path
from pathlib import Path

# to help with 
import math

# for selection of followers
import random

# for selecting random dates
import datetime


def scheduleFollowing():
    # Get the accounts for which we want to add followers
    root_dir = f'{Path(__file__).resolve().parent.parent}/'
    file = f'{root_dir}.config/make_me_feel_famous.json'

    try:
        accounts = json.load(open(file, 'r'))
    except Exception as e:
        print(f"Could not open configration file: {e}")
        exit()  # we can't proceed without the accounts

    for account in accounts:
        try:
            x = accounts[account]['totalIntervals']
        except:
            x = 0

        x += 1  # increment total intervals

        r = accounts[account]['growthRate']

        a = accounts[account]['initialFollowers']

        y = a*((1+r)**x)

        """

        y is the new number of followers
        a is the current number of followers
        r is the growth rate, expreseed as a float
        x is the number of day intervals
        g is the growth interval in days

        """

        g = accounts[account]['growthInterval']


        # make API call to check the current number of users
        consumer_token = os.environ.get('CONSUMER_TOKEN')
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        current_followers = api.get_user(screen_name=account).followers_count

        d = math.ceil(y - current_followers)
        # d is the deficit (The number of followers we need to add to reach the new number).

        if d <= 0:
            # If for some reason the desired number of followers
            # has been reached, don't do anything
            pass
        else:
            potential_followers = []

            try:
                accounts_list = json.load(open(f'{root_dir}accounts/authenticated_accounts.json', 'r'))
            except Exception as e:
                print(f"Could not open accounts file: {e}")
                exit()

            for b in accounts_list:
                try:
                    # get the accounts this user is already following
                    # that are in the config file
                    already_following = accounts_list[b]['following']
                except:
                    # if this attribute doesn't exist yet, assign empty list
                    already_following = []

                if account in already_following:
                    pass
                else:
                    potential_followers.append(b)

            # select d random accounts from our accounts list and schedule them to follow
            # the specified user
            if d > len(potential_followers):
                # we don't have enough accounts to add the desired
                # number of followers, so let's use up all the remaining accounts
                d = len(potential_followers)
                followers = potential_followers
            else:
                followers = random.sample(potential_followers, k=d)

            schedules = json.load(open(f'{root_dir}.config/schedule.json', 'r'))

            for follower in followers:
                # use get() to access the dictionary's value, so that if it doesn't exist,
                # it defaults to None
                s = schedules.get(account)
                if s is None:
                    # first set the key
                    schedules[account] = {}

                if accounts.get(account).get('lastUpdate') is None:
                    # Then set the value
                    schedules[account][follower] = (datetime.datetime.now() + datetime.timedelta(
                            minutes=random.randrange(0, g*24*60)  # random date and time within g days
                    )).strftime('%d-%m-%Y %H:%M')

                else:
                    schedules[account][follower] =  (datetime.datetime.strptime(
                        accounts[account]['lastUpdate'], '%d-%m-%Y %H:%M') + datetime.timedelta(
                            minutes=random.randrange(0, g*24*60)
                    )).strftime('%d-%m-%Y %H:%M')

            # save schedule to json
            with open(f'{root_dir}.config/schedule.json', 'w') as sched:
                sched.write(json.dumps(schedules, indent=4))


            print(f"{d} followers will be added for @{account} in the next {g} days")

        accounts[account]['totalIntervals'] = x

        with open(file, 'w') as f:
            f.write(json.dumps(accounts, indent=4))

    return

scheduleFollowing()
