from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import aiohttp
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALL_TOKENS = ["BTC", "ETH", "SOL", "JUP", "SHDW", "JTO", "WIF", "BONK"]
RESOLUTIONS = {
    '15m': {'resolution': '15'},
    '1h': {'resolution': '60'},
    '4h': {'resolution': '240'},
    '1d': {'resolution': 'D'},
    '1w': {'resolution': 'W'}
}
HOSTING_BASE_URL = "https://shdw-drive.genesysgo.net/3UgjUKQ1CAeaecg5CWk88q9jGHg8LJg9MAybp4pevtFz/"

# Add mapping of tokens to Pyth IDs
TOKEN_IDS = {
    "BTC": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH": "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "SOL": "ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "JUP": "0a0408d619e9380abad35060f9192039ed5042fa6f82301d0e48bb52be830996",
    "SHDW": "823df7874b35e0a6ad4f1f3a8298e1ec8bf3c20d188edbc1e2b56886adb73d38",
    "JTO": "b43660a5f790c69354b0729a5ef9d50d68f1df92107540210b9cccba1f947cc2",
    "WIF": "4ca4beeca86f0d164160323817a4e42b10010a724c2217c6ee41b54cd4cc61fc",
    "BONK": "72b021217ca3fe68922a19aaf990109cb9d84e9ad004b4d2025ad6f529314419"
}

async def get_prices():
    url = "https://hermes.pyth.network/v2/updates/price/latest"
    params = [("ids[]", id) for id in TOKEN_IDS.values()]
    params.append(("parsed", "true"))
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
    
    prices = {}
    for item in data["parsed"]:
        token = next(key for key, value in TOKEN_IDS.items() if value == item["id"])
        price = float(item["price"]["price"]) * 10**item["price"]["expo"]
        prices[token] = f"${price:.2f}"
    
    return prices

@app.get("/", response_class=HTMLResponse)
async def get(request: Request, tokens: List[str] = Query(None)):
    prices = await get_prices()
    
    async def generate_content():
        yield """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>H4x0rM4rk3t - Crypt0 T3rm1n4l</title>
            <link rel="stylesheet" href="/static/styles.css">
            <style>
                #jupiter-widget-container {
                    position: fixed;
                    right: 20px;
                    top: 20px;
                    z-index: 1000;
                }
                #jupiter-widget-handle {
                    width: 100%;
                    height: 20px;
                    background-color: #333;
                    cursor: move;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }
                .coins-container {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                .coin-section {
                    width: 100%;
                }
                .token-list {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 15px;
                    margin-bottom: 20px;
                }
                .token-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .token-checkbox {
                    display: flex;
                    align-items: center;
                }
                .price {
                    font-size: 0.8em;
                    color: #00FF00;
                    margin-top: 5px;
                }
                #show-tokens-btn {
                    background-color: #00FF00;
                    color: #000;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }
                #show-tokens-btn:hover {
                    background-color: #00CC00;
                    transform: scale(1.05);
                }
            </style>
        </head>
        <body>
            <div class="terminal">
                <div id="output">
                    <form method="get" action="/">
                        <div class="token-list">
        """
        for token in ALL_TOKENS:
            checked = "checked" if tokens and token in tokens else ""
            yield f"""
                            <div class="token-container">
                                <label class="token-checkbox">
                                    <input type="checkbox" name="tokens" value="{token}" {checked}>
                                    <span>{token}</span>
                                </label>
                                <span class="price">{prices.get(token, 'N/A')}</span>
                            </div>
            """
        yield """
                        </div>
                        <button id="show-tokens-btn" type="submit">Show Selected Tokens</button>
                    </form>
                    <div class="coins-container">
        """

        if tokens:
            for token in tokens:
                yield f"""
                        <div class="coin-section">
                            <h2>{token}</h2>
                            <div class="analysis">
                """
                for interval in RESOLUTIONS.keys():
                    image_url = f"{HOSTING_BASE_URL}{interval}_Crypto.{token}_USD.png"
                    yield f"""
                                <div class="trend-block">
                                    <h3>{interval} Analysis</h3>
                                    <span class="hover-area" onmouseover="showChart(this)" onmouseout="hideChart(this)">Hover to view graph</span>
                                    <img src="{image_url}" alt="{token} {interval} Candles" class="graph">
                                </div>
                    """
                yield """
                            </div>
                        </div>
                """

        yield """
                    </div>
                </div>
            </div>
            <div id="jupiter-widget-container">
                <div id="jupiter-widget-handle"></div>
                <div id="jupiter-terminal-container"></div>
            </div>
            <script src='https://terminal.jup.ag/main-v3.js'></script>
            <script>
                document.addEventListener('DOMContentLoaded', async () => {
                    await window.Jupiter.init({
                        displayMode: "widget",
                        integratedTargetId: "jupiter-terminal-container",
                        endpoint: "https://damp-fabled-panorama.solana-mainnet.quiknode.pro/186133957d30cece76e7cd8b04bce0c5795c164e/",
                    });

                    const widgetContainer = document.getElementById('jupiter-widget-container');
                    const widgetHandle = document.getElementById('jupiter-widget-handle');
                    let isDragging = false;
                    let currentX;
                    let currentY;
                    let initialX;
                    let initialY;
                    let xOffset = 0;
                    let yOffset = 0;

                    widgetHandle.addEventListener("mousedown", dragStart);
                    document.addEventListener("mousemove", drag);
                    document.addEventListener("mouseup", dragEnd);

                    function dragStart(e) {
                        initialX = e.clientX - xOffset;
                        initialY = e.clientY - yOffset;

                        if (e.target === widgetHandle) {
                            isDragging = true;
                        }
                    }

                    function drag(e) {
                        if (isDragging) {
                            e.preventDefault();
                            currentX = e.clientX - initialX;
                            currentY = e.clientY - initialY;

                            const viewportWidth = window.innerWidth;
                            const viewportHeight = window.innerHeight;
                            const widgetWidth = widgetContainer.offsetWidth;
                            const widgetHeight = widgetContainer.offsetHeight;

                            currentX = Math.max(0, Math.min(currentX, viewportWidth - widgetWidth));
                            currentY = Math.max(0, Math.min(currentY, viewportHeight - widgetHeight));

                            xOffset = currentX;
                            yOffset = currentY;

                            setTranslate(currentX, currentY, widgetContainer);
                        }
                    }

                    function dragEnd(e) {
                        initialX = currentX;
                        initialY = currentY;

                        isDragging = false;
                    }

                    function setTranslate(xPos, yPos, el) {
                        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
                    }

                    window.Jupiter.addEventListener('onSwapSuccess', (event) => {
                        console.log('Swap successful:', event.detail);
                    });

                    window.Jupiter.addEventListener('onSwapError', (event) => {
                        console.error('Swap error:', event.detail);
                    });
                });

                function showChart(span) {
                    const img = span.nextElementSibling;
                    img.style.display = 'block';
                }

                function hideChart(span) {
                    const img = span.nextElementSibling;
                    img.style.display = 'none';
                }
            </script>
        </body>
        </html>
        """

    return StreamingResponse(generate_content(), media_type="text/html")