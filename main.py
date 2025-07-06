from flask import Flask, request, render_template, redirect, url_for, Response, send_from_directory

base_income = 420.08 
child_income = 210.04

money_per_year = []

def reset_money_per_year():
    global money_per_year
    money_per_year = []


def initial_investment(years_married, number_of_children):
    total_income = base_income + number_of_children * child_income
    initial_investment = total_income
    money_per_year.append(round(initial_investment, 2))  # Year 1

    for year in range(years_married - 1):
        initial_investment *= 1.126
        total_income *= 1.0286
        initial_investment += total_income
        money_per_year.append(round(initial_investment, 2))  # Year 2, 3, ...

    return initial_investment


def total_profit(years_invested, initial_investment):
    total_profit = initial_investment
    for year in range(years_invested):
        total_profit *= 1.126
        money_per_year.append(round(total_profit, 2))
    return total_profit


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    reset_money_per_year()
    return render_template('index.html')


@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    num_years_married = request.form.get('years_married', type=int)
    num_children = request.form.get('children', type=int)
    num_years_invested = request.form.get('years_invested', type=int)

    investment = initial_investment(num_years_married, num_children)
    profit = total_profit(num_years_invested, investment)

    investment = round(investment, 2)
    profit = round(profit, 2)

    return render_template('calculate.html', investment=investment, profit=profit, years_married=num_years_married, 
        children=num_children, years_invested=num_years_invested, money_per_year=money_per_year) 


@app.route('/graphs')
def graphs():
    return render_template('graphs.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)