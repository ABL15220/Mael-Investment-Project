from flask import Flask, request, render_template, redirect, url_for, Response, send_from_directory, session
import json
import random
import base64
import os
from datetime import datetime

base_income = 420.08 
child_income = 210.04

money_per_year = []

def reset_money_per_year():
    global money_per_year
    money_per_year = []


def set_index_fund(index_fund):
    returns = 0
    variation = 0

    if index_fund == 'S&P 500':
        returns = 1.126
        variation = 0.025
    elif index_fund == 'All On Black':
        returns = 1
        variation = 1
    elif index_fund == 'US Government Bond':
        returns = 1.03
        variation = 0.005
    elif index_fund == 'Russell 2000':
        returns = 1.2
        variation = 0.25

    return returns, variation


def adjust_returns(returns, variation, index_fund):
    variation = random.uniform(-variation, variation)

    if index_fund == 'All On Black':
        x = random.choice([0, 2])
        returns = x
    else:
        returns += variation

    return returns


def initial_investment(years_married, number_of_children, index_fund, realistic):
    total_income = base_income + number_of_children * child_income
    initial_investment = total_income
    money_per_year.append(round(initial_investment, 2)) 

    if realistic: 
        returns, variation = set_index_fund(index_fund)
    else:
        returns = 1.126

    for year in range(years_married - 1):
        if realistic:
            returns = adjust_returns(returns, variation, index_fund) 
        else:
            returns = 1.126

        initial_investment *= returns
        total_income *= 1.0286
        initial_investment += total_income
        money_per_year.append(round(initial_investment, 2))  

    return initial_investment


def total_profit(years_invested, initial_investment, index_fund, realistic):
    total_profit = initial_investment

    if realistic: 
        returns, variation = set_index_fund(index_fund)
    else:
        returns = 1.126

    for year in range(years_invested):
        if realistic:
            returns = adjust_returns(returns, variation, index_fund) 
        else:
            returns = 1.126

        total_profit *= returns
        money_per_year.append(round(total_profit, 2))

    return total_profit


app = Flask(__name__)

app.secret_key = 'panjo2010!'

USERS_FILE = 'Mael Investment Project/users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)


@app.route('/', methods=['GET', 'POST'])
def index():
    reset_money_per_year()
    return render_template('index.html', username=session.get('username'))


@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    num_years_married = request.form.get('years_married', type=int)
    num_children = request.form.get('children', type=int)
    num_years_invested = request.form.get('years_invested', type=int)
    total_years = num_years_married + num_years_invested
    label_years = list(range(1, total_years + 1))
    index_fund = request.form.get('index_fund', type=str)
    divorce_year = num_years_married - 1
    realistic = request.form.get('realistic') == 'on'

    investment = initial_investment(num_years_married, num_children, index_fund, realistic)
    profit = total_profit(num_years_invested, investment, index_fund, realistic)

    investment = round(investment, 2)
    profit = round(profit, 2)

    return render_template('calculate.html', investment=investment, profit=profit, years_married=num_years_married, 
        children=num_children, years_invested=num_years_invested, money_per_year=money_per_year, total_years=label_years,
        index_fund=index_fund, divorce_year=divorce_year)

@app.route('/graphs')
def graphs():
    if 'username' not in session:
        return redirect(url_for('login_required'))

    username = session['username']
    save_dir = f'Mael Investment Project\static\Graphs\{username}'
    chart_files = sorted(os.listdir(save_dir)) if os.path.exists(save_dir) else []
    chart_paths = [f'Graphs/{username}/{f}' for f in chart_files if f.endswith('.png')]
    return render_template('graphs.html', chart_paths=chart_paths, username=username)


@app.route('/save_chart', methods=['POST'])
def save_chart():
    if 'username' not in session:
        return {'status': 'unauthorized'}, 401

    username = session['username']
    data = request.get_json()
    image_data = data['image']

    header, encoded = image_data.split(",", 1)
    decoded = base64.b64decode(encoded)

    save_dir = os.path.join('Mael Investment Project', 'static', 'Graphs', username)
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_{timestamp}.png"
    file_path = os.path.join(save_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(decoded)

    return {'status': 'success', 'filename': filename}


@app.route('/delete_chart', methods=['POST'])
def delete_chart():
    if 'username' not in session:
        return {'status': 'unauthorized'}, 401

    username = session['username']
    data = request.get_json()
    filename = data.get('filename')

    if filename and filename.startswith(f'Graphs/{username}/'):
        file_path = os.path.join('Mael Investment Project', 'static', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {'status': 'success'}
        else:
            return {'status': 'file_not_found'}, 404
    else:
        return {'status': 'invalid_filename'}, 400


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users:
            return render_template('signup.html', error='Username already exists')
        else:
            users[username] = password  
            save_users(users)
            os.makedirs(f'Mael Investment Project\static\Graphs\{username}', exist_ok=True)
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/login_required')
def login_required():
    return render_template('login_required.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
