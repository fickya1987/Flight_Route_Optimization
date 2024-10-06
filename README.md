---
title: Flight Route Planner
emoji: 🌍
colorFrom: gray
colorTo: pink
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---
# Flight Route Optimization

## Check out the demo here -  [HuggingFace Space](https://huggingface.co/spaces/souvik0306/Flight_Route_Planner)

## Overview

This project focuses on optimizing flight routes to minimize travel time and costs using advanced algorithms and data analysis techniques.

> **Note:** The actual flight time and performance may vary since the dataset used is very rudimentary. In the real world, the same aircraft can have different internal configurations, leading to variations in flight time and fuel consumption.

## Features

- Route calculation based on Weather, Temperature
- Total CO2 Emitted
- Route Feasibility based on Aircraft

## TO DO
* [ ] Integrate an API to calculate distances using dedicated airways instead of the Great Circle Distance.
* [ ] Develop additional optimization methods based on various parameters.
* [ ] Identify layover points for aircraft unable to complete a route in one go, considering computational efficiency.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Flight_Route_Optimization.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Flight_Route_Optimization
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the main script:
   ```bash
   python app.py
   ```
2. Check out the [live demo](https://huggingface.co/spaces/souvik0306/Flight_Route_Planner) to see the project in action.

---
