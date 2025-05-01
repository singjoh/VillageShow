import os
import logging

from dataclasses import dataclass, field
from typing import Callable, List

from nicegui import ui
from VShowDB import vShowDB

LOGGER = logging.getLogger(__name__)

@dataclass 
class Class():
    display_order: int
    display_name: str
    gold_key: int
    silver_key: int
    bronze_key: int
    isDirty: bool = False

@dataclass
class Cup():
    cupname: str
    key: str
    entry_description: str

@dataclass
class Judge():
    code: str
    villager: str
    items: List[Class] = field(default_factory=list)
    cups: List[Cup] = field(default_factory=list)
    isDirty: bool = False

    def get_class(self, display_order: str) -> Class:
        try:
            _class = next((x for x in self.items if x.display_order == display_order))
            return _class
        except:
            raise Exception(f'Item {display_order} not found')
    
    def get_cup(self, cupname: str) -> Cup:
        try:
            cup = next((x for x in self.cups if x.cupname == cupname))
            return cup
        except:
            raise Exception(f'Cup {cupname} not found')
    
    def update(self, display_order: str, field: str, value: str) -> None:
        _class = self.get_class(display_order)
        if field == "gold":
            if _class.gold_key != value:
                _class.isDirty = True
                _class.gold_key = value
        elif field == "silver":
            if _class.silver_key != value:
                _class.isDirty = True
                _class.silver_key = value
        elif field == "bronze":
            if _class.bronze_key != value:
                _class.isDirty = True
                _class.bronze_key = value
        if _class.isDirty:
            self.isDirty = True

    def update_cup(self, cupname: str, field: str, value: str) -> None:
        cup = self.get_cup(cupname)
        if field == "key":
            if cup.key != value:
                cup.key = value
                self.isDirty = True
        elif field == "entry_description":
            if cup.entry_description != value:
                cup.entry_description = value
                self.isDirty = True

@dataclass
class Judges():
    on_change: Callable
    items: List[Judge] = field(default_factory=list)

    def add(self, code: str, villager: str, classes, cups):
        self.items.append(Judge(code, villager, classes, cups))

    def get_judge(self, code: str) -> Judge:
        try:
            judge = next((x for x in self.items if x.code == code))
            return judge
        except:
            raise Exception(f'Judge {code} not found')
    
    def update_villager(self, code: str, value: str) -> None:
        judge = self.get_judge(code)
        if judge.villager != value: 
            judge.isDirty = True
            judge.villager = value
        self.on_change()

    def update_judge_item(self, code: str, display_order: int, field: str, value: str) -> None:
        judge = self.get_judge(code)
        judge.update(display_order, field, value)
        self.on_change()

    def update_judge_cup(self, code: str, cupname: str, field: str, value: str) -> None:
        judge = self.get_judge(code)
        judge.update_cup(cupname, field, value)
        self.on_change()

    def dirtyCount(self):
        return len(list(x for x in self.items if x.isDirty))

    def status(self):
        g,s,b,c = 0,0,0,0
        for judge in self.items:
            for _class in judge.items:
                c += 1
                if _class.gold_key: g += 1
                if _class.silver_key: s += 1
                if _class.bronze_key: b += 1

        return f"G:{g}, S:{s}, B{b} for {c} classes."

    def __flat_items__(self, items):
        return list( ( x.display_order, x.gold_key, x.silver_key, x.bronze_key )
                     for x in items )

    def __flat_cups__(self, cups):
        return list( ( x.cupname, x.key, x.entry_description ) for x in cups )

    def save(self,code,db):
        judge = self.get_judge(code)
        try:
            db.update_judge(judge.code, judge.villager, 
                            self.__flat_items__(judge.items),
                            self.__flat_cups__(judge.cups),
                            )
            judge.isDirty = False
            for item in judge.items: item.isDirty = False
            self.on_change()
        except Exception as x:
            LOGGER.exception(x)
            ui.notify(f'Failed to save {code}')

    def save_all(self,db):
        for judge in (x for x in self.items if x.isDirty):
            try:
                db.update_judge(judge.code, judge.villager, 
                                self.__flat_items__(judge.items),
                                self.__flat_cups__(judge.cups),
                                )
                judge.isDirty = False
                for item in judge.items: item.isDirty = False
            except Exception as x:
                LOGGER.exception(x)
                ui.notify(f'Failed to save {judge.code}')
        self.on_change()

class JudgesPage():
    def __init__(self, db):
        self.__db__ = db

        with ui.card().classes('w-3/5'):
            with ui.splitter(value=50).classes('w-full') as splitter:
                with splitter.before:

                    self.jbox = ui.select(
                            options=[],
                            with_input=True,
                            on_change=lambda e: self.handle_on_change(),
                            ).classes('w-40')

                    self.vbox = ui.select(
                            options = [],
                            with_input=True,
                            on_change=lambda e: self.judges.update_villager(self.jbox.value, e.sender.value),
                            ).classes('w-100')

                with splitter.after:

                    with ui.card().classes('w-60'):
                        self.status_label = ui.label("")
                        with ui.row().classes('justify-between'):
                            self.save = ui.button('Save', on_click = lambda: self.judges.save(self.jbox.value,db))
                            self.save.disable()
                            self.saveall = ui.button('Save All', on_click = lambda: self.judges.save_all(db))
                            self.saveall.disable()
                            self.saveall.classes('ml-auto')

        with ui.card().classes('w-full'):
            ui.label("Gold/Silver/Bronze entry ...")
            self.class_grid = ui.grid(columns=4)

        with ui.card().classes('w-full'):
            ui.label("'Best of' ...")
            self.cup_grid = ui.grid(columns=6).classes('w-full')

        self.__reset_data__()

    def __noop__(self):
        pass

    def dn(self, name, is_child):
        return f'{name}{" (child)" if is_child else ""}'

    def __reset_data__(self):

        # villagers
        villagers = self.__db__.get_villagers()
        v_keys = list(sorted(x[0] for x in villagers))
        self.vbox.set_options(v_keys)

        # entrant keys
        # dict of class -> entry keys
        #
        entries = self.__db__.get_entries_for_judges()
        self.entries = {}
        for code, num, name, is_child, hashkey in entries:
            if code not in self.entries:
                self.entries[code] = {}
            if num not in self.entries[code]:
                self.entries[code][num] = []
            self.entries[code][num].append(hashkey)

        data = self.__db__.get_judge_pages_entry()
        self.cups = {}
        for code, _, cup, num, _ in data:
            if code not in self.cups: self.cups[code] = {}
            if cup not in self.cups[code]: self.cups[code][cup] = {'valid_keys': []}
            if code in self.entries and num in self.entries[code]:
                self.cups[code][cup]['valid_keys'].extend(self.entries[code][num])

        data = self.__db__.get_judge_entry()
        for code, cup, key, entry_description in data:
            self.cups[code][cup]['key'] = key
            self.cups[code][cup]['entry_description'] = entry_description

        self.judges = Judges(on_change=self.__noop__)
        judges = self.__db__.get_judges()
        for judge in judges:
            raw = self.__db__.get_categories_for_judge(judge[0])
            classes = []
            cups = []
            for item in raw:
                classes.append( Class(item[0], self.dn(item[1], item[2]), item[3], item[4], item[5]))
            if judge[0] in self.cups:
                for k, v in self.cups[judge[0]].items():
                    cups.append( Cup(k, v['key'], v['entry_description']))
            self.judges.add(judge[0], judge[1], classes, cups)
        self.jbox.set_options(self.__get_judge_codes__())
        self.judges.on_change = self.refresh_ui
        self.refresh_ui()
        self.handle_on_change()


    def __get_display_order_medal_from_ui(self, obj):
        found = False
        for display_order in self.class_items.keys():
            for medal, x in self.class_items[display_order].items():
                if x == obj:
                    LOGGER.info(f'{display_order}/{medal} - {x}')
                    found = True
                    break
            if found:
                break
        if not found:
            msg = f'Could not find matching grid object {obj}'
            LOGGER.error(msg)
            return

        LOGGER.info(f'{display_order}/{medal} - {x}')
        return display_order, medal

    def __enter_winner__(self, e):
        display_order, medal = self.__get_display_order_medal_from_ui(e.sender)

        key = e.sender.value
        if self.jbox.value not in self.entries:
            if key:
                ui.notify(f'No valid entries for {self.jbox.value}/{display_order}')
                e.sender.value = ''
            else:
                self.judges.update_judge_item(self.jbox.value, display_order, medal, None)
            return
        valid_keys = self.entries[self.jbox.value].get(display_order,[])
        if not key:
            self.judges.update_judge_item(self.jbox.value, display_order, medal, None)
        elif key in valid_keys:
            LOGGER.info(f'Calling update_judge_item with {display_order}, {medal}, {key}')
            self.judges.update_judge_item(self.jbox.value, display_order, medal, key)
        else:
            ui.notify(f'Invalid - "{key}" not in [{', '.join(valid_keys)}]')
            e.sender.value = ''

    def __enter_cup__(self, e):
        found = False
        for cup, v in self.cup_items.items():
            for field, x in v.items():
                if x == e.sender:
                    LOGGER.info(f'{cup} - {x}')
                    found = True
                    break
            if found:
                break

        value = e.sender.value
        if field == 'key':
            valid_keys = self.cups[self.jbox.value][cup]['valid_keys']
            if not value:
                self.judges.update_judge_cup(self.jbox.value, cup, field, None)
            elif value in valid_keys:
                LOGGER.info(f'Calling update_judge_cup with {cup}, {value}')
                self.judges.update_judge_cup(self.jbox.value, cup, field, value)
            else:
                ui.notify(f'Invalid - "{value}" not in [{', '.join(valid_keys)}]')
                e.sender.value = ''
        else:
            self.judges.update_judge_cup(self.jbox.value, cup, field, value)


    def __get_judge_codes__(self):
        return list(sorted(x.code for x in self.judges.items))

    def refresh_ui(self):
        if self.jbox.value:
            judge = self.judges.get_judge(self.jbox.value)
            if judge.isDirty:
                self.save.enable()
            else:
                self.save.disable()
        else:
            self.save.disable()
        if self.judges.dirtyCount():
            self.saveall.enable()
        else:
            self.saveall.disable()
        self.status_label.text = self.judges.status()

    def handle_on_change(self):

        def standard_input(label, value, valid_keys):
            validation={'': lambda x: not x or len(x) < 2 or x in valid_keys}
            return ui.input(label=label, placeholder='Entry key', value=value,
                            validation=validation).classes('w-14 col-span-1').props("hide-bottom-space")

        if self.jbox.value:
            judge = self.judges.get_judge(self.jbox.value)
            self.vbox.value = judge.villager
            self.class_grid.clear()
            self.class_items = {}
            with self.class_grid:
                for _class in sorted(judge.items, key=lambda x: x.display_order):
                    self.class_items[_class.display_order] = {}
                    display_fqdn = f'{_class.display_order}: {_class.display_name}'
                    valid_keys = self.entries.get(judge.code,{}).get(_class.display_order,[])
                    ui.label(display_fqdn)
                    self.class_items[_class.display_order]['gold'] = standard_input('Gold',_class.gold_key, valid_keys)
                    self.class_items[_class.display_order]['silver'] = standard_input('Silver',_class.silver_key, valid_keys)
                    self.class_items[_class.display_order]['bronze'] = standard_input('Bronze',_class.bronze_key, valid_keys)

                for display_order in self.class_items.keys():
                    for medal, x in self.class_items[display_order].items():
                        x.on('keydown.enter', lambda e: self.__enter_winner__(e))
                        x.on('blur', lambda e: self.__enter_winner__(e))

            self.cup_grid.clear()
            self.cup_items = {}
            with self.cup_grid:
                for cup in sorted(judge.cups, key=lambda x: x.cupname):
                    self.class_items[cup.cupname] = None
                    ui.label(cup.cupname).classes('col-span-2')
                    valid_keys = self.cups.get(judge.code,{}).get(cup.cupname,{'valid_keys': []})['valid_keys']
                    self.cup_items[cup.cupname] = {}
                    self.cup_items[cup.cupname]['key'] = standard_input('Entry',cup.key,valid_keys)
                    self.cup_items[cup.cupname]['entry_description'] = ui.input(label='Entry Description',
                                placeholder='Describe Entry', value=cup.entry_description,
                                validation={'Input too Long': lambda x: len(x) < 128}).classes('col-span-3 w-72')
                for cup, v in self.cup_items.items():
                    for k, x in v.items():
                        x.on('keydown.enter', lambda e: self.__enter_cup__(e))
                        x.on('blur', lambda e: self.__enter_cup__(e))

        else:
            self.class_grid.clear()
            self.cup_grid.clear()
        self.refresh_ui()


