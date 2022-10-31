from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import ParseMode,InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from operator import itemgetter
import unidecode

channel_id = '@MdPNoOficial'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Getting mode, so we could define run function for local and Heroku setup
mode = 'dev'
#mode = "dev"
TOKEN = os.getenv("TOKEN")
TOKEN = '2119936964:AAFwfyKHTV40L5lJ-2UtZrelFnauhrkRCVU'
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT =  int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN,
                              webhook_url = "https://{0}.herokuapp.com/{1}".format(HEROKU_APP_NAME, TOKEN)
        )
else:
    logger.error("No MODE  specified!")
    sys.exit(1)

def start(update, context):
    user = update.message.from_user
    logger.info(user)
    msg = 'Hola. Bienvenidx al bot para nada oficial del Mar del Plata Film Festival 2022, powered by ninjaclan. \n'
    msg += 'con /programa accedes al listado de todas las películas. Son un montón y tal vez no todas te interesen. Porque dale, taaaan cinéfilx no es nadie. O nadie tiene taaaaanto tiempo.\n'
    msg += 'con /programa_reducido accedes a un listado reducido de categorías. \n'
    msg += 'con /milista podrás ver tu watch list \n'
    msg += 'con /mispendientes podrás ver las películas de tu watch list que no marcaste como vistas.\n \n'
    msg += ' con /pelicula, /direccion y /pais seguido de una o mas palabras, pueden filtrar por películas que contengan en su '
    msg += 'nombre, director o directora o país las palabras introducidas a continuación del comando. Por ejemplo:\n'
    msg += '  /pelicula girl spider \n'
    msg += 'con /dia seguido de la fecha podés buscar las películas disponibles un día particular, por ejemplo: \n'
    msg += '/dia 19 te va a mostrar las películas disponibles el día 19, indicando la sala.\n\n'
    msg += 'Si esto te resulta de la utilidad suficiente como para que pienses en mi bienestar económico, podés invitarme un cafecito en https://cafecito.app/evil_ipa  \n\n'
    msg += 'Recordá que podés encontrar el programa completo en https://www.mardelplatafilmfest.com/36/es/programacion  \n'
    msg += 'Que lo disfrutes.'
    update.message.reply_text(msg, disable_web_page_preview = True)
    return

def periodic_reminder(dp):
    movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
    movies_req = requests.get(movies_url)
    movies_dict = movies_req.json()
    ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

    for movie in ord_movielist:
        msg = movie["movie_name"] + ' (' + str(movie['movie_year']) +')'+'\n'
        msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] + ' - ' + str(movie['movie_duration']) +'´'
        dp.bot.sendMessage(chat_id=channel_id, text=msg)

def get_program_(update, context):
    try:
        user_id = update.message.from_user['id']
        list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
        wlist_req = requests.get(list_url)
        print(wlist_req.status_code)
        wlist = wlist_req.json()

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()
        ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

        comp = {}
        for movie in ord_movielist:
            if 'Argentina de Cortos - Programa 1' in movie[competition]:
                m_comp = 'Argentina de Cortos - Programa 1'
            elif 'Argentina de Cortos - Programa 2' in movie[competition]:
                m_comp = 'Argentina de Cortos - Programa 2'
            elif 'Latinoamericana de Cortos - Programa 1' in movie[competition]:
                m_comp = 'Latinoamericana de Cortos - Programa 1'
            elif 'Latinoamericana de Cortos - Programa 2' in movie[competition]:
                m_comp = 'Latinoamericana de Cortos - Programa 2'
            elif 'silente' in movie[competition]:
                m_comp = '¿Cuanto tiempo es un siglo?'
            else:
                m_comp = movie[competition]
            if m_comp not in comp.keys():
                comp[m_comp] = []
            comp[m_comp].append(movie)
        
        keyboard = []
        for c in comp.keys():
            keyboard.append([
                InlineKeyboardButton(c, callback_data=('{0},{1},{2}'.format('comp',c, update.message.from_user['id'])))
            ])
            msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
            msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´'

            in_list = False
            if wlist_req.status_code == 200:
                for l in wlist:
                    if l['movie_id'] == movie["id"]:
                        
                        keyboard = [
                            [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',movie["id"], update.message.from_user['id'])))]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        in_list = True

            if not in_list:    
                keyboard = [
                    [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], update.message.from_user['id'])))]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def get_program(update, context):
    try:
        user_id = update.message.from_user['id']

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()
        ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

        comp = {}
        #comp['Las 10 de Calo'] = []
        for movie in ord_movielist:
            if 'Argentina de Cortos - Programa 1' in movie['competition']:
                m_comp = 'Argentina de Cortos Programa 1'

            else:
                m_comp = movie['competition']
            if m_comp not in comp.keys():
                comp[m_comp] = []
            comp[m_comp].append(movie)
        print(comp.keys())
            
        keyboard = []
        for c in comp.keys():
            keyboard.append([
                InlineKeyboardButton(c, callback_data=('{0},{1},{2}'.format('comp',c, update.message.from_user['id'])))
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
        update.message.reply_text(text="Como las películas son muchas, mejor verlas por categoría", parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def get_short_program(update, context):
    try:
        user_id = update.message.from_user['id']

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()
        ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

        cats = []

        comp = {}
        #comp['Las 10 de Calo'] = []
        for movie in ord_movielist:
            if "Competencia" in movie['competition'] or "Autoras" in movie['competition'] or "Hora" in movie['competition'] or movie['isCalos'] == 'Si' or "Trayectorias" in movie['competition'] or "VHS" in movie['competition']:
                if movie['competition'] not in comp.keys():
                    comp[movie['competition']] = []
                comp[movie['competition']].append(movie)
                if movie['isCalos'] == 'Si':
                    comp['Las 10 de Calo'].append(movie)
        
        keyboard = []
        for c in comp.keys():
            if len(c) > 34:
                c = c[:34]
            keyboard.append([
                InlineKeyboardButton(c, callback_data=('{0},{1},{2}'.format('comp',c, update.message.from_user['id'])))
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
        update.message.reply_text(text="Como las películas son muchas, mejor verlas por categoría", parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def button(update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    [action, param, user_id] = query.data.split(',')

    if action == 'add':
        wlist_url = "http://cahbot.pythonanywhere.com/api/watch_lists/"

        data = {
            'movie_id': int(param),
            'user_id': int(user_id)
        }

        logger.info(data)

        r = requests.post(url = wlist_url, json=data)

        logger.info(r.text)

        query.edit_message_text(text=f"Se ha agregado a tu watchlist")

    elif action == 'del':
        wlist_url = "http://cahbot.pythonanywhere.com/api/user_wlist/delete/" + str(param)
        r = requests.delete(url = wlist_url)

        logger.info(r.text)

        query.edit_message_text(text=f"Se ha eliminado de tu watchlist")

    elif action == 'comp':
        try:
            user_id = user_id
            list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
            wlist_req = requests.get(list_url)
            print(wlist_req.status_code)
            wlist = wlist_req.json()

            movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
            movies_req = requests.get(movies_url)
            movies_dict = movies_req.json()

            for movie in movies_dict:
                send_movie = False
                if param == 'Las 10 de Calo':
                    if movie['isCalos'] == 'Si':
                        send_movie = True
                else:
                    if param in movie['competition']:
                        send_movie = True
                
                if send_movie:
                    msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                    msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'
                    #if movie['isOnline'] != 'No':
                        #msg += 'La podés ver online los días: ' + movie['isOnline'] + '\n'
                    if movie['sala'] != 'No':
                        msg += 'La podés ver la sala: ' + movie['sala'] + 'los días: ' + movie['date']
 
                    in_list = False
                    if wlist_req.status_code == 200:
                        for l in wlist:
                            if l['movie_id'] == movie["id"]:
                                
                                keyboard = [
                                    [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], user_id)))]
                                ]
                                if l['seen'] != 'Si':
                                    keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], user_id))))
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                in_list = True

                    if not in_list:    
                        keyboard = [
                            [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], user_id)))]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    dp.bot.sendMessage(chat_id = user_id,text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                
            s_msg = "Para ver otra categoría te recomiendo enviar de nuevo /programa o /programa_reducido"
            dp.bot.sendMessage(chat_id = user_id,text=s_msg, parse_mode=ParseMode.HTML)
        except (IndexError, ValueError):
            update.message.reply_text('Hubo un error')
    elif action == 'see':
        wlist_url = "http://cahbot.pythonanywhere.com/api/user_wlist_seen/" + str(param)
        r = requests.put(url = wlist_url)

        logger.info(r.text)

        query.edit_message_text(text=f"Se ha marcado como vista")
    
    elif action == 'day':
        try:
            user_id = user_id
            list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
            wlist_req = requests.get(list_url)
            print(wlist_req.status_code)
            wlist = wlist_req.json()

            movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
            movies_req = requests.get(movies_url)
            movies_dict = movies_req.json()

            for movie in movies_dict:
                send_movie = False
                dates = movie['date'].split(',')
                days = [d.split()[0] for d in dates]
                if movie['competition'] == param.split(';')[1]:
                    if param.split(';')[0] in days:
                        send_movie = True
                
                if send_movie:
                    msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                    msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'
                    #if movie['isOnline'] != 'No':
                        #msg += 'La podés ver online los días: ' + movie['isOnline'] + '\n'
                    if movie['sala'] != 'No':
                        msg += 'La podés ver la sala: ' + movie['sala'] + 'los días: ' + movie['date']

                    in_list = False
                    if wlist_req.status_code == 200:
                        for l in wlist:
                            if l['movie_id'] == movie["id"]:
                                
                                keyboard = [
                                    [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], user_id)))]
                                ]
                                if l['seen'] != 'Si':
                                    keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], user_id))))
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                in_list = True

                    if not in_list:    
                        keyboard = [
                            [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], user_id)))]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    dp.bot.sendMessage(chat_id = user_id,text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                
            s_msg = "Para ver otra categoría te recomiendo enviar de nuevo el comando deseado"
            dp.bot.sendMessage(chat_id = user_id,text=s_msg, parse_mode=ParseMode.HTML)
        except (IndexError, ValueError):
            update.message.reply_text('Hubo un error')



def get_list(update, context):
    try:
        user_id = update.message.from_user['id']
        list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
        wlist_req = requests.get(list_url)
        wlist = wlist_req.json()
        logger.info(wlist)

        if wlist_req.status_code == 200:
            movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
            movies_req = requests.get(movies_url)
            movies_dict = movies_req.json()
            ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

            for l in wlist:
                for movie in ord_movielist:
                    if l['movie_id'] == movie["id"]:

                        msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                        msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'

                        keyboard = [
                            [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], update.message.from_user['id'])))]
                        ]
                        if l['seen'] != 'Si':
                            keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], update.message.from_user['id']))))
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        update.message.reply_text(text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            msg = "No tenes películas en tu watchlist"
            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def get_pends(update, context):
    try:
        user_id = update.message.from_user['id']
        list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
        wlist_req = requests.get(list_url)
        wlist = wlist_req.json()
        logger.info(wlist)

        if wlist_req.status_code == 200:
            movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
            movies_req = requests.get(movies_url)
            movies_dict = movies_req.json()
            ord_movielist = sorted(movies_dict, key=itemgetter('competition'))

            l_len = True

            for l in wlist:
                if l['seen'] != 'Si':
                    l_len = False
                    for movie in ord_movielist:
                        if l['movie_id'] == movie["id"]:

                            msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                            msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'

                            keyboard = [
                                [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], update.message.from_user['id'])))]
                            ]
                            if l['seen'] != 'Si':
                                keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], update.message.from_user['id']))))
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            
            if l_len:
                msg = "No tenes películas sin mirar en tu watchlist"
                update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)    
        else:
            msg = "No tenes películas sin mirar en tu watchlist"
            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def filter_name(update, context):
    try:
        user_id = update.message.from_user['id']
        keywords = []
        if len(context.args) < 1:
            update.message.reply_text(text='poné una palabra al menos', 
                  parse_mode=ParseMode.HTML)
            return
        for i in range(0, len(context.args)):
            keywords.append(context.args[i])

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()

        movies_list = []
        for movie in movies_dict:
            if all(x.lower() in unidecode.unidecode(movie['movie_name'].lower()) for x in keywords):
                movies_list.append(movie)

        if len(movies_list) > 0:
            
            list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
            wlist_req = requests.get(list_url)
            wlist = wlist_req.json()

            for movie in movies_list:
                msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'
                #if movie['isOnline'] != 'No':
                    #msg += 'La podés ver online los días: ' + movie['isOnline'] + '\n'
                if movie['sala'] != 'No':
                    msg += 'La podés ver la sala: ' + movie['sala'] + 'los días: ' + movie['date']

                in_list = False
                if wlist_req.status_code == 200:
                    for l in wlist:
                        if l['movie_id'] == movie["id"]:
                            
                            keyboard = [
                                [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], user_id)))]
                            ]
                            if l['seen'] != 'Si':
                                keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], user_id))))
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            in_list = True

                if not in_list:    
                    keyboard = [
                        [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], user_id)))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                    dp.bot.sendMessage(chat_id = user_id,text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            dp.bot.sendMessage(chat_id = user_id,text='No se encontraron resultados', parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def filter_director(update, context):
    try:
        user_id = update.message.from_user['id']
        keywords = []
        if len(context.args) < 1:
            update.message.reply_text(text='poné una palabra al menos', 
                  parse_mode=ParseMode.HTML)
            return
        for i in range(0, len(context.args)):
            keywords.append(context.args[i])

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()

        movies_list = []
        for movie in movies_dict:
            if all(x.lower() in unidecode.unidecode(movie['movie_director'].lower()) for x in keywords):
                movies_list.append(movie)

        if len(movies_list) > 0:
            
            list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
            wlist_req = requests.get(list_url)
            wlist = wlist_req.json()

            for movie in movies_list:
                msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'
                #if movie['isOnline'] != 'No':
                    #msg += 'La podés ver online los días: ' + movie['isOnline'] + '\n'
                if movie['sala'] != 'No':
                    msg += 'La podés ver la sala: ' + movie['sala'] + 'los días: ' + movie['date']

                in_list = False
                if wlist_req.status_code == 200:
                    for l in wlist:
                        if l['movie_id'] == movie["id"]:
                            
                            keyboard = [
                                [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], user_id)))]
                            ]
                            if l['seen'] != 'Si':
                                keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], user_id))))
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            in_list = True

                if not in_list:    
                    keyboard = [
                        [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], user_id)))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                    dp.bot.sendMessage(chat_id = user_id,text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            dp.bot.sendMessage(chat_id = user_id,text='No se encontraron resultados', parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def filter_country(update, context):
    try:
        user_id = update.message.from_user['id']
        keywords = []
        if len(context.args) < 1:
            update.message.reply_text(text='poné una palabra al menos', 
                  parse_mode=ParseMode.HTML)
            return
        for i in range(0, len(context.args)):
            keywords.append(context.args[i])

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()

        movies_list = []
        for movie in movies_dict:
            if all(x.lower() in unidecode.unidecode(movie['movie_country'].lower()) for x in keywords):
                movies_list.append(movie)

        if len(movies_list) > 0:
            
            list_url = "http://cahbot.pythonanywhere.com/api/user_wlist/" + str(user_id)
            wlist_req = requests.get(list_url)
            wlist = wlist_req.json()

            for movie in movies_list:
                msg = '<b>' + movie["movie_name"] + '</b>' +'\n'
                msg += "de " + movie['movie_director'] + ' - ' + movie['movie_country'] +'´\n'
                #if movie['isOnline'] != 'No':
                    #msg += 'La podés ver online los días: ' + movie['isOnline'] + '\n'
                if movie['sala'] != 'No':
                    msg += 'La podés ver la sala: ' + movie['sala'] + 'los días: ' + movie['date']

                in_list = False
                if wlist_req.status_code == 200:
                    for l in wlist:
                        if l['movie_id'] == movie["id"]:
                            
                            keyboard = [
                                [InlineKeyboardButton("Quitar de mi lista", callback_data=('{0},{1},{2}'.format('del',l["id"], user_id)))]
                            ]
                            if l['seen'] != 'Si':
                                keyboard[0].append(InlineKeyboardButton("Marcar como vista", callback_data=('{0},{1},{2}'.format('see',l["id"], user_id))))
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            in_list = True

                if not in_list:    
                    keyboard = [
                        [InlineKeyboardButton("Agregar a mi lista", callback_data=('{0},{1},{2}'.format('add',movie["id"], user_id)))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                    dp.bot.sendMessage(chat_id = user_id,text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            dp.bot.sendMessage(chat_id = user_id,text='No se encontraron resultados', parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

def filter_day(update, context):
    try:
        user_id = update.message.from_user['id']
        keyword = ''
        if len(context.args) < 1:
            update.message.reply_text(text='poné una palabra al menos', 
                  parse_mode=ParseMode.HTML)
            return
        else:
            keyword = context.args[0]

        movies_url = "http://cahbot.pythonanywhere.com/api/fest_movies/"
        movies_req = requests.get(movies_url)
        movies_dict = movies_req.json()

        comp = {}
        for movie in movies_dict:
            if keyword in movie['sala'] or keyword in movie['isOnline']:
                if movie['competition'] not in comp.keys():
                    comp[movie['competition']] = []
                comp[movie['competition']].append(movie)

        if len(comp) > 0:
            keyboard = []
            for c in comp.keys():
                s_param = keyword + ';' + c
                logger.info(s_param)
                keyboard.append([
                    InlineKeyboardButton(c, callback_data=('{0},{1},{2}'.format('day',s_param, update.message.from_user['id'])))
                ])
                reply_markup = InlineKeyboardMarkup(keyboard)
                    
            update.message.reply_text(text="Como las películas son muchas, mejor verlas por categoría", parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            dp.bot.sendMessage(chat_id = user_id,text='No se encontraron resultados', parse_mode=ParseMode.HTML)
    except (IndexError, ValueError):
        update.message.reply_text('Hubo un error')

if __name__ == '__main__':
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    if  len(sys.argv) > 1:
        periodic_reminder(dp)
    else:
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("programa", get_program, pass_args=True, pass_chat_data=True))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))
        dp.add_handler(CommandHandler("milista", get_list, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("programa_reducido", get_short_program, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("mispendientes", get_pends, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("pelicula", filter_name, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("direccion", filter_director, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("pais", filter_country, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("dia", filter_day, pass_args=True, pass_chat_data=True))
        #updater.start_polling()
        #updater.idle()
        run(updater)
        updater.idle()
