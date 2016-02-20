#!/bin/python
from kivy.app import App
from kivy.logger import LoggerHistory

from kivy.config import Config

from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.tabbedpanel import TabbedPanelHeader

from kivy.uix.slider import Slider
from  kivy.uix.switch import Switch

from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

from kivy.uix.screenmanager import SlideTransition

from kivy.network.urlrequest import UrlRequest
import urllib
import json

from kivy.storage.jsonstore import JsonStore

from requests.api import post
from sqlite3.dbapi2 import paramstyle

import random

import feedparser
import re
from operator import itemgetter

from datetime import datetime
from dateutil.parser import parse as datetimeparse

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.videoplayer import VideoPlayerPreview

        
from kivy.loader import Loader
from kivy.uix.image import Image

debug = False
   
if debug:
    print('Kvlang debug enabled')
    Builder.load_file('./assets/kvlang/debug.kv')

Builder.load_file('./assets/kvlang/main.kv')


class MyDataStore(object):
    def __init__(self, **kwargs):
        super(MyDataStore, self).__init__(**kwargs)
        
        self.debug = True
        
        if self.debug:
            print('[info] MyDataStore debug enabled')
            
        self.data_store = JsonStore('./dat.json')

        self.feedDict = dict()
        self.feedDict = list()
        self.entries = list()
        
        self.requires_update = False
        
        self.update_feeds(call_origin='MyDataStore')
        
        
                
    def update_feeds(self, call_origin):
        if debug:
            print('[info] updating feed list from {}'.format(call_origin))
            
        self.feedDict = self.get_rss_urls()
        self.entries = self.get_feed_entries()
        
                
    def build_rss_title_key(self, d):
            title = re.sub('[^0-9a-zA-Z]+', '_', d.feed.title).lower()
            return title
        
    def get_rss_urls(self):
        
        if self.requires_update:
            try:
                self.add_rss_feed("https://talkpython.fm/episodes/rss")
                self.get_rss_urls
                self.requires_update = False
            except:
                print('[error] get_rss_urls failed in MyDataStore')
        else:
            try:
                feeds = self.data_store.get('feeds')
                return feeds
            except:
                self.add_rss_feed("https://talkpython.fm/episodes/rss")
                self.get_rss_urls
                self.requires_update = False
    
    def get_feed_entries(self):
        try:
            entries = json.loads(self.data_store.get('feeds')['entries'])
            #print entries
            return entries
        except:
            return '[Fail] could not parse entries at get_feed_entries'
            
    def add_rss_feed(self, url):
        self.url = url
        self.post_dict_list = []
        
        try:
            d = feedparser.parse(self.url)
            
            self.status = d.status
            self.headers = d.headers
            self.title= d.feed.title
            self.rights= d.feed.rights
            self.subtitle= d.feed.subtitle
    
            for post in d.entries:
                self.post_dict_list.append({'published': str(datetimeparse(post.published)),
                                            'title': post.title,
                                            'link': post.link,
                                            'id': post.id,})
        except:
            if self.debug:
                message = '[Fail] add_rss_feed:', self.url
            else:
                message = '[Success] add_rss_feed', self.url
            return message
        
            
            
        try:
            feeds = self.data_store.get('feeds')[self.title]
            if self.debug:
                print '[success] found existing feeds', feeds
        except:
            if self.debug:
                print '[info] no feeds, adding default', self.title, self.url
                
            self.data_store.put('feeds', 
                                status= self.status, 
                                headers= self.headers, 
                                title=self.title, 
                                subtitle= self.subtitle, 
                                url=self.url, 
                                rights = self.rights,
                                entries=json.dumps(self.post_dict_list))     
            

class MyScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(MyScrollView, self).__init__(**kwargs)
        self.process_update = False
        
    def update_episodes(self, dt):
        App.get_running_app().sm.ids['entry_stack_layout'].mydata_store.requires_update = True
        App.get_running_app().sm.ids['entry_stack_layout'].mydata_store.update_feeds(call_origin='MyScrollView')
        App.get_running_app().sm.ids['entry_stack_layout'].update_list()
        self.process_update = False
        
    def on_scroll_move(self, touch):
        if self._get_uid('svavoid') in touch.ud:
            return False

        touch.push()
        touch.apply_transform_2d(self.to_local)
        if self.dispatch_children('on_scroll_move', touch):
            return True
        touch.pop()

        rv = True
        
        uid = self._get_uid()
        if not uid in touch.ud:
            self._touch = False
            return self.on_scroll_start(touch, False)
        ud = touch.ud[uid]
        mode = ud['mode']

        # check if the minimum distance has been travelled
        if mode == 'unknown' or mode == 'scroll':
            if not touch.ud['sv.handled']['x'] and self.do_scroll_x \
                    and self.effect_x:
                width = self.width
                if touch.ud.get('in_bar_x', False):
                    dx = touch.dx / float(width - width * self.hbar[1])
                    self.scroll_x = min(max(self.scroll_x + dx, 0.), 1.)
                    self._trigger_update_from_scroll()
                else:
                    if self.scroll_type != ['bars']:
                        self.effect_x.update(touch.x)
                if self.scroll_x < 0 or self.scroll_x > 1:
                    rv = False
                else:
                    touch.ud['sv.handled']['x'] = True
            if not touch.ud['sv.handled']['y'] and self.do_scroll_y \
                    and self.effect_y:
                height = self.height
                if touch.ud.get('in_bar_y', False):
                    dy = touch.dy / float(height - height * self.vbar[1])
                    self.scroll_y = min(max(self.scroll_y + dy, 0.), 1.)
                    self._trigger_update_from_scroll()
                else:
                    if self.scroll_type != ['bars']:
                        self.effect_y.update(touch.y)
                if self.scroll_y < 0 or self.scroll_y > 1:
                    rv = False
                else:
                    touch.ud['sv.handled']['y'] = True

                # checks if scrolling above top, updates episodes
                
                
                if self.scroll_y > 1 and not self.process_update:
                    rv = False
                    self.process_update = True
                    if self.update_episodes:
                        Clock.schedule_once(self.update_episodes, 2)
                        
                    if debug:
                        print('[info] update request detected')
                else:
                    touch.ud['sv.handled']['y'] = True
   

                    
                
        if mode == 'unknown':
            ud['dx'] += abs(touch.dx)
            ud['dy'] += abs(touch.dy)
            if ((ud['dx'] > self.scroll_distance) or
                    (ud['dy'] > self.scroll_distance)):
                if not self.do_scroll_x and not self.do_scroll_y:
                    # touch is in parent, but _change expects window coords
                    touch.push()
                    touch.apply_transform_2d(self.to_local)
                    touch.apply_transform_2d(self.to_window)
                    self._change_touch_mode()
                    touch.pop()
                    return
                mode = 'scroll'
            ud['mode'] = mode

        if mode == 'scroll':
            ud['dt'] = touch.time_update - ud['time']
            ud['time'] = touch.time_update
            ud['user_stopped'] = True

        return rv
           
            
class MyAudioPlayer(VideoPlayer):
    def __init__(self, **kwargs):
        super(MyAudioPlayer, self).__init__(**kwargs)
        
    def _load_thumbnail(self):
        pass
   
class MyProgressBar(ProgressBar):   
    def __init__(self, **kwargs):
        super(MyProgressBar, self).__init__(**kwargs)
            # Create the screen manager
        self.schedule = 0.5
        self.toggle_on = True
        self.fake_auto_load(self.schedule)
        self.title = "LOADING" 
        
        self.next_screen = 'show_screen'
        pass
            
    def load_text(self):
        return self.title
        
    def fake_auto_load(self, schedule):
        if self.toggle_on:
            Clock.schedule_interval(self.increase, schedule)            
            
    def increase(self, dt):
        if self.value < self.max:
            #print "auto-load"
            self.update(value=random.randrange(20, 50))
        else:
            self.toggle_on = False
            Clock.unschedule(self.increase)
            Clock.schedule_once(self.complete, 0)
            
            
    def update(self, value):
        if self.value < self.max:
            self.value += value
            
    def complete(self, dt):
            #print "COMPLETE LOADED"
            self.manager.transition = SlideTransition(direction='up')
            self.manager.current = 'show_screen'
            

   
class EntryStackLayout(StackLayout):
                                    
    def __init__(self, **kwargs):
        super(EntryStackLayout, self).__init__(**kwargs)
        '''
        Build a list of entries to be displayed on the app
        '''
        self.debug= True
        self.id = 'entry_stack_layout'
        self.name = 'entry_stack_layout'
        self.card_contents = StackLayout(size_hint = [1, 0.0225])    
        self.size_hint = (1,1)
        self.entry_widgets = []
        self.screen_manager = App.get_running_app().sm
        self.mydata_store = {}
        self.requires_update= False
        
        self.build_list()
        
        for i in self.entry_widgets:
            self.add_widget(i)
            

    
    def update_list(self):
        if self.debug:
            print('[info] clearing widgets')

        #self.requires_update = True
        self.card_contents = StackLayout(size_hint = [1, 0.0225])    
        self.size_hint = (1,1)   
        self.entry_widgets = [] 
        self.build_list()
        self.clear_widgets()  
          
        for i in self.entry_widgets:
            i.canvas.ask_update()
            self.add_widget(i)
            #print i.children


            
        
    def build_list(self):
        self.mydata_store = MyDataStore()
        self.data_store = self.mydata_store.data_store
        
        try:
            entries = json.loads(self.data_store.get('feeds')['entries'])
            #print('entries', entries)
        except:
            print('[error] build_list in EntryStackLayout', self.data_store)
        
        try:    
            entries_count = len(entries)
            
    
            self.card_contents.add_widget(Label(text="SCROLL UP TO CHECK FOR UPDATES",
                                           valign='top',
                                           halign='center',
                                           size_hint=[1.0, 0.05],
                                           text_size= [Window.width * 0.45, None],
                                           color=[0.3,0.3,0.3,1.0]))    
            for entry in entries:
                self.size_hint[1] += 0.35           
                self.card_contents.add_widget(Image(source = './assets/images/talkpython-nowrds.png', size_hint = [0.15,0.4]))
                
                self.card_contents.add_widget(Label(text=entry['title'],
                                               valign='top',
                                               size_hint=[0.85, 0.4], 
                                               text_size= [Window.width * 0.35, None]))
                
                self.card_contents.add_widget(MyAudioPlayer(source=entry['id'], 
                                                     thumbnail= './assets/images/talkpython.png',
                                                     size_hint = [1,0.4],
                                                     allow_fullscreen= False
                                                     ))
                
                #card_contents.add_widget(VideoPlayer(source="./assets/videos/hst_1.mpg", size_hint = [1,0.8]))
               
    
                
                self.entry_widgets.append(self.card_contents)
                self.card_contents = StackLayout(size_hint = [1, 0.0225])
        except:
            if debug: 
                print('[error] build_list in EntryStackLayout failed')
            
    
    
    def test_bind(self):
        print('test bind EntryStackLayout', self.test_data_store)

    def update_episodes(self):
        self.mydata_store.update_feeds('EntryStackLayout')
        
        
class PodCastListScreen(Screen):
    screen_manager = ObjectProperty(None, allownone=True)
    def __init__(self, **kwargs):
        super(PodCastListScreen, self).__init__(**kwargs)
        self.screen_manager = App.get_running_app().sm
        self.name = 'PodCastListScreen'
        
        #print('PodCastListScreen', self)
        
    pass

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
    pass


class MyRoot(ScreenManager):
    
    def __init__(self, debug, **kwargs):
        super(MyRoot, self).__init__(**kwargs)
        
        self.debug = True
        if self.debug:
            print('[info] MyRoot debug enabled')
           
        self.mydata_store = MyDataStore()
        self.data_store = self.mydata_store.data_store
    
        
        
class KivyApp(App):
    sm = ScreenManager()
    
    def __init__(self, **kwargs):
        super(KivyApp, self).__init__(**kwargs)
        self.sm = MyRoot(debug)
        
    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'key2': '42'
        })
               
    def build(self):
        return self.sm

if __name__ == '__main__':
    KivyApp().run()