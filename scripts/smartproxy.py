import os
import requests
import json

def getAuthenticationToken():
	url = 'https://api.smartproxy.com/v1/auth'
	username = os.environ.get('PROXY_USERNAME')
	password = os.environ.get('PROXY_PASSWORD')

	token = json.loads(requests.get(url, auth=(username, password)).text)

	return token


def addToWhiteList(ip):
	user_id = os.environ.get('PROXY_USER_ID')
	token = os.environ.get('PROXY_TOKEN')
	url = f"https://api.smartproxy.com/v1/users/{user_id}/whitelisted-ips"
	payload = {"IPAddressList": os.environ.get('WHITELISTED_PROXY_IPS').split(' ')}

	headers = {
	    "Accept": "application/json",
	    "Content-Type": "application/json",
	    "Authorization": f"Token {token}"
	}

	response = requests.post(url, json=payload, headers=headers)

	return response.text

def getRandomIP(country=None):
	token = os.environ.get('PROXY_TOKEN')
	url = "https://api.smartproxy.com/v1/endpoints/type"

	headers = {
	    "Accept": "application/json",
	    "Authorization": f"Token {token}"
	}

	ip = json.loads(requests.get("GET", url, headers=headers).text)

	return ip
