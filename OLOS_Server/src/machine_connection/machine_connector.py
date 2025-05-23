import time
from multiprocessing import Process
from utils.configuration_loader import ConfigurationLoader
from utils.joystick_handler import JoystickHandler
from utils.serial_connection import SerialConnection
from .constants import MachineConstants as constants
import os
from dotenv import load_dotenv

load_dotenv()
# Special module to control the machine command execution


class MachineConnector(Process):
    def __init__(self, machine_connector_data):
        super(MachineConnector, self).__init__()

        # shared objects dictionary with the core
        self.machine_connector_data = machine_connector_data

        # helper instances
        self._serial_connection = SerialConnection()

        # Get the current time seconds
        self._current_refresh_status_time = time.time()

        # flag for machine door status used at the start of the machine to check if the door is open or not for the homing process
        self._is_machine_door_open_on_start = True

        # configuration settings
        self._config = None

    def run(self):
        try:
            self._config = ConfigurationLoader.from_yaml()

            # start serial connection
            self._serial_connection.connect_to_serial(
                self._config.serial_connection.port, self._config.serial_connection.baudrate, self._config.serial_connection.timeout)

            if self._serial_connection.is_serial_connected():

                # notify the core that the machine is connected
                self.add_to_serial_read_queue(constants.MACHINE_CONNECTION_DATA_TYPE,
                                              constants.HIGH_PRIORITY_COMMAND,
                                              True)

                self.start_machine_communication()

            else:
                print("There is no serial connection")
                # notify the core that the machine is disconnected
                self.add_to_serial_read_queue(constants.MACHINE_CONNECTION_DATA_TYPE,
                                              constants.HIGH_PRIORITY_COMMAND,
                                              False)

                self.reconnect_to_serial()

        except Exception as error:
            print("Serial Connection Error:", error)
            self._serial_connection.disconnect_serial()

            # notify the core that the machine is disconnected
            self.add_to_serial_read_queue(constants.MACHINE_CONNECTION_DATA_TYPE,
                                          constants.HIGH_PRIORITY_COMMAND,
                                          False)

            self.reconnect_to_serial()

    # Start fetching and sending data

    def start_machine_communication(self):

        self.reset_counter()
        while True:
            self.handle_reading_from_serial()
            self.handle_writing_to_serial()
            self.fetch_machine_status()

            if not self.machine_connector_data.is_job_execute_process:
                time.sleep(constants.TIMEOUT)

    # Writing data to the serial port

    def handle_writing_to_serial(self):
        '''
        make sure that the queue is not empty and 
        all the command in the machine got executed
        and the machine is not changing the tool to not overflow the buffer
        '''

        if not self.machine_connector_data.serial_write_queue.empty():
            type, gcode_command = self.machine_connector_data.serial_write_queue.get()
            if gcode_command:
                # increase the counter to wait for
                # an ok message after sending a command to the machine
                self.machine_connector_data.ok_messages_counter += 1

                self._serial_connection.write_to_serial(gcode_command)

    # Reading data from the serial
    def handle_reading_from_serial(self):
        # read incoming bytes from serial and convert it to string
        data_to_fetch = self._serial_connection.read_from_serial()
        if data_to_fetch:
            if constants.GRBL_ANSWER_OK in data_to_fetch:
                # decrease the counter because the machine replied
                # with an ok message after sending a command to the machine
                self.machine_connector_data.ok_messages_counter -= 1

            # check if the machine's door is open (for the homing the machine process)
            elif self._is_machine_door_open_on_start and data_to_fetch.startswith('<Idle'):
                self._is_machine_door_open_on_start = False

                if self._config.home_machine_on_start:
                    self.homing_machine()

            # machine status reply
            elif data_to_fetch.startswith('<') and data_to_fetch.endswith('>'):
                self.add_to_serial_read_queue(constants.MACHINE_STATUS_DATA_TYPE,
                                              constants.MIDDLE_PRIORITY_COMMAND,
                                              data_to_fetch)

            # ignore gcode parser state
            elif data_to_fetch.startswith('[') and data_to_fetch.endswith(']'):
                pass

            # rest of commands
            else:
                if constants.TOOL_CHANGER_SUCCESS in data_to_fetch:
                    # check if the machine finished changing the tool
                    # it will reply with TOCK message
                    self.machine_connector_data.is_tool_change_process = False
                    # reset the counter after tool change because the pico will
                    # execute different commands where the server will not count
                    self.reset_counter()

                elif constants.TOOL_CHANGER_ERROR in data_to_fetch:
                    # Error happened during changing the tool
                    if os.getenv('ENV') == 'development':
                        print('Error happened during changing the tool')
                    self.stop_machine()

                elif constants.SOFT_LIMITS_TRIGGER == data_to_fetch:
                    # make sure that the counter stay updated if the command is not passed to the machine
                    self.reset_counter()

                self.add_to_serial_read_queue(constants.SERIAL_COMMAND_DATA_TYPE,
                                              constants.LOW_PRIORITY_COMMAND,
                                              data_to_fetch)

    def fetch_machine_status(self):
        # Refresh every specific time interval while the machine in pause/run status
        time_interval = constants.STATUS_REFRESH_INTERVAL_PAUSE if self.machine_connector_data.is_machine_pause else constants.STATUS_REFRESH_INTERVAL_RUN
        if time.time() - self._current_refresh_status_time > time_interval:
            self.update_machine_status()

    def update_machine_status(self):
        # Update the time
        self._current_refresh_status_time = time.time()

        # Stop asking the status after a specific value
        if self.machine_connector_data.ok_messages_counter <= constants.MAX_COUNTER_VALUE:
            # Send a status command to the machine
            self.add_to_serial_write_queue(constants.MACHINE_STATUS_DATA_TYPE,
                                           constants.MIDDLE_PRIORITY_COMMAND, constants.GRBL_COMMAND_STATUS)
    # add new command to the serial write queue

    def add_to_serial_write_queue(self, type, priority, command):
        self.machine_connector_data.serial_write_queue.put(
            type, priority, command)

    # add new message to the serial read queue
    def add_to_serial_read_queue(self, type, priority, message=None):
        self.machine_connector_data.serial_read_queue.put(
            type, priority, message)

    def homing_machine(self):
        self.reset_the_machine_system()

        # notify the core that the machine is homing
        self.add_to_serial_read_queue(constants.MACHINE_STATUS_DATA_TYPE,
                                      constants.MIDDLE_PRIORITY_COMMAND,
                                      constants.GRBL_COMMAND_DUMMY_STATUS_HOMING)

        # add stop command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.NORMAL_COMMAND_DATA_TYPE, constants.MIDDLE_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_HOMING)

    def unlock_machine(self):
        self.reset_the_machine_system()

        # add stop command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.NORMAL_COMMAND_DATA_TYPE, constants.MIDDLE_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_UNLOCK)

    def pause_machine(self):
        self.machine_connector_data.is_machine_pause = True
        # add pause command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.REAL_TIME_COMMAND_DATA_TYPE, constants.HIGH_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_PAUSE)

        # update the status directly to prevent the delay in the interface (1 second while pause)
        self.add_to_serial_write_queue(constants.REAL_TIME_COMMAND_DATA_TYPE, constants.MIDDLE_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_STATUS)

    def stop_machine(self):
        # reset the system
        self.reset_the_machine_system()

        # add stop command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.REAL_TIME_COMMAND_DATA_TYPE, constants.HIGH_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_STOP)

    def resume_machine(self):
        self.machine_connector_data.is_machine_pause = False
        # add resume command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.REAL_TIME_COMMAND_DATA_TYPE, constants.HIGH_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_RESUME)

    def return_to_zero(self):
        self.add_to_serial_write_queue(constants.NORMAL_COMMAND_DATA_TYPE,
                                       constants.MIDDLE_PRIORITY_COMMAND, constants.GRBL_COMMAND_RETURN_TO_ZERO)

    def reset_zero(self):
        self.reset_counter()
        # add reset zero command to the queue so that the serial will get notified
        self.add_to_serial_write_queue(constants.NORMAL_COMMAND_DATA_TYPE, constants.MIDDLE_PRIORITY_COMMAND,
                                       constants.GRBL_COMMAND_RESET_ZERO)

    def reset_the_machine_system(self):
        self.machine_connector_data.is_tool_change_process = False
        self.machine_connector_data.is_machine_pause = False
        self.reset_counter()
        self.flush_write_queue()
        self.flush_read_queue()

    def reset_counter(self):
        self.machine_connector_data.ok_messages_counter = -1

    # delete all the elements inside the write queue
    def flush_write_queue(self):
        # clear the write queue
        while not self.machine_connector_data.serial_write_queue.empty():
            self.machine_connector_data.serial_write_queue.get()

    # delete all the elements inside the read queue
    def flush_read_queue(self):
        # clear the write queue
        while not self.machine_connector_data.serial_read_queue.empty():
            self.machine_connector_data.serial_read_queue.get()

    # Handshake custom protocol to make sure that the
    # machine is ready to receive the next command
    def is_machine_ready(self):
        if (self.machine_connector_data.ok_messages_counter <= 0 and
            not self.machine_connector_data.is_tool_change_process and
                not self.machine_connector_data.is_machine_pause):
            return True

        return False

    # try to reconnect to serial incase of not detecting any device or
    # serial port is busy
    def reconnect_to_serial(self):
        while not self._serial_connection.is_serial_connected():
            print('Trying to connect to serial...')
            time.sleep(1)

            # retry to run the process again
            self.run()
