import json
import os
import time

from bs4 import BeautifulSoup
import requests
import telebot

token = os.environ.get('TELEGRAM_TOKEN')
user = os.environ.get('TGUSER')

file_path = 'cars.txt'

URL = ('https://auto.ru/krasnoyarsk/cars/vendor-foreign/all/?top_days=3&year_from=2009&price_to=500000&km_age_to='
       '150000&displacement_to=2000&transmission=ROBOT&transmission=AUTOMATIC&transmission=VARIATOR&transmission='
       'AUTO&steering_wheel=LEFT&sort=cr_date-desc&clearance_from=140')

# owners options LESS_THAN_TWO / ONE

bot = telebot.TeleBot(token)


def check_cars():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                                        "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"})
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, features='html.parser')
    cars = soup.find_all('div', {'class': 'ListingItem-module__container'}, limit=5)
    cars_dict = {
        tag_link[-2]:
            {
                'model': model,
                'link': tag.find('a', {'class': 'OfferThumb'}).attrs['href'],
            }

        for tag in cars
        if (tag_link := tag.find('a', {'class': 'OfferThumb'}).attrs['href'].split('/'),
            model := tag_link[-4],)
        if model in ['toyota', 'nissan', 'honda', 'volvo', 'kia', 'renault',
                     'chevrolet', 'mitsubishi', 'mazda', 'ford', 'audi',
                     'hyundai', 'skoda', 'volkswagen', ]
    }
    return cars_dict


def check_file():
    timer = 960

    while True:
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                cars_in_file = json.load(f)
        except Exception:
            cars_in_file = dict()
        if cars_in_file is None:
            cars_in_file = dict()
        checked = check_cars()

        if result := checked.keys() - cars_in_file.keys():
            car = result.pop()
            with open(file_path, mode='w', encoding='utf-8') as f:
                cars_in_file.update({car: checked[car]})
                f.write(json.dumps(cars_in_file))
            bot.send_message(chat_id=user, text=checked[car]['link'])
        else:
            print('no')
            if timer == 0:
                bot.send_message(chat_id=user, text='No new cars in last 8 hours')
                timer = 960
            else:
                timer -= 1
            print(timer)

        time.sleep(30)


check_file()

bot.polling()
