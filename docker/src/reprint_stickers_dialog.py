from typing import List
from nicegui import ui

class ReprintStickersDialog(ui.dialog):

    def __init__(self, available_villagers: List[str]) -> None:
        super().__init__()

        with self, ui.card():
            ui.label('Select villagers to reprint').classes('text-lg font-bold')

            with ui.row().classes('w-full gap-4'):
                # Left side - Available villagers
                with ui.column().classes('w-2/5'):
                    ui.label('Available villagers').classes('font-bold')
                    self.available_list = ui.select(
                        options=sorted(available_villagers),
                        multiple=True
                    ).classes('w-full')

                # Middle - Buttons
                with ui.column().classes('w-1/5 justify-center gap-2'):
                    ui.button('→', on_click=self._move_right).classes('w-full')
                    ui.button('←', on_click=self._move_left).classes('w-full')

                # Right side - Selected villagers
                with ui.column().classes('w-2/5'):
                    ui.label('Reprint selection').classes('font-bold')
                    self.selected_list = ui.select(
                        options=[],
                        multiple=True
                    ).classes('w-full')

            # Dialog buttons
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Print', on_click=self._handle_print)

    def _move_right(self):
        selected = self.available_list.value
        if not selected:
            return

        current_selected = self.selected_list.options or []
        selected_set = set(current_selected) if current_selected else set()

        for item in selected:
            selected_set.add(item)

        self.selected_list.set_options(sorted(selected_set))

        current_available = self.available_list.options or []
        available_set = set(current_available)
        available_set -= selected_set

        self.available_list.set_options(sorted(available_set))
        self.available_list.value = None

    def _move_left(self):
        selected = self.selected_list.value
        if not selected:
            return

        current_available = self.available_list.options or []
        available_set = set(current_available) if current_available else set()

        for item in selected:
            available_set.add(item)

        self.available_list.set_options(sorted(available_set))

        current_selected = self.selected_list.options or []
        selected_set = set(current_selected)
        selected_set -= set(selected)

        self.selected_list.set_options(sorted(selected_set))
        self.selected_list.value = None

    async def _handle_print(self):
        self.submit(self.selected_list.options or [])
