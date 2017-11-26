#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
import ConfigParser
import re, sys


# On recupere l' user et le pass du fichier de config
config = ConfigParser.RawConfigParser()
config.read('arretsurimage.cfg')
login = config.get('asi', 'user')
password = config.get('asi', 'password')


# Telecharge le flux rss
urlFlux = sys.argv[1]
strFlux = urllib.urlopen(urlFlux).read()

# Recupere les items
compItems = re.compile('<item>(.*?)</item>', re.DOTALL)
items = re.findall(compItems, strFlux)

# Recupere le nom de l'emission
nomEmission = re.findall('<title>([^<]*)</title>', strFlux)[0]

# On ecrit le fichier rss
fichierRss = open(sys.argv[2], 'w')
fichierRss.write('''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
<channel>
<title>%s</title>'''%(nomEmission))

# On active le support des cookies pour urllib2
cookiejar = cookielib.CookieJar()
urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

# On envoie login/password au site qui nous renvoie un cookie de session
values = {'username':login, 'password':password }
data = urllib.urlencode(values)
request = urllib2.Request("http://www.arretsurimages.net/forum/login.php", data)
url = urlOpener.open(request)  # Notre cookiejar reçoit automatiquement les cookies
page = url.read(50000)

# Parcourt les items
for item in items:
    
    # Recupere l'url de la page
    urlPage = re.findall('<link>(.*)</link>', item)[0]

    # Recupere la page de l'emission
    #req = urllib2.Request(urlPage)
    resp = urlOpener.open(urlPage)
    strPage = resp.read()

    # Recuper la date de publication de l'episode
    datePub = re.findall('<pubDate>([^<]*)</pubDate>', item)[0]

    # Recupere le titre de l'emission
    titre = re.findall('<title>([^<]*)</title>', item)[0]

    # Recupere l'url de la page du fichier mp3
    urlPageMp3 = re.findall('<a href="([^"]*)" target="_blank" class="bouton-MP3"></a>', strPage)[0]

    # Recupere la page contenant l'url du fichier mp3
    resp = urlOpener.open(urlPageMp3)
    strPageMp3 = resp.read()
   
    # Recupere l'url final du fichier mp3
    #urlMp3 = re.findall("<a href='([^']*)'>cliquer ici</a>", strPageMp3)[0]
    urlMp3 = re.findall('<a id="file" href="([^"]*)" download>suivre ce lien</a>', strPageMp3)[0]

    # Ecrit l'item dans le fichier rss
    fichierRss.write('''


    
<item>
  <title>%s</title>
  <guid>%s</guid>
  <enclosure url="%s" type="audio/mpeg"/>
  <pubDate>%s</pubDate>
</item>'''%(titre, urlMp3, urlMp3, datePub))

# En ecrit la fin du flux rss
fichierRss.write('</channel></rss>')

fichierRss.close()
