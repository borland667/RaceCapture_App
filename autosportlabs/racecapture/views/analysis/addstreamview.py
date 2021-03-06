import os
from datetime import datetime
from threading import Thread
import kivy
kivy.require('1.9.1')
from kivy.app import Builder
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.screenmanager import Screen
from utils import kvFind
from kivy.adapters.listadapter import ListAdapter
from autosportlabs.uix.button.featurebutton import FeatureButton
from autosportlabs.uix.textwidget import FieldInput
from autosportlabs.racecapture.views.util.alertview import alertPopup, confirmPopup
from autosportlabs.racecapture.views.file.loaddialogview import LoadDialog
from autosportlabs.racecapture.views.file.savedialogview import SaveDialog
from autosportlabs.util.timeutil import format_time
from iconbutton import IconButton
from fieldlabel import FieldLabel
from iconbutton import LabelIconButton
from autosportlabs.uix.toast.kivytoast import toast

Builder.load_file('autosportlabs/racecapture/views/analysis/addstreamview.kv')

class AddStreamView(BoxLayout):
    def __init__(self, settings, datastore, **kwargs):
        super(AddStreamView, self).__init__(**kwargs)
        stream_select_view = self.ids.streamSelectScreen
        stream_select_view.bind(on_select_stream=self.on_select_stream)

        cloud_connect_view = self.ids.cloudConnectScreen
        cloud_connect_view.settings = settings
        cloud_connect_view.datastore = datastore

        wireless_connect_view = self.ids.wirelessConnectScreen
        wireless_connect_view.settings = settings
        wireless_connect_view.datastore = datastore

        file_connect_view = self.ids.fileConnectScreen
        file_connect_view.settings = settings
        file_connect_view.datastore = datastore
        file_connect_view.bind(on_connect_stream_complete=self.connect_stream_complete)
        file_connect_view.bind(on_connect_stream_start=self.connect_stream_start)

        session_import_view = self.ids.session_import_screen
        session_import_view.datastore = datastore
        session_import_view.bind(on_add=self.add_session)
        session_import_view.bind(on_delete=self.delete_session)
        session_import_view.bind(on_close=self.close)

        self.register_event_type('on_connect_stream_start')
        self.register_event_type('on_connect_stream_complete')
        self.register_event_type('on_add_session')
        self.register_event_type('on_delete_session')
        self.register_event_type('on_close')

    def add_session(self, instance, session):
        self.dispatch('on_add_session', session)

    def delete_session(self, instance, session):
        self.dispatch('on_delete_session', session)

    def on_delete_session(self, *args):
        pass

    def on_add_session(self, *args):
        pass

    def on_connect_stream_start(self, *args):
        pass

    def on_connect_stream_complete(self, *args):
        pass

    def on_select_stream(self, instance, stream_type):
        self.ids.screens.current = stream_type

    def connect_stream_start(self, *args):
        self.dispatch('on_connect_stream_start')

    def connect_stream_complete(self, instance, session_id):
        self.dispatch('on_connect_stream_complete', session_id)

    def close(self, *args):
        self.dispatch('on_close')

    def on_close(self, *args):
        pass

class AddStreamSelectView(Screen):
    def __init__(self, **kwargs):
        super(AddStreamSelectView, self).__init__(**kwargs)
        self.register_event_type('on_select_stream')

    def select_stream(self, stream):
        self.dispatch('on_select_stream', stream)

    def on_select_stream(self, stream):
        pass

class BaseStreamConnectView(Screen):
    settings = None
    datastore = None
    def __init__(self, **kwargs):
        super(BaseStreamConnectView, self).__init__(**kwargs)
        self.register_event_type('on_connect_stream_complete')
        self.register_event_type('on_connect_stream_start')

    def on_connect_stream_complete(self, *args):
        pass

    def on_connect_stream_start(self, *args):
        pass

class CloudConnectView(BaseStreamConnectView):
    pass

class WirelessConnectView(BaseStreamConnectView):
    pass

class FileConnectView(BaseStreamConnectView):
    def __init__(self, **kwargs):
        super(FileConnectView, self).__init__(**kwargs)

    def on_enter(self):
        log_import_view = self.ids.log_import
        log_import_view.bind(on_import_complete=self.import_complete)
        log_import_view.bind(on_import_start=self.import_start)
        log_import_view.datastore = self.datastore
        log_import_view.settings = self.settings

    def import_start(self, *args):
        self.dispatch('on_connect_stream_start')

    def import_complete(self, instance, session_id):
        self.dispatch('on_connect_stream_complete', session_id)


class SessionImportView(BaseStreamConnectView):

    def __init__(self, **kwargs):
        super(SessionImportView, self).__init__(**kwargs)
        self.register_event_type('on_add')
        self.register_event_type('on_delete')
        self.register_event_type('on_close')

    def on_enter(self, *args):
        # Find sessions, append to session list
        sessions = self.datastore.get_sessions()

        if len(sessions) == 0:
            self.ids.session_list.add_widget(Label(text="No saved sessions"))

        for session in sessions:
            session_view = SessionListItem(session)
            session_view.ids.name.text = session.name
            session_view.ids.date.text = format_time(datetime.fromtimestamp(session.date))
            session_view.bind(on_delete=self.delete_session)
            session_view.bind(on_add=self.add_session)

            self.ids.session_list.add_widget(session_view)

    def on_scroll(self, *args):
        pass

    def delete_session(self, list_item):
        self.datastore.delete_session(list_item.session.session_id)
        self.ids.session_list.remove_widget(list_item)
        self.dispatch('on_delete', list_item.session)
        toast("Session deleted", center_on=self)

    def add_session(self, list_item):
        self.dispatch('on_add', list_item.session)
        toast("Session loaded", center_on=self)

    def close(self, *args):
        self.dispatch('on_close')

    def on_add(self, *args):
        Logger.debug("SessionImportView: on_add: {}".format(args))

    def on_delete(self, *args):
        pass

    def on_close(self, *args):
        pass


class SessionListItem(BoxLayout):

    def __init__(self, session, **kwargs):
        super(SessionListItem, self).__init__(**kwargs)
        self.session = session
        self.register_event_type('on_delete')
        self.register_event_type('on_add')

    def delete_session(self, *args):
        popup = None

        def confirm_delete(instance, delete):
            if delete:
                self.dispatch('on_delete')
            popup.dismiss()

        popup = confirmPopup("Delete", "Are you sure you sure you want to delete session '{}'?".format(self.session.name),
                             confirm_delete)

    def add_session(self, *args):
        self.dispatch('on_add')

    def on_delete(self, *args):
        pass

    def on_add(self, *args):
        pass


class LogImportWidget(BoxLayout):
    datastore = ObjectProperty(None)
    settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LogImportWidget, self).__init__(**kwargs)
        self.register_event_type('on_import_complete')
        self.register_event_type('on_import_start')
        self._log_path = None

    def on_import_start(self, *args):
        pass

    def on_import_complete(self, session_id):
        pass

    def close_dstore_select(self, *args):
        self.datastore_select.dismiss()
        self.datastore_select = None

    def set_dstore_path(self, instance):
        filename = os.path.join(instance.path, instance.filename)
        if not filename.endswith('.sq3'):
            filename = filename + '.sq3'
        self.ids.dstore_path.text = filename
        self.datastore_select.dismiss()

    def select_dstore(self):
        ok_cb = self.close_dstore_select
        content = SaveDialog(ok=self.set_dstore_path,
                             cancel=self.close_dstore_select,
                             filters=['*' + '.sq3'])
        self.datastore_select = Popup(title="Select Datastore", content=content, size_hint=(0.9, 0.9))
        self.datastore_select.open()

    def close_log_select(self, *args):
        self._log_select.dismiss()
        self._log_select = None

    def set_log_path(self, instance):
        path = instance.selection[0]
        self._log_path = path
        base_name = self._extract_base_logfile_name(path)
        self.ids.session_name.text = base_name
        self.ids.log_path.text = base_name
        self.ids.import_button.disabled = False

        self._log_select.dismiss()
        self.set_import_file_path(instance.path)

    def _extract_base_logfile_name(self, path):
        session_name, file_extension = os.path.splitext(os.path.basename(path))
        return session_name

    def set_import_file_path(self, path):
        self.settings.userPrefs.set_pref('preferences', 'import_datalog_dir', path)

    def get_import_file_path(self):
        return self.settings.userPrefs.get_pref('preferences', 'import_datalog_dir')

    def select_log(self):
        ok_cb = self.close_log_select
        content = LoadDialog(ok=self.set_log_path,
                             cancel=self.close_log_select,
                             filters=['*' + '.LOG', '*' + '.log'],
                             user_path=self.get_import_file_path())
        self._log_select = Popup(title="Select Log", content=content, size_hint=(0.9, 0.9))
        self._log_select.open()

    def _loader_thread(self, logpath, session_name, session_notes):
        Clock.schedule_once(lambda dt: self.dispatch('on_import_start'))
        session_id = self.datastore.import_datalog(logpath, session_name, session_notes, self._update_progress)
        Clock.schedule_once(lambda dt: self.dispatch('on_import_complete', session_id))

    def _update_progress(self, percent_complete=0):
        if self.ids.current_status.text != "Loading log records":
            self.ids.current_status.text = "Loading log records"
        self.ids.log_load_progress.value = int(percent_complete)

    def _set_form_disabled(self, disabled):
        self.ids.browse_button.disabled = disabled
        self.ids.session_name.disabled = disabled
        self.ids.import_button.disabled = disabled
        self.ids.session_notes.disabled = disabled

    def load_log(self):
        logpath = self._log_path
        session_name = self.ids.session_name.text.strip()
        session_notes = self.ids.session_notes.text.strip()

        dstore_path = self.settings.userPrefs.datastore_location

        if not os.path.isfile(logpath):
            alertPopup("Invalid log specified",
                      "Unable to find specified log file: {}. \nAre you sure it exists?".format(logpath))
            return

        if self.datastore.db_path != dstore_path:
            if self.datastore.is_open:
                self.datastore.close()

            if os.path.isfile(dstore_path):
                self.datastore.open_db(dstore_path)
            else:
                self.datastore.new(dstore_path)

        Logger.info("LogImportWidget: loading log: {}".format(self.ids.log_path.text))

        # choose a default name if the user deletes the suggested name
        if not session_name or len(session_name) == 0:
            session_name = self._extract_base_logfile_name(logpath)
            self.ids.session_name.text = session_name

        self.ids.current_status.text = "Initializing Datastore"

        self._set_form_disabled(True)
        t = Thread(target=self._loader_thread, args=(logpath, session_name, session_notes))
        t.daemon = True
        t.start()

