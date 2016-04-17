import kivy
kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.app import Builder
from utils import *
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseMultiChannelConfigView, BaseChannelView
from autosportlabs.racecapture.config.rcpconfig import *
from mappedspinner import MappedSpinner
from kivy.metrics import dp

GPIO_CHANNELS_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/gpiochannelsview.kv'

class GPIOChannelsView(BaseMultiChannelConfigView):
    def __init__(self, **kwargs):
        Builder.load_file(GPIO_CHANNELS_VIEW_KV)
        super(GPIOChannelsView, self).__init__(**kwargs)
        self.channel_title = 'Digital Input/Output '
        self.accordion_item_height = dp(85)

    def channel_builder(self, index, max_sample_rate):
        editor = GPIOChannel(id = 'gpio' + str(index), channels=self.channels)
        editor.bind(on_modified = self.on_modified)
        if self.config:
            editor.on_config_updated(self.config.channels[index], max_sample_rate)
        return editor
    
    def get_specific_config(self, rcp_cfg):
        return rcp_cfg.gpioConfig
    
class GPIOModeSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(GPIOModeSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'Input', 1:'Output'}, 'Input')
        
class GPIOChannel(BaseChannelView):
    def __init__(self, **kwargs):
        super(GPIOChannel, self).__init__(**kwargs)
                    
    def on_mode(self, instance, value):
        if self.channelConfig:
            self.channelConfig.mode = instance.getValueFromKey(value)
            self.channelConfig.stale = True
            self.dispatch('on_modified', self.channelConfig)
            
    def on_config_updated(self, channelConfig, max_sample_rate):
        self.ids.sr.setValue(channelConfig.sampleRate, max_sample_rate)

        self.ids.chan_id.setValue(channelConfig)
        self.ids.mode.setFromValue(channelConfig.mode)
        self.channelConfig = channelConfig
