import os
import sqlite3


class DataBaseConnections:
    def __init__(self, material_library_helper, ai_helper):
        self._materials_library_helper = material_library_helper
        self._ai_helper = ai_helper

        # Get the absolute path of the database file
        db_path = os.path.abspath(os.path.join(__file__, "../../olos.db"))

        # Connect to the database using the absolute path
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self._connection.cursor()

        # set the cursor for helper classes to be able to modify on the database
        self._materials_library_helper.set_database_cursor(cursor)

        if self._ai_helper:
            self._ai_helper.set_database_cursor(cursor)

        self.create_all_necessary_tables()

    def create_all_necessary_tables(self):
        self._materials_library_helper.create_materials_library_tables()
        self._materials_library_helper.add_default_materials_data_to_materials_library_tables()

        if self._ai_helper:
            self._ai_helper.create_ai_settings_tables()
        # commit the transaction of data to the tables
        self._connection.commit()
