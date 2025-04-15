import json
from core.constants import CoreConstants as constants
from utils.default_materials_data import DefaultMaterialsData


class MaterialsLibraryHelper:
    def __init__(self):
        self.cursor = None

    def set_database_cursor(self, db_cursor):
        self.cursor = db_cursor

    def create_materials_library_tables(self):
        # materials table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT,
            isEditable BOOLEAN NOT NULL CHECK (isEditable IN (0, 1))
        )
        """)

        # thicknesses table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Thicknesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER,
            thickness FLOAT NOT NULL,
            FOREIGN KEY (material_id) REFERENCES Materials(id)
        )
        """)

        # operations table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thickness_id INTEGER,
            operation_type TEXT NOT NULL,
            power FLOAT NOT NULL,
            speed FLOAT NOT NULL,
            tool TEXT NOT NULL,
            FOREIGN KEY (thickness_id) REFERENCES Thicknesses(id)
        )
        """)

        # engraving settings table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Engraving_Settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id INTEGER,
            algorithm TEXT NOT NULL,
            resolution FLOAT NOT NULL,
            gray_shift INTEGER NOT NULL,
            block_size INTEGER,
            block_distance INTEGER,
            FOREIGN KEY (operation_id) REFERENCES Operations(id)
        )
        """)

    def handle_get_materials_list(self):
        # Fetch all materials
        self.cursor.execute("""
        SELECT id, name, image, isEditable FROM Materials
        """)
        materials = self.cursor.fetchall()

        result = []

        for material in materials:
            material_id, material_name, material_image, isEditable = material

            # Fetch thicknesses related to the current material
            self.cursor.execute("""
            SELECT id, thickness FROM Thicknesses WHERE material_id = ?
            """, (material_id,))
            thicknesses = self.cursor.fetchall()

            material_thicknesses_list = []

            for thickness in thicknesses:
                thickness_id, thickness_value = thickness

                # Fetch operations related to the current thickness
                self.cursor.execute("""
                SELECT id, operation_type, power, speed, tool FROM Operations WHERE thickness_id = ?
                """, (thickness_id,))
                operations = self.cursor.fetchall()

                thickness_operations_list = []

                for operation in operations:
                    operation_id, operation_type, power, speed, tool = operation

                    # Prepare the operation dictionary
                    operation_dict = {
                        'operationId': operation_id,
                        'operationType': operation_type,
                        'power': power,
                        'speed': speed,
                        'tool': tool,
                    }

                    # If the operation is 'Engrave', fetch engraving settings
                    if operation_type == 'Engrave':
                        self.cursor.execute("""
                        SELECT algorithm, resolution, gray_shift, block_size, block_distance FROM Engraving_Settings WHERE operation_id = ?
                        """, (operation_id,))
                        engrave_settings = self.cursor.fetchone()

                        if engrave_settings:
                            algorithm, resolution, gray_shift, block_size, block_distance = engrave_settings

                            # Add the dithering settings to the operation dictionary
                            operation_dict['dithering'] = {
                                'algorithm': algorithm,
                                'resolution': resolution,
                                'grayShift': gray_shift,
                                'blockSize': block_size,
                                'blockDistance': block_distance,

                            }

                    thickness_operations_list.append(operation_dict)

                # Prepare the thickness dictionary
                thickness_dict = {
                    'thicknessId': thickness_id,
                    'thicknessValue': thickness_value,
                    'thicknessOperations': thickness_operations_list,
                }

                material_thicknesses_list.append(thickness_dict)

            # Prepare the material dictionary
            material_dict = {
                'materialId': material_id,
                'materialName': material_name,
                'materialImage': material_image,
                'materialThicknesses': material_thicknesses_list,
                'isEditable': isEditable
            }

            result.append(material_dict)

        json_result = json.dumps(result, indent=4)

        response = self.fastapi_material_library_response(
            constants.MATERIALS_LIBRARY_DATA_TYPE, constants.LIST_MATERIAL_PROCESS, json_result, True)

        return response

    def handle_add_new_material(self, data):
        # Insert the material data into the Materials table
        self.cursor.execute("""
        INSERT INTO Materials (name, image, isEditable) VALUES (?, ?, ?)
        """, (data.materialName.strip(), data.materialImage, True))

        material_id = self.cursor.lastrowid

        # Loop through each thickness in the materialThickness list
        for thickness in data.materialThicknesses:
            self.cursor.execute("""
            INSERT INTO Thicknesses (material_id, thickness) VALUES (?, ?)
            """, (material_id, float(thickness.thicknessValue)))
            thickness_id = self.cursor.lastrowid

            # Loop through each operation in the thicknessOperations list
            for operation in thickness.thicknessOperations:
                self.cursor.execute("""
                INSERT INTO Operations (thickness_id, operation_type, power, speed, tool) VALUES (?, ?, ?, ?, ?)
                """, (thickness_id, operation.operationType, operation.power, operation.speed, operation.tool))
                operation_id = self.cursor.lastrowid

                # If there is dithering data, insert it into Engraving_Settings
                if operation.operationType == 'Engrave' and operation.dithering:
                    dithering = operation.dithering
                    self.cursor.execute("""
                    INSERT INTO Engraving_Settings (operation_id, algorithm, resolution, gray_shift, block_size, block_distance) VALUES (?, ?, ?, ?, ?, ?)
                    """, (operation_id, dithering.algorithm, dithering.resolution, dithering.grayShift, dithering.blockSize, dithering.blockDistance))

        # Commit the transaction to save changes
        self.cursor.connection.commit()

        # get the material list after adding a new material
        result = self.handle_get_materials_list()
        return result

    def handle_update_material(self, data):
        material_id = data.materialId
        # Update the material data in the Materials table
        self.cursor.execute("""
        UPDATE Materials SET name = ?, image = ? WHERE id = ?
        """, (data.materialName.strip(), data.materialImage, material_id))

        # Get existing thicknesses and operations for the material
        self.cursor.execute("""
        SELECT id FROM Thicknesses WHERE material_id = ?
        """, (material_id,))
        existing_thicknesses = {row[0] for row in self.cursor.fetchall()}

        for thickness in data.materialThicknesses:
            thickness_value = float(thickness.thicknessValue)

            # Check if thickness already exists
            self.cursor.execute("""
            SELECT id FROM Thicknesses WHERE material_id = ? AND thickness = ?
            """, (material_id, thickness_value))
            thickness_row = self.cursor.fetchone()

            if thickness_row:
                # Get the existing thickness ID
                thickness_id = thickness_row[0]
            else:
                # Insert new thickness and get its ID
                self.cursor.execute("""
                INSERT INTO Thicknesses (material_id, thickness) VALUES (?, ?)
                """, (material_id, thickness_value))
                thickness_id = self.cursor.lastrowid
            existing_thicknesses.discard(thickness_id)

            # Get existing operations for this thickness
            self.cursor.execute("""
            SELECT id FROM Operations WHERE thickness_id = ?
            """, (thickness_id,))
            existing_operations = {row[0] for row in self.cursor.fetchall()}

            for operation in thickness.thicknessOperations:
                operation_type = operation.operationType
                power = operation.power
                speed = operation.speed
                tool = operation.tool

                # Check if operation already exists
                self.cursor.execute("""
                SELECT id FROM Operations WHERE thickness_id = ? AND operation_type = ?
                """, (thickness_id, operation_type))
                operation_row = self.cursor.fetchone()

                if operation_row:
                    # Update existing operation
                    operation_id = operation_row[0]
                    self.cursor.execute("""
                    UPDATE Operations SET power = ?, speed = ?, tool = ? WHERE id = ?
                    """, (power, speed, tool, operation_id))
                else:
                    # Insert new operation
                    self.cursor.execute("""
                    INSERT INTO Operations (thickness_id, operation_type, power, speed, tool) VALUES (?, ?, ?, ?, ?)
                    """, (thickness_id, operation_type, power, speed, tool))
                    operation_id = self.cursor.lastrowid

                existing_operations.discard(operation_id)

                # If the operation is 'Engrave', update or insert dithering settings
                if operation_type == 'Engrave' and operation.dithering:
                    dithering = operation.dithering
                    self.cursor.execute("""
                    SELECT id FROM Engraving_Settings WHERE operation_id = ?
                    """, (operation_id,))
                    engraving_row = self.cursor.fetchone()

                    if engraving_row:
                        # Update existing engraving settings
                        self.cursor.execute("""
                        UPDATE Engraving_Settings SET algorithm = ?, resolution = ?, gray_shift = ?, block_size = ?, block_distance = ? WHERE id = ?
                        """, (dithering.algorithm, dithering.resolution, dithering.grayShift, dithering.blockSize, dithering.blockDistance, engraving_row[0]))
                    else:
                        # Insert new engraving settings
                        self.cursor.execute("""
                        INSERT INTO Engraving_Settings (operation_id, algorithm, resolution, gray_shift, block_size, block_distance) VALUES (?, ?, ?, ?, ?, ?)
                        """, (operation_id, dithering.algorithm, dithering.resolution, dithering.grayShift, dithering.blockSize, dithering.blockDistance))

            # Delete any operations not present in the update data
            if existing_operations:
                self.cursor.execute(f"""
                DELETE FROM Operations WHERE id IN ({','.join('?' for _ in existing_operations)})
                """, tuple(existing_operations))

        # Delete any thicknesses not present in the update data
        if existing_thicknesses:
            self.cursor.execute(f"""
            DELETE FROM Thicknesses WHERE id IN ({','.join('?' for _ in existing_thicknesses)})
            """, tuple(existing_thicknesses))

        # Commit the changes to save the updates
        self.cursor.connection.commit()

        # get the material list after updating a new material
        result = self.handle_get_materials_list()
        return result

    def handle_fetch_material_image(self, material_name):
        # Delete Engraving_Settings related to the material
        self.cursor.execute("""
        SELECT image FROM Materials WHERE name = ? 
        """, (material_name,))

        # Fetch the result
        result = self.cursor.fetchone()

        # Check if the material was found
        if result:
            # Return the image (the first and only column in the result)
            return result[0]
        else:
            return None

    def handle_delete_material(self, material_id):
        # Delete Engraving_Settings related to the material
        self.cursor.execute("""
        DELETE FROM Engraving_Settings WHERE operation_id IN (
            SELECT id FROM Operations WHERE thickness_id IN (
                SELECT id FROM Thicknesses WHERE material_id = ?
            )
        )
        """, (material_id,))

        # Delete Operations related to the material
        self.cursor.execute("""
        DELETE FROM Operations WHERE thickness_id IN (
            SELECT id FROM Thicknesses WHERE material_id = ?
        )
        """, (material_id,))

        # Delete Thicknesses related to the material
        self.cursor.execute("""
        DELETE FROM Thicknesses WHERE material_id = ?
        """, (material_id,))

        # Delete the Material
        self.cursor.execute("""
        DELETE FROM Materials WHERE id = ?
        """, (material_id,))

        # Commit the changes to save the deletions
        self.cursor.connection.commit()

        # get the material list after deleting a new material
        result = self.handle_get_materials_list()
        return result

    def add_default_materials_data_to_materials_library_tables(self):
        DefaultMaterialsData.add_default_data(self.cursor)

    def handle_error_requests(self, process):
        return self.fastapi_material_library_response(
            type=constants.MATERIALS_LIBRARY_DATA_TYPE,
            process=process,
            materials_list='',
            success=False
        )

    def fastapi_material_library_response(self, type, process, materials_list, success):
        return {
            'type': type,
            'data': {
                'process': process,
                'materialsList': materials_list,
                'success': success
            }
        }
