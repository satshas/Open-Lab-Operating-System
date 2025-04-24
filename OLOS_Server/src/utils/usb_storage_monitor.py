import os
import stat
import time
import platform
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, DEVTYPE, DEVNAME
from core.constants import CoreConstants as constants

from utils.websocket_json_data import WebsocketJsonData


class USBStorageMonitor:
    def __init__(self, jobs_manager, images_manager, core_websocket_write_queue):
        self._jobs_manager = jobs_manager
        self._images_manager = images_manager
        self.write_queue = core_websocket_write_queue

        # Create and start the USB monitor
        self._monitor = USBMonitor()

    def start(self):
        self._monitor.start_monitoring(
            on_connect=self._on_connect, on_disconnect=self._on_disconnect)

    def _is_usb_storage(self, device_info):
        return device_info.get(DEVTYPE) in ['USBSTOR', 'usb_device']

    def _on_connect(self, device_id, device_info):
        if self._is_usb_storage(device_info):
            # Check if the device is ready for use
            mount_point = None
            while True:
                mount_point = self._resolve_mount_point(
                    device_info)
                if mount_point:
                    break
                time.sleep(0.5)

            if mount_point:
                files_data = self._get_usb_storage_files_data(mount_point)
                res = WebsocketJsonData.parse_usb_storage_monitor_data_to_json(
                    device_name=device_info[ID_MODEL],
                    job_files_data=files_data["job_files_list"],
                    image_files_data=files_data["image_files_list"],
                    is_connected=True
                )
                self.write_queue.put(constants.USB_STORAGE_MONITOR_DATA_TYPE,
                                     constants.MIDDLE_PRIORITY_COMMAND,
                                     res)

    def _on_disconnect(self, device_id, device_info):
        if self._is_usb_storage(device_info):
            res = WebsocketJsonData.parse_usb_storage_monitor_data_to_json(
                device_name=device_info[ID_MODEL],
                job_files_data=[],
                image_files_data=[],
                is_connected=False)

            self.write_queue.put(constants.USB_STORAGE_MONITOR_DATA_TYPE,
                                 constants.MIDDLE_PRIORITY_COMMAND,
                                 res)

    def _resolve_mount_point(self, device_info):
        system = platform.system()
        if system == "Windows":
            return self._get_windows_mount_point()

        elif system == "Linux":
            return self._get_linux_mount_point()

        elif system == "Darwin":
            return self._get_mac_mount_point()

        print(f"Could not resolve mount point for {device_info.get(DEVNAME)}.")
        return None

    def _get_windows_mount_point(self):
        import win32api
        import win32file

        # Wait for a few seconds to ensure the device is fully mounted
        time.sleep(5)
        drives = win32api.GetLogicalDriveStrings().split('\x00')
        for drive in drives:
            drive_type = win32file.GetDriveType(drive)
            if drive_type == win32file.DRIVE_REMOVABLE:
                return drive

    def _get_linux_mount_point(self):
        import pyudev
        import psutil

        context = pyudev.Context()
        removable = [device for device in context.list_devices(
            subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
        for device in removable:
            partitions = [device.device_node for device in context.list_devices(
                subsystem='block', DEVTYPE='partition', parent=device)]
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    return p.mountpoint

        return None

    def _get_mac_mount_point(self):
        volumes_dir = "/Volumes"
        for mount in os.listdir(volumes_dir):
            mount_path = os.path.join(volumes_dir, mount)
            if os.path.ismount(mount_path):
                return mount_path

    def _get_usb_storage_files_data(self, mount_point):
        if not os.path.isdir(mount_point):
            return {"job_files_list": [], "image_files_list": []}

        def is_file_hidden(filepath):
            # Check if file or directory is hidden (dotfile or hidden attribute)
            name = os.path.basename(os.path.abspath(filepath))
            return name.startswith('.') or has_hidden_attribute(filepath)

        def has_hidden_attribute(filepath):
            # Check if hidden attribute is set (for Windows)
            try:
                return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except AttributeError:
                # If the attribute does not exist (non-Windows), return False
                return False

        def collect_file_data(file_id, filename, file_path, mount_point, file_type):
            if file_type == "job":
                return self._get_file_data(file_id, filename, file_path, mount_point)
            elif file_type == "image":
                return self._get_image_data(file_id, filename, file_path, mount_point)

        job_files_list = []
        image_files_list = []
        job_id = 0
        image_id = 0

        # Walk the directory
        for root, dirs, files in os.walk(mount_point):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not is_file_hidden(os.path.join(root, d))]

            for filename in files:
                file_path = os.path.join(root, filename)
                if not is_file_hidden(file_path):  # Skip hidden files
                    if filename.lower().endswith(constants.ACCEPTED_JOB_FILES_EXTENSIONS):
                        job_files_list.append(
                            collect_file_data(job_id, filename, file_path, mount_point, "job")
                        )
                        job_id += 1
                    elif filename.lower().endswith(tuple(constants.ACCEPTED_IMAGE_FILES_EXTENSIONS.keys())):
                        image_files_list.append(
                            collect_file_data(image_id, filename, file_path, mount_point, "image")
                        )
                        image_id += 1

        return {"job_files_list": job_files_list, "image_files_list": image_files_list}

    def _get_file_data(self, id, filename, file_path, mount_point):
        file_size = self._jobs_manager.get_file_size(
            file_path)
        file_creation_time = self._jobs_manager.get_file_creation_time(
            file_path)
        return {'id': id, "file": filename, "path": file_path, "size": file_size, "date": file_creation_time, "mountPoint": mount_point}

    def _get_image_data(self, id, image_name, image_path, mount_point):
        image_size = self._images_manager.get_image_size(
            image_path)
        image_creation_time = self._images_manager.get_image_creation_time(
            image_path)
        return {'id': id, "file": image_name, "path": image_path, "size": image_size, "date": image_creation_time, "mountPoint": mount_point}
