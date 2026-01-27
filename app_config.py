from gfss_parameter import BASE
from configparser import ConfigParser

styles = ['color','dark']

port=5099
host='localhost'
LOG_PATH = "logs"
#URL_LOGIN = 'http://192.168.1.34:8000'
LOAD_PATH = './loads/'
src_lang = 'file'
language = 'ru'
REPORT_PATH='reports/'
UPLOAD_DIR='uploads'

permit_post = ['Специалист', 'Главный специалист', 'Юрист', 'Внештатный работник',  ]
boss_post = ['Директор','Заместитель директора','Руководитель','Главный разработчик',]

sso_server = 'http://192.168.1.34:8825'
