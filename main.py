
import asyncio
import websockets
import json
import requests

# ====== CONFIG ======
DERIV_API_TOKEN = "aHyz4CrUtU2sKV"
TELEGRAM_BOT_TOKEN = "8048018636:AAGKZKSxIX77mgiJ-dABWYiXVgGz_6k4tdY"
TELEGRAM_CHAT_ID = "1499158720"

SYMBOLS = ["R_75", "R_10", "frxEURUSD", "frxGBPUSD", "XAUUSD"]
URL = "wss://ws.deriv.com/websockets/v3"

# ====== TELEGRAM SEND FUNCTION ======
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

# ====== HANDLE TICK DATA ======
async def handle_ticks(symbol):
    try:
        async with websockets.connect(URL) as ws:
            # Authorize
            await ws.send(json.dumps({"authorize": DERIV_API_TOKEN}))
            auth = await ws.recv()
            auth_data = json.loads(auth)
            if "error" in auth_data:
                print(f"[{symbol}] Authorization failed:", auth_data["error"]["message"])
                return

            # Subscribe to ticks
            await ws.send(json.dumps({
                "ticks": symbol,
                "subscribe": 1
            }))

            # Process incoming tick data
            while True:
                response = await ws.recv()
                data = json.loads(response)

                if "tick" in data:
                    price = data["tick"]["quote"]
                    print(f"[{symbol}] Price: {price}")

                    # Example signal condition
                    if price % 1 < 0.01:
                        send_telegram_message(f"{symbol} Signal Alert: Price = {price}")

                await asyncio.sleep(1)

    except Exception as e:
        print(f"[{symbol}] Error:", e)

# ====== MAIN ======
async def main():
    tasks = [handle_ticks(symbol) for symbol in SYMBOLS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
