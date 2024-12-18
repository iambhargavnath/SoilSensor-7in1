import serial #Pyserial
import time
import pandas as pd

counter = 0

# Function to convert hexadecimal to decimal
def hexa_to_decimal(value, significance_of_byte, nibbles_to_format):
    byte_order = nibbles_to_format - 1
    msn = (value >> 4) * (16 ** byte_order)  # Most Significant Nibble
    lsn = (value & 0x0F) * (16 ** (byte_order - 1))  # Least Significant Nibble

    if significance_of_byte and value == 0xFF:
        return -256  # Negative if all bits are high
    return msn + lsn

class SoilSensor:
    def __init__(self, serial_port):
        self.serial_port = serial_port

    def read_register(self, frame, size):
        self.serial_port.reset_input_buffer()  # Clear buffer before reading
        self.serial_port.write(frame)
        time.sleep(0.2)  # Give the sensor time to respond
        buffer = self.serial_port.read(size)
        if len(buffer) == size:
            return buffer
        return None

    def read_temperature(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x12, 0x00, 0x02, 0x64, 0x0E])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            value = hexa_to_decimal(buffer[5], True, 4) + hexa_to_decimal(buffer[6], False, 2)
            temperature = value / 10
            return temperature
        return None

    def read_conductivity(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xce])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            conductivity = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            return conductivity
        return None

    def read_moisture(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x12, 0x00, 0x02, 0x64, 0x0e])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            value = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            moisture = value/10
            return moisture
        return None

    def read_nitrogen(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x1e, 0x00, 0x01, 0xe4, 0x0c])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            nitrogen = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            return nitrogen
        return None

    def read_ph(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0b])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            value = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            ph = value / 100  # Scale the value accordingly
            return ph
        return None

    def read_phosphorus(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            phosphorus = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            return phosphorus
        return None

    def read_potassium(self):
        inquiry_frame = bytes([0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0])
        buffer = self.read_register(inquiry_frame, 7)
        if buffer:
            potassium = hexa_to_decimal(buffer[3], True, 4) + hexa_to_decimal(buffer[4], False, 2)
            return potassium
        return None
    
if __name__ == "__main__":
    try:
        # Replace "COM8" with your serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
        with serial.Serial(port="COM6", baudrate=9600, timeout=1) as serial_port:
            soil_sensor = SoilSensor(serial_port)
            data = []  # List to hold the data

            while True:
                counter += 1
                print(f"--- Data Sample {counter} ---")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
                temperature = soil_sensor.read_temperature()
                time.sleep(0.1)
                conductivity = soil_sensor.read_conductivity()
                time.sleep(0.1)
                moisture = soil_sensor.read_moisture()
                time.sleep(0.1)
                nitrogen = soil_sensor.read_nitrogen()
                time.sleep(0.1)
                ph = soil_sensor.read_ph()
                time.sleep(0.1)
                phosphorus = soil_sensor.read_phosphorus()
                time.sleep(0.1)
                potassium = soil_sensor.read_potassium()

                # Print values to console
                if temperature is not None:
                    print(f"Soil Temperature: {temperature:.2f}°C")
                if conductivity is not None:
                    print(f"Soil Conductivity: {conductivity}us/cm")
                if moisture is not None:
                    print(f"Soil Humidity: {moisture}%")
                if nitrogen is not None:
                    print(f"Soil Nitrogen: {nitrogen}mg/kg")
                if ph is not None:
                    print(f"Soil pH: {ph:.2f}")
                if phosphorus is not None:
                    print(f"Soil Phosphorus: {phosphorus}mg/kg")
                if potassium is not None:
                    print(f"Soil Potassium: {potassium}mg/kg")

                print("")

                # Store data in a list
                data.append({
                    "Timestamp": timestamp,
                    "Temperature (°C)": temperature,
                    "Conductivity (us/cm)": conductivity,
                    "Moisture (%)": moisture,
                    "Nitrogen (mg/kg)": nitrogen,
                    "pH": ph,
                    "Phosphorus (mg/kg)": phosphorus,
                    "Potassium (mg/kg)": potassium
                })

                # Create a DataFrame and save to CSV
                df = pd.DataFrame(data)
                df.to_csv('soil_sensor_data.csv', index=False)

                time.sleep(1)  # Refresh

    except Exception as e:
        print(f"Error: {e}")
