# Apple Environmental Data Dashboard

This project is a Dash web application that visualizes Apple's environmental data, specifically tracking greenhouse gas emissions and progress towards the 2030 Net Zero goal.

## Features

- **Interactive Visualizations**: View gross emissions over time.
- **Scope Filtering**: Filter emissions data by Scope 1, Scope 2, and Scope 3.
- **Goal Tracking**: (In Development) Visual indicators for the 2030 Net Zero target.

## Prerequisites

- Python 3.x
- pip

## Installation

1.  Clone the repository or navigate to the project directory.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python3 main.py
    ```
2.  Open your web browser and navigate to:
    `http://127.0.0.1:8050/`

## Project Structure

- `main.py`: Main application file containing the Dash layout and callbacks.
- `assets/`: Directory containing static assets and the dataset (`greenhouse_gas_emissions.csv`).
- `requirements.txt`: Python package dependencies.
