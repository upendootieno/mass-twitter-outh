## INITIAL CONFIGURATION

### Twitter APP
Create an app with read and write permissions [here](https://developer.twitter.com/en/portal/apps/new).

### AntiCaptcha
To bypass reCAPTCHA V2, we'll need a recaptcha solve service. Create an account with anticaptcha.com and recharge your account.

#### Configurations
1: Take note of your api key.

2: To keep the expenses practical, set your maximum bid to $3 for every 1000 captchas. The codebase has been designed to tolerate lower bid rates by waiting for workers to be idle.

### .config/make_me_feel_famous.json
This file contains the account(s) that the authenticated accounts will engage with ie the accounts that will be followed, get their tweets liked, responded to, retweeted etc. Use this sample to configure the file;


	{
		{
		"username": {
			"initialFollowers: 77"
			"growthInterval": 7,
			"growthRate":  0.01,
		},
	}

In the above example, the user's followers will increase by 1% every 7 days.

### .config/tweets.txt
Store the tweets you want the accounts to publish here. A tweet and an account that publishes it will be selected at random.

### .config/replies.txt
Store the responses to tweets you want your accounts to send.

### Environment Variables
Add environment variables, using ".env.sample" as your guide.


## ACCOUNT GROWTH ALGORITHM

In order to simulate realistic growth, twitter following is not ranomized. Instead, it's guided by a mathematical equation.


### Exponential Growth

f(x) = a(1+r)<sup>x</sup>


Where a is the initial number of followers, r is the percentage in growth expressed as float, and x the growth factor in days. The growth rate will be limited to a very small number, for instance 0.01. In this case, it means that the follower count for the user would increase by 1% every x days.


## UNFOLLOW ALGORITHM

To keep things even more realistic, a calculated number of unfollowers will be implemented.

## all_accounts.json
This file stores all the accounts, with their login credentials.

This file has no default. It will be created by running `prepare_accounts.py`. You can also add the accounts manually to the json file following this format;

    {
		{
		    "username1": {
		        "email": "someemail@email.com",
		        "password": "somepassword",
		        "followers": "17",
		        "created": "2012",
		        "country": "Australia",
		        "two_factor": 0
		    },
		    "username2": {
		        "email": "someemail@email.com",
		        "password": "somepassword",
		        "followers": "0",
		        "created": "2017",
		        "country": "Kenya",
		        "two_factor": 0
		    }
		    .
		    .
		    .
    }

## authenticated_accounts.json
This file has all the accounts whose authentication with the app was completed.

Defaults to empty json.

## failed_accounts.json
This file will store the accounts that failed to authenticate with the app, and therefore cannot be accessed.

Defaults to empty json.


To authenticate accounts, run; `python mass_oauth.py`. This will attempt authentication for accounts defined in `all_accounts.json`, but not present in `authenticated_accounts.json`


You can pass a command line argument to also re-attempt authentication for the accounts that had previously failed;

`python mass_oauth.py retry-failed`
