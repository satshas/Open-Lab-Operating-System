from core.constants import CoreConstants as constants


class ImagesManagerHelper:
    def __init__(self, images_manager):
        self._images_manager = images_manager

    def handle_list_images_data(self):
        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.LIST_IMAGES_DATA_PROCESS,
            image_data={
                'imageName': '',
                'imageSource': '',
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    def handle_upload_image(self, image_name, image_content):
        # Create a new image with the same name of the image uploaded
        self._images_manager.write_image_file(image_name, image_content)
        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.UPLOAD_IMAGE_PROCESS,
            image_data={
                'imageName': '',
                'imageSource': '',
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    # delete specific image base on its name

    def handle_delete_image(self, image_name):
        # delete the image from the system
        self._images_manager.delete_image(image_name)

        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.DELETE_IMAGE_PROCESS,
            image_data={
                'imageName': '',
                'imageSource': '',
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    def handle_rename_file(self, old_image_name, new_image_name):
        self._images_manager.rename_image(old_image_name, new_image_name)

        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.RENAME_IMAGE_PROCESS,
            image_data={
                'imageName': new_image_name,
                'imageSource': '',
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    def handle_fetch_image_data(self, image_name):
        image_source_str = self._images_manager.get_image_source_string(
            image_name)

        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.FETCH_IMAGE_DATA_PROCESS,
            image_data={
                'imageName': image_name,
                'imageSource': image_source_str,
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    # copy usb image to system

    def handle_copy_image_to_system(self, image_path):
        self._images_manager.copy_image_file(image_path)

        response = self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=constants.UPLOAD_USB_IMAGE_FILE_PROCESS,
            image_data={
                'imageName': '',
                'imageSource': '',
            },
            images_list=self._images_manager.get_images_list(),
            success=True,
        )

        return response

    def handle_error_requests(self, process):
        return self.fastapi_images_manager_response(
            type=constants.IMAGES_MANAGER_DATA_TYPE,
            process=process,
            image_data={
                'imageName': '',
                'imageSource': '',
            },
            images_list='',
            success=False,
        )

    def fastapi_images_manager_response(self, type, process, image_data, images_list, success):
        return {
            'type': type,
            'data': {
                'process': process,
                'imageData': image_data,
                'imagesListData': images_list,
                'success': success,
            }
        }
