import kivy
kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.app import Builder
from samplerateview import *
from utils import *
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.widgets.scrollcontainer import ScrollContainer

GPS_CHANNELS_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/gpschannelsview.kv'
            
class GPSChannelsView(BaseConfigView):
    gpsConfig = None
    lap_config = None
    
    def __init__(self, **kwargs):
        Builder.load_file(GPS_CHANNELS_VIEW_KV)            
        super(GPSChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.ids.sr.bind(on_sample_rate = self.on_sample_rate)
                
    def onPosActive(self, instance, value):
        if self.gpsConfig:
            self.gpsConfig.positionEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')
                    
    def onSpeedActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.speedEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')
                        
    def onDistActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.distanceEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')
                                                
    def onAltitudeActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.altitudeEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')

    def onSatsActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.satellitesEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')
                
    def onGpsQualityActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.qualityEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')

    def onGpsDOPActive(self, instance, value):
        if self.gpsConfig:        
            self.gpsConfig.DOPEnabled = 1 if value else 0
            self.gpsConfig.stale = True
            self.dispatch('on_modified')

    def on_sample_rate(self, instance, value):
        if self.gpsConfig:
            self.gpsConfig.sampleRate = value
            self.gpsConfig.stale = True
            self.dispatch('on_modified')
            if self.lap_config.primary_stats_enabled():
                self.lap_config.set_primary_stats(value)
                    
    def on_config_updated(self, rc_cfg):
        gpsConfig = rc_cfg.gpsConfig
        self.ids.sr.setValue(gpsConfig.sampleRate, rc_cfg.capabilities.sample_rates.gps)
        self.ids.position.active = gpsConfig.positionEnabled
        self.ids.speed.active = gpsConfig.speedEnabled
        self.ids.distance.active = gpsConfig.distanceEnabled
        self.ids.altitude.active = gpsConfig.altitudeEnabled
        self.ids.satellites.active = gpsConfig.satellitesEnabled
        self.ids.quality.active = gpsConfig.qualityEnabled
        self.ids.dop.active = gpsConfig.DOPEnabled
        self.gpsConfig = gpsConfig
        self.lap_config = rc_cfg.lapConfig
        