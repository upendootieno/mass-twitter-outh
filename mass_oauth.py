# for catching full tracebacks on error
from sys import exc_info

import time

# for automating browsers
from selenium import webdriver

# for setting up proxy
from selenium.webdriver.common.proxy import Proxy, ProxyType

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


# Get random browser
def getBrowser():
    try:
        all_drivers = ['chromedriver', 'geckodriver', 'operadriver']
        selected_driver = all_drivers[random.randrange(0, 1)]  # choose only chromdriver for now

        # Get proxy to make requests from different IP address everytime
        ip_address = '110.74.195.65:8000'
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.autodetect = False
        proxy.http_proxy = proxy.socks_proxy = proxy.ssl_proxy = ip_address

        dir = f'{Path(__file__).resolve().parent}'

        if selected_driver == 'chromedriver':
            options = webdriver.ChromeOptions()
            options.proxy = proxy
            options.add_argument("ignore-certificate-errors")
            driver = webdriver.Chrome(f'{dir}/chromedriver', options=options)
        elif selected_driver == 'geckodriver':
            driver = webdriver.Firefox(f'{dir}/geckodriver')
        else:
            driver = webdriver.Opera(f'{dir}/operadriver')
    except Exception as e:
        driver = None
        print(e)

    return (f"{selected_driver}:{ip_address}", driver)


# Test function
def login(username, password):
    driver = getBrowser()[1]
    driver.get('http://167.99.236.148:1337')
    driver.find_element_by_name('username').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_class_name('login100-form-btn').click()
    driver.save_screenshot("something.png")


def get_redirect_url(auth):
    logger = logging.getLogger(__name__)

    try:
        redirect_url = auth.get_authorization_url()
        return redirect_url
    except tweepy.TweepError as e:
        logger.error(e, exc_info=True)
        return 'error'


def saveResults(results_file, success, username, email, password, followers, created, country, browser, time, access, secret, screenshot, error):
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
            "auth_attempt": {"browser": browser, "time": time},
        }
    else:
        results[username] = {
            "email": email, "password": password,
            "followers": followers, "created": created, "country": country,
            "auth_attempt": {"browser": browser, "time": time},
            "screenshot": screenshot, "error": error
        }

    with open(results_file, 'w') as f:
        f.write(json.dumps(results, indent=4))


def twitterLogin(email, password, username, followers, created, country, two_factor=False):
    try:
        # pick a random browser
        driver_and_browser = getBrowser()
        driver = driver_and_browser[1]
        browser = driver_and_browser[0]
        auth_time = datetime.datetime.now(datetime.timezone.utc)

        # Authenticate to the app
        consumer_token = os.environ.get('CONSUMER_TOKEN')
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        callback_url = 'http://127.0.0.1'  # just a dummy callback url, doesn't really do anything
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret, callback_url)

        # Go to twitter auth page
        url = get_redirect_url(auth)

        driver.get(url)

        time.sleep(3)

        # Input credentials
        driver.find_element_by_name('session[username_or_email]').send_keys(email)
        time.sleep(3)
        driver.find_element_by_name('session[password]').send_keys(password)

        # click on the allow button
        driver.find_element_by_id('allow').click()

        # Get the url parameters returned
        keys_url = driver.current_url
        parsed = urlparse.urlparse(keys_url)
        auth_token = parse_qs(parsed.query)['oauth_token'][0]
        verifier = parse_qs(parsed.query)['oauth_verifier'][0]

        # Get and save the keys
        auth.request_token = {'oauth_token': auth_token, 'oauth_token_secret': verifier}
        keys = auth.get_access_token(verifier)

        saveResults(
            'success.json', True, username, email,
            password, followers, created, country, browser,
            str(auth_time), keys[0], keys[1],
            None, None
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(e, exc_info=True)
        driver.save_screenshot(f'{username}.png')
        saveResults(
            'fail.json', False, username, email,
            password, followers, created, country, browser,
            str(auth_time), None, None,
            f'{username}.png', str(e)
        )


def authenticate_accounts():
    with open('accounts.txt', 'r') as accounts_file:
        accounts = accounts_file.read().split('\n')

    # Read accounts from the right source later
    for account in accounts:
        try:
            attributes = account.split('|')

            credentials = attributes[0].split(': ')[1].split(':')
            email = credentials[0]
            password = credentials[1].replace(' ', '')

            username = attributes[1].split(': ')[1].replace(' ', '')

            followers = attributes[2].split(': ')[1].replace(' ', '')
            created = attributes[3].split(': ')[1].replace(' ', '')
            country = attributes[4].split(': ')[1]
            two_factor = False

            # check whether is 2FA or not
            if len(attributes) > 5:
                # this is 2FA
                two_factor = True

            twitterLogin(email, password, username, followers, created, country, two_factor)

        except Exception as e:
            print(e)


authenticate_accounts()
