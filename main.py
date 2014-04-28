#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# import kivy
# kivy.require('1.0.6') # replace with your current kivy version !
import feedparser
import urllib

from kivy.app import App
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label

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

        # for search_query
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


class MyBar(BoxLayout):
    pass


class CategoryView(Screen):

    carousel = ObjectProperty()
    bar = ObjectProperty()
    pass


class CategoryList(Accordion):

    def createList(self, rss):

        # loop over entries in the request
        for feed in rss["entries"]:

            # create an item with title of the article
            item = CategoryArticle(title=feed["title"])

            # create a label and update values
            item.label.text = item.label.text % (
                ", ".join(
                    [
                        x["name"] for x in feed["authors"]
                    ]
                ),
                feed["summary_detail"]["value"],
            )

            # add the item to the accordion
            self.add_widget(item)


class CategoryArticle(AccordionItem):
    label = ObjectProperty()


class CategoryArticleLabel(Label):
    pass


class Category(Button):

    view = ObjectProperty()

    def on_press(self):
        self.makeView()

    def makeView(self):

        # create a new screen
        self.view = CategoryView(name=self.text)

        # switch to the screen
        self.screenManager.switch_to(
            self.view,
            direction="right",
            duration=1.,
        )

        # request the range of values
        self.makeRequest()

    def makeRequest(self):
        req = ArxivAPI(
            self.properties,
            on_success=self.success,
            on_failure=self.failure,
        )
        req.wait()

    def success(self, request, result):

        # parse the result of the request for RSS feeds
        rss = feedparser.parse(result)

        # create view of the flux
        self.createView(rss)

    def failure(self, request, result):
        if self.properties["start"] != 0:
            self.properties["start"] -= self.properties["max_results"]

    def createView(self, rss):

        # create an accordion layout
        accordion = CategoryList()
        accordion.createList(rss)

        # add the accordion
        self.view.carousel.add_widget(accordion)

    def addScreenManager(self, screen):
        self.screenManager = screen


class ArkivRoot(ScreenManager):
    menu = ObjectProperty()
    layout = ObjectProperty()


class ArKivApp(App):

    def build(self):
        root = ArkivRoot()
        root.layout.bind(minimum_height=root.layout.setter('height'))
        for k, v in CATEGORIES.items():
            but = Category(text=k)
            but.addScreenManager(root)
            but.properties = v
            root.layout.add_widget(but)
        return root


if __name__ == '__main__':
    ArKivApp().run()

# vim: set tw=79 :
