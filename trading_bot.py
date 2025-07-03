import logging
import threading
import time
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from tkinter import Tk, Button, Label, messagebox
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
account_number = os.getenv("ACCOUNT_NUMBER")
password = os.getenv("PASSWORD")
server = os.getenv("SERVER")

if not account_number or not password or not server:
    raise ValueError("Missing ACCOUNT_NUMBER, PASSWORD, or SERVER in .env")

ACCOUNT_NUMBER = int(account_number)

# Constants
CRYPTO = 'BTCUSD'
STOP_LOSS = 3
TAKE_PROFIT = 5
MAGIC_NUMBER = 66
CHECK_INTERVAL = 5
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20

running = False

logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_symbol(symbol):
    info = mt5.symbol_info(symbol)
    if info is None or not info.visible:
        if not mt5.symbol_select(symbol, True):
            logging.error(f"Failed to select symbol {symbol}")
            return False
    return True

def initialize_mt5():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")
    if not mt5.login(ACCOUNT_NUMBER, password=password, server=server):
        raise RuntimeError(f"Login failed: {mt5.last_error()}")
    if not ensure_symbol(CRYPTO):
        raise RuntimeError(f"Symbol {CRYPTO} not found")
    logging.info("MT5 connected.")

def get_data():
    utc_from = datetime.now() - pd.Timedelta(days=1)
    utc_to = datetime.now()
    rates = mt5.copy_rates_range(CRYPTO, mt5.TIMEFRAME_M10, utc_from, utc_to)
    if rates is None:
        logging.error("Data fetch failed.")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calculate_rsi(data, period=RSI_PERIOD):
    delta = data['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)

def calculate_macd(data):
    exp1 = data['close'].ewm(span=MACD_FAST, adjust=False).mean()
    exp2 = data['close'].ewm(span=MACD_SLOW, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=MACD_SIGNAL, adjust=False).mean()
    return macd, signal

def calculate_bollinger_bands(data, period=BB_PERIOD):
    sma = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

def has_open_position(order_type):
    positions = mt5.positions_get(symbol=CRYPTO)
    if positions is None:
        return False
    return any(p.type == order_type for p in positions)

def open_trade(order_type):
    info = mt5.account_info()
    tick = mt5.symbol_info_tick(CRYPTO)
    if info is None or tick is None:
        logging.error("Account/tick error.")
        return

    equity = info.equity
    ask, bid = tick.ask, tick.bid
    lot = round((equity / 20) / ask, 2)
    sl = bid - (bid * STOP_LOSS / 100) if order_type == mt5.ORDER_TYPE_BUY else ask + (ask * STOP_LOSS / 100)
    tp = bid + (bid * TAKE_PROFIT / 100) if order_type == mt5.ORDER_TYPE_BUY else ask - (ask * TAKE_PROFIT / 100)

    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': CRYPTO,
        'volume': lot,
        'type': order_type,
        'price': bid if order_type == mt5.ORDER_TYPE_BUY else ask,
        'sl': sl,
        'tp': tp,
        'magic': MAGIC_NUMBER,
        'comment': 'AutoTrader',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"Trade success: {result}")
    else:
        logging.error(f"Trade failed: {result.retcode}, comment: {result.comment}")

def trade():
    while running:
        df = get_data()
        if df is None or len(df) < 30:
            time.sleep(CHECK_INTERVAL)
            continue

        df['RSI'] = calculate_rsi(df)
        df['MACD'], df['Signal'] = calculate_macd(df)
        df['Upper_BB'], df['Lower_BB'] = calculate_bollinger_bands(df)

        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        signal = df['Signal'].iloc[-1]
        close_price = df['close'].iloc[-1]
        lower_band = df['Lower_BB'].iloc[-1]
        upper_band = df['Upper_BB'].iloc[-1]

        if rsi < 30 and macd > signal and close_price <= lower_band and not has_open_position(mt5.ORDER_TYPE_BUY):
            logging.info(f"Buy signal: RSI={rsi:.2f}")
            open_trade(mt5.ORDER_TYPE_BUY)

        elif rsi > 70 and macd < signal and close_price >= upper_band and not has_open_position(mt5.ORDER_TYPE_SELL):
            logging.info(f"Sell signal: RSI={rsi:.2f}")
            open_trade(mt5.ORDER_TYPE_SELL)
        else:
            logging.info("No trade signal.")

        time.sleep(CHECK_INTERVAL)

def start_bot():
    global running
    if not running:
        running = True
        threading.Thread(target=trade, daemon=True).start()
        status_label.config(text="Bot is running...", fg="green")
        logging.info("Bot started.")

def stop_bot():
    global running
    if running:
        running = False
        status_label.config(text="Bot stopped.", fg="red")
        logging.info("Bot stopped.")

# GUI Setup
root = Tk()
root.title("Crypto Trading Bot")
status_label = Label(root, text="Bot is stopped.", fg="red")
status_label.pack(pady=10)
Button(root, text="Start Bot", command=start_bot, bg="green", fg="white").pack(pady=5)
Button(root, text="Stop Bot", command=stop_bot, bg="red", fg="white").pack(pady=5)

def on_closing():
    stop_bot()
    mt5.shutdown()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

try:
    initialize_mt5()
except Exception as e:
    messagebox.showerror("Error", f"MT5 Initialization Failed: {e}")
    root.destroy()

root.mainloop()
