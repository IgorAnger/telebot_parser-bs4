import os
from dotenv import load_dotenv
import telebot
from telebot import types
from bs4 import BeautifulSoup
import requests

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
bot.enable_save_next_step_handlers(delay=2)

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    start_answer = bot.send_message(chat_id, f'Salut, {message.from_user.first_name} {message.from_user.last_name}, type any text to proceed')
    bot.register_next_step_handler(start_answer, send_provs)

def send_provs(message): 
    answer_provs = bot.send_message(message.chat.id, f'{get_provincia()} \n\nPlease type name of the interested provincia:')
    bot.register_next_step_handler(answer_provs, send_comms)

def send_comms(message):
    provincia_name = message.text
    answer_comms = bot.send_message(message.chat.id, f'{get_commune(provincia_name)}')
    bot.register_next_step_handler(answer_comms, send_advs)

def send_advs(message):
    commune_name = message.text
    bot.send_message(message.chat.id, f'Top advs: \n {get_advs(commune_name)}')

'''GET NAMES OF PROVINCIA'''
def get_provincia():
    url = 'https://www.immobiliare.it/#map-list'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    locs = soup.find_all('a', class_ = 'nd-listMeta__link')
    provincia_list = []
    for loc in locs:
        if loc.text not in provincia_list:
            provincia_list.append(loc.text)
    return '\n'.join(provincia_list)

'''GET COMMUNE NAME'''
def get_commune(provincia_name):
    provincia_name = str(provincia_name.lower())
    url = f'https://www.immobiliare.it/vendita-case/{provincia_name}-provincia/comuni/'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    locs = soup.find_all('a', class_ = 'nd-listMeta__link')
    commune_list = []
    for loc in locs:
        if loc.text not in commune_list:
            commune_list.append(loc.text)
    return '\n'.join(commune_list)

def get_advs(commune_name):
    commune_name = str(commune_name.lower())
    url = f'https://www.immobiliare.it/vendita-case/{commune_name}/'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    results = soup.find(id='__next')
    ads_list,  price_list = [], []
    adverts = results.find_all('a', class_ = 'in-card__title')
    for advert in adverts:
        ads_list.append(advert.text)
    prices = soup.find_all('div', class_ = 'in-realEstateListCard__features--range')
    if prices:
        for price in prices:
            price_list.append(price.text)
    else:
        prices = soup.find_all('li', class_ = 'nd-list__item in-feat__item in-feat__item--main in-realEstateListCard__features--main')
        for price in prices:
            price_list.append(price.text)
    ad_prc_list = []
    for i in ads_list:
        for k in price_list:
            adprc_str = f'{i} : {k}'
            ad_prc_list.append(adprc_str)
    '''ad_prc_dic = {}
    for adv in ads_list:
        for prc in price_list:
            ad_prc_dic[adv] = prc
            price_list.remove(prc)
            break'''
    return '\n'.join(ad_prc_list)

bot.polling(non_stop = True)