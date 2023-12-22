import mido
from Config import Config

def get_port_selection(ports, message: str) -> str:
    index = -1
    while index < 0 or index >= len(ports):
        for i in range(ports.__len__()):
            print("[" + str(i) + "] " + ports[i])
        try:        
            input_str = input(message)
            if input_str == "": return ""
            index = int(input_str)
        except ValueError as e:
            print("Invalid input. Please enter a number corresponding to an input port.")
    return ports[index]

def get_csv_path() -> str:
    path = input("Please enter the path to the CSV file (input nothing to skip): ")
    return path
    

def setup_config(config: Config):
    num_ports = 0
    while num_ports <= 0:
        try:        
            num_ports = int(input("Number of MIDI connections to intercept: "))
        except ValueError as e:
            print("Invalid input. Please enter a number.")
        
    device_input_port_names = []
    rtp_output_port_names = []
    rtp_input_port_names = []
    device_output_port_names = []
    csv_paths = []

    for i in range(num_ports):

        device_input_port_name = get_port_selection(mido.get_input_names(), "Please select the input port to intercept for connection " + str(i + 1) + " (input nothing to skip):\n")
        rtp_output_port_name = get_port_selection(mido.get_output_names(), "Please select the port that \"" + device_input_port_name + "\" will be routed to (input nothing to skip):\n")
        rtp_input_port_name = get_port_selection(mido.get_input_names(), "Please select the second input port for connection " + str(i + 1) + " (input nothing to skip):\n")
        device_output_port_name = get_port_selection(mido.get_output_names(), "Please select the port that \"" + rtp_input_port_name + "\" will be routed to (input nothing to skip):\n")
        
        csv_path = get_csv_path()

        device_input_port_names.append(device_input_port_name)
        rtp_output_port_names.append(rtp_output_port_name)
        rtp_input_port_names.append(rtp_input_port_name)
        device_output_port_names.append(device_output_port_name)
        
        csv_paths.append(csv_path)


    config.set_device_count(num_ports)
    for index in range(num_ports):

        device_input_port_name = device_input_port_names[index]
        rtp_output_port_name = rtp_output_port_names[index]
        rtp_input_port_name = rtp_input_port_names[index]
        device_output_port_name = device_output_port_names[index]
        csv_path = csv_paths[index]

        if (device_input_port_name != ""): config.set_device_in(index, device_input_port_names[index])
        if (rtp_output_port_name != ""): config.set_rtp_out(index, rtp_output_port_names[index])
        if (rtp_input_port_name != ""): config.set_rtp_in(index, rtp_input_port_names[index])
        if (device_output_port_name != ""): config.set_device_out(index, device_output_port_names[index])
        if (csv_path != ""): config.set_csv_path(index, csv_paths[index])

    config.write()

    
