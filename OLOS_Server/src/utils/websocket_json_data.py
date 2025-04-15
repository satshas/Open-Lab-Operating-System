import datetime
import json
import re
from core.constants import CoreConstants as constants


class WebsocketJsonData:
    @classmethod
    def parse_grbl_status_to_json(cls, machine_status):
        # Define regular expressions to extract values
        state_pattern = re.compile(r'<(\w+)|')
        machine_position_pattern = re.compile(
            r'MPos:([-\d.]+),([-\d.]+),([-\d.]+)')
        work_coordinate_offset_pattern = re.compile(
            r'WCO:([-\d.]+),([-\d.]+),([-\d.]+)')
        buffer_pattern = re.compile(r'Bf:(\d+),(\d+)')
        feed_speed_pattern = re.compile(r'FS:(\d+),(\d+)')
        override_pattern = re.compile(r'Ov:(\d+),(\d+),(\d+)')
        machine_tool_pattern = re.compile(r'T:(\d+)')

        # Extract values using regular expressions
        state_match = state_pattern.search(machine_status)
        machine_position_match = machine_position_pattern.search(
            machine_status)
        work_coordinate_offset_match = work_coordinate_offset_pattern.search(
            machine_status)
        buffer_match = buffer_pattern.search(machine_status)
        feed_speed_match = feed_speed_pattern.search(machine_status)
        override_match = override_pattern.search(machine_status)
        machine_tool_match = machine_tool_pattern.search(machine_status)

        # Create a dictionary with extracted values
        status_dict = {
            "type": constants.MACHINE_STATUS_DATA_TYPE,
            "state": state_match.group(1) if state_match else None,
            "machine_position": {
                "x": float(machine_position_match.group(1)) if machine_position_match else None,
                "y": float(machine_position_match.group(2)) if machine_position_match else None,
                "z": float(machine_position_match.group(3)) if machine_position_match else None,
            },
            "work_coordinate_offset": {
                "x": float(work_coordinate_offset_match.group(1)) if work_coordinate_offset_match else None,
                "y": float(work_coordinate_offset_match.group(2)) if work_coordinate_offset_match else None,
                "z": float(work_coordinate_offset_match.group(3)) if work_coordinate_offset_match else None,
            },
            "buffer_state": {
                "commands_queued": float(buffer_match.group(1)) if buffer_match else None,
                "buffer_length": float(buffer_match.group(2)) if buffer_match else None,
            },
            "feed_and_speed": {
                "feed_rate": float(feed_speed_match.group(1)) if feed_speed_match else None,
                "speed": float(feed_speed_match.group(2)) if feed_speed_match else None,
            },
            "overrides": {
                "feed": float(override_match.group(1)) if override_match else None,
                "rapids": float(override_match.group(2)) if override_match else None,
                "spindle": float(override_match.group(3)) if override_match else None,
            },
            "machine_tool": float(machine_tool_match.group(1)) if machine_tool_match else None
        }

        return json.dumps(status_dict, indent=2)

    @classmethod
    def parse_serial_command_to_json(cls, command):
        dict = {"type": constants.SERIAL_COMMAND_DATA_TYPE,
                "text": command,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        return json.dumps(dict, indent=2)

    @classmethod
    def parse_job_execution_command_to_json(cls, command, line_index, total_lines, file_timer):
        dict = {"type": constants.JOB_EXECUTION_DATA_TYPE,
                "text": command,
                "line_index": line_index,
                "total_lines": total_lines,
                "file_timer": file_timer,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        return json.dumps(dict, indent=2)

    @classmethod
    def parse_file_manager_message_to_json(cls, opened_filename, file_content, files_list):
        dict = {"type": constants.JOBS_MANAGER_DATA_TYPE,
                "opened_file": opened_filename,
                "file_content": file_content,
                "files_list": files_list,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        return json.dumps(dict, indent=2)

    @classmethod
    def parse_connection_status_to_json(cls, success):
        dict = {"type": constants.MACHINE_CONNECTION_DATA_TYPE,
                "success": success,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        return json.dumps(dict, indent=2)

    @classmethod
    def parse_cameras_frame_to_json(cls, frameStr):
        dict = {"type": constants.CAMERAS_SYSTEM_STREAM_DATA_TYPE,
                "frame": frameStr,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        return json.dumps(dict, indent=2)

    @classmethod
    def parse_usb_storage_monitor_data_to_json(cls, device_name, job_files_data, image_files_data, is_connected):
        dict = {"type": constants.USB_STORAGE_MONITOR_DATA_TYPE,
                "device_name": device_name,
                "job_files_data": job_files_data,
                "image_files_data": image_files_data,
                "is_connected": is_connected,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        return json.dumps(dict, indent=2)
