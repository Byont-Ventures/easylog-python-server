# Python Health Agent

This guide explains how to create a simple Python server that receives step count data from the Flutter app and processes it.

## Setup

1. Install required packages:

```bash
pip install flask pandas numpy matplotlib
```

2. Create a basic Flask server:

```python
from flask import Flask, request, jsonify, send_file
import pandas as pd
import datetime
import os

app = Flask(__name__)

# Store data in memory for simplicity, replace with database for production
step_data = {}

@app.route('/health_data', methods=['POST'])
def receive_health_data():
    """
    Receives step count data from the Flutter app.

    Accepts single day data or date range data in JSON format.
    """
    try:
        data = request.json

        # Check if it's single day data or date range
        if 'date' in data and 'steps' in data:
            # Single day data
            date = data['date']
            steps = data['steps']
            step_data[date] = steps
            print(f"Received step data for {date}: {steps} steps")

        elif 'date_range' in data and 'steps_data' in data:
            # Date range data
            steps_data = data['steps_data']
            start_date = data['date_range']['start']
            end_date = data['date_range']['end']

            # Store all the data
            for date, steps in steps_data.items():
                step_data[date] = steps

            print(f"Received step data for period {start_date} to {end_date}")

        return jsonify({"status": "success", "message": "Data received"}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health_data/summary', methods=['GET'])
def get_health_summary():
    """
    Generates a summary of the collected step data.

    Returns statistics including total days, total steps, average steps, etc.
    """
    try:
        if not step_data:
            return jsonify({"status": "error", "message": "No data available"}), 404

        # Convert to DataFrame for analysis
        df = pd.DataFrame(list(step_data.items()), columns=['date', 'steps'])

        summary = {
            "total_days": len(df),
            "total_steps": int(df['steps'].sum()),
            "average_steps": round(df['steps'].mean(), 2),
            "max_steps": int(df['steps'].max()),
            "min_steps": int(df['steps'].min()),
            "latest_date": df['date'].max()
        }

        return jsonify({"status": "success", "summary": summary}), 200

    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health_data/chart', methods=['GET'])
def generate_step_chart():
    """
    Generates a chart visualization of the step data.

    Returns a PNG image of the step count over time.
    """
    try:
        if not step_data:
            return jsonify({"status": "error", "message": "No data available"}), 404

        # Convert to DataFrame for plotting
        df = pd.DataFrame(list(step_data.items()), columns=['date', 'steps'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Plot data
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['steps'], marker='o')
        plt.title('Daily Step Count')
        plt.xlabel('Date')
        plt.ylabel('Steps')
        plt.grid(True)

        # Save chart to file
        chart_path = 'step_chart.png'
        plt.savefig(chart_path)

        return send_file(chart_path, mimetype='image/png')

    except Exception as e:
        print(f"Error generating chart: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

3. Run the server:

```bash
python app.py
```

## API Endpoints

### 1. Receive Health Data

- **URL**: `/health_data`
- **Method**: `POST`
- **Accepts**:
  - Single day payload:
    ```json
    {
      "date": "2023-10-15",
      "steps": 8432
    }
    ```
  - Date range payload:
    ```json
    {
      "date_range": {
        "start": "2023-10-10",
        "end": "2023-10-15"
      },
      "steps_data": {
        "2023-10-10": 7845,
        "2023-10-11": 6543,
        "2023-10-12": 9876,
        "2023-10-13": 5432,
        "2023-10-14": 7654,
        "2023-10-15": 8432
      }
    }
    ```

### 2. Get Health Summary

- **URL**: `/health_data/summary`
- **Method**: `GET`
- **Returns**: Summary statistics of collected step data

## Advanced Features

### Data Visualization

Add a route to generate and return step count visualizations:

```python
# Note: The chart generation endpoint is already included in the main server code above
# Import matplotlib at the top of your file:
# import matplotlib.pyplot as plt
```

### Activity Analysis

Add a function to analyze step data and provide insights:

```python
def analyze_activity(steps_df):
    """Analyze step data to provide insights."""
    insights = []

    # Calculate daily averages by weekday
    steps_df['weekday'] = steps_df['date'].dt.day_name()
    weekday_avg = steps_df.groupby('weekday')['steps'].mean().to_dict()

    # Find most and least active days
    most_active_day = max(weekday_avg.items(), key=lambda x: x[1])
    least_active_day = min(weekday_avg.items(), key=lambda x: x[1])

    insights.append(f"Most active day is typically {most_active_day[0]} with an average of {round(most_active_day[1])} steps")
    insights.append(f"Least active day is typically {least_active_day[0]} with an average of {round(least_active_day[1])} steps")

    # Check for trend
    if len(steps_df) >= 7:
        recent_trend = steps_df.sort_values('date').tail(7)
        avg_recent = recent_trend['steps'].mean()
        avg_overall = steps_df['steps'].mean()

        if avg_recent > avg_overall * 1.1:
            insights.append("Your activity has increased in the past week!")
        elif avg_recent < avg_overall * 0.9:
            insights.append("Your activity has decreased in the past week.")

    return insights
```

## Integration with AI Models

You can extend this server to use AI for health predictions:

```python
def predict_health_metric(steps_history):
    """
    Example function to predict a health metric based on step history.
    In a real implementation, this would use a trained model.
    """
    # This is a placeholder for an actual model prediction
    # You could use scikit-learn, TensorFlow, or any other ML framework

    recent_steps = steps_history[-7:]  # Last week of data
    avg_steps = sum(recent_steps) / len(recent_steps)

    # Very simple "model" - just for demonstration
    if avg_steps > 10000:
        return "Excellent activity level. Keep it up!"
    elif avg_steps > 7500:
        return "Good activity level. Try to increase slightly for optimal health."
    elif avg_steps > 5000:
        return "Moderate activity level. Consider increasing your daily steps."
    else:
        return "Low activity level. Try to find ways to walk more during your day."
```

## Testing with cURL

Test your API with:

```bash
# Send single day data
curl -X POST http://localhost:5000/health_data \
  -H "Content-Type: application/json" \
  -d '{"date": "2023-10-15", "steps": 8432}'

# Get summary
curl -X GET http://localhost:5000/health_data/summary
```

## Deployment

To deploy this to a server:

1. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. Consider using a process manager like Supervisor to keep the service running.

3. For simplicity, you can also deploy to platforms like Heroku, Render, or PythonAnywhere.

## Using Health Data in Your Python Agent

Here's how to integrate the health data with your existing AI agent:

```python
import requests
import json
from datetime import datetime, timedelta

class HealthAwareAgent:
    def __init__(self, health_api_url="http://localhost:5000"):
        self.health_api_url = health_api_url

    def get_health_summary(self):
        """Fetch health summary from the API."""
        try:
            response = requests.get(f"{self.health_api_url}/health_data/summary")
            if response.status_code == 200:
                return response.json()["summary"]
            else:
                print(f"Error fetching health summary: {response.json()['message']}")
                return None
        except Exception as e:
            print(f"Error connecting to health API: {e}")
            return None

    def generate_health_insights(self):
        """Generate personalized insights based on health data."""
        summary = self.get_health_summary()
        if not summary:
            return "No health data available to analyze."

        insights = []

        # Basic analysis
        avg_steps = summary["average_steps"]
        if avg_steps > 10000:
            insights.append("You're doing great with your step count! Keep it up!")
        elif avg_steps > 7500:
            insights.append("You're close to the recommended 10,000 steps per day. A little more effort would be perfect!")
        elif avg_steps > 5000:
            insights.append("You have moderate activity. Try to increase your daily steps to reach the recommended 10,000.")
        else:
            insights.append("Your activity level is lower than recommended. Consider finding ways to walk more.")

        # Compare to previous records
        if summary["total_days"] > 7:
            # Fetch last week's data for comparison (this would require an additional endpoint)
            # For this example, we're simplifying
            insights.append("Based on your trend, you might benefit from setting a daily step goal.")

        return "\n".join(insights)

    def recommend_activity(self, current_steps=0):
        """Recommend additional activity based on current step count."""
        summary = self.get_health_summary()
        if not summary:
            return "I don't have enough data to make recommendations yet."

        target_steps = 10000
        average_steps = summary["average_steps"]

        if current_steps >= target_steps:
            return "You've already reached your daily step goal! Great job!"

        steps_needed = target_steps - current_steps

        # Calculate recommended activity
        if steps_needed > 5000:
            return f"You need {steps_needed} more steps today. Consider a long walk or jog (about {round(steps_needed/1300)} km)."
        elif steps_needed > 2500:
            return f"You need {steps_needed} more steps. A 30-minute walk would help you reach your goal."
        else:
            return f"Just {steps_needed} more steps to reach your goal! A quick 10-15 minute walk should do it."

# Example usage
if __name__ == "__main__":
    agent = HealthAwareAgent()

    # Get insights
    insights = agent.generate_health_insights()
    print("Health Insights:")
    print(insights)

    # Get activity recommendation
    current_steps = 6500  # This would come from the most recent data
    recommendation = agent.recommend_activity(current_steps)
    print("\nActivity Recommendation:")
    print(recommendation)
```

This agent can be integrated into a larger AI system or chatbot to provide health-related insights and recommendations based on the user's step data.
