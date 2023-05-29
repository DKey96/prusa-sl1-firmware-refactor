from slafw.admin.control import AdminControl
from slafw.admin.menu import AdminMenu


class OnlyM1FeatureRoot(AdminMenu):
    def __init__(self, control: AdminControl):
        super().__init__(control)
        self.add_back()
        self.add_label("Only M1 Feature Label")
