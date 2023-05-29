# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.items import AdminBoolValue, AdminAction

from slafw.admin.control import AdminControl
from slafw.admin.menus.common.firmware.logging import LoggingMenu as LoggingMenuCommon
from slafw.libPrinter import Printer


class LoggingMenu(LoggingMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminBoolValue("Debug logging", self._get_debug_enabled, self._set_debug_enabled, "logs-icon"),
                AdminAction("Truncate logs", self._truncate_logs, "delete_small_white"),
                AdminAction("Upload to Cucek", self._upload_dev, "upload_cloud_color"),
            )
        )
