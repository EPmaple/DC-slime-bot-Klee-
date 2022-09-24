from datetime import datetime
from flask import Flask, render_template, request
from threading import Thread
import os
import subprocess
import traceback

app = Flask('KleemoteControl')

def run():
    app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def utcTimestamp():
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

def handleError(e):
  try:
    print(f'# TRACE:\n{traceback.format_exc()}')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in handleError(): {err}')

@app.route('/')
def home():
    #return 'Hello. I am alive!'
    return render_template('status.html')

@app.route('/reset', methods = ['POST'])
def restart():
  try:
    inputKey = request.form['key'].strip()
    allowedKey = os.getenv('RESET_KEY').strip()
    if inputKey == allowedKey:
        print(f'{utcTimestamp()} INFO keep_alive.restart() is initiated...')
        subprocess.call(['./ps.sh'], shell=True)
        subprocess.call(['echo kill 1 && kill 1'], shell=True)
        return 'Restarting...'
    else:
        print(f'{utcTimestamp()} WARN keep_alive.restart() is averted.')
        return "I'm afraid you are not authorized to do that."
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in keep_alive.restart(): {err}')
    handleError(err)
    return 'ERROR!'

@app.route('/test')
def test():
  try:
    a = 1/0
    return 'OK?'
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in keep_alive.test(): {err}')
    handleError(err)
    return 'ERROR!'

