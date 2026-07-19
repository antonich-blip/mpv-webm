from tests.mpv_ipc import MpvScriptMessageEvent
from .base_test_case import BaseTestCase
from pathlib import Path

import time

class TestMultiSegmentEncode(BaseTestCase):
    def _seek_to(self, seconds):
        self.sendCommandToMpv({
            'command': ['set_property', 'time-pos', seconds],
        })
        # Give mpv some time to finish the seek before the script reads time-pos.
        time.sleep(0.5)

    def test_multi_segment_encode(self):
        self.openTestVideoFile(Path('tests/videos/big_buck_bunny_10s.mp4'))

        # Precise seeks, so the sections don't snap to keyframes (and possibly
        # collapse into empty ones).
        self.sendCommandToMpv({
            'command': ['set_property', 'hr-seek', 'yes'],
        })
        self.sendCommandToMpv({
            'command': ['set_property', 'pause', True],
        })

        self.sendKeyPress('Shift+W')
        self.waitForEvent('webm-show-main-page')

        # I'm not sure why this is needed...
        time.sleep(1)

        # First section: 1s to 3s, committed with '+'.
        self._seek_to(1)
        self.sendKeyPress('1')
        self._seek_to(3)
        self.sendKeyPress('2')
        self.sendKeyPress('+')

        # Second section: 5s to 7s, left as the current selection.
        self._seek_to(5)
        self.sendKeyPress('1')
        self._seek_to(7)
        self.sendKeyPress('2')

        self.sendKeyPress('e')

        finished_event = self.waitForEvent('webm-encode-finished', timeout=240)
        self.assertIsInstance(finished_event, MpvScriptMessageEvent)
        self.assertEqual(['webm-encode-finished', 'success'], finished_event.args)

    def test_clear_segments_encode(self):
        self.openTestVideoFile(Path('tests/videos/big_buck_bunny_10s.mp4'))

        self.sendCommandToMpv({
            'command': ['set_property', 'hr-seek', 'yes'],
        })
        self.sendCommandToMpv({
            'command': ['set_property', 'pause', True],
        })

        self.sendKeyPress('Shift+W')
        self.waitForEvent('webm-show-main-page')

        # I'm not sure why this is needed...
        time.sleep(1)

        # Commit a section, then drop all selections with '-'.
        self._seek_to(1)
        self.sendKeyPress('1')
        self._seek_to(3)
        self.sendKeyPress('2')
        self.sendKeyPress('+')
        self.sendKeyPress('-')

        # '-' resets the selection to the whole file, so this should encode.
        self.sendKeyPress('e')

        finished_event = self.waitForEvent('webm-encode-finished', timeout=240)
        self.assertIsInstance(finished_event, MpvScriptMessageEvent)
        self.assertEqual(['webm-encode-finished', 'success'], finished_event.args)
