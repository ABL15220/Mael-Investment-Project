from flask import Flask, request, render_template, redirect, url_for, Response, send_from_directory

base_income = 420.08 
child_income = 210.04


def initial_investment(years_married, number_of_children):
    total_income = base_income + number_of_children * child_income
    initial_investment = 0
    initial_investment += total_income

    for year in range(years_married - 1):
        initial_investment *= 1.126
        total_income *= 1.0286
        initial_investment += total_income

    return initial_investment


def total_profit(years_invested, initial_investment):
    total_profit = 0
    total_profit += initial_investment

    for year in range(years_invested):
        total_profit *= 1.126

    return total_profit


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
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
        children=num_children, years_invested=num_years_invested) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)