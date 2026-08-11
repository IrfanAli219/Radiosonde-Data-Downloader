# Radiosonde-Data-Downloader

Radiosonde Data Downloader is a Python-based automation system that downloads, organizes, and processes atmospheric radiosonde observations. The project supports automated weather data retrieval, NetCDF dataset processing, and efficient organization of downloaded observations for further analysis.

## Features

- Automatic radiosonde weather data downloading
- Support for multiple weather stations
- NetCDF (.nc) data processing
- Duplicate download prevention
- Organized data storage by date and time

## Technologies Used

- Python
- Requests
- xarray
- NetCDF4
- NumPy
- Pandas

## Installation

bash
git clone https://github.com/IrfanAli219/Radiosonde-Data-Downloader.git
cd Radiosonde-Data-Downloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


## Usage

bash
python main.py


## License

This project is licensed under the MIT License.