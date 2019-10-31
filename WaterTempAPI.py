#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import bs4

URLs = ['https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_au_hoengg.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_unterer_letten.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/flussbad_oberer_letten.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/strandbad_tiefenbrunnen.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/strandbad_wollishofen.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/freibad_seebach.html',
        'https://www.stadt-zuerich.ch/ssd/de/index/sport/schwimmen/sommerbaeder/freibad_zwischen_den_hoelzern.html']

class WaterTempAPI():

    def __init__(self):
        super().__init__()


    def getTemp(self, urlIndex = 0):

        l = len(URLs)
        if urlIndex < 0 or urlIndex > l -1:
            return('parameter must be between 0 and ' + str(l-1), 'err', 'err')
        self.urlIndex = urlIndex

        try:
            res = requests.get(URLs[self.urlIndex])
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, "html.parser")

            title = soup.title.string
            tagCont = soup.findAll(id='baederinfos_temperature_value')
            temp = str(tagCont[0])

            return(title, temp)

        except requests.exceptions.RequestException as e:
            print(e)

