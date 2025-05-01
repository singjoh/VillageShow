import os
import logging

from dataclasses import dataclass, field
from typing import Callable, List

from nicegui import ui
from VShowDB import vShowDB

LOGGER = logging.getLogger(__name__)

@dataclass
class Entry():
    id: int
    name: str

@dataclass
class Villager():
    name: str
    age: int
    items: List[Entry] = field(default_factory=list)
    isDirty: bool = False

    def add_entry(self, entry: str) -> None:
        id = 0
        for item in self.items:
            if item.id > id: id = item.id
        id += 1
        self.items.append(Entry(id, entry))
        return id

    def remove_entry(self, id: int) -> None:
        entry = next((x for x in self.items if x.id == id))
        self.items.remove(entry)

    def total_cost(self):
        if not(self.items): return 0
        cost = 0.5 * len(self.items)
        if self.age and self.age < 18:
            return cost
        return cost + 0.5

@dataclass
class Villagers():
    on_change: Callable
    items: List[Villager] = field(default_factory=list)

    def get_villager(self, name: str) -> Villager:
        try:
            villager = next((x for x in self.items if x.name == name))
            return villager
        except:
            raise Exception(f'Villager {name} not found')
    
    def add(self, name: str, age: int, entries) -> None:
        self.items.append(Villager(name, age, entries))
        self.on_change()

    def remove(self, name: str) -> None:
        if name is None:
            return
        villager = self.get_villager(name)
        self.items.remove(villager)
        self.on_change()

    def add_entry(self, name: str, entry: str) -> None:
        villager = self.get_villager(name)
        villager.isDirty = True
        return villager.add_entry(entry)

    def remove_entry(self, name: str, entry: str) -> None:
        villager = self.get_villager(name)
        villager.remove_entry(entry)
        villager.isDirty = True

    def update(self, name: str, field: str, value: str) -> None:
        villager = self.get_villager(name)
        if field == "age":
            if value:
                if (villager.age and villager.age != int(value)) or not villager.age:
                    villager.isDirty = True
                    villager.age = int(value)
            else:
                if villager.age:
                    villager.isDirty = True
                    villager.age = None

        # address
        # phone
        self.on_change()

    def dirtyCount(self):
        return len(list(x for x in self.items if x.isDirty))

    def status(self):
        msg = f"Total villagers: {len(self.items)}"
        # totan entrants
        c_d = self.dirtyCount()
        if c_d:
            msg += f" ({c_d} are not saved)"
        return msg

    def save(self,name,db):
        villager = self.get_villager(name)
        try:
            LOGGER.info(f'Trying to save villager: {villager.name}')
            db.upsert_villager(villager.name, villager.age, villager.items)
            villager.isDirty = False
            self.on_change()
        except Exception as x:
            LOGGER.exception(x)
            ui.notify(f'Failed to save {name}')

    def save_all(self,db):
        for villager in (x for x in self.items if x.isDirty):
            try:
                LOGGER.info(f'Trying to save villager: {villager.name}')
                db.upsert_villager(villager.name, villager.age, villager.items)
                villager.isDirty = False
            except Exception as x:
                LOGGER.exception(x)
                ui.notify(f'Failed to save {villager.name}')
        self.on_change()

class VillagersPage():
    def __init__(self, db):
        self.__db__ = db
        self.villagers = Villagers(on_change=self.refresh_ui)
        self.categories = []
        self.__c_keys__ = []
        self.__c_ids__ = []

        with ui.card().classes('w-3/5'):
            with ui.splitter(value=50).classes('w-full') as splitter:
                with splitter.before:
                    with ui.row():

                        self.vbox = ui.select(
                                options=self.__get_v_keys__(),
                                new_value_mode='add-unique',
                                with_input=True,
                                on_change=lambda e: self.handle_on_change(e),
                                ).classes('w-40')
                        self.vbox.on('new-value', lambda e: self.handle_new(e))

                        self.delete_button = ui.button(icon='delete', on_click=lambda e: self.delete_villager(self.vbox.value)).classes('w-1').props('size=xs color=red').tooltip('remove')


                    self.age = ui.input(label='Age', placeholder='Age on show date', 
                       validation={'Integer only': lambda value: value == "" or value.isdigit()}).classes('w-40')
                    self.age.on('keydown.enter', lambda e: self.villagers.update(self.vbox.value, 'age', e.sender.value))
                    self.age.on('blur', lambda e: self.villagers.update(self.vbox.value, 'age', e.sender.value))
                with splitter.after:
                    with ui.card().classes('w-60'):
                        # save controls
                        self.status_label = ui.label("")
                        with ui.row().classes('justify-between'):
                            self.save = ui.button('Save', on_click = lambda: self.villagers.save(self.vbox.value,db))
                            self.save.disable()
                            self.saveall = ui.button('Save All', on_click = lambda: self.villagers.save_all(db))
                            self.saveall.disable()
                            self.saveall.classes('ml-auto')

        # address
        # phone

        with ui.row().classes('w-full'):
            with ui.card().classes('w-2/5'):
                with ui.splitter(value=35).classes('w-full') as splitter:
                    with splitter.before:
                        self.number_input = ui.input(
                                label='Class', 
                                validation={'Bad Class': lambda x: self.valid_classnum(x)}).classes('w-14')
                        self.number_input.on('keydown.enter', lambda x: self.add_entry_by_id(self.number_input.value))
                    with splitter.after:
                        with ui.card().classes('w-60'):
                            with ui.row():
                                self.cbox = ui.select(options=self.__c_keys__,
                                                      with_input=True).classes('w-20')
                                ui.button('Add', on_click = lambda: self.add_entry(self.cbox.value))
            with ui.card().classes('w-1/5'):
                self.totals = ui.label("")

        self.entries_card = ui.card()

        self.__reset_data__()

    def valid_classnum(self, n):
        if n:
            return int(n) in self.__c_ids__
        return True # trivial case

    def __noop__(self):
        pass

    def fqdn(self, num, name, is_child):
        return f'{num}: {name}{" (child)" if is_child else ""}'

    def __reset_data__(self):

        self.categories = self.__db__.get_categories()
        self.__c_keys__ = list(self.fqdn(x[0],x[1],x[2]) for x in sorted(self.categories, key=lambda v: v[0]))
        self.__c_ids__ = list(x[0] for x in sorted(self.categories, key=lambda v: v[0]))
        self.cbox.set_options(self.__c_keys__)
        self.cbox.update()

        vdict = {}
        for e in self.__db__.get_entries():
            if e[0] not in vdict:
                vdict[e[0]] = []
            id = len(vdict[e[0]])
            vdict[e[0]].append(Entry(id, self.fqdn(e[1], e[2], e[3])))

        self.villagers = Villagers(on_change=self.__noop__)

        villagers = self.__db__.get_villagers()
        for v in villagers:
            self.villagers.add(v[0], v[1], vdict.get(v[0],[]))
        self.vbox.set_options(self.__get_v_keys__())
        self.vbox.update()
        self.villagers.on_change=self.refresh_ui
        self.refresh_ui()

    def __get_v_keys__(self):
        return list(sorted(x.name for x in self.villagers.items))

    def delete_villager(self, name):
        LOGGER.info(f'Trying to remove {name}')
        try:
            self.__db__.delete_villager(name)
        except Exception as x:
            ui.notify(f'Failed to delete {name}, {x}')
            return

        self.vbox.value = ''
        self.villagers.remove(name)
        self.vbox.set_options(self.__get_v_keys__())
        self.vbox.update()

    def add_entry_by_id(self, id):
        classname = None
        for num, name, is_child in self.categories:
            if str(num) == id:
                self.add_entry(self.fqdn(num,name,is_child))
                break
        self.number_input.value = ''

    def add_entry(self, classname):
        name = self.vbox.value
        if not name: return
        if not classname: return

        villager = self.villagers.get_villager(name)
        if (villager.age is None or villager.age >= 18) and classname[-7:] == '(child)' :
            ui.notify('Adult cannot enter a child class!')
            return

        id = self.villagers.add_entry(name, classname)
        self.__add_row_to_entries_card(classname, id)
        self.totals.text = f'£{villager.total_cost():.2f}'
        self.refresh_status()

    def remove_entry(self, id):
        name = self.vbox.value
        if not name: return
        self.villagers.remove_entry(name, id)
        self.refresh_ui()

    def __add_row_to_entries_card(self, classname, id):   
        with self.entries_card:
            with ui.row():
                ui.button(icon='delete', on_click=lambda e: self.remove_entry(id)).classes('w-1').props('size=xs color=red').tooltip('remove')
                ui.label(classname)

    def refresh_status(self):
        if self.vbox.value:
            villager = self.villagers.get_villager(self.vbox.value)
            if villager.isDirty:
                self.save.enable()
            else:
                self.save.disable()
        else:
            self.save.disable()
        if self.villagers.dirtyCount():
            self.saveall.enable()
        else:
            self.saveall.disable()
        self.status_label.text = self.villagers.status()

    def refresh_ui(self):
        self.refresh_status()
        self.entries_card.clear()
        if self.vbox.value:
            villager = self.villagers.get_villager(self.vbox.value)
            self.age.value = str(villager.age) if villager.age else ''
            for entry in villager.items:
                self.__add_row_to_entries_card(entry.name, entry.id)   
            self.totals.text = f'£{villager.total_cost():.2f}'
        else:
            self.age.value = ""
            self.totals.value = f'£0.0'

    def handle_on_change(self, e):
        self.refresh_ui()

    def handle_new(self, e):
        new_value = e.args[0].title()

        self.villagers.add(new_value, None, [])
        self.vbox.set_options(self.__get_v_keys__())
        self.vbox.value = new_value
        self.vbox.update()

        self.entries_card.clear()
