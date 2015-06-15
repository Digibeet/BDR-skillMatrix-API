from flask import Flask
import json
from flask.ext.mysqldb import MySQL

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
def send_partials():
    cursor = mysql.connection.cursor()
    query = ("SELECT * FROM skillMatrix")
    try:
        cursor.execute(query)
    except mysql.connector.Error as error:
        print(error.msg)
    else:
        print("Query succeeded")
    result = []
    for name, group in cursor:
        print name, group
        result.append({"name": name, "group": group})
    cursor.close()
    print result
    return json.dumps(result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()