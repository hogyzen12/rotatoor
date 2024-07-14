# rotatoor
Rotator is an opinioted dahsboard for market metrics, and portfolio management. 
It was created from a lack of one unified place to access candle charts for tokens.
The goal is to allow the user instant access in one place to show carts for every timeframe preseneted in a performant and uniform manner.

Usage is intuitive, with a simple select token box, and then a basic ui for viewing the charts by mousing over them.

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
Python and bash are consistently chosen due to their beginer firendly nature, being the most used languages for any beginner dev.

The API has one goal, and that is performant loading. 
Prices are fetched witha Just in Time approach as this is a single call to the Pyth API (quick and light), and then displaying the images.
Jupiter Widget feature is implemented as well to allow for instant wallet connectivity and for swapping to be done without leaving the terminal.
This is an easy way to implement Web3 functionality in a dashboard/app without needing the full wallet connector integration.
Helpful if you're starting. 


HOW TO RUN IT YOURSLEF

First look to get the fastapi running. To do this i suggest using a virtual environment, despite my hate for them. Let's dive in. 

## Prerequisites

Before we begin, make sure you have the following installed on your system:

- Python 3.7 
- pip (Python package installer)
- Git

## Setting Up the FastAPI Endpoint/ Frontend to run locally:

1. Open a new terminal window.

2. Clone the repository (replace `<repository-url>` with the actual URL):
git clone XXX
cd XXX
4. 

