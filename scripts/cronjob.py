import os
import re

# for resolving file path
from pathlib import Path

# for scheduling of liking/retweeting/replying and following
from crontab import CronTab

import datetime


def createCronJob(command, follow_time, comment, is_growth_scheduler=False, interval=None):
	"""
	Since the scheduler for following works differently (with intervals instead of specific days),
	we specify the 'is_growth_scheduler' argument. If True, we will aslo require the interval
	argument. A cron job will be created to run every 'interval' days at midnight.
	"""

	# Get current user's crontab
	cron = CronTab(user=True)

	# delete existing job(s) with the same comment
	cron.remove_all(comment=comment)

	# create a cron object
	job  = cron.new(command=command, comment=comment)

	if is_growth_scheduler and interval:
		# schdule job to run every interval days at midnight
		job.minute.on(0)
		job.hour.on(0)
		job.day.every(interval)
	else:
		# set a specific date and time to run the job
		job.setall(follow_time)

	cron.write()

	return

def deleteCronJob(comment):
	cron = CronTab(user=True)
	cron.remove_all(comment=comment)
	cron.write()
	print("Removed associated cronjob")
	return
