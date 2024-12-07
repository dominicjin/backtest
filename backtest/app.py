from flask import Flask, render_template, request
from data import get_data
from strategy import back_test

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def result():
    start_date = request.form['start']
    end_date = request.form['end']
    stock_code = request.form['stock_code']

    rate, total_value = run_backtest(start_date, end_date, stock_code)

    return render_template('result.html', rate=rate, total_value=total_value)


def run_backtest(start_date, end_date, stock_code):
    if stock_code == '':
        get_data(start_date, end_date)
    else:
        get_data(start_date, end_date, stock_code)
    rate, total_value = back_test(start_date, end_date)
    return rate, total_value

if __name__ == "__main__":
    app.run()
