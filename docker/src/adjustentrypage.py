import os
import logging

from dataclasses import dataclass, field
from typing import Callable, List

from nicegui import ui
from VShowDB import vShowDB
from are_you_sure import are_you_sure

LOGGER = logging.getLogger(__name__)

class AdjustEntryPage():
    def __init__(self, db):
        self.__db__ = db
        self.villagers = {}
        self.categories = {}

        with ui.card().classes('w-3/5'):
            self.vbox = ui.select(
                    options=self.__get_v_keys__(),
                    with_input=True,
                    on_change=lambda e: self.handle_on_change(e),
                    ).classes('w-40')

            with ui.grid(columns=3):

                self.hash = ui.input(label='Entry Ref', placeholder='Entry Ref', 
                           validation={'Enter Valid Entry Ref': lambda value: self.__is_valid_key(self.vbox.value, value)}).classes('w-40')
                self.hash.on('keydown.enter', lambda e: self.__set_entry(self.vbox.value, e.sender.value,'hash'))
                self.hash.on('blur', lambda e: self.__set_entry(self.vbox.value, e.sender.value,'hash'))
                self.old_entry = ui.label('').classes('col-span-2')
                self.new_id = ui.input(label='Entry Id', placeholder='Entry Id', 
                           validation={'Enter Valid Entry Id': lambda value: self.__is_valid_num(value)}).classes('w-40')
                self.new_id.on('keydown.enter', lambda e: self.__set_entry(self.vbox.value, e.sender.value,'id'))
                self.new_id.on('blur', lambda e: self.__set_entry(self.vbox.value, e.sender.value,'id'))
                self.new_entry = ui.label('').classes('col-span-2')
            self.save = ui.button('Save', on_click = lambda: self.__save())
            self.save.disable()

        self.__reset_data__()

    def valid_classnum(self, n):
        if n:
            return int(n) in self.__c_ids__
        return True # trivial case

    def __noop__(self):
        pass

    async def __save(self):
        id = int(self.new_entry.text.split(':')[0])
        reason = ( "Apply Changes Year\n"
                   f"This will associate entry ref {self.hash.value} with category {self.new_entry.text}.\n\n"
                   f"After the change, manually mark the sticky label with the new class {id}."
                   "\nPlease confirm you want to continue ..."
                  )
        x = await are_you_sure(reason)
        if not x:
            ui.notify('Save Changes - cancelled')
            return
        try:
            self.__db__.adjust_entry(self.hash.value, id)
            ui.notify('Changes applied to database, update the sticky label and return to villager.')
            self.__reset_data__()
        except Exception as x:
            LOGGER.exeception(x)
            ui.notify(f'Failed to save - {x}')

    def fqdn(self, num, name, is_child):
        return f'{num}: {name}{" (child)" if is_child else ""}'

    def __reset_data__(self):

        categories = self.__db__.get_categories()
        self.categories = {}
        for num, name, is_child in self.__db__.get_categories():
            self.categories[num] = self.fqdn(num, name, is_child)

        self.villagers = {}

        villagers = self.__db__.get_villagers()
        for v in villagers:
            self.villagers[v[0]] = {}

        entries = self.__db__.get_entry_hashes()
        for v, num, name, ref, is_child in entries:
            self.villagers[v][ref] = self.fqdn(num, name, is_child)

        self.vbox.set_options(self.__get_v_keys__())
        self.vbox.update()
        self.refresh_ui()

    def __get_v_keys__(self):
        return list(sorted(self.villagers.keys()))

    def __is_valid_key(self, villager, value):
        if value:
            return value in self.villagers[villager]
        return True # empty cell

    def __is_valid_num(self, n):
        if n:
            return int(n) in self.categories.keys()
        return True # empty cell

    def __set_entry(self, villager, value, field):
        if field == 'hash':
            self.old_entry.text = self.villagers[villager].get(value,'')
        elif field == "id":
            if value:
                self.new_entry.text = self.categories.get(int(value),'')
            else:
                self.new_entry.text = ''
        self.refresh_status()

    def refresh_status(self):
        if self.old_entry.text and self.new_entry.text:
            self.save.enable()
        else:
            self.save.disable()

    def refresh_ui(self):
        self.hash.value= ''
        self.new_id.value= ''
        self.old_entry.text = ''
        self.new_entry.text = ''
        self.refresh_status()

    def handle_on_change(self, e):
        self.refresh_ui()

