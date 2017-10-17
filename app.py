import requests
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import logging
import yaml

from jira import JIRA

app = Flask(__name__)

#jira_server = 'http://localhost:8085/'

log = logging.getLogger(__name__)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


jira_server = cfg['protocol'].append('://')
jira_server += cfg['port']

@app.route('/')
def home():

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "You are successful logged in!  <a href='/logout'>Logout</a>"


@app.route('/login', methods=['POST'])
def login():
    jira = authenticate_via_jira(request.form['username'], request.form['password'])
    if jira is None:
        flash("Authentication faild")
    else:
        session['logged_in'] = True
        print_jira_projects_out(jira)
    return home()


def authenticate_via_jira(username, password):
    log.info("Connecting to JIRA: %s" % jira_server)

    # This is naother kind of test. That actually print the forbidden error.
   # r = requests.get('https://jira/',verify=False,  auth=(username, password))
   # print r.text

    options = {'server': jira_server ,'verify': False}
    if username is not None and (password is not None or  not ""):
        try:
          jira = JIRA(basic_auth=(username, password), server=jira_server, validate=False, options=options)
        except Exception, e:
            log.error(
                "\nAuthentication to JIRA unsuccessful. "
                "Ensure the user used has sufficient access and that Username and Password were correct\n\n " % e)
            return None
    return jira


# This is just for debug purpose .
def print_jira_projects_out(jira):

    projects = jira.projects()
    for v in projects:
        print v.__getattribute__( 'name')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='localhost', port=4000)