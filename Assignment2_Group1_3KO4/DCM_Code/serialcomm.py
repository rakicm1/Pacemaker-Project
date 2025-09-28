import json
import struct
import serial
import time

# Constants
SERIAL_PORT = 'COM3'  # Replace 'COMx' with your actual COM port
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout for serial communication in seconds
SYNC = 0x16
FN_CODE_SET_PARAMS = 0x55

PORTS_ARRAY = {"COM3", "COM6"}

def read_user_parameters(filename, username):
    """
    Reads parameters for a specific user from a JSON file.
    :param filename: The path to the JSON file.
    :param username: The username to look up.
    :return: A dictionary of user parameters or None if the user is not found.
    """
    try:
        with open(filename, "r") as file:
            users = json.load(file)
        user_data = users.get(username)
        if not user_data:
            print(f"User '{username}' not found in the file.")
            return None
        return user_data.get("parameters")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


def create_packet(sync, fn_code, params):
    """
    Creates a packet based on user parameters.
    :param sync: SYNC byte.
    :param fn_code: Function code byte.
    :param params: User parameters dictionary.
    :return: A bytearray packet.
    """
    packet = bytearray()

    # Append fields
    packet.append(sync)                  # 1 byte for SYNC
    packet.append(fn_code)               # 1 byte for FN_CODE
    packet.append(ord(params["mode"][0]))  # 1 byte for mode (assuming 'mode' is a single character)
    packet.append(params["Lower Rate Limit (ppm)"])   # 1 byte
    packet.append(params["Upper Rate Limit (ppm)"])   # 1 byte
    packet.extend(struct.pack('<f', params["Ventricular Amplitude (V)"]))  # 4 bytes float
    packet.extend(struct.pack('<f', params["Ventricular Pulse Width (ms)"]))  # 4 bytes float
    packet.extend(struct.pack('<f', params["Ventricular Sensitivity (mV)"]))  # 4 bytes float
    packet.extend(struct.pack('<f', params["Maximum Sensor Rate (ppm)"]))  # 4 bytes float
    packet.extend(struct.pack('<H', params["VRP (ms)"]))  # 2 bytes uint16
    packet.extend(struct.pack('<H', params["Reaction Time (s)"]))  # 2 bytes uint16
    packet.append(params.get("Response Factor", 1))  # 1 byte
    packet.append(params.get("Rate Smoothing (%)", 6))  # 1 byte

    return packet


def receive_packet(ser):
    """
    Receives and parses a packet from the serial port.
    :param ser: Serial object.
    """
    try:
        # Define packet length
        packet_length = 45  # Adjusted for expected packet structure
        received_data = ser.read(packet_length)

        if len(received_data) != packet_length:
            raise ValueError(f"Incomplete packet received! Expected {packet_length} bytes, got {len(received_data)}.")

        # Parse fields
        mode = received_data[0]  # 1 byte
        lower_rate = received_data[1]  # 1 byte
        upper_rate = received_data[2]  # 1 byte
        atr_amp = struct.unpack('<f', received_data[3:7])[0]  # 4 bytes float
        vent_amp = struct.unpack('<f', received_data[7:11])[0]  # 4 bytes float
        atr_width = struct.unpack('<f', received_data[11:15])[0]  # 4 bytes float
        vent_width = struct.unpack('<f', received_data[15:19])[0]  # 4 bytes float
        vrp = struct.unpack('<H', received_data[19:21])[0]  # 2 bytes uint16
        arp = struct.unpack('<H', received_data[21:23])[0]  # 2 bytes uint16
        hysteresis = received_data[23]  # 1 byte
        rate_smoothing = received_data[24]  # 1 byte
        activity_threshold = received_data[25]  # 1 byte
        reaction_time = received_data[26]  # 1 byte
        response_factor = received_data[27]  # 1 byte
        recovery_time = received_data[28]  # 1 byte

        # Electrograms
        vent_electrogram = struct.unpack('<H', received_data[29:31])[0]  # 2 bytes uint16
        atr_electrogram = struct.unpack('<H', received_data[31:33])[0]  # 2 bytes uint16

        # Display received data
        print("Received Data:")
        print(f"Mode: {mode}")
        print(f"Lower Rate Limit: {lower_rate}")
        print(f"Upper Rate Limit: {upper_rate}")
        print(f"Atrium Pulse Amplitude: {atr_amp}")
        print(f"Ventricle Pulse Amplitude: {vent_amp}")
        print(f"Atrium Pulse Width: {atr_width}")
        print(f"Ventricle Pulse Width: {vent_width}")
        print(f"VRP: {vrp}")
        print(f"ARP: {arp}")
        print(f"Hysteresis: {hysteresis}")
        print(f"Rate Smoothing: {rate_smoothing}")
        print(f"Activity Threshold: {activity_threshold}")
        print(f"Reaction Time: {reaction_time}")
        print(f"Response Factor: {response_factor}")
        print(f"Recovery Time: {recovery_time}")
        print(f"Ventricle Electrogram: {vent_electrogram}")
        print(f"Atrium Electrogram: {atr_electrogram}")

    except Exception as e:
        print("Error receiving or parsing packet:", str(e))


# Main Execution
if __name__ == "__main__":
    json_file = "users.json"  # Replace with actual JSON file
    username = "james"  # Replace with the username to process

    # Load user parameters
    user_params = read_user_parameters(json_file, username)
    if user_params:
        try:
            # Initialize serial communication
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
            ser.reset_output_buffer()
            ser.reset_input_buffer()

            # Create and send packet
            packet = create_packet(SYNC, FN_CODE_SET_PARAMS, user_params)
            ser.write(packet)
            print("Packet sent successfully.")

            # Receive and parse packet
            time.sleep(1)  # Allow time for response
            receive_packet(ser)

        except Exception as e:
            print(f"Error during UART communication: {e}")
        finally:
            ser.close()
            print("Serial communication closed.")
