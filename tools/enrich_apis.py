import os
import requests
from dotenv import load_dotenv
import pycountry
import pandas as pd

load_dotenv()

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
IPINFO_API_KEY = os.getenv("IPINFO_API_KEY")


def abuseipdb_api(ip):
    # Defining the api-endpoint
    url = 'https://api.abuseipdb.com/api/v2/check'

    params = {
        'ipAddress': ip
    }

    headers = {
        'Accept': 'application/json',
        'Key': ABUSEIPDB_API_KEY
    }

    response = requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def ipinfo_api(ip):
    print(ip)
    response = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={IPINFO_API_KEY}")
    response.raise_for_status()
    return response.json()


def convert_country_code(country_code):
    try:
        return pycountry.countries.get(alpha_2=country_code).alpha_3
    except:
        return country_code

def get_country_code(file="csv/classified_log.csv"):
    classified_dataframe = pd.read_csv("../csv/classified_log.csv")
    temp = {}
    for ip in classified_dataframe['IP']:
        if ip not in temp:
            temp[ip] = convert_country_code(ipinfo_api(ip).get("country_code"))
    classified_dataframe['Country Code'] = classified_dataframe['IP'].map(temp)
    classified_dataframe.to_csv(file, index=False)

def enrich_ip(ip_list):
    enriched = []
    for ip in ip_list:
        abuseipdb_response = abuseipdb_api(ip).get("data")

        enriched.append({
            "ip": ip,
            "isPublic": abuseipdb_response.get("isPublic"),
            "organization": abuseipdb_response.get("isp"),
            "country_code": convert_country_code(abuseipdb_response.get("countryCode")),
            "usage_type": abuseipdb_response.get("usageType"),
            "abuse_score": abuseipdb_response.get("abuseConfidenceScore"),
        })
    return enriched
