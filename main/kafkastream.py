import requests
import json
from kafka import KafkaProducer
import os
from dotenv import load_dotenv


def formatdata(stuff):
    out={}
    out['country'] = stuff['name']
    out['coordinates_lon'] = stuff['coord']['lon']
    out['coordinates_lat'] = stuff['coord']['lat']
    out['weather_main']=stuff['weather'][0]['main']
    out['weather_type']=stuff['weather'][0]['description']
    out['temperature_main']=stuff['main']['temp']
    out['temperature_range_min'] = stuff['main']['temp_min']
    out['temperature_range_max'] = stuff['main']['temp_max']
    out['humidity']=stuff['main']['humidity']
    out['pressure']=stuff['main']['pressure']
    out['visibility']=stuff['visibility']
    out['wind_speed']=stuff['wind']['speed']
    out['wind_deg']=stuff['wind']['deg']

    return out


load_dotenv()

lat = os.getenv("weather_lat")
lon = os.getenv("weather_lon")
api_key = os.getenv("weather_apikey")


def streamdata():
    weatherAPI_endpoint = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    

    resp = requests.get(url=weatherAPI_endpoint)
    data=formatdata(resp.json())
    print(json.dumps(data, indent = 4))

    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=30000)
    producer.send('weather_now', json.dumps(data, indent = 4).encode('utf-8'))
    

streamdata()