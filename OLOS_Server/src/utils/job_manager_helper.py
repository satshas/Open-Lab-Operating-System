import multiprocessing
import re
from core.constants import CoreConstants as constants
from files_manager.jobs_manager import JobsManager
from utils.materials_library_helper import MaterialsLibraryHelper


def generate_file(gcode_file_data, queue):
    jobs_manager = JobsManager()
    material_library_helper = MaterialsLibraryHelper()
    file_manager_helper = JobsManagerHelper(
        jobs_manager, material_library_helper)

    # generate gcode for image file(s)
    jobs_manager.generate_gcode_file(
        gcode_file_data)

    filename = gcode_file_data.name

    response = file_manager_helper.fastapi_jobs_manager_response(
        type=constants.JOBS_MANAGER_DATA_TYPE,
        process=constants.GENERATE_JOB_PROCESS,
        file_data={
            'fileName': filename,
            'fileContent': '',
            'materialName': '-',
            'materialImage': '',
            'materialThickness': '-'
        },
        files_list=jobs_manager.get_files_list(),
        success=True
    )
    queue.put(response)


class JobsManagerHelper:
    def __init__(self, jobs_manager, material_library_helper):
        self._jobs_manager = jobs_manager
        self._material_library_helper = material_library_helper

        # running generating process on seperate process
        self._generate_file_process = None

    def handle_upload_file(self, filename, file_content):
        # Create a new file with the same name of the file uploaded
        self._jobs_manager.write_gcode_file(filename, file_content)
        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.UPLOAD_JOB_PROCESS,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )

        return response

    # open selected file by user

    def handle_open_file(self, filename):
        self._jobs_manager.open_file(filename)

        material_name, material_image, material_thickness = self._get_opened_file_material_settings()
        file_content = self._jobs_manager.get_opened_file_content()

        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.OPEN_JOB_PROCESS,
            file_data={
                'fileName': filename,
                'fileContent': file_content if file_content else '',
                'materialName': material_name if material_name else '-',
                'materialImage': material_image if material_image else '',
                'materialThickness': material_thickness if material_thickness else '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )

        return response

    # start executing the gcode commands inside the opened file

    def handle_start_file(self, machine_connector, job_execution_timer):
        opened_file = self._jobs_manager.get_open_filename()
        # make sure the file is open
        if opened_file is not None:
            # reopen in case of restarting the file again
            self._jobs_manager.open_file(opened_file)

            # when start executing file reset the counter
            machine_connector.reset_counter()

            # reset the job execution timer and start new one
            job_execution_timer.reset()
            job_execution_timer.start()

            material_name, material_image, material_thickness = self._get_opened_file_material_settings()
            file_content = self._jobs_manager.get_opened_file_content()

            # get opened file
            response = self.fastapi_jobs_manager_response(
                type=constants.JOBS_MANAGER_DATA_TYPE,
                process=constants.START_JOB_PROCESS,
                file_data={
                    'fileName': opened_file,
                    'fileContent': file_content,
                    'materialName': material_name,
                    'materialImage': material_image,
                    'materialThickness': material_thickness
                },
                files_list=self._jobs_manager.get_files_list(),
                success=True,
            )

        else:
            print('There is no file open in the system')
            # get opened file
            response = self.fastapi_jobs_manager_response(
                type=constants.JOBS_MANAGER_DATA_TYPE,
                process=constants.START_JOB_PROCESS,
                file_data={
                    'fileName': '-',
                    'fileContent': '',
                    'materialName': '-',
                    'materialImage': '',
                    'materialThickness': '-'
                },
                files_list=self._jobs_manager.get_files_list(),
                success=False,
            )

        return response

    # delete specific file base on its name

    def handle_delete_file(self, filename):
        # delete the file from the system
        self._jobs_manager.delete_file(filename)

        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.DELETE_JOB_PROCESS,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )

        return response

    # download specific file based on its name

    def handle_download_file(self, filename):
        # download the file from the system
        file_path = self._jobs_manager.get_file_path(filename)
        return file_path

    def handle_generate_gcode_file(self, gcode_file_data, write_queue):
        # Start the generate_images function in a separate process
        self._generate_file_process = multiprocessing.Process(
            target=generate_file, args=(gcode_file_data, write_queue))
        self._generate_file_process.start()

    def handle_cancel_generate_file(self):
        # Signal the cancel event and terminate the process if it's running
        if self._generate_file_process is not None:
            self._generate_file_process.terminate()
            self._generate_file_process.join()

        files_list = self._jobs_manager.get_files_list(),
        result = self.fastapi_jobs_manager_response(
            constants.JOBS_MANAGER_DATA_TYPE, constants.CANCEL_GENERATE_JOB_PROCESS, '', files_list, True
        )

        return result

    def handle_rename_file(self, old_filename, new_filename):
        self._jobs_manager.rename_file(old_filename, new_filename)

        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.RENAME_JOB_PROCESS,
            file_data={
                'fileName': new_filename,
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )

        return response

    def handle_check_opened_file(self):
        file_name = self._jobs_manager.get_open_filename()
        material_name, material_image, material_thickness = self._get_opened_file_material_settings()
        file_content = self._jobs_manager.get_opened_file_content()

        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.CHECK_JOB_PROCESS,
            file_data={
                'fileName': file_name if file_name else '-',
                'fileContent': file_content if file_content else '',
                'materialName': material_name if material_name else '-',
                'materialImage': material_image if material_image else '',
                'materialThickness': material_thickness if material_thickness else '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )
        return response

    # copy usb file to system

    def handle_copy_file_to_system(self, file_path):
        self._jobs_manager.copy_gcode_file(file_path)

        response = self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=constants.UPLOAD_USB_JOB_FILE_PROCESS,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage':  '',
                'materialThickness': '-'
            },
            files_list=self._jobs_manager.get_files_list(),
            success=True,
        )

        return response

    def _get_opened_file_material_settings(self):
        file_content = self._jobs_manager.get_opened_file_content()
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
        material_image = ''
        if self._material_library_helper:
            material_image = self._material_library_helper.handle_fetch_material_image(
                material_name)

        return material_name, material_image, material_thickness

    def handle_error_requests(self, process):
        return self.fastapi_jobs_manager_response(
            type=constants.JOBS_MANAGER_DATA_TYPE,
            process=process,
            file_data={
                'fileName': '-',
                'fileContent': '',
                'materialName': '-',
                'materialImage': '',
                'materialThickness': '-'
            },
            files_list='',
            success=False,
        )

    def fastapi_jobs_manager_response(self, type, process, file_data, files_list, success):
        return {
            'type': type,
            'data': {
                'process': process,
                'fileData': file_data,
                'filesListData': files_list,
                'success': success,
            }
        }
