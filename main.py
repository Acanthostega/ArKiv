#!/usr/bin/env python2
#-*- coding: utf-8 -*-

#import kivy
#kivy.require('1.0.6') # replace with your current kivy version !
import feedparser
import urllib

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
#from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen

CATEGORIES = {
    "Astrophysics": {
        "search_query": "cat:astro-ph",
        "start": 0,
        "max_results": 10,
    }
}


class Parameters(object):

    def __init__(self):

        self.params = list()

    def __call__(self):

        # loop over list and create a good one
        tmp = [x[0] + ":" + str(x[1]) for x in self.params]
        tmp2 = list()
        for x, y in zip(tmp, self.params):
            if y != "":
                tmp2.append(x + "+" + y + "+")
            else:
                tmp2.append(x)
        return "".join(tmp2)

    def append(self, x):

        if len(x) != 3:
            self.params.append(x)


class QueryConstruct(object):

    def __call__(self, query):

        #for search_query
        if "search_query" in query:
            if not isinstance(query["search_query"], str):
                query["search_query"] = query["search_query"]()

        # encode the url
        return urllib.urlencode(query)


class ArxivAPI(UrlRequest):

    base_url = 'http://export.arxiv.org/api/query?'

    def __init__(self, query, *args, **kwargs):

        url = self.base_url + QueryConstruct()(query)
        tmp = kwargs.copy()
        tmp["url"] = url
        super(ArxivAPI, self).__init__(*args, **tmp)


class Primary(Button):

    def on_press(self):

        req = ArxivAPI(
            self.properties,
            on_success=self.success,
        )
        req.wait()

    def success(self, request, result):

        rss = feedparser.parse(result)
        print rss


class Arkiv(Screen):

    pass


class ArKivApp(App):

    def build(self):
        sm = ScreenManager()
        ar = Arkiv()
        sm.add_widget(ar)
        sc = ScrollView(size_hint_x=1)
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for k, v in CATEGORIES.items():
            but = Primary(text=k, size_hint_y=None, height=40)
            but.properties = v
            layout.add_widget(but)
        sc.add_widget(layout)
        ar.add_widget(sc)
        return ar


if __name__ == '__main__':
    ArKivApp().run()

# vim: set tw=79 :
