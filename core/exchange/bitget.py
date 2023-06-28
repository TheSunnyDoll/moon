## bitget api
import os
import logging
import time
import ccxt
import pandas as pd
import json
import requests, hmac, hashlib
import urllib.parse
from typing import Optional, Tuple
from ccxt.base.errors import RateLimitExceeded

log = logging.getLogger(__name__)

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG
# logging.basicConfig()  # Enable logging

class Bitget:
    def __init__(self, exchange_id, api_key, secret_key, passphrase=None):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.name = exchange_id
        self.initialise()
        self.symbols = self._get_symbols()

    def initialise(self):
        exchange_class = getattr(ccxt, self.exchange_id)
        exchange_params = {
            "apiKey": self.api_key,
            "secret": self.secret_key,
        }
        if os.environ.get('https_proxy') and os.environ.get('http_proxy'):
            exchange_params["proxies"] = {
                'http': os.environ.get('http_proxy'),
                'https': os.environ.get('https_proxy'),
        }
        if self.exchange_id.lower() == 'huobi':
            exchange_params['options'] = {
                'defaultType': 'swap',
                'defaultSubType': 'linear',
            }
        if self.passphrase:
            exchange_params["password"] = self.passphrase

        self.exchange = exchange_class(exchange_params)
        #print(self.exchange.describe())  # Print the exchange properties

    def _get_symbols(self):
        while True:
            try:
                markets = self.exchange.load_markets()
                symbols = [market['symbol'] for market in markets.values()]
                return symbols
            except ccxt.errors.RateLimitExceeded as e:
                log.warning(f"Rate limit exceeded: {e}, retrying in 10 seconds...")
                time.sleep(10)
            except Exception as e:
                log.warning(f"An error occurred while fetching symbols: {e}, retrying in 10 seconds...")
                time.sleep(10)


    # Bitget
    def get_current_candle_bitget(self, symbol: str, timeframe='1m', retries=3, delay=60):
        """
        Fetches the current candle for a given symbol and timeframe from Bitget.

        :param str symbol: unified symbol of the market to fetch OHLCV data for
        :param str timeframe: the length of time each candle represents
        :returns [int]: A list representing the current candle [timestamp, open, high, low, close, volume]
        """
        for _ in range(retries):
            try:
                # Fetch the most recent 2 candles
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=2)

                # The last element in the list is the current (incomplete) candle
                current_candle = ohlcv[-1]

                return current_candle

            except RateLimitExceeded:
                print("Rate limit exceeded... sleeping for {} seconds".format(delay))
                time.sleep(delay)
        
        raise RateLimitExceeded("Failed to fetch candle data after {} retries".format(retries))

    # Bitget 
    def set_leverage_bitget(self, symbol, leverage, params={}):
        """
        Set the level of leverage for a market.

        :param str symbol: unified market symbol
        :param float leverage: the rate of leverage
        :param dict params: extra parameters specific to the Bitget API endpoint
        :returns dict: response from the exchange
        """
        try:
            if hasattr(self.exchange, 'set_leverage'):
                return self.exchange.set_leverage(leverage, symbol, params)
            else:
                print(f"The {self.exchange_id} exchange doesn't support setting leverage.")
                return None
        except ccxt.BaseError as e:
            print(f"An error occurred while setting leverage: {e}")
            return None
        
    
    # Bitget
    def get_market_data_bitget(self, symbol: str) -> dict:
        values = {"precision": 0.0, "leverage": 0.0, "min_qty": 0.0}
        try:
            self.exchange.load_markets()
            symbol_data = self.exchange.market(symbol)

            if self.exchange.id == 'bybit':
                if "info" in symbol_data:
                    values["precision"] = symbol_data["info"]["price_scale"]
                    values["leverage"] = symbol_data["info"]["leverage_filter"][
                        "max_leverage"
                    ]
                    values["min_qty"] = symbol_data["info"]["lot_size_filter"][
                        "min_trading_qty"
                    ]
            elif self.exchange.id == 'bitget':
                if "precision" in symbol_data:
                    values["precision"] = symbol_data["precision"]["price"]
                if "limits" in symbol_data:
                    values["min_qty"] = symbol_data["limits"]["amount"]["min"]
            else:
                log.warning("Exchange not recognized for fetching market data.")

        except Exception as e:
            log.warning(f"An unknown error occurred in get_market_data(): {e}")
        return values
    
    def get_balance_bitget(self, quote, account_type='futures'):
        if account_type == 'futures':
            if self.exchange.has['fetchBalance']:
                # Fetch the balance
                balance = self.exchange.fetch_balance(params={'type': 'swap'})

                for currency_balance in balance['info']:
                    if currency_balance['marginCoin'] == quote:
                        return float(currency_balance['equity'])
        else:
            # Handle other account types or fallback to default behavior
            pass

    def get_price_precision(self, symbol):
        market = self.exchange.market(symbol)
        smallest_increment = market['precision']['price']
        price_precision = len(str(smallest_increment).split('.')[-1])
        return price_precision

    def get_balance(self, quote: str) -> dict:
        values = {
            "available_balance": 0.0,
            "pnl": 0.0,
            "upnl": 0.0,
            "wallet_balance": 0.0,
            "equity": 0.0,
        }
        try:
            data = self.exchange.fetch_balance()
            if "info" in data:
                if "result" in data["info"]:
                    if quote in data["info"]["result"]:
                        values["available_balance"] = float(
                            data["info"]["result"][quote]["available_balance"]
                        )
                        values["pnl"] = float(
                            data["info"]["result"][quote]["realised_pnl"]
                        )
                        values["upnl"] = float(
                            data["info"]["result"][quote]["unrealised_pnl"]
                        )
                        values["wallet_balance"] = round(
                            float(data["info"]["result"][quote]["wallet_balance"]), 2
                        )
                        values["equity"] = round(
                            float(data["info"]["result"][quote]["equity"]), 2
                        )
        except Exception as e:
            log.warning(f"An unknown error occurred in get_balance(): {e}")
        return values
    

        # Universal
    def get_orderbook(self, symbol) -> dict:
        values = {"bids": [], "asks": []}
        try:
            data = self.exchange.fetch_order_book(symbol)
            if "bids" in data and "asks" in data:
                if len(data["bids"]) > 0 and len(data["asks"]) > 0:
                    if len(data["bids"][0]) > 0 and len(data["asks"][0]) > 0:
                        values["bids"] = data["bids"]
                        values["asks"] = data["asks"]
        except Exception as e:
            log.warning(f"An unknown error occurred in get_orderbook(): {e}")
        return values

    # Bitget
    def get_positions_bitget(self, symbol) -> dict:
        values = {
            "long": {
                "qty": 0.0,
                "price": 0.0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
            "short": {
                "qty": 0.0,
                "price": 0.0,
                "realised": 0,
                "cum_realised": 0,
                "upnl": 0,
                "upnl_pct": 0,
                "liq_price": 0,
                "entry_price": 0,
            },
        }
        try:
            data = self.exchange.fetch_positions([symbol])
            for position in data:
                side = position["side"]
                values[side]["qty"] = float(position["contracts"])  # Use "contracts" instead of "contractSize"
                values[side]["price"] = float(position["entryPrice"])
                values[side]["realised"] = round(float(position["info"]["achievedProfits"]), 4)
                values[side]["upnl"] = round(float(position["unrealizedPnl"]), 4)
                if position["liquidationPrice"] is not None:
                    values[side]["liq_price"] = float(position["liquidationPrice"])
                else:
                    print(f"Warning: liquidationPrice is None for {side} position")
                    values[side]["liq_price"] = None
                values[side]["entry_price"] = float(position["entryPrice"])
        except Exception as e:
            log.warning(f"An unknown error occurred in get_positions_bitget(): {e}")
        return values
    
        # Universal
    def get_current_price(self, symbol: str) -> float:
        current_price = 0.0
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            if "bid" in ticker and "ask" in ticker:
                current_price = (ticker["bid"] + ticker["ask"]) / 2
        except Exception as e:
            log.warning(f"An unknown error occurred in get_positions(): {e}")
        return current_price

    def get_moving_averages(
        self, symbol: str, timeframe: str = "1m", num_bars: int = 20
    ) -> dict:
        values = {"MA_3_H": 0.0, "MA_3_L": 0.0, "MA_6_H": 0.0, "MA_6_L": 0.0}
        try:
            bars = self.exchange.fetch_ohlcv(
                symbol=symbol, timeframe=timeframe, limit=num_bars
            )
            df = pd.DataFrame(
                bars, columns=["Time", "Open", "High", "Low", "Close", "Volume"]
            )
            df["Time"] = pd.to_datetime(df["Time"], unit="ms")
            df["MA_3_High"] = df.High.rolling(3).mean()
            df["MA_3_Low"] = df.Low.rolling(3).mean()
            df["MA_6_High"] = df.High.rolling(6).mean()
            df["MA_6_Low"] = df.Low.rolling(6).mean()
            values["MA_3_H"] = df["MA_3_High"].iat[-1]
            values["MA_3_L"] = df["MA_3_Low"].iat[-1]
            values["MA_6_H"] = df["MA_6_High"].iat[-1]
            values["MA_6_L"] = df["MA_6_Low"].iat[-1]
        except Exception as e:
            log.warning(f"An unknown error occurred in get_moving_averages(): {e}")
        return values


    def get_open_orders_bitget(self, symbol: str) -> list:
        open_orders = []
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            #print(f"Raw orders: {orders}")  # Add this line to print raw orders
            for order in orders:
                if "info" in order:
                    info = order["info"]
                    if "state" in info and info["state"] == "new":  # Change "status" to "state"
                        order_data = {
                            "id": info.get("orderId", ""),  # Change "order_id" to "orderId"
                            "price": info.get("price", 0.0),  # Use the correct field name
                            "qty": info.get("size", 0.0),  # Change "qty" to "size"
                            "side": info.get("side", ""),
                            "reduce_only": info.get("reduceOnly", False),
                        }
                        open_orders.append(order_data)
        except Exception as e:
            log.warning(f"An unknown error occurred in get_open_orders_debug(): {e}")
        return open_orders
    
    def cancel_long_entry_bitget(self, symbol: str) -> None:
        self.cancel_entry_bitget_by_side(symbol, order_side="open_long")

    def cancel_short_entry_bitget(self, symbol: str) -> None:
        self.cancel_entry_bitget_by_side(symbol, order_side="open_short")

    # Bitget
    def cancel_entry_bitget_by_side(self, symbol: str,order_side: str) -> None:
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            
            for order in orders:
                order_info = order["info"]
                order_id = order_info["orderId"]
                order_status = order_info["state"]
                side = order_info["side"]
                reduce_only = order_info["reduceOnly"]
                
                if (
                    order_status != "Filled"
                    and order_status != "Cancelled"
                    and side == order_side
                    and not reduce_only
                ):
                    self.exchange.cancel_order(symbol=symbol, id=order_id)
                    log.info(f"Cancelling order: {order_id}")
        except Exception as e:
            log.warning(f"An unknown error occurred in cancel_entry(): {e}")

    def _cancel_entry(self, symbol: str, order_side: str) -> None:
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            for order in orders:
                if "info" in order:
                    order_id = order["info"]["order_id"]
                    order_status = order["info"]["order_status"]
                    side = order["info"]["side"]
                    reduce_only = order["info"]["reduce_only"]
                    if (
                        order_status != "Filled"
                        and side == order_side
                        and order_status != "Cancelled"
                        and not reduce_only
                    ):
                        self.exchange.cancel_order(symbol=symbol, id=order_id)
                        log.info(f"Cancelling {order_side} order: {order_id}")
        except Exception as e:
            log.warning(f"An unknown error occurred in _cancel_entry(): {e}")

    def cancel_all_entries(self, symbol: str) -> None:
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            long_orders = 0
            short_orders = 0

            # Count the number of open long and short orders
            for order in orders:
                order_info = order["info"]
                order_status = order_info["state"]
                order_side = order_info["side"]
                reduce_only = order_info["reduceOnly"]
                
                if order_status != "Filled" and order_status != "Cancelled" and not reduce_only:
                    if order_side == "open_long":
                        long_orders += 1
                    elif order_side == "open_short":
                        short_orders += 1

            # Cancel extra long or short orders if more than one open order per side
            if long_orders > 1 or short_orders > 1:
                for order in orders:
                    order_info = order["info"]
                    order_id = order_info["orderId"]
                    order_status = order_info["state"]
                    order_side = order_info["side"]
                    reduce_only = order_info["reduceOnly"]

                    if (
                        order_status != "Filled"
                        and order_status != "Cancelled"
                        and not reduce_only
                    ):
                        self.exchange.cancel_order(symbol=symbol, id=order_id)
                        print("Cancelling order: {order_id}")
                        # log.info(f"Cancelling order: {order_id}")
        except Exception as e:
            log.warning(f"An unknown error occurred in cancel_entry(): {e}")

    def get_open_take_profit_order_quantity_bitget(self, orders, side):
        for order in orders:
            if order['side'] == side and order['params'].get('reduceOnly', False):
                return order['amount']
        return None
    
        # Bitget
    def get_order_status_bitget(self, symbol, side):
        open_orders = self.exchange.fetch_open_orders(symbol)

        for order in open_orders:
            if order['side'] == side:
                return order['status']

        return None  # Return None if the order is not found

    # Bitget
    def cancel_entry_bitget(self, symbol: str) -> None:
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            
            for order in orders:
                order_info = order["info"]
                order_id = order_info["orderId"]
                order_status = order_info["state"]
                order_side = order_info["side"]
                reduce_only = order_info["reduceOnly"]
                
                if (
                    order_status != "Filled"
                    and order_status != "Cancelled"
                    and not reduce_only
                ):
                    self.exchange.cancel_order(symbol=symbol, id=order_id)
                    log.info(f"Cancelling order: {order_id}")
        except Exception as e:
            log.warning(f"An unknown error occurred in cancel_entry(): {e}")

    def cancel_close_bitget(self, symbol: str, side: str) -> None:
        side_map = {"long": "close_long", "short": "close_short"}
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            if len(orders) > 0:
                for order in orders:
                    if "info" in order:
                        order_id = order["info"]["orderId"]
                        order_status = order["info"]["state"]
                        order_side = order["info"]["side"]
                        reduce_only = order["info"]["reduceOnly"]

                        if (
                            order_status != "filled"
                            and order_side == side_map[side]
                            and order_status != "canceled"
                            and reduce_only
                        ):
                            self.exchange.cancel_order(symbol=symbol, id=order_id)
                            log.info(f"Cancelling order: {order_id}")
        except Exception as e:
            log.warning(f"An unknown error occurred in cancel_close_bitget(): {e}")

    def create_take_profit_order(self, symbol, order_type, side, amount, price=None, reduce_only=False):
        if order_type == 'limit':
            if price is None:
                raise ValueError("A price must be specified for a limit order")

            if side not in ["buy", "sell"]:
                raise ValueError(f"Invalid side: {side}")
            if self.exchange_id == 'okx':
                params = {'tdMode':'cross','ccy':'USDT','reduceOnly': reduce_only}
            else:
                params = {"reduceOnly": reduce_only}
            return self.exchange.create_order(symbol, order_type, side, amount, price, params)
        else:
            raise ValueError(f"Unsupported order type: {order_type}")


    def market_close_position_bitget(self, symbol, side, amount):
        """
        Close a position by creating a market order in the opposite direction.
        
        :param str symbol: Symbol of the market to create an order in.
        :param str side: Original side of the position. Either 'buy' (for long positions) or 'sell' (for short positions).
        :param float amount: The quantity of the position to close.
        """
        # Determine the side of the closing order based on the original side of the position
        if side == "buy":
            close_side = "sell"
        elif side == "sell":
            close_side = "buy"
        else:
            raise ValueError("Invalid order side. Must be either 'buy' or 'sell'.")

        # Create a market order in the opposite direction to close the position
        self.create_order(symbol, 'market', close_side, amount)

    def create_limit_order(self, symbol, side, amount, price, reduce_only=False, **params):
        if side == "buy":
            return self.create_limit_buy_order(symbol, amount, price, reduce_only=reduce_only, **params)
        elif side == "sell":
            return self.create_limit_sell_order(symbol, amount, price, reduce_only=reduce_only, **params)
        else:
            raise ValueError(f"Invalid side: {side}")

    def create_limit_buy_order(self, symbol: str, qty: float, price: float, **params) -> None:
        if self.exchange_id == 'okx':
            self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='buy',
                amount=qty,
                price=price,
                params={**params, 'tdMode':'cross','ccy':'USDT'}
            )
        else:
            self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='buy',
                amount=qty,
                price=price,
                **params
            )

    def create_limit_sell_order(self, symbol: str, qty: float, price: float, **params) -> None:
        if self.exchange_id == 'okx':
            self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='sell',
                amount=qty,
                price=price,
                params={**params, 'tdMode':'cross','ccy':'USDT'}
            )
        else:
            self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side='sell',
                amount=qty,
                price=price,
                **params
            )

    def create_order(self, symbol, order_type, side, amount, price=None, reduce_only=False, **params):
        if reduce_only:
            params.update({'reduceOnly': 'true'})
        if self.exchange_id == 'bybit':
            order = self.exchange.create_order(symbol, order_type, side, amount, price, params=params)
        else:
            if order_type == 'limit':
                if side == "buy":
                    order = self.create_limit_buy_order(symbol, amount, price, **params)
                elif side == "sell":
                    order = self.create_limit_sell_order(symbol, amount, price, **params)
                else:
                    raise ValueError(f"Invalid side: {side}")
            elif order_type == 'market':
                #... handle market orders if necessary
                order = self.create_market_order(symbol, side, amount, params)
            else:
                raise ValueError("Invalid order type. Use 'limit' or 'market'.")

        return order
