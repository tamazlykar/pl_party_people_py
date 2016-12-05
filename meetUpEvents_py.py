import sys
import re
import requests
import time

from http.server import BaseHTTPRequestHandler, HTTPServer

messageBody = ''
cssStyle = '<style>img {width: 558px;} #header {text-align: center;    padding-bottom: 30px;}#main {    width: 600px;    margin: 0 auto;}#nextWeek {    font-size: 24px;}.dayOfWeek h2 {    text-align: center;}.event {    border: 1px solid black;    margin-bottom: 5px;}.event h3 {    text-align: center;}.event .date{    text-align: right;    padding-top: 0px;    padding-right: 30px;    padding-left: 0px;    padding-bottom: 10px;}.event .description {    padding-top: 0px;    padding-right: 20px;    padding-left: 20px;    padding-bottom: 0px;}.event .address {    text-align: right;    padding-right: 30px;} a{width: 558px; word-break: break-all;}</style>'



class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)

        self.send_header('Content-type', 'text/html')
        self.end_headers()

        htmlBeg = '<html><head><title>MeetUP Events for your next week in Seattle</title>' + cssStyle + '</head><body>' + \
            '<div id="header"><h1>MeetUP Events for your next week in Seattle</h1></div><div id="main">'
        message = messageBody
        htmlEnd = '</div></body></html>'
        self.wfile.write(bytes(htmlBeg + message + htmlEnd, "utf8"))
        return


def run():
    print('starting server...')

    # Server settings
    server_address = ('127.0.0.1', 5555)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('server running on 127.0.0.1:5555')
    httpd.serve_forever()


def getJsonRequest():
    url = 'https://api.meetup.com/2/categories?key=676e713e5f123c3f786f2277597a7a43&photo-host=public&page=5'
    url = 'https://api.meetup.com/2/open_events?key=676e713e5f123c3f786f2277597a7a43&' + \
        'photo-host=public' + \
        '&zip=98101&' + \
        'topic=web,machine-learning,softwaredev,computer-programming,web-development&' + \
        'category=34&' + \
        'time=' + str(getNewWeekInMs()) + ', ' + str(getEndOfNewWeekInMs(getNewWeekInMs()))+ '&' + \
        'only=name,description,time,venue'
    site = requests.get(url)
    return site.json()


def buildHTML(events):
    def createDayOfWeek(events):
        if (len(events) == 0):
            return ''
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        beginnig = '<div class="dayOfWeek"><h2>' + days[events[0]['weekDay']] +  '</h2>'
        innerHtml = ''
        ending = '</div>'
        for event in events:
            innerHtml = innerHtml + createEventHTML(event)
        return beginnig + innerHtml + ending

    def createEventHTML(event):
        def createName(name):
            return '<h3>' + name + '</h3>'

        def createDescription(desc):
            return '<div class="description">' + desc + '</div>'

        def createAddress(addr):
            return '<div class="address">' + addr + '</div>'

        def createDate(date):
            return '<div class="date">' + date + '</div>'

        result = '<div class="event">'
        if ('name' in event):
            result += createName(event['name'])
        if ('description' in event):
            result += createDescription(event['description'])
        if ('address' in event):
            result += createAddress(event['address'])
        if ('time' in event):
            result += createDate(event['time'])
        return result + '</div>'

    html = ''
    for day in range(7):
        dayEvents = []
        for event in events:
            if (event['weekDay'] == day):
                dayEvents.append(event)
        html = html + createDayOfWeek(dayEvents)

    return html


def transformData(data):
    def getTimeTuple(msec):
        seattle_time_offset = 28800
        sec = msec//1000
        return time.gmtime(sec-seattle_time_offset)

    def convertTime(msec):
        t = getTimeTuple(msec)
        return time.asctime(t)

    def getDayOfWeek(msec):
        t = getTimeTuple(msec)
        return t.tm_wday

    results = data['results']
    for event in results:
        event['weekDay'] = getDayOfWeek(event['time'])
        event['time'] = convertTime(event['time'])
        if ('venue' in event):
            addr = event['venue']
            event['address'] = addr['localized_country_name'] + ', ' + \
                addr['city'] + ', ' + \
                addr['address_1'] + ', ' + \
                addr['name']
        else:
            event['address'] = ''

    return results


def getNewWeekInMs():
    t = time.time()
    t = round(t)
    newWeek = t + (7 - (time.localtime().tm_wday + 1)%7  + 1) * 24 * 60 * 60
    return newWeek * 1000

def getEndOfNewWeekInMs(newWeek):
    return newWeek + 7 * 24 * 60 * 60 * 1000 


getNewWeekInMs()
newData = transformData(getJsonRequest())
messageBody = buildHTML(newData)
run()

# 0123456
# 0123456
