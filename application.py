from collections import defaultdict
from datetime import timedelta
from flask import Flask, make_response, request, current_app
import json
from flask.ext.mysqldb import MySQL
from functools import update_wrapper

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
application.config['MYSQL_HOST']='bdr.cckczjviguyp.us-east-1.rds.amazonaws.com'
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

add_scoring = ("INSERT INTO scorings "
    "(user_name, skill_name, score) "
    "VALUES (%s, %s, %s)")

@application.route('/skills/score/<skill>/<score>/<account>', methods=['Get', 'POST'])
@crossdomain(origin='*')
def score_skill_for_account(skill, score, account):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(add_scoring, (account, skill, score))
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

@application.route('/skills')
@crossdomain(origin='*')
def get_all_skills_per_group():
    cursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    cursor.execute(query)
    result = defaultdict(list)
    for name, group in cursor:
        result[group].append({"skill": name})
    cursor.close()
    return json.dumps(result)

@application.route('/skills/<user>')
@crossdomain(origin='*')
def get_all_skills_per_group_from_user(user):
    print ("getting matrix for user ", user)
    matrixCursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    matrixCursor.execute(query)
    result = defaultdict(list)
    for name, group in matrixCursor:
        skillCursor = mysql.connection.cursor()
        query = ("SELECT * FROM scorings "
                 "WHERE user_id = " + user + " AND skill_name = '" + name + "'")
        print (query)
        skillCursor.execute(query)
        scoring = skillCursor.fetchall()
        if len(scoring) == 0:
            result[group].append({"skill": name, "score": 0})
        else:
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            print scoring
            result[group].append({"skill": name, "score": scoring[0][2]})
        skillCursor.close()
    matrixCursor.close()
    return json.dumps(result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()