import sys
from btc_monitor.config import MY_BTC_BUY_PRICE, MY_BTC_AMOUNT
from btc_monitor.report import format_my_position

print(f"Config: Buy={MY_BTC_BUY_PRICE}, Amount={MY_BTC_AMOUNT}")
print("Result:")
print(format_my_position(120000000.0))
