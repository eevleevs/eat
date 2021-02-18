from bottle import abort, get, post, request, response, run, static_file
from bson import json_util
from datetime import datetime
import os
from pymongo import MongoClient
import quopri
import re


db = MongoClient(os.environ['MONGODB']).eat


@get('/')
def eat():
    return static_file('index.html', root='static')


@post('/')
def eat_hook():
    s = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:eatcal\r\n'
    m = re.search(r'K\S{1,6}re (\w*?) .*?\((\d*?)\)[\s\S]*?madplan([\s\S]*?)Tak fordi du er kunde hos os', request.body.read().decode())
    for i in re.findall(r'(\d{1,2})\/(\d{1,2})-(\d{4})[\s\S]*?\)([\s\S]*?)\(', m[3]):
        d = f'{i[2]}{i[1].zfill(2)}{i[0].zfill(2)}'
        try:
            i3 = quopri.decodestring(i[3]).decode()
        except ValueError:
            i3 = i[3]
        i3 = i3.replace('\n', ' ').strip()
        s += f'BEGIN:VEVENT\r\nUID:{d}\r\nDTSTART;VALUE=DATE:{d}\r\nDTEND;VALUE=DATE:{d}\r\nSUMMARY:{m[1]}: {i3}\r\nEND:VEVENT\r\n'
    s += 'END:VCALENDAR\r\n'
    id = f'{m[2]}{m[1].lower()}'
    db.eat.replace_one({'_id': id}, {'_id': id, 'date': datetime.utcnow(), 'text': s}, upsert=True)
    response.status = 201


@get(('/<id>.ics', '/<id>'))
def eat_cal(id):
    response.content_type = 'text/calendar; charset=utf-8'
    response.set_header('Cache-Control', 'no-cache, must-revalidate')
    try:
        return db.eat.find_one({'_id': id})['text']
    except TypeError:
        abort(404, 'Not found.')


if __name__ == '__main__':
    run(host='0.0.0.0', server='waitress')