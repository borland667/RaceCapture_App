import kivy
kivy.require('1.9.0')
from kivy.app import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.spinner import SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from iconbutton import IconButton
from settingsview import SettingsSwitch
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.config.rcpconfig import *
from autosportlabs.racecapture.theme.color import ColorScheme
from fieldlabel import FieldLabel
from utils import *
import os

from mappedspinner import MappedSpinner

CAN_CHANNELS_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/canchannelsview.kv'

class LargeSpinnerOption(SpinnerOption):
    pass

class LargeMappedSpinner(MappedSpinner):
    pass
    
class LargeFieldLabel(FieldLabel):
    pass

class LargeTextInput(TextInput):
    pass

class CANChannelConfigView(BoxLayout):
    
    def __init__(self, can_channel_cfg, channels, max_sample_rate, can_filters, **kwargs):
        super(CANChannelConfigView, self).__init__(**kwargs)
        self.can_channel_cfg = can_channel_cfg
        self.channels = channels
        self.max_sample_rate = max_sample_rate
        self.can_filters = can_filters
        self.init_view()
    
    def on_sample_rate(self, instance, value):
        if self.can_channel_cfg:
            self.can_channel_cfg.sampleRate = instance.getValueFromKey(value)

    def init_view(self):
        channel_editor = self.ids.chan_id
        channel_editor.on_channels_updated(self.channels)
        channel_editor.setValue(self.can_channel_cfg)
        
        sample_rate_spinner = self.ids.sr
        sample_rate_spinner.set_max_rate(self.max_sample_rate)
        sample_rate_spinner.setFromValue(self.can_channel_cfg.sampleRate)
        
        self.ids.endian.setValueMap({0: 'Big (MSB)', 1: 'Small (LSB)'}, 0)
        self.update_mapping_spinners()
        
        self.ids.filters.setValueMap(self.can_filters.filters, self.can_filters.default_value)

    def on_bit_mode(self, instance, value):
        print('bit mode ' + str(value))
        self.set_mapping_choices(value)

    def update_mapping_spinners(self):
        bit_mode = self.can_channel_cfg.bit_offset % 8 and self.can_channel_cfg.bit_length % 8
        self.set_mapping_choices(bit_mode)
        
    def set_mapping_choices(self, bit_mode):
        choices = 63 if bit_mode else 7
        self.ids.offset.setValueMap(self.create_bit_choices(choices), 0)
        self.ids.length.setValueMap(self.create_bit_choices(1 + choices), 0)

    def create_bit_choices(self, max_choices):
        bit_choices = {}
        for i in range(0,max_choices + 1):
            bit_choices[i]=str(i)
        return bit_choices

class CANFilters(object):
    
    filters = None
    default_value = None
    def __init__(self, base_dir, **kwargs):
        super(CANFilters, self).__init__(**kwargs)
        self.load_CAN_filters(base_dir)

    
    def load_CAN_filters(self, base_dir):
        if self.filters != None:
            return
        try:
            print("loading can filters")
            self.filters = {}
            can_filters_json = open(os.path.join(base_dir, 'resource', 'settings', 'can_channel_filters.json'))
            can_filters = json.load(can_filters_json)['can_channel_filters']
            for k in sorted(can_filters.iterkeys()):
                if not self.default_value:
                    self.default_value = k 
                self.filters[int(k)] = can_filters[k] 
        except Exception as detail:
            raise Exception('Error loading CAN filters: ' + str(detail))

class CANChannelView(BoxLayout):
    channels = None
    can_channel_cfg = None
    max_sample_rate = 0
    channel_index = 0

    def __init__(self, channel_index, can_channel_cfg, max_sample_rate, channels, **kwargs):
        super(CANChannelView, self).__init__(**kwargs)
        self.channel_index = channel_index
        self.can_channel_cfg = can_channel_cfg
        self.max_sample_rate = max_sample_rate
        self.channels = channels
        self.register_event_type('on_delete_channel')
        self.register_event_type('on_customize_channel')
        self.register_event_type('on_modified')
        self.set_channel()
            
    def on_modified(self):
        pass

    def on_sample_rate(self, instance, value):
        self.can_channel_cfg.sampleRate = instance.getValueFromKey(value)
        self.dispatch('on_modified')
                    
    def on_delete_channel(self, channel_index):
        pass
    
    def on_customize_channel(self, channel_index):
        pass
    
    def on_delete(self):
        self.dispatch('on_delete_channel', self.channel_index)
    
    def on_customize(self):
        self.dispatch('on_customize_channel', self.channel_index)
        
    def set_channel(self):
        sample_rate_spinner = self.ids.sr
        sample_rate_spinner.set_max_rate(self.max_sample_rate)        
        sample_rate_spinner.setFromValue(self.can_channel_cfg.sampleRate)
        
        self.ids.channel_name.text = '{}'.format(self.can_channel_cfg.name)
        self.ids.can_bus.text = '{}'.format(self.can_channel_cfg.can_channel)
        self.ids.can_id.text = '{}'.format(self.can_channel_cfg.can_id)
        self.ids.can_offset_len.text = u'{} -> {}'.format(self.can_channel_cfg.bit_offset, self.can_channel_cfg.bit_length)
        self.ids.can_formula.text = u'(A \u00D7 {}) + {}'.format(self.can_channel_cfg.multiplier, self.can_channel_cfg.adder)
        
                
class CANChannelsView(BaseConfigView):
    DEFAULT_CAN_SAMPLE_RATE = 1    
    can_channels_cfg = None
    max_sample_rate = 0
    can_grid = None
    can_channels_settings = None
    can_filters = None
    
    def __init__(self, **kwargs):
        Builder.load_file(CAN_CHANNELS_VIEW_KV)
        super(CANChannelsView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')
        self.can_grid = self.ids.can_grid
        can_channels_enable = self.ids.can_channels_enable
        can_channels_enable.bind(on_setting=self.on_can_channels_enabled)
        can_channels_enable.setControl(SettingsSwitch())
        self.update_view_enabled()
        self.can_filters = CANFilters(kwargs.get('base_dir'))

    def on_modified(self, *args):
        if self.can_channels_cfg:
            self.can_channels_cfg.stale = True
            self.dispatch('on_config_modified', *args)

    def on_can_channels_enabled(self, instance, value):
        if self.can_channels_cfg:
            self.can_channels_cfg.enabled = value
            self.dispatch('on_modified')
                    
    def on_config_updated(self, rc_cfg):
        can_channels_cfg = rc_cfg.can_channels
        max_sample_rate = rc_cfg.capabilities.sample_rates.sensor
        self.ids.can_channels_enable.setValue(can_channels_cfg.enabled)
        
        self.reload_can_channel_grid(can_channels_cfg, max_sample_rate)
        self.can_channels_cfg = can_channels_cfg
        self.max_sample_rate = max_sample_rate
        self.update_view_enabled()

    def update_view_enabled(self):
        add_disabled = True
        if self.can_channels_cfg:
            if len(self.can_channels_cfg.channels) < CAN_CHANNELS_MAX:
                add_disabled = False
                
        self.ids.add_can_channel.disabled = add_disabled
            
    def add_can_channel(self, index, can_channel_cfg, max_sample_rate):
        channel_view = CANChannelView(index, can_channel_cfg, max_sample_rate, self.channels)
        channel_view.bind(on_delete_channel=self.on_delete_channel)
        channel_view.bind(on_customize_channel=self.on_customize_channel)
        channel_view.bind(on_modified=self.on_modified)
        self.can_grid.add_widget(channel_view)

    def reload_can_channel_grid(self, can_channels_cfg, max_sample_rate):
        self.can_grid.clear_widgets()
        for i in range(len(can_channels_cfg.channels)):
            can_channel_cfg = can_channels_cfg.channels[i]
            self.add_can_channel(i, can_channel_cfg, max_sample_rate)
        self.update_view_enabled()
        
    def on_add_can_channel(self):
        if (self.can_channels_cfg):
            can_channel = CANChannel()
            can_channel.sampleRate = self.DEFAULT_CAN_SAMPLE_RATE
            self.can_channels_cfg.channels.append(can_channel)
            self.add_can_channel(len(self.can_channels_cfg.channels) - 1, can_channel, self.max_sample_rate)
            self.update_view_enabled()
            self.dispatch('on_modified')

    def on_delete_channel(self, instance, channel_index):
        del self.can_channels_cfg.channels[channel_index]
        self.reload_can_channel_grid(self.can_channels_cfg, self.max_sample_rate)
        self.dispatch('on_modified')

    def on_customize_channel(self, instance, channel_index):
        def popup_dismissed():
            pass
            
        content = CANChannelConfigView(self.can_channels_cfg.channels[channel_index], self.channels, self.max_sample_rate, self.can_filters)
        popup = Popup(title="Customize CAN Mapping", content=content, size_hint=(0.75, 0.75))
        popup.bind(on_dismiss=popup_dismissed)
        popup.open()
        self._popup = popup