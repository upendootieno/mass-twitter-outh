# for catching full tracebacks on error
from sys import exc_info

import time

# for automating browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import tweepy
import random
import logging

# for resolving chromdriver path
import os
from pathlib import Path

# for extracting query params
import urllib.parse as urlparse
from urllib.parse import parse_qs

# for saving results into json files
import json

# to record time when auth was attempted
# and to delay data entry
import time
import datetime

# to match urls
import re

# for solving recaptchas
from anticaptcha import solveRecaptcha

# to randomize ip address
from smartproxy import getRandomIP

# to accpet CL arguments
import sys
import argparse

# for multithreading support
import multiprocessing as mp
import threading

# for splitting accounts dictionary for multithreading
from itertools import islice
import math

# Get random browser
def getWebDriver():
    try:
        proxy_ip = 'gate.smartproxy.com'
        proxy_port = '7000'
        proxy = f'{proxy_ip}:{proxy_port}'

        dir = f'{Path(__file__).resolve().parent.parent}'

        webdriver.DesiredCapabilities.CHROME['proxy']={
            "httpProxy":proxy,
            "ftpProxy":proxy,
            "sslProxy":proxy,
            
            "proxyType":"MANUAL",
            
        }

        # Get the correct executable depending on OS
        current_os = sys.platform
        if 'win' in current_os:
            executable_location = f'{dir}/drivers/chromedriver.exe'
        elif 'linux' in current_os:
            executable_location = f'{dir}/drivers/chromedriver'

        # for macOS
        elif 'darwin' in current_os:
            executable_location = f'{dir}/drivers/mac/chromedriver'
        else:
            print('Unsupported Operating System')
            exit()

        driver = webdriver.Chrome(executable_path=f'{dir}/drivers/chromedriver')
    except Exception as e:
        print(e)
        exit()

    return driver


def get_redirect_url(auth):
    logger = logging.getLogger(__name__)

    try:
        redirect_url = auth.get_authorization_url()
        return redirect_url
    except tweepy.TweepError as e:
        logger.error(e, exc_info=True)
        return 'error'


def saveResults(results_file, success, username, email, password, followers, created, country, time, access, secret, screenshot, error, url):
    # load file
    try:
        results = json.load(open(results_file, 'r'))
    except Exception:
        results = {}  # initialize to an empty dictionary

    if success == True:
        results[username] = {
            "email": email, "password": password,
            "tokens": {"access_token": access, "access_secret": secret},
            "followers": followers, "created": created, "country": country,
            "auth_attempt": {"time": time},
        }
    else:
        results[username] = {
            "email": email, "password": password,
            "followers": followers, "created": created, "country": country,
            "auth_attempt": {"time": time},
            "screenshot": screenshot, "error": error, "url": url
        }

    with open(results_file, 'w') as f:
        f.write(json.dumps(results, indent=4))


def getTokensOrHandleRedirects(driver, username, email, username_login, auth):
    # Get the current url to know status
    url = driver.current_url

    # reCAPTCHA required
    if re.match('https://twitter.com/login/check', url) is not None:
        solveRecaptcha(driver, email)
    # email or phone number confirmation required
    elif re.match('https://twitter.com/account/login_challenge', url) is not None:
        if username_login:
            challenge_response = email
        else:
            challenge_response = username

        if re.search('challenge_type=RetypePhoneNumber', url) is not None:
            # we can't take care of this for now, so just pass
            pass
        else:
            driver.find_element_by_name('challenge_response').send_keys(challenge_response)
            driver.find_element_by_id('email_challenge_submit').click()
            time.sleep(2)
            # The function will call itself to check status again.
            getTokensOrHandleRedirects(driver, username, email, username_login, auth)
    elif re.match('https://twitter.com/home', url) is not None:
        # at this point we are logged in, so just get tokens
        driver.get(get_redirect_url(auth))
        getTokensOrHandleRedirects(driver, username, email, username_login, auth)

    # if we've been redirected back to auth page
    elif re.match('https://api.twitter.com/oauth/authorize', url):
        driver.find_element_by_id('allow').click()
    else:
        pass

    # check url again
    time.sleep(2)
    url = driver.current_url

    if re.match('http://127.0.0.1', url) is not None:
        parsed = urlparse.urlparse(url)
        auth_token = parse_qs(parsed.query)['oauth_token'][0]
        verifier = parse_qs(parsed.query)['oauth_verifier'][0]

    return (auth_token, verifier)


def twitterLogin(email, password, username, followers, created, country, username_login, two_factor=False):
    accounts_dir = f'{Path(__file__).resolve().parent.parent}/accounts/'

    try:
        # configure browser
        driver = getWebDriver()

        auth_time = datetime.datetime.now(datetime.timezone.utc)

        # Authenticate to the app
        consumer_token = os.environ.get('CONSUMER_TOKEN')
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        callback_url = 'http://127.0.0.1'  # just a dummy callback url, doesn't really do anything
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret, callback_url)

        # Go to twitter auth page
        url = get_redirect_url(auth)

        driver.get(url)

        # Input credentials according to the specified login type
        if username_login:
            username_or_email = username
        else:
            username_or_email = email

        driver.find_element_by_name('session[username_or_email]').send_keys(username_or_email)
        driver.find_element_by_name('session[password]').send_keys(password)

        # click on the allow button
        driver.find_element_by_id('allow').click()

        tokens = getTokensOrHandleRedirects(driver, username, email, username_login, auth)

        # Get and save the keys
        auth.request_token = {'oauth_token': tokens[0], 'oauth_token_secret': tokens[1]}
        keys = auth.get_access_token(tokens[1])

        saveResults(
            f'{accounts_dir}authenticated_accounts.json', True, username, email,
            password, followers, created, country,
            str(auth_time), keys[0], keys[1],
            None, None, None
        )
        driver.quit()
    except Exception as e:
        screenshots_dir = f'{Path(__file__).resolve().parent.parent}/screenshots/'
        logger = logging.getLogger(__name__)
        logger.error(e, exc_info=True)
        driver.save_screenshot(f'{screenshots_dir}{username}.png')
        saveResults(
            f'{accounts_dir}failed_accounts.json', False, username, email,
            password, followers, created, country,
            str(auth_time), None, None,
            f'{screenshots_dir}{username}.png', str(e), driver.current_url
        )
        driver.quit()


def authenticate_accounts(accounts_list, username_login):
    for account in accounts_list:
        try:
            email = accounts_list[account]['email']
            password = accounts_list[account]['password']

            followers = accounts_list[account]['followers']
            created = accounts_list[account]['created']
            country = accounts_list[account]['country']
            two_factor = accounts_list[account]['two_factor']

            print(f'@{account}')

            twitterLogin(email, password, account, followers, created, country, username_login, two_factor)

        except Exception as e:
            print(e)


def splitDicitonary(dictionary, size):
    it = iter(dictionary)
    for i in range(0, len(dictionary), size):
        # each yield is a dictionary
        yield {k:dictionary[k] for k in islice(it, size)}


def main():
    # Get command line arguments to determine whether to retry and/or
    # to log in by username instead of email
    parser = argparse.ArgumentParser(description='Get runtime options')

    parser.add_argument('--retry-failed', action='store_true',
                        help='If supplied, the script will retry failed authentications')
    parser.add_argument('--username-login', action='store_true',
                        help='If supplied, login will be username-based instead of email')

    args = parser.parse_args()
    retry_failed = args.retry_failed
    username_login = args.username_login

    accounts_dir = f'{Path(__file__).resolve().parent.parent}/accounts/'

    try:
        all_accounts = json.load(open(f'{accounts_dir}all_accounts.json', 'r'))
        authenticated = list(json.load(open(f'{accounts_dir}authenticated_accounts.json', 'r')).keys())
        failed = list(json.load(open(f'{accounts_dir}failed_accounts.json', 'r')).keys())
    except Exception as e:
        print(f"There was a problem opening an accounts file: {e}")
        exit()

    if retry_failed:
        exclude = authenticated
    else:
        exclude = authenticated + failed

    for key in exclude:
        all_accounts.pop(key)

    print(f'Retrieved {len(all_accounts)} accounts. Attempting authentication')


    # to keep track of how long it takes to auth all accounts
    start_time = time.time()

    # authenticate_accounts(all_accounts, username_login)

    # create a list of threads
    threads = []

    # split the dicitonary into smaller dictionaries for parallel processing
    # the number of dictionaries (and threads) will depend on number of CPUs
    # or the env variable THREADS if provided
    max_threads = int(os.environ.get('THREADS'))
    if max_threads is None:
        max_threads = mp.cpu_count()

    chunk_size = math.floor(len(all_accounts) / max_threads)
    if chunk_size == 0:
        chunk_size = 1  # Each dictionary will be assigned a thread. This is unrealistic, so define a reasonable number of threads

    for chunk in splitDicitonary(all_accounts, chunk_size):
        # create a thread for each accounts dictionary
        threads.append(threading.Thread(target=authenticate_accounts, args=(chunk, username_login)))

    # start all threads
    for thread in threads:
        thread.start()

    # wait for all threads to finish processing
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time

    print(f"Done in {total_time} seconds")


if __name__ == '__main__':
    main()
