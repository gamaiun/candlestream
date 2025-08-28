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

# HTML page with improved debugging
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Synthetic Stock Stream</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #prices { white-space: pre-wrap; font-family: monospace; }
        #error { color: red; }
    </style>
</head>
<body>
    <h1>Live Synthetic Stock Prices</h1>
    <p>Fetch stock data at <code>https://candlestream-1vdrp3j1w-tapak217gmailcoms-projects.vercel.app/prices</code></p>
    <div id="error"></div>
    <div id="prices"></div>
    <script>
        async function fetchPrices() {
            try {
                const response = await fetch("/prices");
                if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
                const data = await response.json();
                const pricesDiv = document.getElementById("prices");
                data.forEach(stock => {
                    pricesDiv.innerText += `Symbol: ${stock.symbol}, Price: ${stock.price}, Time: ${new Date(stock.timestamp * 1000).toISOString()}\n`;
                });
                const lines = pricesDiv.innerText.split("\n");
                if (lines.length > 100) pricesDiv.innerText = lines.slice(-100).join("\n");
            } catch (error) {
                document.getElementById("error").innerText = `Fetch error: ${error.message}`;
                console.error("Fetch error:", error);
            }
        }
        fetchPrices(); // Initial fetch
        setInterval(fetchPrices, 1000); // Poll every second
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/prices")
async def get_prices():
    try:
        # Update stock prices
        data = []
        for symbol, price in stocks.items():
            change_percent = random.uniform(-0.01, 0.01)
            stocks[symbol] = max(0, price + price * change_percent)
            data.append({
                "symbol": symbol,
                "price": round(stocks[symbol], 2),
                "timestamp": int(time.time())
            })
        return data
    except Exception as e:
        return {"error": str(e)}

# WebSocket endpoint (unused on Vercel)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = []
            for symbol, price in stocks.items():
                change_percent = random.uniform(-0.01, 0.01)
                stocks[symbol] = max(0, price + price * change_percent)
                data.append({
                    "symbol": symbol,
                    "price": round(stocks[symbol], 2),
                    "timestamp": int(time.time())
                })
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()