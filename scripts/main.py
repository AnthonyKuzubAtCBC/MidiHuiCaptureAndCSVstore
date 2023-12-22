import midiParser
import csvWriter
import csvReader
import setup

import mido
import time
import logger
import sys

from Cell import Cell
from Config import Config
from threading import Thread, Event
from midiParser import Direction

UPDATE_PERIOD = 0.5  # Seconds
POLL_PERIOD = 0.01  # Seconds
stop_flag = Event()

LCD_POSITION_INDEX = 5
LCDS_PER_ROW = 8
SEGMENTS_PER_LCD = 7   # number of segments in each lcd section


def lcd_seg_to_cell(table: list[list[int]], pos: int) -> Cell:
    """Returns the cell corresponding to the lcd segment
    :param table: The table containing the lcd text data
    :param pos: The position of the lcd segment
    :return: The cell corresponding to the lcd segment
    """

    # the lcd section (1-8 is first row, 9-16 is second row)
    lcd_section = pos // SEGMENTS_PER_LCD

    lcd_row_index = midiParser.get_row_num(
        'lcd_line_' + str(lcd_section // LCDS_PER_ROW), table)
    lcd_column_index = lcd_section % LCDS_PER_ROW

    if lcd_row_index is None:
        print("lcd_line_" + str(lcd_section // LCDS_PER_ROW) + " not found")
        return None

    return Cell(lcd_row_index, lcd_column_index)


def init_device_from_table(table: list[list[int]], output_port_name: str) -> None:
    """Sets all the faders to the values in the table
    :param table: The table to read from
    :param output_port_name: The name of the output port to write to
    """

    try:
        output_port = mido.open_output(output_port_name)
    except Exception as e:
        logger.log_error(e, f"Error in midi input thread:")
        stop_flag.set()
        return

    # i know theres alot of magic numbers here but i think eventually i might redo this function
    # so i wont worry about it for now

    # faders
    fader_row = table[midiParser.get_row_num('pitchwheel_0', table)]
    for column in range(midiParser.ROW_SIZE):
        value = int(fader_row[column])
        message = mido.Message('pitchwheel')
        message.channel = column
        message.pitch = value
        output_port.send(message)

    # buttons leds
    for led in range(4):
        led_row = table[midiParser.get_row_num(
            'note_led_on_' + str(led), table)]
        for column in range(midiParser.ROW_SIZE):
            value = int(led_row[column])
            message = mido.Message('note_on')
            message.note = column + led * midiParser.ROW_SIZE
            message.velocity = value
            output_port.send(message)

    # knob leds
    knob_led_row = table[midiParser.get_row_num('control_change_6', table)]
    for column in range(midiParser.ROW_SIZE):
        value = int(knob_led_row[column])
        message = mido.Message('control_change')
        message.control = column + 6 * midiParser.ROW_SIZE
        message.value = value
        output_port.send(message)

    output_port.close()


def update_table_lcd(table: list[list[int]], message) -> None:
    """Updates the lcd portion of the table based on the midi message
    :param table: The table to update
    :param message: The midi message to parse
    :param direction: The direction of the midi message (incoming from or outgoing to rtp)
    """

    length = (len(message.data) - 1) - LCD_POSITION_INDEX
    # This is the "id" of the starting lcd segment
    starting_pos = message.data[LCD_POSITION_INDEX]

    pos = starting_pos

    # Parses through the message.data and upates each affected character in the table induvidually
    # for each ascii character in the message
    for char_index in range(LCD_POSITION_INDEX + 1, LCD_POSITION_INDEX + length + 1):

        cell = lcd_seg_to_cell(table, pos)

        new_char = chr(message.data[char_index])

        seg = pos % SEGMENTS_PER_LCD

        # replace the character at the position seg in the string
        str_val = table[cell.row][cell.column]
        str_val = str_val[:seg] + new_char + str_val[seg + 1:]
        table[cell.row][cell.column] = str_val

        pos += 1


def update_table(table: list[list[int]], message, direction: Direction) -> None:
    """Updates the table based on the midi message
    :param table: The table to update
    :param message: The midi message to parse
    :param direction: The direction of the midi message (incoming from or outgoing to rtp)
    """

    if message.type == 'sysex':
        update_table_lcd(table, message)
        return

    cell = midiParser.parse_message(message, direction, table)
    if cell is None:
        return

    table[cell.row][cell.column] = midiParser.get_message_value(message)

    # csvWriter.write_table('hui_data.csv', table)


def update_csv(csv_path: str, table: list[list[int]], period: int) -> None:
    """Updates the csv file periodically
    :param csv_path: The path to the csv file
    :param table: The table to write to the csv file
    """

    while not stop_flag.is_set():
        csvWriter.write_table(csv_path, table)
        time.sleep(period)


def poll_ports(device_input_ports, device_output_ports, rtp_input_ports, rtp_output_ports, tables, direction: Direction) -> None: 
    for device_input_port, device_output_port, rtp_input_port, rtp_output_port, table in zip(device_input_ports, device_output_ports, rtp_input_ports, rtp_output_ports, tables):

        for message in device_input_port.iter_pending():
            if message.type != 'aftertouch': # dont log aftertouch messages beacuse they are very spammy. Aftertouch controls the vu meter
                logger.log_midi_message(message, device_input_port.name, True)
            update_table(table, message, Direction.OUTGOING)
            rtp_output_port.send(message)

        for message in rtp_input_port.iter_pending():
            if message.type != 'aftertouch': # dont log aftertouch messages beacuse they are very spammy. Aftertouch controls the vu meter
                logger.log_midi_message(message, rtp_input_port.name, True)
            update_table(table, message, Direction.INCOMING)
            device_output_port.send(message)


def poll_devices_from_config(config: Config):
    """Polls the devices specified in the config file
    :param config: The config file to read from
    """

    device_input_ports = []
    device_output_ports = []
    rtp_input_ports = []
    rtp_output_ports = []
    tables = []

    csv_paths = []

    try:
        for device_num in range(config.get_device_count()):
            device_input_ports.append(mido.open_input(config.get_device_in(device_num)))
            device_output_ports.append(mido.open_output(config.get_device_out(device_num)))
            rtp_input_ports.append(mido.open_input(config.get_rtp_in(device_num)))
            rtp_output_ports.append(mido.open_output(config.get_rtp_out(device_num)))
            csv_paths.append(config.get_csv_path(device_num))
            tables.append(csvReader.read_table(csv_paths[device_num]))

    except Exception as e:
        logger.log_error(e, f"Error while trying to open midi ports:")
        logger.log_info("Make sure the device is plugged in and that no other programs are using it", True)
        stop_flag.set()

    while (stop_flag.is_set() is False):
        poll_ports(device_input_ports, device_output_ports, rtp_input_ports, rtp_output_ports, tables, Direction.OUTGOING)
        for table, csv_path in zip(tables, csv_paths):
            csvWriter.write_table(csv_path, table)
        
        time.sleep(POLL_PERIOD)


if __name__ == "__main__":

    threads = []
    config = Config('config.ini')

    # Setup the config file
    if sys.argv.__contains__('--setup'):
        setup.setup_config(config)
        exit()

    if config.get_device_count() == 0:
        setup.setup_config(config)

    # Create the threads for each physical midi device
    poll_devices_from_config(config)

    # Wait for a keyboard interrupt
    try:
        while stop_flag.is_set() is False:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.log_info("Keyboard interrupt received", True)
        stop_flag.set()  # Set the stop flag to stop the threads

