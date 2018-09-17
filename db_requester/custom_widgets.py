from PyQt5.QtWidgets import QComboBox


class DbComboBox(QComboBox):
    """ Slightly modified ComboBox for caching params at previous """

    def __init__(self, *args, **kwargs):
        QComboBox.__init__(self, *args, **kwargs)
        self.previous_choice = None
        self.combo_db_field_cache = {}

    def load_items(self, items_name):
        self.addItems(items_name)

        for name in items_name:
            name = name.lower()
            if name not in self.combo_db_field_cache:
                self.combo_db_field_cache.update({name: ''})

    def save_previous_path(self, path):
        self.combo_db_field_cache[self.previous_choice] = path
