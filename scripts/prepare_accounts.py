import json
from pathlib import Path

accounts_dir = f'{Path(__file__).resolve().parent.parent}/accounts/'

import os

with open(f'{accounts_dir}accounts.txt', 'r') as accounts_file:
    accounts = accounts_file.read().split('\n')

for account in accounts:
    attributes = account.split('|')

    credentials = attributes[0].split(': ')[1].split(':')
    email = credentials[0]
    password = credentials[1].replace(' ', '')

    username = attributes[1].split(': ')[1].replace(' ', '')

    followers = attributes[2].split(': ')[1].replace(' ', '')
    created = attributes[3].split(': ')[1].replace(' ', '')
    country = attributes[4].split(': ')[1].replace(' ', '')
    two_factor = 0  # False

    # check whether is 2FA or not
    if len(attributes) > 5:
        # this is 2FA
        two_factor = 1  # True

    # load file
    try:
        results = json.load(open(f'{accounts_dir}all_accounts.json', 'r'))
    except Exception:
        results = {}  # initialize to an empty dictionary

    
    results[username] = {
        "email": email, "password": password, "followers": followers,
        "created": created, "country": country, "two_factor": two_factor
    }

    if two_factor:
        results[username]['Challenge'] = attributes[5].split(': ')[1]

    with open(f'{accounts_dir}all_accounts.json', 'w') as f:
        f.write(json.dumps(results, indent=4))
