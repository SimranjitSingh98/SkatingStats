import json
import pandas as pd

# Carica il file JSON
with open('dataskating.json', 'r') as f:
    data = json.load(f)

    

# Extract the main event information
event_id = list(data.keys())[0]
event_info = data[event_id]

# Extract athletes data
athletes_data = event_info['athletes']

# Prepare a DataFrame to hold athlete information
athletes_list = []

for athlete_id, athlete_info in athletes_data.items():
    athlete_data = {
        'athlete_id': athlete_id,
        'eliminated': athlete_info['eliminated'],
        'points': athlete_info['points'],
        'laps_done': athlete_info['lapsDone'],
        'rank': athlete_info['rank'],
        'lap_times': athlete_info['lapTimes'],
        'total_times': athlete_info['totalTimes'],
        'best_lap': athlete_info['bestLap']
    }
    athletes_list.append(athlete_data)

# Create a DataFrame
athletes_df = pd.DataFrame(athletes_list)

# Display the DataFrame
athletes_df.head()
