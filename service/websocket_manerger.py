import json

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot

from service.market_data import MarketDataService
from ui.watchlist.watchlist import TargetCard


class WebSocketManager(QObject):
    tradesMessageReceived = pyqtSignal(dict)

    def __init__(self, market_data_service: MarketDataService):
        super().__init__()
        self.maintainingCards = {}
        self._market_data_service = market_data_service
        self._market_data_service.websocket_connect(self.on_message_callback)

    def on_message_callback(self, message):
        """Receive raw SDK messages on the WebSocket thread."""
        rowdata = json.loads(message)
        event = rowdata.get("event")
        data = rowdata.get("data", {})
        if event == "data":
            self.tradesMessageReceived.emit(data)
        elif event == "subscribed":
            symbol = data.get("symbol")
            if symbol in self.maintainingCards:
                self.maintainingCards[symbol]["channel_id"] = data.get(
                    "id")
        elif event == "error":
            print(f"WebSocket error: {data.get('message')}")
        else:
            print(f"WebSocket message received: {rowdata}")

    def maintain_target_cards(self, symbols: set[str]):
        """Synchronize WebSocket subscriptions with the cards currently in the UI."""
        for symbol in list(self.maintainingCards.keys()):
            if symbol not in symbols:
                channel_id = self.maintainingCards[symbol]["channel_id"]
                if channel_id is not None:
                    print(
                        f"Unsubscribing from WebSocket for symbol: {symbol}, channel_id: {channel_id}")
                    self._market_data_service.WebSocketUnsubscribe(channel_id)
                del self.maintainingCards[symbol]
        for symbol in symbols:
            if symbol not in self.maintainingCards:
                self.maintainingCards[symbol] = {"channel_id": None}
                self._market_data_service.WebSocketSubscribe("trades", symbol)
