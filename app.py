from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import json
import random
import time

app = FastAPI()

# Initialize stock data
stocks = {
    "FAKE1": 100.0,
    "FAKE2": 50.0,
    "FAKE3": 200.0
}

# HTML page for visualization
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Synthetic Stock Stream</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #prices { white-space: pre-wrap; font-family: monospace; }
    </style>
</head>
<body>
    <h1>Live Synthetic Stock Prices</h1>
    <p>Connect to the WebSocket API at <code>wss://your-app-name.onrender.com/ws</code></p>
    <div id="prices"></div>
    <script>
        // Use wss:// for production (Render.com)
        const ws = new WebSocket("wss://" + window.location.host + "/ws");
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const pricesDiv = document.getElementById("prices");
            data.forEach(stock => {
                pricesDiv.innerText += `Symbol: ${stock.symbol}, Price: ${stock.price}, Time: ${new Date(stock.timestamp * 1000).toISOString()}\n`;
            });
            // Keep only the latest 100 lines
            const lines = pricesDiv.innerText.split("\n");
            if (lines.length > 100) pricesDiv.innerText = lines.slice(-100).join("\n");
        };
        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = []
        for symbol, price in stocks.items():
            # Random fluctuation (-1% to +1%)
            change_percent = random.uniform(-0.01, 0.01)
            stocks[symbol] = max(0, price + price * change_percent)
            data.append({
                "symbol": symbol,
                "price": round(stocks[symbol], 2),
                "timestamp": int(time.time())
            })
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(1)  # Update every second

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)