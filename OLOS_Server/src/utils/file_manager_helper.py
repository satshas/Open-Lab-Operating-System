import re
from core.constants import CoreConstants as constants


class FileManagerHelper:
    def __init__(self, gcode_file_manager, material_library_helper):
        self._gcode_file_manager = gcode_file_manager
        self._material_library_helper = material_library_helper

    def handle_upload_file(self, filename, file_content):
        # Create a new file with the same name of the file uploaded
        self._gcode_file_manager.write_gcode_file(filename, file_content)
        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.UPLOAD_FILE_PROCESS,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    # open selected file by user

    def handle_open_file(self, filename):
        self._gcode_file_manager.open_file(filename)

        material_name, material_image, material_thickness = self._get_opened_file_material_settings()
        file_content = self._gcode_file_manager.get_opened_file_content()

        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.OPEN_FILE_PROCESS,
            file_data={
                'fileName': filename,
                'fileContent': file_content if file_content else '',
                'materialName': material_name if material_name else '-',
                'materialImage': material_image if material_image else '',
                'materialThickness': material_thickness if material_thickness else '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    # start executing the gcode commands inside the opened file

    def handle_start_file(self, machine_connector, file_execution_timer):
        opened_file = self._gcode_file_manager.get_open_filename()
        # make sure the file is open
        if opened_file is not None:
            # reopen in case of restarting the file again
            self._gcode_file_manager.open_file(opened_file)

            # when start executing file reset the counter
            machine_connector.reset_counter()

            # reset the file execution timer and start new one
            file_execution_timer.reset()
            file_execution_timer.start()

            material_name, material_image, material_thickness = self._get_opened_file_material_settings()
            file_content = self._gcode_file_manager.get_opened_file_content()

            # get opened file
            response = self.fastapi_file_manager_response(
                type=constants.FILE_MANAGER_DATA_TYPE,
                process=constants.START_FILE_PROCESS,
                file_data={
                    'fileName': opened_file,
                    'fileContent': file_content,
                    'materialName': material_name,
                    'materialImage': material_image,
                    'materialThickness': material_thickness
                },
                files_list=self._gcode_file_manager.get_files_list(),
                success=True
            )

        else:
            print('There is no file open in the system')
            # get opened file
            response = self.fastapi_file_manager_response(
                type=constants.FILE_MANAGER_DATA_TYPE,
                process=constants.START_FILE_PROCESS,
                file_data={
                    'fileName': '-',
                    'fileContent': '',
                    'materialName': '-',
                    'materialImage': '',
                    'materialThickness': '-'
                },
                files_list=self._gcode_file_manager.get_files_list(),
                success=False
            )

        return response

    # delete specific file base on its name

    def handle_delete_file(self, filename):
        # delete the file from the system
        self._gcode_file_manager.delete_file(filename)

        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.DELETE_FILE_PROCESS,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    # download specific file based on its name

    def handle_download_file(self, filename):
        # download the file from the system
        file_path = self._gcode_file_manager.get_file_path(filename)
        return file_path

    def handle_generate_gcode_file(self, cutting_svg_file=None, marking_svg_file=None, image_file=None, gcode_settings={}):
        # generate gcode for svg/image file(s)
        self._gcode_file_manager.generate_gcode_file(
            cutting_svg_file, marking_svg_file, image_file, gcode_settings)

        filename = gcode_settings.get('fileName')

        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.GENERATE_FILE_PROCESS,
            file_data={
                'fileName': filename,
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    def handle_rename_file(self, old_filename, new_filename):
        self._gcode_file_manager.rename_file(old_filename, new_filename)

        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.RENAME_FILE_PROCESS,
            file_data={
                'fileName': new_filename,
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    def handle_check_opened_file(self):
        file_name = self._gcode_file_manager.get_open_filename()
        material_name, material_image, material_thickness = self._get_opened_file_material_settings()
        file_content = self._gcode_file_manager.get_opened_file_content()

        response = self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=constants.CHECK_FILE_PROCESS,
            file_data={
                'fileName': file_name if file_name else '-',
                'fileContent': file_content if file_content else '',
                'materialName': material_name if material_name else '-',
                'materialImage': material_image if material_image else '',
                'materialThickness': material_thickness if material_thickness else '-'
            },
            files_list=self._gcode_file_manager.get_files_list(),
            success=True
        )

        return response

    def _get_opened_file_material_settings(self):
        file_content = self._gcode_file_manager.get_opened_file_content()
        # Extracting material settings values from file content
        material_name_match = re.search(
            f"{constants.MATERIAL_NAME_SEARCH_KEYWORD}\s*(.*)", file_content)
        material_thickness_match = re.search(
            f"{constants.MATERIAL_THICKNESS_SEARCH_KEYWORD}\s*(.*)", file_content)

        material_name = material_name_match.group(
            1) if material_name_match else ''
        material_thickness = material_thickness_match.group(
            1) if material_thickness_match else ''

        # fetch material image from the database if any
        material_image = self._material_library_helper.handle_fetch_material_image(
            material_name)

        return material_name, material_image, material_thickness

    def handle_error_requests(self, process):
        return self.fastapi_file_manager_response(
            type=constants.FILE_MANAGER_DATA_TYPE,
            process=process,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list='',
            success=False
        )

    def fastapi_file_manager_response(self, type, process, file_data, files_list, success):
        return {
            'type': type,
            'data': {
                'process': process,
                'fileData': file_data,
                'filesListData': files_list,
                'success': success
            }
        }
