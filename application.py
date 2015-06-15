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

@application.route('/skills')
@crossdomain(origin='*')
def send_partials():
    cursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    try:
        cursor.execute(query)
    except mysql.connector.Error as error:
        print(error.msg)
    else:
        print("Query succeeded")
    result = defaultdict(list)
    for name, group in cursor:
        result[group].append({"skill": name})
    cursor.close()
    return json.dumps(result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()