import datetime
from mido import Message as MidiMessage
from Config import Config
from midiParser import Direction

config = Config('config.ini')

log_path = config.get_log_path()
log_filename = config.get_log_prefix()

log_file = f"{log_path}/{log_filename}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"


def log_midi_message(message: MidiMessage, device_name: str, print_to_console: bool) -> None:
    log_entry("INFO", f"{device_name} {message.hex()} {message}",
              print_to_console)


def log_error(exception: Exception, message: str) -> None:
    log_entry("ERROR", message + " " + str(exception), True)


def log_info(message: str, print_to_console: bool) -> None:
    log_entry("INFO", message, print_to_console)


def log_entry(level: str, message: str, print_to_console: bool = False) -> None:
    """Logs a message to the log file or console.
    :param level: The log level (INFO or ERROR)
    :param message: The message to log
    :param print_to_console: Whether to print the message to the console
    """

    current_time = datetime.datetime.now()
    system_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    log_entry = f"[{system_time}] {level}: {message}"

    with open(log_file, 'a') as file:
        file.write(log_entry + "\n")

    if print_to_console:
        print(log_entry)
