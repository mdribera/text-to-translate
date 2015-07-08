#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

import creds
import os
import logging
from twilio.rest import TwilioRestClient
import urllib, urllib2
import json as simplejson

account = creds.twilio['account']
token = creds.twilio['token']
client = TwilioRestClient(account, token)

    
def get_languages():
    f = open('langabbrev.csv', 'r')
    dic_of_lang = {}
    for x in f:
        data = x.rstrip().replace('\"', '').split(',')
        dic_of_lang[data[0].lower()] = data[1]
    languages = dic_of_lang
    return languages

languages = get_languages()

class MainHandler(webapp.RequestHandler):
    def get(self):
        # grab info from request
        raw = self.request.get("Body",None).split("->")
        phone_number = self.request.get("From",None)
        # if there was a separator (->)
        if len(raw) == 2:
            # decipher language command and code
            command = get_language_code(raw[1].strip())
            # if it's a real language
            if command != False:
                source = raw[0].strip()
                response_data = translate(source, command)
                response_str = response_data[1] + "->" + response_data[0]
            # if it's not something we recognize
            else:
                response_str = "Sorry, chap! We cannot find that desired language in our system."
                # response_str = raw
        # if there was no separator (->)
        else:
            response_str = "Enter a phrase followed by the language you want it translated to separated by \"->\" Eg: \"Guten Tag! -> english\" No, we can't translate texts from your parents."
        # send response to phone number
        print response_str.encode('utf-8')
        client.sms.messages.create(to=phone_number, from_="12068553672", body= response_str)
        
def get_language_code(language):
    if language.lower() in languages:
        return languages[language.lower()]
    elif language.lower() in languages.values():
        return language.lower() 
    else:
        return False
    
def translate(q, target):
    base_url = "https://www.googleapis.com/language/translate/v2?key=" + creds.google['key'] + "&"
    params = {}
    params['q'] = q
    params['target'] = target
    
    url = base_url + urllib.urlencode(params)

    translated_results = get_safe(url)
    translated_str = translated_results.read()
    translated = simplejson.loads(translated_str)
    answer = [translated['data']['translations'][0]['translatedText'], 
              translated['data']['translations'][0]['detectedSourceLanguage']]
    return answer
      
def get_safe(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        return None

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
#    get_languages()
    main()
