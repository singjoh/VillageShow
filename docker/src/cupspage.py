import os
import logging

from dataclasses import dataclass, field
from typing import Callable, List

from nicegui import ui
from VShowDB import vShowDB

LOGGER = logging.getLogger(__name__)

@dataclass
class Cup():
    sname: str
    name: str
    description: str
    points_type: bool
    cup_number: int
    isDirty: bool = False

@dataclass
class Cups():
    on_change: Callable
    items: List[Cup] = field(default_factory=list)

    def get_cup(self, sname: str) -> Cup:
        try:
            cup = next((x for x in self.items if x.sname == sname))
            return cup
        except:
            raise Exception(f'cup {sname} not found')
    
    def add(self, sname: str, name: str, description: str, points_type: bool, cup_number: int) -> None:
        LOGGER.info(f'adding cup {sname}, {name}, {description}, {points_type}, {cup_number}')
        self.items.append(Cup(sname, name, description, points_type, cup_number))
        self.on_change()

    def remove(self, sname: str) -> None:
        if sname is None:
            return
        cup = self.get_cup(sname)
        self.items.remove(cup)
        self.on_change()

    def update(self, sname: str, field: str, value: str) -> None:
        if sname is None:
            return
        cup = self.get_cup(sname)
        if field == "name":
            if cup.name != value: cup.isDirty = True
            cup.name = value
        elif field == "description":
            if cup.description != value: cup.isDirty = True
            cup.description = value
        elif field == "points_type":
            if cup.points_type != value: cup.isDirty = True
            cup.points_type = value
        elif field == "cup_number":
            if cup.cup_number != value: cup.isDirty = True
            if value:
                cup.cup_number = int(value)
            else:
                cup.cup_number = None
        self.on_change()

    def dirtyCount(self):
        return len(list(x for x in self.items if x.isDirty))

    def status(self):
        msg = f"Total items: {len(self.items)}"
        c_d = self.dirtyCount()
        if c_d:
            msg += f" ({c_d} are not saved)"
        return msg

    def save(self,sname,db):
        cup = self.get_cup(sname)
        try:
            LOGGER.info(f'Trying to save cup: {cup.sname}')
            db.upsert_cup(cup.sname, cup.name, cup.description, cup.points_type, cup.cup_number)
            cup.isDirty = False
            self.on_change()
        except Exception as x:
            LOGGER.exception(x)
            ui.notify(f'Failed to save {sname}')

    def save_all(self,db):
        for cup in (x for x in self.items if x.isDirty):
            try:
                db.upsert_cup(cup.sname, cup.name, cup.description, cup.points_type, cup.cup_number)
                cup.isDirty = False
                self.on_change()
            except Exception as x:
                LOGGER.exception(x)
                ui.notify(f'Failed to save {cup.sname}')
        self.on_change()

class CupsPage():
    def __init__(self, db):
        self.__db__ = db
        self.cups = Cups(on_change=self.refresh_ui)

        with ui.row():
            self.cbox = ui.select(
                    options=self.__get_cup_keys__(),
                    new_value_mode='add-unique',
                    with_input=True,
                    on_change=lambda e: self.handle_on_change(e),
                    ).classes('w-40')
            self.cbox.on('new-value', lambda e: self.handle_new(e))
            self.delete_button = ui.button(icon='delete', on_click=lambda e: self.delete_cup(self.cbox.value)).classes('w-1').props('size=xs color=red').tooltip('remove')

        self.cup_number = ui.input(label='Number', placeholder='start typing',
           validation={'Integer only': lambda value: value == "" or value.isdigit()}).classes('w-20')

        self.cup_number.on('keydown.enter', lambda e: self.cups.update(self.cbox.value, 'cup_number', self.cup_number.value)),
        self.cup_number.on('blur', lambda e: self.cups.update(self.cbox.value, 'cup_number', self.cup_number.value)),

        self.name = ui.input(label='Name', placeholder='start typing',
           validation={'Input too long': lambda value: len(value) < 128}).classes('w-full no-wrap')
        self.name.on('keydown.enter', lambda e: self.cups.update(self.cbox.value, 'name', self.name.value)),
        self.name.on('blur', lambda e: self.cups.update(self.cbox.value, 'name', self.name.value)),

        self.description = ui.input(label='Description', placeholder='start typing',
           validation={'Input too long': lambda value: len(value) < 512}).classes('w-full wrap')
        self.description.on('keydown.enter', lambda e: self.cups.update(self.cbox.value, 'description', self.description.value)),
        self.description.on('blur', lambda e: self.cups.update(self.cbox.value, 'description', self.description.value)),

        self.points_type = ui.checkbox('Sum of points', on_change=lambda e: self.cups.update(self.cbox.value, 'points_type', e.value))

        with ui.card():
            self.status_label = ui.label("")
            with ui.row().classes('justify-between'):
                self.save = ui.button('Save', on_click = lambda: self.cups.save(self.cbox.value,db))
                self.save.disable()
                self.saveall = ui.button('Save All', on_click = lambda: self.cups.save_all(db))
                self.saveall.disable()
                self.saveall.classes('ml-auto')

        with ui.card():
            self.cat_list = ui.list()

        # add another card here with the results of a select from the database
        self.__reset_data__();

    def __noop__(self):
        pass

    def __reset_data__(self):

        self.cups = Cups(on_change=self.__noop__)
        cups = self.__db__.get_cups()
        for cup in cups:
            self.cups.add(cup[0], cup[1], cup[2], cup[3], cup[4])
        self.cbox.set_options(self.__get_cup_keys__())
        self.cups.on_change = self.refresh_ui
        self.refresh_ui()

    def __get_cup_keys__(self):
        return list(sorted(x.sname for x in self.cups.items))

    def delete_cup(self, cup_name):
        LOGGER.info(f'Trying to delete {cup_name}')
        try:
            self.__db__.delete_cup(cup_name)
        except Exception as x:
            ui.notify(f'Failed to delete {cup_name}, {x}')
            return

        self.cbox.value = ''
        self.cups.remove(cup_name)
        self.cbox.set_options(self.__get_cup_keys__())
        self.cbox.update()

    def refresh_ui(self):
        if self.cbox.value:
            cup = self.cups.get_cup(self.cbox.value)
            LOGGER.info(cup)
            self.cup_number.value = str(cup.cup_number) if cup.cup_number else ''
            self.name.value = cup.name
            self.description.value = cup.description
            self.points_type.value = cup.points_type
            if cup.isDirty:
                self.save.enable()
            else:
                self.save.disable()
            self.cat_list.clear()
            with self.cat_list:
                for display_order, name, is_child in self.__db__.get_categories_for_cup(self.cbox.value):
                    item = f'{display_order}: {name} {"(childi)" if is_child else ""}'
                    LOGGER.info(f'item: {item}')
                    ui.item_label(item)
        else:
            self.cup_number.value = ""
            self.name.value = ""
            self.description.value = ""
            self.points_type.value = False
            self.save.disable()
        if self.cups.dirtyCount():
            self.saveall.enable()
        else:
            self.saveall.disable()
        self.status_label.text = self.cups.status()


    def handle_on_change(self, e):
        # ui.notify('Selected ' + e.value)
        self.refresh_ui()

    def handle_new(self, e):
        new_value = e.args[0]
        # ui.notify(f'Adding {new_value}')

        self.cups.add(new_value, '', '')
        self.cbox.set_options(self.__get_cup_keys__())
        self.cbox.value = new_value
        self.cbox.update()

