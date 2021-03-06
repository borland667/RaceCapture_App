#
# Race Capture App
#
# Copyright (C) 2014-2016 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

import unittest
from mock import Mock
from autosportlabs.racecapture.data.sessionrecorder import SessionRecorder


class TestSessionRecorder(unittest.TestCase):

    def setUp(self):
        self.mock_rcp_api = Mock()
        self.mock_databus = Mock()
        self.mock_datastore = Mock()
        self.mock_track_manager = Mock()

        self.mock_databus.getMeta = Mock(return_value=None)
        self.mock_rcp_api.add_connect_listener = Mock()
        self.mock_rcp_api.add_disconnect_listener = Mock()
        self.mock_databus.addMetaListener = Mock()
        self.mock_databus.addSampleListener = Mock()
        self.mock_datastore.create_session = Mock(return_value=1)
        self.mock_datastore.init_session = Mock(return_value=1)

    def test_starts(self):

        session_recorder = SessionRecorder(self.mock_datastore, self.mock_databus, self.mock_rcp_api,
                                           self.mock_track_manager)

        # Should not be recording yet, not connected to RCP and not on dash screen
        self.assertFalse(session_recorder.recording, "Does not record if not connected to RCP, view is not 'dash'\
         and no meta")

        session_recorder.on_view_change('dash')
        self.assertFalse(session_recorder.recording, "Does not record if not connected to RCP and no meta")

        # Get subscription to connect event and call it
        connect_listener = self.mock_rcp_api.add_connect_listener.call_args[0][0]
        connect_listener()
        self.assertFalse(session_recorder.recording, "Does not record if connected to RCP and no meta")

        # Get meta subscription and call it
        meta_listener = self.mock_databus.addMetaListener.call_args[0][0]
        meta_listener({"foo": "bar"})
        self.assertTrue(session_recorder.recording, "Records when all conditions met")

    def test_creates_session(self):
        self.mock_databus.getMeta = Mock(return_value={"foo": "bar"})

        session_recorder = SessionRecorder(self.mock_datastore, self.mock_databus, self.mock_rcp_api,
                                           self.mock_track_manager, current_view='dash')

        # Get subscription to connect event and call it
        connect_listener = self.mock_rcp_api.add_connect_listener.call_args[0][0]
        connect_listener()

        self.assertEqual(len(self.mock_datastore.init_session.mock_calls), 1, "Creates a new session")

    def test_stops_on_view_change(self):
        self.mock_databus.getMeta = Mock(return_value={"foo": "bar"})

        session_recorder = SessionRecorder(self.mock_datastore, self.mock_databus, self.mock_rcp_api,
                                           self.mock_track_manager, current_view='dash')

        # Get subscription to connect event and call it
        connect_listener = self.mock_rcp_api.add_connect_listener.call_args[0][0]
        connect_listener()

        self.assertTrue(session_recorder.recording, "Session recorder is recording")

        session_recorder.on_view_change('analysis')
        self.assertFalse(session_recorder.recording, "Session recorder stops recording when view changes to\
         non-recording view")

    def test_stops_on_disconnect(self):
        self.mock_databus.getMeta = Mock(return_value={"foo": "bar"})

        session_recorder = SessionRecorder(self.mock_datastore, self.mock_databus, self.mock_rcp_api,
                                           self.mock_track_manager, current_view='dash')

        # Get subscription to connect event and call it
        connect_listener = self.mock_rcp_api.add_connect_listener.call_args[0][0]
        connect_listener()

        self.assertTrue(session_recorder.recording, "Session recorder is recording")

        disconnect_listener = self.mock_rcp_api.add_disconnect_listener.call_args[0][0]
        disconnect_listener()
        self.assertFalse(session_recorder.recording, "Session recorder stops recording on disconnect")


def main():
    unittest.main()

if __name__ == "__main__":
    main()
