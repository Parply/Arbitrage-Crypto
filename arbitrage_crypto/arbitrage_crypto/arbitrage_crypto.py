from catalyst.utils.run_algo import run_algorithm
from catalyst.api import symbol, order
import pandas as pd
import matplotlib.pyplot as plt

def initialize(context):
    """
    Initialise algorithm
    """
    # set exchanges
    context.bitfinex = context.exchanges['bitfinex']
    context.poloniex = context.exchanges['poloniex']

    # set trading pairs
    context.bitfinex_trading_pair = symbol('btc_usdt',context.bitfinex.name)
    context.poloniex_trading_pair = symbol('btc_usdt',context.poloniex.name)

def is_profitable_after_fees(sell_price, buy_price, sell_market, buy_market):
    """
    Calculate if expected to be profitable

    returns True/False
    """
    # get fees
    sell_fee = get_fee(sell_market,sell_price)
    buy_fee = get_fee(buy_market,buy_price)

    # calculate extected profit
    expected_profit = sell_price - buy_price - sell_fee - buy_fee

    if expected_profit > 0: 
        # if  expected to be profitable return true and print
        print("Sell {} at {}, Buy {} at {}".format(sell_market.name,sell_price,buy_market.name,buy_price))
        print("Total fees:{}".format(buy_fee + sell_fee))
        print("Expected profit: {}".format(expected_profit))
        return True
    return False


def get_fee(market, price):
    """
    Get fees of market and apply them to price
    """
    return round(market.api.fees['trading']['taker'] * price,5)

def get_adjusted_prices(price):
    """
    adjust prices for slippage
    """
    adj_sell_price = price * (1-slippage)
    adj_buy_price = price * (1+slippage)
    return adj_sell_price,adj_buy_price

def handle_data(context, data):
    """
    With data decide if to place orders
    """
    # get prices
    poloniex_price = data.current(context.poloniex_trading_pair, 'price')
    bitfinex_price = data.current(context.bitfinex_trading_pair, 'price')

    #adjust prices
    sell_p,buy_p = get_adjusted_prices(poloniex_price)
    sell_b,buy_b = get_adjusted_prices(bitfinex_price)

    
    
    # if bitfinex < poloniex calculate if profitable
    if is_profitable_after_fees(sell_p, buy_b, context.poloniex, context.bitfinex):
        print('Data: {}'.format(data.current_dt))
        print('Poloniex: {}, Bitfinex: {}'.format(poloniex_price,bitfinex_price))
        print("Buy on bitfinex, sell on poloniex")
        order(asset=context.bitfinex_trading_pair,
              amount=1,
              limit_price=buy_b)
        order(asset=context.poloniex_trading_pair,
              amount=-1,
              limit_price=sell_p)
    # if bitfinex > poloniex calculate if profitable
    elif is_profitable_after_fees(sell_b, buy_p, context.bitfinex, context.poloniex):
        print('Data: {}'.format(data.current_dt))
        print('Poloniex: {}, Bitfinex: {}'.format(poloniex_price,bitfinex_price))
        print("Sell on bitfinex, buy on poloniex")
        order(asset=context.bitfinex_trading_pair,
              amount=-1,
              limit_price=sell_b)
        order(asset=context.poloniex_trading_pair,
              amount=1,
              limit_price=buy_p)

def analyze(context,perf):
    """
    analyse performanxe
    """
    #print(perf)
    # portfolio value
    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')
    # volatility
    ax2 = plt.subplot(212, sharex=ax1)
    perf.algo_volatility.plot(ax=ax2)
    ax2.set_ylabel('Volatility')
    plt.show()

if __name__ == '__main__':
    # input region of time to test 
    print("Backtesting region. Give in YYYY-MM-DD")
    start_input = input("Start date:")
    end_input = input("End date:")
    # slippage input
    slippage = float(input("Slippage:"))
    # run
    run_algorithm(initialize=initialize,
                  handle_data=handle_data,
                  analyze=analyze,
                  capital_base=1000,
                  live=False,
                  quote_currency='usdt',
                  exchange_name='bitfinex, poloniex',
                  data_frequency='minute',
                  start=pd.to_datetime(str(start_input),utc=True),
                  end=pd.to_datetime(str(end_input),utc=True),
                  )







