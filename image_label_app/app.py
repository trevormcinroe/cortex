from flask import Flask, session, render_template, url_for, request, redirect, jsonify
from db_utils.db_connectors import user_query, increment_user_count
from db_utils.admin import query_db
from file_utils.imgs import *
import os

# pdf_folder = 'C:/Users/trevor_mcinroe/PycharmProjects/cortex/image_label_app/usr_holders'

# Configuration of the app itself
app = Flask(__name__)

# This is the folder that contains the images
IMAGES_FOLDER = os.path.join('static', 'images')
app.config['images_folder'] = IMAGES_FOLDER


@app.route('/', methods=['POST', 'GET'])
def home():

    if not session.get('logged_in'):

        return render_template('login_page.html')

    else:

        return render_template('dashboard.html')

@app.route('/logging-in', methods=['POST', 'GET'])
def check_login():

    # Grabbing the user-entered username and password on the 'login_page.html' FORM
    POSTED_USERNAME = str(request.form['username'])
    POSTED_PASSWORD = str(request.form['password'])

    # Making the
    username, password_check = user_query(db_name='core', usr=POSTED_USERNAME, pswd=POSTED_PASSWORD)

    # If the password matches, send them to the dashboard
    # The username.split will grab the user's first name from the email 'first_last@domain.com'
    if password_check:
        session['logged_in'] = True
        session['username'] = username

        return redirect(url_for('dashboard'))

    # This ELSE catches the other two possibilities: 1) no user, 2) password does not match
    # The url_for() function looks for the name of a function under an app.route()
    # In our case, this is under app.route('/')
    else:

        return redirect(url_for('home'))


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if not session.get('logged_in'):

        return redirect(url_for('home'))

    else:

        # The image that is being displayed
        img = os.path.join('..',
                           app.config['images_folder'],
                           image_grab(raw_folder=r'C:\Users\trevor_mcinroe\PycharmProjects\cortex\image_label_app\static\images'))
        print(img)
        return render_template('dashboard.html',
                               image=img)


@app.route('/logo-submit', methods=['POST', 'GET'])
def l_submit():

    image_sort(raw_folder=app.config['images_folder'],
               image=os.path.join(r'C:\Users\trevor_mcinroe\PycharmProjects\cortex\image_label_app\static\images',
                                  str(request.form['logo_path'])),
               sorted_folder=r'C:\Users\trevor_mcinroe\PycharmProjects\cortex\image_label_app\static\images',
               selection='logo')

    # Updating the count of images sorted by the user in the session
    increment_user_count(db_name='core', usr=session['username'])

    return redirect(url_for('dashboard'))


@app.route('/no-logo-submit', methods=['POST', 'GET'])
def nl_submit():

    image_sort(raw_folder=app.config['images_folder'],
               image=os.path.join(r'C:\Users\trevor_mcinroe\PycharmProjects\cortex\image_label_app\static\images',
                                  str(request.form['nlogo_path'])),
               sorted_folder=r'C:\Users\trevor_mcinroe\PycharmProjects\cortex\image_label_app\static\images',
               selection='no_logo')

    # Updating the count of images sorted by the user in the session
    increment_user_count(db_name='core', usr=session['username'])

    return redirect(url_for('dashboard'))



@app.route('/getting_data', methods=['POST', 'GET'])
def mhmm():

    all_results = query_db(db_name='core')

    data = [
        {
            'username': usr[1],
            'count': usr[4]
        }
        for usr in all_results
    ]

    data = {'data': data}

    return jsonify(data)


@app.route('/administrative', methods=['POST', 'GET'])
def mhmm2():
    if not session.get('logged_in'):

        return render_template('login_page.html')

    else:

        if session['username'] != 'trevor_mcinroe@quadraticinsights.com':

            return redirect(url_for('dashboard'))

        else:

            return render_template('test_table.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run()
