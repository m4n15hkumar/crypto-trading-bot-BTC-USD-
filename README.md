# crypto-trading-bot-BTC-USD-
BTC/USD trading bot(Meta trader + python)
A Python-based automated crypto trading bot for BTC/USD, using real-time technical indicators (RSI, MACD, Bollinger Bands) to detect buy/sell signals and execute trades on MetaTrader 5. Includes a GUI for easy control and multithreading for smooth background execution.

🚀 Features
📈 Technical Analysis: Uses RSI, MACD, and Bollinger Bands to generate high-confidence trade signals

💱 Auto Trading: Places trades (BUY/SELL) on MetaTrader 5 based on signal logic

🛑 Risk Management: Supports dynamic lot size, Stop Loss and Take Profit levels

🖥️ GUI Interface: Built with Tkinter to easily start/stop the bot and view status

🧠 Multithreaded: Runs in the background without freezing the interface

📦 Logging & Error Handling: All trades and issues are recorded to trading_bot.log

🛠️ Tech Stack
Component	Technology
Language	Python 3
Trading Platform	MetaTrader 5
Indicators	RSI, MACD, Bollinger Bands
GUI	Tkinter
Logging	Python logging module
Data Analysis	Pandas, NumPy
Secure Config	.env file (dotenv)

📂 Project Structure
bash
Copy code
/crypto-trading-bot
├── trading_bot.py       # Main bot logic and GUI
├── .env                 # Secure credentials (not uploaded to GitHub)
├── trading_bot.log      # Auto-generated log file
└── requirements.txt     # Dependencies
📸 Screenshots
(Add your screenshots in a folder named assets/ and link below)

markdown
Copy code
![Bot GUI](assets/bot-gui.png)
⚙️ How It Works
Connects to MetaTrader 5 using user credentials from .env file

Fetches historical price data for BTC/USD every few seconds

Computes RSI, MACD, and Bollinger Bands using pandas

Based on logic:

Buy when RSI < 30, MACD crosses above Signal, and price touches lower BB

Sell when RSI > 70, MACD crosses below Signal, and price hits upper BB

Places orders with Stop Loss / Take Profit levels

Continues until user stops the bot from the GUI

✅ Setup Instructions
Install MetaTrader 5 terminal (with a demo/live account)

Install required Python packages:

bash
Copy code
pip install MetaTrader5 pandas numpy python-dotenv
Create a .env file with your credentials:

dotenv
Copy code
ACCOUNT_NUMBER=your_account_number
PASSWORD=your_password
SERVER=your_broker_server
Run the bot:

bash
Copy code
python trading_bot.py
🧠 Future Enhancements
📊 Add real-time chart in the GUI

🧪 Include backtesting feature

🔐 Add authentication layer before trading

🌐 Web-based dashboard (Flask or Django)
