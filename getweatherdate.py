import time
import os
import locale
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
import json
from dotenv import load_dotenv
import math

config = load_dotenv('.env')

LAT = os.getenv('LAT')
LON = os.getenv('LON')
API_KEY = os.getenv('API_KEY')
API_LANG = os.getenv('API_LANG')

URL = f'https://api.openweathermap.org/data/3.0/onecall?lat=' + LAT + '&lon=' + LON + '&appid=' + API_KEY + '&lang=' + API_LANG + '&units=metric'

def text_align_dates(day : str, month : str, daynumber: str, draw : ImageDraw.ImageDraw, img : Image.Image, myfont : ImageFont.ImageFont):
    day_text = day
    day_bbox = draw.textbbox((0, 0), day_text, font=myfont)
    day_width = day_bbox[2] - day_bbox[0]
    image_width, image_height = img.size
    day_x = image_width - day_width - 10
    
    daynumber_text = daynumber + " " + month
    daynumber_bbox = draw.textbbox((0, 0), daynumber_text, font=myfont)
    daynumber_width = daynumber_bbox[2] - daynumber_bbox[0]
    daynumber_x = image_width - daynumber_width - 10
    return day_x, daynumber_x, day_text, daynumber_text

def text_align_weather(temptoday : str, description : str, draw : ImageDraw.ImageDraw, img : Image.Image, myfont : ImageFont.ImageFont):
    temptoday_text = str(temptoday) + "°C"
    temptoday_bbox = draw.textbbox((0, 0), temptoday_text, font=myfont)
    temptoday_width = temptoday_bbox[2] - temptoday_bbox[0]
    image_width, image_height = img.size
    temptoday_x = image_width - temptoday_width - 10
    
    description_text = description
    description_bbox = draw.textbbox((0, 0), description_text, font=myfont)
    description_width = description_bbox[2] - description_bbox[0]
    description_x = image_width - description_width - 10
    return temptoday_x, description_x, temptoday_text, description_text


def weather_api_call():
    response = requests.get(URL)
    posts = response.json()
    
    # Save the posts data to a JSON file
    with open('weather_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(posts, json_file, ensure_ascii=False, indent=4)
        
    temptoday = posts['daily'][0]['temp']['day']
    icon = posts['daily'][0]['weather'][0]['icon']
    description = posts['daily'][0]['weather'][0]['description']
    return (temptoday, icon, description)


def get_weather(picpath : str):
    locale.setlocale(locale.LC_TIME, "fr_CA.UTF-8")
    day = time.strftime("%A").capitalize()
    month = time.strftime("%B").capitalize()
    daynumber = time.strftime("%d")
    img = Image.open(picpath).convert("RGBA")
    img = img.resize((800, 480))
    myfont = ImageFont.truetype("Biko_Regular.otf", 50)
    text_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    
    temptoday, icon, description = weather_api_call()
    
    temptoday = math.floor(temptoday)
    
    print(temptoday)
    print(icon)
    print(description)
    
    day_x, daynumber_x, day_text, daynumber_text = text_align_dates(day, month, daynumber, draw, img, myfont)
    temptoday_x, description_x, temptoday_text, description_text = text_align_weather(temptoday, description, draw, img, myfont)
    

    
    icon_img = Image.open("icons/" + icon + ".png").convert("RGBA")
    draw.text((day_x, 10), day_text, font=myfont, fill=(255, 255, 255, 200), stroke_width=2,  stroke_fill=(0, 0, 0, 64))
    draw.text((daynumber_x, 60), daynumber + " " + month, font=myfont, fill=(255, 255, 255, 200), stroke_width=2,  stroke_fill=(0, 0, 0, 64))
    draw.text((temptoday_x, 370), temptoday_text, font=myfont, fill=(255, 255, 255, 200), stroke_width=2,  stroke_fill=(0, 0, 0, 64))
    draw.text((description_x, 420), description_text, font=myfont, fill=(255, 255, 255, 200), stroke_width=2,  stroke_fill=(0, 0, 0, 64))
    text_layer.paste(icon_img, (temptoday_x - 110, 310), icon_img)
    
    img = Image.alpha_composite(img, text_layer)
    
    return(img)