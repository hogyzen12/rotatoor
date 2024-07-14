# Rotatoor

Rotatoor is an opinionated dashboard for market metrics and portfolio management. It provides a unified platform to access candle charts for various tokens across multiple timeframes, presented in a performant and simple manner. It is easily modifiable for other dashboard uses following the Bash-Python-Fastapi-Solana-ShdwDrive stack.

Start by running the frontend which is pure python, before moving onto the backend which needs some more local file configs. 
You will need the solana cli set up along with shadow drive. 
I suggest exporting the wallet into a hot wallet using the privkey to make setting up shadow drive easier/less of a command line issue.
You will need your own storage account on shadow drive if running the backend . 
Generate a solana keypair as the docs show below, fund it with at least 0.25 SHDW and 0.05 SOL. 
Go to: https://portal.shdwdrive.com/dashboard/storage/accounts
and create a new account there with your keypair. The account is where your files will be stored, so make sure to upload them. 
Run the python script to populate the graphs folder, then uplaod it or drag and drop it to you created folder.

Any error are most likely due to setup, i suggest ChatGPTing them if needed initially - then feel free to message me on twitter :)
Happy charting!

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Setting Up the FastAPI Endpoint (Frontend)](#setting-up-the-fastapi-endpoint-frontend)
  - [Setting Up the Backend](#setting-up-the-backend)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- Instant access to charts for multiple tokens and timeframes
- Intuitive user interface with simple token selection
- Real-time price updates using Pyth API
- Integrated Jupiter Widget for wallet connectivity and token swapping
- Performant loading with Just-in-Time price fetching, and one off compute

## Architecture

Rotatoor follows an opinionated separation of compute and delivery:

- **Backend**: Generates graphs every 15 minutes using Python and uploads them to SHDW drive.
- **Frontend**: FastAPI-based website for displaying charts and interacting with users.

Developer wise, it is opinionated in its separation of compute, and delivery. 
Graphs are created every 15 minutes, and fully controlled within the api_backend.
The backend runs a visualisation python script for every asset for every timeframe every 15 minute, and saves the resulting plots.
The saved plots are then uploaded to SHDW drive, utilising the deterministic naming feature, so that the updated graph is hosted to the same url.
THe plotter.py code integrates with the Pyth API endpoint for fetching the data, in classic tradingview manner, i.e.
Open, High, Low, Close
the standard format for candlestick data.

Following the unix philosophy, each file does one thing, with the python code being responsible for the creation of the plots.
upload_worker.sh is a bash script that manages the python script run time, and uploads the images to Shadow drive so they can be displayed by the frontend.
The api_backend can be run on any home computer/within the terminal to generate up to date plots, and can also be hosted on any free server.
The use of python along with bash ensures portability to any server/computer

THe frontend or deployed website, utilised fastapi, another opinioted API framework based in python. 
Python and bash are consistently chosen due to their beginer friendly nature, being the most used languages for any beginner dev.
The API has one goal, and that is performant loading. 
Prices are fetched witha Just in Time approach as this is a single call to the Pyth API (quick and light), and then displaying the images.
Jupiter Widget feature is implemented as well to allow for instant wallet connectivity and for swapping to be done without leaving the terminal.
This is an easy way to implement Web3 functionality in a dashboard/app without needing the full wallet connector integration.
Helpful if you're starting. 

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git
- Solana CLI tools
- Shadow Drive CLI

## Installation

### Setting Up the FastAPI Endpoint (Frontend)

1. Clone the repository:
   ```bash
   git clone https://github.com/hogyzen12/rotatoor.git
   cd rotatoor
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```bash
   cd rotatoor
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

   The server Docs should now be running at `http://127.0.0.1:8000/docs`.

### Setting Up the Backend

1. Install Solana CLI tools:
   ```bash
   sh -c "$(curl -sSfL https://release.solana.com/v1.14.7/install)"
   ```

2. Add Solana to your PATH:
   ```bash
   export PATH="/home/yourusername/.local/share/solana/install/active_release/bin:$PATH"
   ```

3. Create a new Solana keypair:
   ```bash
   solana-keygen new --outfile ~/.config/solana/id.json
   ```

4. Set Solana configuration:
   ```bash
   solana config set --url https://api.mainnet-beta.solana.com
   ```

5. Install Shadow Drive CLI:
   ```bash
   cargo install --git https://github.com/shadow-drive/shadow-drive-cli
   ```

6. Create a Shadow Drive account:
   ```bash
   shdw-drive create-account -s <size-in-kb>
   ```

7. Modify `upload_worker.sh` and `plotter.py` with your specific configurations.

8. Install backend requirements:
   ```bash
   cd api_backend
   pip install numpy matplotlib aiohttp
   ```

9. Run the backend:
   ```bash
   bash upload_worker.sh
   ```

## Usage

1. Navigate to `http://127.0.0.1:8000` in your web browser.
2. Select tokens from the dropdown menu.
3. Hover over timeframes to view detailed charts.
4. Use the Jupiter Widget for wallet connectivity and token swapping.

## Development

Rotatoor follows these development principles:

- Unix philosophy: Each file does one thing well.
- Python for plotting and FastAPI for the frontend.
- Bash scripts for managing runtime and uploads.

## Contact

Your Name - [@your_twitter](https://x.com/bill_papas_12)

Project Link: [https://github.com/hogyzen12/rotatoor](https://github.com/hogyzen12/rotatoor)

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pyth Network](https://pyth.network/)
- [Jupiter](https://jup.ag/)
- [Shadow Drive](https://shadow.cloud/)
- [Solana](https://solana.com/)


