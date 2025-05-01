import platform
from typing import Optional

from nicegui import events, ui

class date_picker(ui.dialog):

    def __init__(self, db) -> None:
        super().__init__()

        self.years = db.get_years()

        with self, ui.card():
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'year', 'headerName': 'Select Year'}],
                'rowSelection': 'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        self.year = Path(e.args['data']['year'])
        self.submit([str(self.year)])

    async def _handle_ok(self):
        rows = await ui.run_javascript(f'getElement({self.grid.id}).gridOptions.api.getSelectedRows()')
        self.submit([r['year'] for r in rows][0])
