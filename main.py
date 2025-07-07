from flask import Flask, request, render_template, redirect, url_for, Response, send_from_directory
import random

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

@app.route('/', methods=['GET', 'POST'])
def index():
    reset_money_per_year()
    return render_template('index.html')


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
    return render_template('graphs.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)