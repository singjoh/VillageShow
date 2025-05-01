import platform
import logging

from nicegui import events, ui

LOGGER = logging.getLogger(__name__)

class year_picker(ui.dialog):

    def __init__(self, db) -> None:
        super().__init__()

        self.years = sorted(db.get_years(), reverse=True)

        with self, ui.card():
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'year', 'headerName': 'Select Year'}],
                'rowSelection': 'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.grid.options['rowData'] = [{'year': str(year)} for year in self.years]
        self.grid.update()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        self.year = Path(e.args['data']['year'])
        self.submit([str(self.year)])

    async def _handle_ok(self):
        rows = await ui.run_javascript(f'getElement({self.grid.id}).gridOptions.api.getSelectedRows()')
        self.submit([r['year'] for r in rows][0])
