import base64
import io
from collections import Counter

import flask
from flask import request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, cast, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from datetime import datetime
from scipy.stats import pearsonr, spearmanr, kendalltau

app = flask.Flask(__name__)
dburl = "mysql://dbmasteruser:!F]Bu4GMBFEk+}Q!-P+R16=^3fL|,diQ@ls-eb91d5a"
dburl = dburl + "9ff69edf18bec677735146d61b9cc3554.ctc8ucq8gai5.eu-central-1.rds.amazonaws.com:3306/MarketDataDB"
app.config['SQLALCHEMY_DATABASE_URI'] = dburl
app.config["DEBUG"] = True

db = SQLAlchemy(app)


class CongressionalTrades(db.Model):
    __tablename__ = "CongressionalTrades"
    id = db.Column(db.Integer, primary_key=True)
    amountFrom = db.Column('amountFrom', db.Float(precision=2), nullable=True)
    amountTo = db.Column('amountTo', db.Float(precision=2), nullable=True)
    assetName = db.Column('assetName', db.String(100), nullable=True)
    filingDate = db.Column('filingDate', db.String(100), nullable=True)
    name = db.Column('name', db.String(100), nullable=True)
    ownerType = db.Column('ownerType', db.String(100), nullable=True)
    position = db.Column('position', db.String(100), nullable=True)
    symbol = db.Column('symbol', db.String(100), nullable=True)
    transactionDate = db.Column('transactionDate', db.String(100), nullable=True)
    transactionType = db.Column('transactionType', db.String(100), nullable=True)
    party = db.Column('party', db.String(100), nullable=True)
    conditions = db.Column('conditions', db.String(100), nullable=True)

    def __repr__(self):
        return f'<CongressionalTrades {self.id}>'


@app.route('/', methods=['GET'])
def index():
    congressionaltrade = CongressionalTrades.query.all()
    return render_template('congressionaltrade.html', trades=congressionaltrade)


@app.route('/histogram', methods=['GET', 'POST'])
def histogram():
    if request.method == 'POST':

        # Parse parameters from the URL query string
        symbol = request.form['symbol']

        congressionaltrades = CongressionalTrades.query.filter_by(symbol=symbol).all()


        years = [datetime.strptime(trade.transactionDate, "%Y-%m-%d").year for trade in congressionaltrades]

        # Create histogram
        fig = plt.figure()
        ax = fig.add_subplot(111)
        n, bins, patches = ax.hist(years, bins=16, cumulative=0)
        ax.set_xlabel('Years', size=10)
        ax.set_ylabel('Frequency', size=10)
        ax.legend()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid()


        # Save the plot to a .png image in memory
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)

        # Plot url
        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template('Histogram.html', plot_url=plot_url)
    else:
        return render_template('Histogram.html')

@app.route('/pvalue', methods=['GET', 'POST'])
def pvalue():
    if request.method == 'POST':

        # Parse parameters from the URL query string

        congressionaltrades = CongressionalTrades.query.all()

        years = [datetime.strptime(trade.transactionDate, "%Y-%m-%d").year for trade in congressionaltrades]
        yearsWithCount = {}
        for year in years:
            count = years.count(year)
            yearsWithCount[str(year)] = count

        data = pd.DataFrame([(datetime.strptime(trade.transactionDate, "%Y-%m-%d").year, years.count(datetime.strptime(trade.transactionDate, "%Y-%m-%d").year)) for trade in congressionaltrades], columns=['transactionDate', 'count'])

        sns.scatterplot(x='transactionDate', y='count', data=data)
        plt.show()

        # Calculate Pearson's correlation
        pearson_corr, pearson_p = pearsonr(data['transactionDate'], data['count'])

        # Calculate Spearman's rank correlation
        spearman_corr, spearman_p = spearmanr(data['transactionDate'], data['count'])

        # Calculate Kendall's tau
        kendall_corr, kendall_p = kendalltau(data['transactionDate'], data['count'])

        return render_template('PValue.html', pearson_corr=pearson_corr, pearson_p=pearson_p,spearman_corr=spearman_corr, spearman_p=spearman_p,kendall_corr=kendall_corr,kendall_p=kendall_p)
    else:
        return render_template('PValue.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)