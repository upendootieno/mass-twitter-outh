## INITIAL CONFIGURATION

### Twitter APP
Create an app with read and write permissions [here](https://developer.twitter.com/en/portal/apps/new).

### AntiCaptcha
To bypass reCAPTCHA V2, we'll need a recaptcha solve service. Create an account with anticaptcha.com and recharge your account.

#### Configurations
1: Take note of your api key.
2: To keep the expenses practical, set your maximum bid to $3 for every 1000 captchas. The codebase has been designed to tolerate lower bid rates by waiting for workers to be idle.

### Environment Variables
Add environment variables, using ".env.sample" as your guide.
