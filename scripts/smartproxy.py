import os
import requests
import json
import sys

def getAuthenticationToken():
    url = 'https://api.smartproxy.com/v1/auth'
    username = os.environ.get('PROXY_USERNAME')
    password = os.environ.get('PROXY_PASSWORD')

    token = json.loads(requests.post(url, auth=(username, password)).text)

    return token

def getSubscription(headers, user_id):
    url = f"https://api.smartproxy.com/v1/users/{user_id}/subscriptions"

    response = requests.get(url, headers=headers)

    return response.text


def addToWhiteList(ip_string):
    user_id = os.environ.get('PROXY_USER_ID')
    token = os.environ.get('PROXY_TOKEN')

    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {token}"
    }

    # check maximum IPs we can have with the current subscription
    ip_cap = json.loads(getSubscription(headers, user_id))[0]['ip_address_limit']

    ip_list = ip_string.split(' ')

    # if the IPs supplied exceed the cap, throw an error
    if ip_cap < len(ip_list):
        print(f'Your Smartproxy subscription allows a maximum of {ip_cap} IPs. You supplied {len(ip_list)}')
        exit()
    else:
        url = f"https://api.smartproxy.com/v1/users/{user_id}/whitelisted-ips"

        # check the IPs we have already whitelisted
        ips = json.loads(requests.get(url, headers=headers).text)
        x = ip_cap - len(ips)  # x is the number of ips remaining
        if x <= 0:
            if x < 0:
                x= 0  # for display purposes. We can't have -ve ips remaining

            overwrite = input(f'You are trying to whitelist {len(ip_list)} more IP addresses but have {x} spots.\nEnter Y to overwrite existing IPs, any other button to exit\n')

            if overwrite.lower() == 'y':
                # Delete all currently whitelisted IP addresses
                for ip in ips:
                    print(requests.request("DELETE", url + f"/{ip['id']}", headers=headers).text)
            else:
                exit()

        # Whitelist IP addresses
        payload = {"IPAddressList": ip_list}
        headers['Content-Type'] = 'application/json'

        response = requests.post(url, json=payload, headers=headers)

    return json.loads(response.text)

def getRandomIP(country=None):
    token = os.environ.get('PROXY_TOKEN')
    url = "https://api.smartproxy.com/v1/endpoints/type"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {token}"
    }

    ip = json.loads(requests.get("GET", url, headers=headers).text)

    return ip

def main():
    if len(sys.argv) > 2 and sys.argv[1] == 'whitelist':
        print(addToWhiteList(sys.argv[2]))
    elif len(sys.argv) > 1 and sys.argv[1] == 'gettoken':
        print(getAuthenticationToken())
    else:
        print(
        """
        HELP:
        1. Get Authentication token and user id (Requires PROXY_USERNAME and PROXY_PASSWORD env variables)
        python smartproxy.py gettoken

        2. Whitelist IP address (Requires PROXY_USER_ID and PROXY_TOKEN env variables)
        python smartproxy.py whitelist '142.54.168.213 196.202.190.135'
        """
        )

if __name__ == '__main__':
    main()
