from sys import exc_info
from selenium import webdriver
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
import datetime
from datetime import timezone


# Get random browser
def getBrowser():
    all_drivers = ['chromedriver', 'geckodriver', 'operadriver']
    selected_driver = all_drivers[random.randrange(0, 1)]  # choose only chromdriver for now

    dir = f'{Path(__file__).resolve().parent}'

    if selected_driver == 'chromedriver':
        driver = webdriver.Chrome(f'{dir}/chromedriver')
    elif selected_driver == 'geckodriver':
        driver = webdriver.Firefox(f'{dir}/geckodriver')
    else:
        driver = webdriver.Opera(f'{dir}/operadriver')

    return (selected_driver, driver)


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


def saveResults(results_file, success, username, browser, time, access, secret, screenshot, error):
    # load file
    try:
        results = json.load(open(results_file, 'r'))

        if success == True:
            {
                "username": username, "browser": browser,
                "tokens": {"access_token": access, "access_secret": secret},
                "time": time
            }
        else:
            {
                "username": username, "browser": browser,
                "time": time, "screenshot": screenshot,
                "error": error
            }

    except Exception:
        results = {}  # initialize to an empty dictionary


def twitterLogin(username, password, two_factor=False):
    try:
        # pick a random browser
        driver_and_browser = getBrowser()
        driver = driver_and_browser[1]
        browser = driver_and_browser[0]
        time = datetime.datetime.now(timezone.utc)

        # Authenticate to the app
        consumer_token = os.environ.get('CONSUMER_TOKEN')
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        callback_url = 'http://127.0.0.1:8000/signup'  # just a dummy callback url, doesn't really do anything
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret, callback_url)

        # Go to twitter auth page
        url = get_redirect_url(auth)
        driver.get(url)

        # Input credentials
        driver.find_element_by_name('session[username_or_email]').send_keys(username)
        driver.find_element_by_name('session[password]').send_keys(password)

        # click on the allow button
        driver.find_element_by_id('allow')

        # Get the url parameters returned
        keys_url = driver.getCurrentUrl()
        parsed = urlparse.urlparse(keys_url)
        auth_token = parse_qs(parsed.query)['oauth_token'][0]
        verifier = parse_qs(parsed.query)['oauth_verifier'][0]

        # Get and save the keys
        auth.request_token = {'oauth_token': auth_token, 'oauth_token_secret': verifier}
        keys = auth.get_access_token(verifier)

        saveResults('success.json', True, username, browser, str(time), keys[0], keys[1], None, None)
    except Exception as e:
        driver.save_screenshot(f'{username}.png')
        saveResults('fail.json', False, username, browser, str(time), None, None, f'{username}.png', e)


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
            two_factor = False

            # check whether is 2FA or not
            if len(attributes) > 5:
                # this is 2FA
                two_factor = True

            # twitterLogin(email, password, two_factor)

        except Exception as e:
            print(e)


# authenticate_accounts()

# Test
# login('email', 'password')
