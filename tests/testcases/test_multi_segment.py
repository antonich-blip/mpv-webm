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


class TestMultiSegmentSpeed(BaseTestCase):
    """Sections spliced into one EDL timeline must also honor playback speed."""

    FRAME = 64 * 64 * 3

    def makeColorSource(self):
        # Green everywhere except a red band covering source seconds 2..3.
        return self.createVideo(
            name="sections.mkv", size="64x64", duration=5, color="green",
            filters="drawbox=x=0:y=0:w=iw:h=ih:color=red:t=fill:"
                    "enable='between(t,2,3)'",
        )

    def addSections(self, *sections):
        # Commit all but the last section, as '+' does; the last one stays the
        # current selection, exactly as when picking them by hand.
        for count, (start, end) in enumerate(sections[:-1], 1):
            self.setRange(start, end)
            event = self.scriptMessage("mpv-webm-add-segment", event="webm-segment-added")
            self.assertEqual(event.args[1], str(count))
        self.setRange(*sections[-1])

    def frameColor(self, data, index):
        frame = data[index * self.FRAME:(index + 1) * self.FRAME]
        pixels = len(frame) // 3
        return sum(frame[0::3]) / pixels, sum(frame[1::3]) / pixels

    def test_sections_survive_speed_change(self):
        source = self.makeColorSource()
        for speed in (1, 0.5, 2):
            with self.subTest(speed=speed):
                self.openTestVideoFile(source)
                self.setProperty("speed", speed)
                # 0.5s of green, then 1s of red: 1.5s of source in total.
                self.addSections((0.5, 1), (2, 3))
                self.updateScriptOptions({"output_format": "avc",
                                          "output_template": f"sections_{speed}"})
                event = self.scriptMessage("mpv-webm-encode", event="webm-encode-finished", timeout=60)
                self.assertEqual(event.args, ["webm-encode-finished", "success"], self.getLog())

                out = self.tempdir / f"sections_{speed}.mp4"
                duration = float(self.probeVideo(out)["format"]["duration"])
                self.assertAlmostEqual(duration, 1.5 / speed, delta=0.25)

                data = self.decodeVideo(out)
                frames = len(data) // self.FRAME
                self.assertGreater(frames, 2)
                red, green = self.frameColor(data, 0)
                self.assertGreater(green, red, f"speed={speed}: should start green")
                red, green = self.frameColor(data, frames - 1)
                self.assertGreater(red, green, f"speed={speed}: should end red")

    def test_copy_refuses_speed_change(self):
        self.openTestVideoFile(self.makeColorSource())
        self.setProperty("speed", 2)
        self.setRange(1, 3)
        self.updateScriptOptions({"output_format": "copy", "output_template": "copied"})
        event = self.scriptMessage("mpv-webm-encode", event="webm-encode-finished")
        self.assertEqual(event.args[:2], ["webm-encode-finished", "fail"])
        self.assertIn("speed", event.args[2])
        self.assertFalse((self.tempdir / "copied.mkv").exists())
