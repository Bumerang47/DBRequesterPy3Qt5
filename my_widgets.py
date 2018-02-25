from PyQt5.QtWidgets import QComboBox


class DbComboBox(QComboBox):
    """
    Slightly modified ComboBox for added atributes
    """

    def __init__(self, *args, **kwargs):
        QComboBox.__init__(self, *args, **kwargs)
        self.previous_choice = None
        self.combo_db_field_cache = {}

    def loadItems(self, new_list):
        """
        Alternative .addItems with initialisation cache to connection db
        @param new_list: list for add items
        @return: None. Setting to new ComboBox elements and extend attribute
        """
        self.addItems(new_list)

        for item in new_list:
            _item = item.lower()
            if _item not in self.combo_db_field_cache:
                self.combo_db_field_cache.update({_item: ''})

    def savePreviousPath(self, path):
        # Saving path connection to last the selected type
        self.combo_db_field_cache[self.previous_choice] = path

    def selectText(self, text):
        # Support method for select item at name
        index = self.findText(text)
        if index >= 0:
            self.setCurrentIndex(index)
