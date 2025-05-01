import platform
from typing import Optional

from nicegui import events, ui

class are_you_sure(ui.dialog):

    def __init__(self, reason) -> None:
        super().__init__()

        with self, ui.card():
            ui.label(reason).style('white-space: pre-wrap') #.classes('break')
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)

    async def _handle_ok(self):
        self.submit(True)
