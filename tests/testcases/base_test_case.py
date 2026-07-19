from abc import ABCMeta
from pathlib import Path
import os
import unittest
import subprocess
import json
import uuid
from typing import List
from dataclasses import dataclass
from tests.mpv_ipc import MpvIPC

@dataclass
class MpvEvent:
    event_name: str
    args: list

class BaseTestCase(unittest.TestCase, metaclass=ABCMeta):
    mpv_process: subprocess.Popen
    mpv_ipc: MpvIPC

    def setUp(self) -> None:
        super().setUp()

        # Start a mpv process with the script loaded
        # Use a UUID on the socket to avoid collisions with previous running instances.
        socket_address = f'/tmp/mpvsocket-{str(uuid.uuid4())}'
        script_path = Path('build/webm.lua')
        mpv_process_args = [
            # Sandboxed mpv wrappers (e.g. bubblewrap with a private /tmp) hide
            # the IPC socket from us; MPV_DEV_MPV can point at a plain binary.
            os.environ.get('MPV_DEV_MPV', 'mpv'),
            '-v',
            '--no-config',
            # Without a terminal on stdin, mpv would read EOF and quit immediately.
            '--no-input-terminal',
            '--vo=null',
            '--ao=null',
            '--load-scripts=no',
            # --load-scripts=no doesn't cover scripts injected with --script by
            # wrapper scripts (e.g. Nix-wrapped mpv); clear those too.
            '--scripts=',
            '--idle=yes',
            f'--input-ipc-server={socket_address}',
        ]

        # Log to a file instead of a pipe: nothing reads the pipe during the
        # test, so mpv's verbose output would eventually fill it and deadlock.
        self.mpv_log_path = f'{socket_address}.log'
        self._mpv_log_file = open(self.mpv_log_path, 'wb')

        self.mpv_process = subprocess.Popen(
            mpv_process_args,
            stdout=self._mpv_log_file,
            stderr=subprocess.STDOUT,
        )

        self.mpv_ipc = MpvIPC()
        self.mpv_ipc.connect(socket_address)
        self.mpv_ipc.start()
        
        self.mpv_ipc.send_command({
            'command': ['enable_event', 'client-message'],
        })

        self.mpv_ipc.send_command({
            'command': ['load-script', str(script_path.absolute())],
        })

        self.mpv_ipc.wait_for_event('webm-script-loaded')
    
    def tearDown(self) -> None:
        self.mpv_process.terminate()
        self.mpv_ipc.stop()
        self._mpv_log_file.close()

        super().tearDown()

    def sendCommandToMpv(self, data: dict, timeout: float = 10) -> None:
        return self.mpv_ipc.send_command(data, timeout)
    
    def updateScriptOptions(self, new_options: dict) -> None:
        self.sendCommandToMpv({
            'command': ['script-message', 'mpv-webm-set-options', json.dumps(new_options)],
        })

    def openTestVideoFile(self, path: Path) -> None:
        self.sendCommandToMpv({
            'command': ['loadfile', str(path.absolute()), 'replace'],
        })
        self.waitForEvent('file-loaded')
    
    def sendKeyPress(self, key: str) -> None:
        self.sendCommandToMpv({
            'command': ['keypress', key],
        })
    
    def waitForEvent(self, event_name: str, timeout: float = 5):
        event = self.mpv_ipc.wait_for_event(event_name, timeout)
        if not event:
            self.fail(f'No {event_name} event was fired')
        
        return event
