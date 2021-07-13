# INITIAL CONFIGURATION

## Location
When setting up the app on a server, the project root dir **MUST** be located in `/home`. Cron jobs will attempt to look for files from that dir.

## Cron job
Add this cron job

    `*/10 * * * * python /home/mass-twitter-outh/scripts/schedule_engagement.py`

## Twitter APP
Create an app with read and write permissions [here](https://developer.twitter.com/en/portal/apps/new).

## AntiCaptcha
To bypass reCAPTCHA V2, we'll need a recaptcha solve service. Create an account with anticaptcha.com and recharge your account.

### Configurations
1: Take note of your api key.


2: To keep the expenses practical, set your maximum bid to $3 for every 1000 captchas. The codebase has been designed to tolerate lower bid rates by waiting for workers to be idle.

## SmartProxy

1: Get authentication token and user id by running the command below.

    python smartproxy.py gettoken

This requires the presence of the 'PROXY_USERNAME' and 'PROXY_PASSWORD' env variables.
Store the results in the 'PROXY_USER_ID' and 'PROXY_TOKEN' env variables.


2: Whitelist your IP address by running the command below, replacing the sample IP address with yours. You may have to overwrite existing IP addresses if you have reached your cap.

    python smartproxy.py whitelist '192.168.0.1'

## .config/make_me_feel_famous.json
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

After editing the file, you will need to run this command to set up a growth scheduler for the account.

    python schedule_following.py --setup-scheduler

The command will set up a cron job for each account in the file, that will run every `growthInterval` days. If some accounts already have cron jobs, they will be overwritten.

## .config/tweets.txt
Store the tweets you want the accounts to publish here. A tweet and an account that publishes it will be selected at random.

## .config/comments.txt
Store the responses to tweets you want your accounts to send.

## Environment Variables
Add environment variables, using ".env.sample" as your guide.


# ACCOUNT GROWTH ALGORITHM

In order to simulate realistic growth, twitter following is not ranomized. Instead, it's guided by a mathematical equation.


## Exponential Growth

f(x) = a(1+r)<sup>x</sup>


Where a is the initial number of followers, r is the percentage in growth expressed as float, and x the growth factor in days. The growth rate will be limited to a very small number, for instance 0.01. In this case, it means that the follower count for the user would increase by 1% every x days.


# UNFOLLOW ALGORITHM

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


By default, the script attempts to log in with email. If you want to switch to username login, run;

`python mass_oauth.py --username-login`


You can pass a command line argument to also re-attempt authentication for the accounts that had previously failed;

`python mass_oauth.py --retry-failed`


# ENGAGEMENT ALGORITHM
A cron job will run every 10 minutes to check for new activity. The `last_tweets.json` file stores the last tweets sent by each user in the 'make_me_feel_famous.json' file.

**Note:** We could use the streaming API to monitor activity in realtime. However, it's not the best approach in this use case for many reasons that won't be discussed in this README.

If there's a new tweet, it is assigned a random number of likes and retweets, between 1 and 1000. Random accounts are then selected and cron jobs added for them to like and retweet the tweet for the next 5 days.

**Note:** A better algorithm will be written to calculate metrics and engage with tweets, according to the following the specified account has.


# TECHNICAL DOCS

## Job Scheduling
All scripts that need to be run at specific times are run from cron jobs.

The format for each cronjob is `cron-job # comment`. For example, this cron job is for following an account;

    python scripts/engagement.py --follow-account cl1973 TaraHer77162822 # cl1973_TaraHer77162822


After running the scheduled tasks, the cron job is deleted.


# TROUBLESHOOTING

1: "This version of ChromDriver only supports chrome version xx"

You need to download a chromedriver version that matches your chrome browser and store it in the drivers directory.
