import re
import csv
import os
from collections import Counter, defaultdict
import pandas as pd
from datetime import datetime


def save_csv(data, filename):
    os.makedirs("../csv", exist_ok=True)
    with open(f"csv/{filename}", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def parse_log(log_file='sample_auth.log', output_file='csv/raw_log.csv'):
    # Get timestamp and IP
    pattern = re.compile(r'^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}):\d{2}:\d{2} .* (Failed|Accepted) password for (invalid user )?(\w+) from ([\d.]+) port (\d+)')
    logs = []
    current_year = datetime.now().year

    with open(log_file, 'r') as local_log_file:
        for log in local_log_file:
            match = pattern.search(log)
            if match:
                logs.append(
                    {
                        'DateTime': datetime.strptime(match.group(1) + f" { current_year}", "%b %d %H %Y"),
                        'Status': match.group(2),
                        'Username': match.group(4),
                        'IP': match.group(5),
                        'Port': match.group(6)
                    }
                )

    file_exists = os.path.isfile(output_file)

    with open(output_file, 'a', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=['DateTime', 'Status', 'Username', 'IP', 'Port'])

        if not file_exists:
            writer.writeheader()

        writer.writerows(logs)

    classify_ips()
    hourly_logs_distribution()


def classify_ips(input_file='csv/raw_log.csv', output_file='csv/classified_log.csv', threshold=3):
    dataframe = pd.read_csv(input_file)
    classified = dataframe.groupby(['DateTime', 'IP', 'Status']).size().unstack(fill_value=0).reset_index()

    def classify(row):
        if row.get('Failed', 0) >= threshold:
            return 'major'
        elif row.get('Failed', 0) > 0:
            return 'minor'
        else:
            return 'safe'

    classified['Label'] = classified.apply(classify, axis=1)
    classified.to_csv(output_file, index=False)


def hourly_logs_distribution(input_file='csv/classified_log.csv', output_file='csv/hourly_logs_summary.csv'):
    dataframe = pd.read_csv(input_file)
    distribution = dataframe.groupby(['DateTime', 'Label']).size().unstack(fill_value=0).reset_index()
    distribution.to_csv(output_file, index=False)


def get_major_ips(input_file='csv/classified_log.csv'):
    dataframe = pd.read_csv(input_file)
    return dataframe[dataframe['Label'] == 'major']['IP'].unique().tolist()


def get_minor_ips():
    dataframe = pd.read_csv(input_file)
    return dataframe[dataframe['Label'] == 'minor']['IP'].unique().tolist()
