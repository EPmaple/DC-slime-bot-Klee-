from datetime import datetime
import os
import requests
import traceback

def utcTimestamp():
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

#logging

logfileTimestamp = utcTimestamp()
logfile = f'log/{logfileTimestamp}_main.log'
#chatlogfile = f'log/{logfileTimestamp}_chat.log'

#modified version of log, input: message of string type
#prints to console and also logs the message to a file
def log(message):
  timestamp = utcTimestamp()
  print(f'{timestamp} {message}')
  try:
    with open(f'{logfile}', 'a') as outfile:
      outfile.write(f'{timestamp} {message}\n')
  except Exception as err:
    print(f'{timestamp} ERROR in log(): {err}')
  return timestamp

#error handler helper
def handleError(e):
    try:
        logTimestamp = log(f'ERROR TRACE:\n{traceback.format_exc()}# TRACE END\n')
        sendWebhook(f'Klee encountered an error (T⌓T). Please check log at https://replit.com/@traffyboi/Slime-bot-for-DC#{logfile} at time {logTimestamp} -> {type(e).__name__}.')
    except Exception as err:
        print(f'{utcTimestamp()} ERROR in handleError(): {err}')

#helper to call discord webhook API
def sendWebhook(msg):
    webhookUrl = 'https://discord.com/api/webhooks/' + os.getenv('WEBHOOK_ID_TOKEN')
    r = requests.post(webhookUrl, data={'content': msg})
    print(f'{utcTimestamp()} DEBUG Webhook response code: {r.status_code}')
    r.raise_for_status()  #raise error if response status_code is 4XX or 5XX
