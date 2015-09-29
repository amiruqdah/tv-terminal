#!/usr/bin/env python
# encoding: utf-8

__author__ = 'amir.uqdah@pacbell.net'
import telegram
import sqlite3
import requests
import shlex
import re
import os

def main():
    print "Initiating"
    bot = telegram.Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')
    last_update_id = bot.getUpdates()[-1].update_id;

    while True:
        for update in bot.getUpdates(offset=last_update_id, timeout=10):
            text = update.message.text
            chat_id = update.message.chat_id
            update_id = update.update_id

            if text:
                last_update_id = update_id + 1
                if(text.split()[0].lower() == '/random'):
                    print "Picking random tv show"
                    random(bot,chat_id)
                elif(text.split()[0].lower() == '/info'):
                    print "Grabbing info" 
                    info(bot,chat_id,text.partition(' ')[2].strip("\"\""))
                elif(text.split()[0].lower() == '/watch'):
                    print "Watching tv show"
                    inf = text.split(' ',1)[1]
                    watch(bot,chat_id,inf)
                elif(text.split()[0].lower() == '/list'):
                    print "Listing tv show"
                    inf = text.split(' ',1)[1]
                    flist(bot,chat_id,inf)


def random(bot,chat_id):
    conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '\\television.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM show ORDER BY RANDOM() LIMIT 1")
    r = cursor.fetchone()
    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    bot.sendMessage(chat_id,text="%s\nNow watching: *%s*" % (r[0].strip('[]').replace("'",""),r[4]),parse_mode=telegram.ParseMode.MARKDOWN)
def watch(bot,chat_id,inf):
    try:
        temp = shlex.split(str(inf))
        print temp
        name = temp[0].strip("\"\"")
        print name
        season = temp[1]
        print season
        episode = temp[2]
        print episode
        conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '\\television.db')
        cursor = conn.cursor()
        se = "%%Season %s Episode %s%%" % (season,episode)
        sn = name
        cursor.execute("SELECT episode_link_direct,name,episode_name FROM show WHERE episode_name LIKE ? AND name LIKE ?", (se,sn))
        r = cursor.fetchone()
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        bot.sendMessage(chat_id,text="%s\nNow watching: *%s*" % (r[0].strip('[]').replace("'",""),r[2]),parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        bot.sendPhoto(chat_id,photo="http://24.media.tumblr.com/c2088c3c87a89f3fe156fcfd9104205e/tumblr_mzl0z5VYmJ1sp41dro4_500.gif")
        bot.sendMessage(chat_id,text="I can't find it!")
def info(bot,chat_id,series):
    payload = {'q':series}
    r = requests.get("http://api.tvmaze.com/singlesearch/shows",params=payload)
    try:
        jo = r.json()
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        bot.sendPhoto(chat_id=chat_id,photo=jo['image']['original'])
        genres = ""
        for genre in jo['genres']:
            genres += "%s " % genre
        TAG_RE = re.compile(r'<[^>]+>')
        NUM_RE = re.compile(r'^[0-9]*$')
        bot.sendMessage(chat_id,text=
            "Rating: %s\nLanguage: %s\nRuntime: %s min\nStatus: %s\nGenre: %s\nSummary: %s" % 
            (unicode(jo['rating']),jo['language'],jo['runtime'],jo['status'],genres,TAG_RE.sub('', jo['summary'])))
    except:
        pass
def flist(bot,chat_id,inf):
    try:
        temp = shlex.split(str(inf))
        name = temp[0].strip("\"\"")
        try:
            season = temp[1]
        except:
            season='1'
        conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '\\television.db')
        series_name = "\"" + name + "\""
        season_name = season.replace("",'%% %%')
        cursor = conn.cursor()
        custom_keyboard = [["Moar","Stop"]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        tstr = ""
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        for i,row in enumerate(cursor.execute("SELECT episode_name FROM show WHERE name LIKE %s AND episode_name LIKE \'%%Season %s %%\'" % (series_name,season))):
             tstr+= row[0].replace(u'\u2013','-').replace(u"\u2019", "'") + "\n"
             if i % 20 == 0 and i != 0:
               bot.sendMessage(chat_id,text=tstr);
               tstr=''
        bot.sendMessage(chat_id,text=tstr);
    except:
        pass


if __name__ == '__main__':
    main()