from os import environ
from FlaskApp import app
if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.secret_key='secret123'    
    app.run(HOST,PORT,debug=True,ssl_context='adhoc')
    
    

