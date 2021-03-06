from collections import defaultdict
from datetime import timedelta
from flask import Flask, make_response, request, current_app
import json
from flask.ext.mysqldb import MySQL
from functools import update_wrapper
import random
import time

today = str(time.strftime("%Y-%m-%d"))

def crossdomain(origin=None, methods=None, headers=None,
max_age=21600, attach_to_all=True,
automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

#setup mysql connection
application.config['MYSQL_USER']='BDR'
application.config['MYSQL_PASSWORD']='BDRforlife'
application.config['MYSQL_HOST']='bdr.c7uzpeqksgw0.eu-central-1.rds.amazonaws.com'
application.config['MYSQL_PORT']=3306
application.config['MYSQL_DB']='BDR'
mysql = MySQL(application)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))


add_skill = ("INSERT INTO skillMatrix "
    "(skill_name, skill_group_name) "
    "VALUES (%s, %s)")

delete_skill = ("DELETE FROM skillMatrix "
    "WHERE skill_name=%s AND skill_group_name=%s; ")

def add_account(parameters):
    query = "INSERT INTO accounts (user_id, user_name, password, email, phone, creation_date) VALUES ("+parameters['id']+", '"+parameters['name']+"', '"+parameters['password']+"', '"+parameters['email']+"', '"+parameters['phone']+"', '"+parameters['date']+"')"
    return query

def delete_account(account):
    query = "DELETE FROM accounts WHERE user_name='" +account+"'"
    return query

def add_skill_group(parameters):
    query =("INSERT INTO skillGroups "
    "(skill_group_name) "
    "VALUES ('" + parameters['group'] + "')")
    return query

def add_scoring(parameters):
    query = "INSERT INTO scorings (user_id, skill_name, score, score_date) VALUES (" + parameters['user_id'] + ",'" + parameters['skill_name'] + "'," + parameters['score'] +",'"+parameters['date']+ "') ON DUPLICATE KEY UPDATE score = " + parameters['score']
    return query

def add_remark(parameters):
    query = "INSERT INTO remarks (user_id, remark) VALUES (" + parameters['user_id'] + ",'" + parameters['remark']+"') ON DUPLICATE KEY UPDATE remark = '" + parameters['remark']+"'"
    return query

def add_examples(parameters):
    query = "INSERT INTO examples (skill_name, examples) VALUES ('" + parameters['skill_name'] + "','" + parameters['examples']+"') ON DUPLICATE KEY UPDATE examples = '" + parameters['examples']+"'"
    return query

@application.route('/skills/score/<skill>/<score>/<account>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def score_skill_for_account(skill, score, account):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_scoring({"user_id": account, "skill_name": skill, "score":score, "date": today}))
    conn.commit()
    return ("OK")

@application.route('/addUser/<name>/<password>/<email>/<phone>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def add_account_to_users(name, password, email, phone):
    id = random.randrange(1000000000)
    print id
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_account({"id":str(id), "name":name, "password": password, "email": email, "phone": phone, "date": today}))
    conn.commit()
    return ("OK")

@application.route('/addSkillGroup/<group>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def add_skillGroup_to_matrix(group):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_skill_group({"group": group}))
    conn.commit()
    return ("OK")
    
@application.route('/addSkill/<group>/<skill>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def add_skill_to_matrix(group, skill):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_skill, (skill, group))
    conn.commit()
    return ("OK")

@application.route('/addRemark/<account>/<remark>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def add_remark_to_remarks(account, remark):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_remark({"user_id": account, "remark": remark}))
    conn.commit()
    return ("OK")

@application.route('/addExamples/<skill>/<examples>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def add_examples_to_skill(skill, examples):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_examples({"skill_name": skill, "examples": examples}))
    conn.commit()
    return ("OK")

@application.route('/deleteSkill/<group>/<skill>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def delete_skill_from_matrix(group, skill):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(delete_skill, (skill, group))
    conn.commit()
    return ("OK")

@application.route('/deleteAccount/<account>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def delete_account_from_accounts(account):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(delete_account(account))
    conn.commit()
    return ("Account " + account + " deleted")

@application.route('/editAccount/<account>/phone/<phone>/email/<email>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def edit_phone_and_email_in_account(account, phone, email):
    conn = mysql.connection
    cursor = conn.cursor()
    query = ("UPDATE accounts SET phone='"+phone+"', email='"+email+"' WHERE user_id="+account)
    cursor.execute(query)
    conn.commit()
    return("Account " + account + " updated")

@application.route('/editAccount/<account>/password/<password>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def edit_password_in_account(account, password):
    conn = mysql.connection
    cursor = conn.cursor()
    query = ("UPDATE accounts SET password='"+password+"' WHERE user_id="+account)
    cursor.execute(query)
    conn.commit()
    return("Account " + account + " updated")

@application.route('/editAccount/<account>/remark/<remark>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def remark_in_remarks(account, remark):
    conn = mysql.connection
    cursor = conn.cursor()
    query = ("UPDATE remarks SET remark='"+remark+"' WHERE user_id="+account)
    cursor.execute(query)
    conn.commit()
    return("Remark for account " + account + " updated")

@application.route('/examples')
@crossdomain(origin='*')
def get_all_examples_per_skill():
    cursor = mysql.connection.cursor()
    query = ("SELECT * FROM examples")
    cursor.execute(query)
    result = defaultdict(dict)
    for skill, examples in cursor:
        result[skill] = examples
    cursor.close()
    return json.dumps(result)

@application.route('/skills')
@crossdomain(origin='*')
def get_all_skills_per_group():
    cursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    cursor.execute(query)
    result = defaultdict(dict)
    for name, group in cursor:
        result[group][name] = name
    cursor.close()
    return json.dumps(result)

@application.route('/skills/examples')
@crossdomain(origin='*')
def get_all_skills_per_group_with_examples():
    cursor = mysql.connection.cursor()
    query = ("SELECT skill_group_name, skill_name FROM skillMatrix")
    cursor.execute(query)
    skills = defaultdict(dict)
    for group, name in cursor:
        exampleCursor = mysql.connection.cursor()
        query = ("SELECT examples FROM examples "
                 "WHERE skill_name = '" + name + "'")
        exampleCursor.execute(query)
        examples = exampleCursor.fetchall()
        if len(examples) == 0:
            skills[group][name] = ""
        else:
            skills[group][name] = examples[0][0]
        exampleCursor.close()
    cursor.close()
    return json.dumps(skills)

@application.route('/skills/<user>')
@crossdomain(origin='*')
def get_all_skills_per_group_from_user(user):
    print ("getting matrix for user ", user)
    matrixCursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    matrixCursor.execute(query)
    skills = defaultdict(dict)
    for name, group in matrixCursor:
        skillCursor = mysql.connection.cursor()
        query = ("SELECT * FROM scorings "
                 "WHERE user_id = " + user + " AND skill_name = '" + name + "'")
        skillCursor.execute(query)
        scoring = skillCursor.fetchall()
        if len(scoring) == 0:
            skills[group][name] = {"score": 0}
        else:
            skills[group][name] = {"score": scoring[0][2]}
        skillCursor.close()
        
        exampleCursor = mysql.connection.cursor()
        query = ("SELECT examples FROM examples "
                 "WHERE skill_name = '" + name + "'")
        exampleCursor.execute(query)
        examples = exampleCursor.fetchall()
        if len(examples) == 0:
            skills[group][name]["examples"] = ""
        else:
            print "TEST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            print examples
            skills[group][name]["examples"] = examples[0][0]
        exampleCursor.close()
    matrixCursor.close()
    return json.dumps(skills)

@application.route('/accounts')
@crossdomain(origin='*')
def get_all_accounts():
    cursor = mysql.connection.cursor()
    query = ("SELECT user_id, user_name, email, phone, creation_date FROM accounts")
    cursor.execute(query)
    result = {}
    for id, name, email, phone, date in cursor:
        result[name] = {'id': id, 'email': email, 'phone': phone, 'date': date.strftime("%Y-%m-%d")}
    del result['BDRadmin']
    return json.dumps(result)

@application.route('/user/<user>')
@crossdomain(origin='*')
def get_all_info_from_user(user):
    cursor = mysql.connection.cursor()
    query = ("SELECT user_name, password, email, phone, creation_date FROM accounts WHERE user_id = " + user)
    cursor.execute(query)
    result = {}
    for name, password, email, phone, date in cursor:
            result = {'name': name, 'email': email, 'phone': phone, 'date': date.strftime("%Y-%m-%d")}
    return json.dumps(result)

@application.route('/user/<user>/name')
@crossdomain(origin='*')
def get_name_from_user(user):
    cursor = mysql.connection.cursor()
    query = ("SELECT user_name FROM accounts WHERE user_id = " + user)
    print query
    cursor.execute(query)
    result = {}
    for name in cursor:
        result = {'name': name[0]}
    return json.dumps(result)

@application.route('/user/<user>/remark')
@crossdomain(origin='*')
def get_remark_from_user(user):
    cursor = mysql.connection.cursor()
    query = ("SELECT remark FROM remarks WHERE user_id = " + user)
    print query
    cursor.execute(query)
    result = {}
    for remark in cursor:
        result = {'remark': remark[0]}
    return json.dumps(result)


@application.route('/user/<user>/password/<password>')
@crossdomain(origin='*')
def get_id_from_user_password_combination(user, password):
    print ("getting id for user ", user, " with password ", password)
    cursor = mysql.connection.cursor()
    query = ("SELECT user_id FROM accounts WHERE user_name = '" + user + "' AND password = '" + password + "'")
    print query
    cursor.execute(query)
    result = {}
    for id in cursor:
        result = {'id': id[0]}
    return json.dumps(result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()