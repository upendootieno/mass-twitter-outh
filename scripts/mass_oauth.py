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

# to randomize user agent
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

# for solving recaptchas
from anticaptcha import solveRecaptcha

# to randomize ip address
from smartproxy import getRandomIP


# Get random browser
def getWebDriver():
    try:
        proxy_ip = 'gate.smartproxy.com'
        proxy_port = '7000'
        proxy = f'{proxy_ip}:{proxy_port}'

        dir = f'{Path(__file__).resolve().parent.parent}'

        options = Options()
        ua = UserAgent()
        userAgent = ua.random
        print(userAgent)
        options.add_argument(f'user-agent={userAgent}')

        webdriver.DesiredCapabilities.CHROME['proxy']={
            "httpProxy":proxy,
            "ftpProxy":proxy,
            "sslProxy":proxy,
            
            "proxyType":"MANUAL",
            
        }
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


def getTokensOrHandleRedirects(driver):
    # Get the current url to know status
    url = driver.current_url

    # reCAPTCHA required
    if re.match('https://twitter.com/login/check', url) is not None:
        solveRecaptcha(driver, email)
    elif re.match('https://twitter.com/account/login_challenge', url) is not None:
        challenge_response = username

        if re.search('challenge_type=RetypePhoneNumber', url) is not None:
            # try to change challenge type to screen name
            # driver.navigate().to(re.sub('challenge_type=RetypePhoneNumber', 'challenge_type=RetypeScreenName', url))
            driver.execute_script('document.getElementsByName("challenge_type")[0].value = "RetypeScreenName"')

        driver.find_element_by_name('challenge_response').send_keys(challenge_response)
        driver.find_element_by_id('email_challenge_submit').click()
        time.sleep(3)
        driver.find_element_by_id('allow').click()
    else:
        pass

    # check url again
    url = driver.current_url

    if re.match('http://127.0.0.1', url) is not None:
        parsed = urlparse.urlparse(url)
        auth_token = parse_qs(parsed.query)['oauth_token'][0]
        verifier = parse_qs(parsed.query)['oauth_verifier'][0]

    return (auth_token, verifier)


def twitterLogin(email, password, username, followers, created, country, two_factor=False):
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

        time.sleep(3)

        # Input credentials
        driver.find_element_by_name('session[username_or_email]').send_keys(email)
        time.sleep(3)
        driver.find_element_by_name('session[password]').send_keys(password)

        # click on the allow button
        driver.find_element_by_id('allow').click()

        tokens = getTokensOrHandleRedirects(driver)

        # Get and save the keys
        auth.request_token = {'oauth_token': tokens[0], 'oauth_token_secret': tokens[1]}
        keys = auth.get_access_token(tokens[1])

        saveResults(
            'success.json', True, username, email,
            password, followers, created, country,
            str(auth_time), keys[0], keys[1],
            None, None, None
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(e, exc_info=True)
        driver.save_screenshot(f'{username}.png')
        saveResults(
            'fail.json', False, username, email,
            password, followers, created, country,
            str(auth_time), None, None,
            f'{username}.png', str(e), url
        )
        time.sleep(3600)


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
