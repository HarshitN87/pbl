# Interview Study Planner

A Streamlit application to help prepare for technical interviews by organizing concepts, problems, and generating personalized study plans.

## Features

- View recommended concepts and problems based on your progress
- Interactive concept dependency graph visualization
- Generate customized study plans based on your timeline
- Track your progress on different concepts and problems
- Filter problems by concept

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

2. Open your browser and navigate to http://localhost:8501

## How it Works

The application uses a study planner algorithm that:
- Manages concept dependencies
- Tracks your progress on different problems
- Recommends concepts and problems based on your current proficiency
- Generates a personalized study plan that respects concept dependencies

## Project Structure

- `streamlit_app.py`: The main Streamlit application
- `study_planner.py`: Core logic for the study planner
- `requirements.txt`: Required Python dependencies

## Customization

You can modify the concepts and problems in the `streamlit_app.py` file to customize the content according to your needs.
