# for automating browser
from selenium import webdriver
from pathlib import Path
import time
from selenium.webdriver.common.keys import Keys
import os
import requests
import json

from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def solveRecaptcha(driver, email):
    # anticaptcha key
    anti_captcha_api_key = os.environ.get('ANTI_CAPTCHA_KEY')

    driver.find_element_by_name('session[username_or_email]').send_keys(email)
    driver.find_element_by_name('session[username_or_email]').send_keys(Keys.RETURN)

    # recaptcha test site
    url = 'https://twitter.com/login/check'
    driver.get(url)

    recaptcha_site_key = '6LfOP30UAAAAAFBC4jbzu890rTdXBXBNHx9eVZEX'

    headers = {
        "Content-Type" : "application/json",
        "Accept" : "application/json"
    }


    # Request captcha solution
    params = {
        "clientKey": anti_captcha_api_key,
        "task": {
            "type" : "RecaptchaV2TaskProxyless",
            "websiteURL" : url,
            "websiteKey" : recaptcha_site_key,
            # "proxyType" : "http",
            # "proxyAddress" : ip.split(':')[0],
            # "proxyPort" : ip.split(':')[1],
            # "userAgent" : driver.execute_script("return navigator.userAgent;"),
        }
    }

    error_id = -1  # if it changes to 0, that means the task ran successfully

    while error_id != 0:
        solution_request = json.loads(requests.post(
            'https://api.anti-captcha.com/createTask',
            headers = headers,
            json = params
        ).text)

        error_id = solution_request['errorId']

        print(solution_request)

        # wait 5 seconds for a worker to solve the CAPTCHA
        # or to get idle workers if bid is low
        time.sleep(5)

    # reset error_id
    error_id = -1

    # Retrieve captcha solution
    params = {
        "clientKey": anti_captcha_api_key,
        "taskId" : solution_request['taskId']
    }

    status = 'processing'
    while status == 'processing':
        solution = json.loads(requests.post(
            'https://api.anti-captcha.com/getTaskResult',
            headers = headers,
            json = params
        ).text)

        status = solution['status']

        print(solution)

        # Wait 3 seconds before retrying
        time.sleep(3)

    # reset status
    status = 'processing'

    # inject solution
    driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % solution['solution']['gRecaptchaResponse'])
    time.sleep(1)

    # # click "I am not a robot"
    # iframe = driver.find_element(By.TAG, '//main[@role="main"]/div/div/iframe')
    # driver.switch_to.frame(iframe)
    # driver.find_element_by_xpath('//div[2]/div[3]/div[1]/div/div/span[@role="checkbox"]').click()

    # driver.switch_to.default_content()

    # # Press verify button
    # iframe = driver.find_element(By.XPATH, '//div[2]/div[4]/iframe')
    # driver.switch_to.frame(iframe)

    time.sleep(1)  # give js time to update document
    driver.execute_script('document.getElementById("recaptcha-token").value = "%s"' % solution['solution']['gRecaptchaResponse'])
    driver.find_element(By.ID, 'recaptcha-verify-button').click()

    # print(driver.execute_script("return grecaptcha.render('example', {'site_key': %s, 'callback': null})" % recaptcha_site_key))
