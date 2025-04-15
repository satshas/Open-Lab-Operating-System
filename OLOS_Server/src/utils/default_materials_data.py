class DefaultMaterialsData:
    @classmethod
    def add_default_data(cls, cursor):
        # material
        cursor.execute("""
        INSERT OR IGNORE INTO Materials (id, name, image, isEditable) VALUES
        (1, 'default', '', 0)
        """)

        # thickness
        # 1
        cursor.execute("""
        INSERT OR IGNORE INTO Thicknesses (id, material_id, thickness) VALUES
        (1, 1, 1)""")

        # 2
        cursor.execute("""
        INSERT OR IGNORE INTO Thicknesses (id, material_id, thickness) VALUES
        (2, 1, 2)
        """)

        # 3
        cursor.execute("""
        INSERT OR IGNORE INTO Thicknesses (id, material_id, thickness) VALUES
        (3, 1, 3)
        """)

        # operations
        # 1-1
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (1, 1, 'Cut', 10, 3000, 'CO2')
        """)

        # 1-2
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (2, 1, 'Mark', 10, 3000, 'CO2')
        """)

        # 1-3
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (3, 1, 'Engrave', 20, 3000, 'Diode')
        """)

        # 2-1
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (4, 2, 'Cut', 25, 2000, 'CO2')
        """)

        # 2-2
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (5, 2, 'Mark', 25, 2000, 'CO2')
        """)

        # 2-3
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (6, 2, 'Engrave', 40, 2500, 'Diode')
        """)

        # 3-1
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (7, 3, 'Cut', 40, 1500, 'CO2')
        """)

        # 3-2
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (8, 3, 'Mark', 40, 1000, 'CO2')
        """)

        # 3-3
        cursor.execute("""
        INSERT OR IGNORE INTO Operations (id, thickness_id, operation_type, power, speed, tool) VALUES
        (9, 3, 'Engrave', 60, 1500, 'Diode')
        """)

        # engraving settings

        # 1
        cursor.execute("""
        INSERT OR IGNORE INTO Engraving_Settings (id, operation_id, algorithm, resolution, gray_shift, block_size, block_distance) VALUES
        (1, 3, 'Halftone', 200, 0, 0.5, 0.1)
        """)

        # 2
        cursor.execute("""
        INSERT OR IGNORE INTO Engraving_Settings (id, operation_id, algorithm, resolution, gray_shift, block_size, block_distance) VALUES
        (2, 6, 'Floyd-Steinberg', 200, 0, 0.5, 0.1)
        """)

        # 3
        cursor.execute("""
        INSERT OR IGNORE INTO Engraving_Settings (id, operation_id, algorithm, resolution, gray_shift, block_size, block_distance) VALUES
        (3, 9, 'Average', 200, 0, 0.5, 0.1)
        """)
