# This file is part of the SLA firmware
# Copyright (C) 2023 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Dict, List, Optional, Iterable, Callable

from slafw.admin.base_menu import AdminMenuBase
from slafw.admin.items import AdminItem


class AdminMenuContext:
    def __init__(self, strategy):
        # Strategy should be already initialized before inserted here as an attribute
        self.strategy = strategy
        self.logger = strategy.logger
        self._control = strategy._control
        self.items_changed = strategy.items_changed
        self.value_changed = strategy.value_changed
        self._items: Dict[str, AdminItem] = strategy._items

    @property
    def items(self) -> Dict[str, AdminItem]:
        return self.strategy.items

    def enter(self, menu: AdminMenuBase):
        self.strategy.enter(menu)

    def exit(self):
        self.strategy.exit()

    def add_item(self, item: AdminItem, emit_changed=True):
        self.strategy.add_item(item, emit_changed)

    def add_items(self, items: Iterable[AdminItem]):
        self.strategy.add_items(items)

    def add_label(self, initial_text: Optional[str] = None, icon=""):
        return self.strategy.add_label(initial_text, icon)

    def add_back(self, bold=True):
        self.strategy.add_back(bold)

    def del_item(self, item: AdminItem):
        self.strategy.del_item(item)

    def list_files(self, path: Path, filters: List[str], callback: Callable, icon):
        self.strategy.list_files(path, filters, callback, icon)

    def on_enter(self):
        self.strategy.on_enter()

    def on_reenter(self):
        self.strategy.on_reenter()

    def on_leave(self):
        self.strategy.on_leave()
