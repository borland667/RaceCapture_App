import kivy
kivy.require('1.9.1')
from autosportlabs.racecapture.views.dashboard.tachometerview import TachometerView
from autosportlabs.racecapture.views.dashboard.rawchannelview import RawChannelView
from autosportlabs.racecapture.views.dashboard.laptimeview import LaptimeView
from autosportlabs.racecapture.views.dashboard.comboview import ComboView
from autosportlabs.racecapture.views.dashboard.gaugeview import GaugeView
from autosportlabs.racecapture.views.dashboard.widgets.digitalgauge import DigitalGauge
from autosportlabs.racecapture.views.dashboard.widgets.stopwatch import PitstopTimerView
from kivy.app import Builder
from kivy.uix.screenmanager import *
from autosportlabs.racecapture.views.dashboard.widgets.tachometer import Tachometer
from utils import kvFind, kvFindClass
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge
from kivy.logger import Logger
from kivy.clock import Clock

DASHBOARD_VIEW_KV = 'autosportlabs/racecapture/views/dashboard/dashboardview.kv'

class DashboardView(Screen):
    
    _settings = None
    _databus = None
    _screen_mgr = None
    _gaugeView = None
    _tachView = None
    _rawchannelView = None
    _laptimeView = None
    _comboView = None
    Builder.load_file(DASHBOARD_VIEW_KV)
    
    def __init__(self, **kwargs):
        super(DashboardView, self).__init__(**kwargs)
        self.register_event_type('on_tracks_updated')
        self._databus = kwargs.get('dataBus')
        self._settings = kwargs.get('settings')
        self._alert_widgets = {}
        self.init_view()

            
    def on_tracks_updated(self, trackmanager):
        pass
        
    def initGlobalGauges(self):
        databus = self._databus
        settings = self._settings
 
        activeGauges = list(kvFindClass(self, Gauge))
        
        for gauge in activeGauges:
            gauge.settings = settings
            gauge.data_bus = databus
         
    def init_view(self):
        screenMgr = kvFind(self, 'rcid', 'screens')
        
        databus = self._databus
        settings = self._settings
        
        self.initGlobalGauges()
        
        gaugeView = GaugeView(name='gaugeView', databus=databus, settings=settings)
        tachView = TachometerView(name='tachView', databus=databus, settings=settings)
        laptimeView = LaptimeView(name='laptimeView', databus=databus, settings=settings)
        #comboView = ComboView(name='comboView', databus=databus, settings=settings)
        rawChannelView = RawChannelView(name='rawchannelView', databus=databus, settings=settings)
        
        screenMgr.add_widget(gaugeView)
        screenMgr.add_widget(tachView)
        screenMgr.add_widget(laptimeView) 
        #screenMgr.add_widget(comboView)
        screenMgr.add_widget(rawChannelView)

        gauges = list(kvFindClass(self, DigitalGauge))

        for gauge in gauges:
            gauge.settings = self._settings
            gauge.data_bus = databus

        self._gaugeView = gaugeView
        self._tachView = tachView
        self._rawchannelView = rawChannelView
        self._laptimeView = laptimeView
        #self._comboView = comboView
        self._screen_mgr = screenMgr
        
        self._alert_widgets['pit_stop'] = PitstopTimerView(databus, 'Pit Stop')
        
        databus.start_update()
        Clock.schedule_once(lambda dt: self._show_last_view())
        
        

    def on_nav_left(self):
        self._screen_mgr.transition=SlideTransition(direction='right')
        self._show_screen(self._screen_mgr.previous())

    def on_nav_right(self):
        self._screen_mgr.transition=SlideTransition(direction='left')
        self._show_screen(self._screen_mgr.next())

    def _show_screen(self, screen):
        self._screen_mgr.current = screen
        self._settings.userPrefs.set_pref('preferences', 'last_dash_screen', screen)

    def _show_last_view(self):
        last_screen_name = self._settings.userPrefs.get_pref('preferences', 'last_dash_screen')
        self._screen_mgr.current = last_screen_name
