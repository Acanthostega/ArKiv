#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# import kivy
# kivy.require('1.0.6') # replace with your current kivy version !
import feedparser
import urllib

from kivy.app import App
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel

CATEGORIES = {
    "Astrophysics":
    {
        "Astrophysics of Galaxies": {
            "search_query": "cat:astro-ph.GA",
            "start": 0,
            "max_results": 10,
        },
        "Cosmology\nand Non-galactic Astrophysics": {
            "search_query": "cat:astro-ph.CO",
            "start": 0,
            "max_results": 10,
        },
        "Earth and Planetary Astrophysics": {
            "search_query": "cat:astro-ph.EP",
            "start": 0,
            "max_results": 10,
        },
        "High Energy\nAstrophysical Phenomena": {
            "search_query": "cat:astro-ph.HE",
            "start": 0,
            "max_results": 10,
        },
        "Instrumentation\nand Methods for Astrophysics": {
            "search_query": "cat:astro-ph.IM",
            "start": 0,
            "max_results": 10,
        },
        "Solar and Stellar Astrophysics": {
            "search_query": "cat:astro-ph.SR",
            "start": 0,
            "max_results": 10,
        },
    },
    "Condensed Matter":
    {
        "Disordered Systems\nand Neural Networks": {
            "search_query": "cat:cond-mat.dis-nn",
            "start": 0,
            "max_results": 10,
        },

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


class Menu(TreeView):
    pass


class MyBar(BoxLayout):
    pass


class CategoryView(BoxLayout):

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


class Category(TreeViewLabel):

    layout = ObjectProperty()


class SubCategory(Button, TreeViewNode):

    view = ObjectProperty()

    def on_press(self):
        self.makeView()

    def makeView(self):

        # create a new screen
        self.view = CategoryView(name=self.text)

        try:
            self.screenManager.remove_widget(self.screenManager.main_panel)
        except Exception as e:
            print e
        self.screenManager.add_widget(self.view)

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


class ArkivRoot(BoxLayout):
    pass


class ArKivApp(App):

    def build(self):
        root = ArkivRoot()
        nav = NavigationDrawer()
        root.add_widget(nav)
        nav.anim_type = "slide_above_simple"
        menu = Menu()
        for name, category in CATEGORIES.items():
            view = Category(text=name)
            for subname, v in category.items():
                sub = SubCategory()
                sub.properties = v
                sub.text = subname
                sub.addScreenManager(nav)
                menu.add_node(sub, view)
            menu.add_node(view)
        nav.add_widget(menu)
        return root


if __name__ == '__main__':
    ArKivApp().run()

# vim: set tw=79 :
