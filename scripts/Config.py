import configparser


class Config:

    def __init__(self, config_path: str):
        self.configParser = configparser.ConfigParser()
        self.configParser.read(config_path)

    def get_device_count(self) -> int:
        return int(self.configParser.get('MIDI', 'DEVICE_COUNT'))

    def get_rtp_in(self, device_num) -> str:
        return self.configParser.get('MIDI', 'RTPMIDI_INPUT_PORT_' + str(device_num))

    def get_rtp_out(self, device_num) -> str:
        return self.configParser.get('MIDI', 'RTPMIDI_OUTPUT_PORT_' + str(device_num))

    def get_device_in(self, device_num) -> str:
        return self.configParser.get('MIDI', 'MIDI_DEVICE_INPUT_PORT_' + str(device_num))

    def get_device_out(self, device_num) -> str:
        return self.configParser.get('MIDI', 'MIDI_DEVICE_OUTPUT_PORT_' + str(device_num))

    def get_csv_path(self, device_num) -> str:
        return self.configParser.get('CSV', 'PATH_TO_CSV_FILE_' + str(device_num))

    def get_log_path(self) -> str:
        return self.configParser.get('LOGS', 'LOG_PATH')

    def get_log_prefix(self) -> str:
        return self.configParser.get('LOGS', 'LOG_FILE_PREFIX')
    
    def set_device_count(self, count: int):
        self.configParser.set('MIDI', 'DEVICE_COUNT', str(count))

    def set_rtp_in(self, device_num, port_name: str):
        self.configParser.set('MIDI', 'RTPMIDI_INPUT_PORT_' + str(device_num), port_name)

    def set_rtp_out(self, device_num, port_name: str):
        self.configParser.set('MIDI', 'RTPMIDI_OUTPUT_PORT_' + str(device_num), port_name)

    def set_device_in(self, device_num, port_name: str):
        self.configParser.set('MIDI', 'MIDI_DEVICE_INPUT_PORT_' + str(device_num), port_name)

    def set_device_out(self, device_num, port_name: str):
        self.configParser.set('MIDI', 'MIDI_DEVICE_OUTPUT_PORT_' + str(device_num), port_name)

    def set_csv_path(self, device_num, path: str):
        self.configParser.set('CSV', 'PATH_TO_CSV_FILE_' + str(device_num), path)

    def write(self):
        with open('config.ini', 'w') as configfile:
            self.configParser.write(configfile)