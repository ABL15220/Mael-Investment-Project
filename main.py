from flask import Flask, request, render_template, redirect, url_for, Response, send_from_directory
import random

base_income = 420.08 
child_income = 210.04

money_per_year = []

def reset_money_per_year():
    global money_per_year
    money_per_year = []


def set_returns(index_fund):
    returns = 0

    if index_fund == 'sp_500':
        returns = 1.126
    elif index_fund == 'all_black':
        returns = 2
    elif index_fund == 'us_gov_bonds':
        returns = 1.03
    elif index_fund == 'russell_2000':
        returns = 1.25

    return returns


def initial_investment(years_married, number_of_children, returns):
    total_income = base_income + number_of_children * child_income
    initial_investment = total_income
    money_per_year.append(round(initial_investment, 2)) 

    for year in range(years_married - 1):
        initial_investment *= returns
        total_income *= 1.0286
        initial_investment += total_income
        money_per_year.append(round(initial_investment, 2))  

    return initial_investment


def total_profit(years_invested, initial_investment, returns):
    total_profit = initial_investment
    for year in range(years_invested):
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
    returns = request.form.get('index_fund', type=str)

    investment = initial_investment(num_years_married, num_children, returns=set_returns(returns))
    profit = total_profit(num_years_invested, investment, returns=set_returns(returns))

    investment = round(investment, 2)
    profit = round(profit, 2)

    return render_template('calculate.html', investment=investment, profit=profit, years_married=num_years_married, 
        children=num_children, years_invested=num_years_invested, money_per_year=money_per_year, total_years=label_years) 


@app.route('/graphs')
def graphs():
    return render_template('graphs.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)