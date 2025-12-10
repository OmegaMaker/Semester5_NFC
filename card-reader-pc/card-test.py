from py122u import nfc
import time

reader = nfc.Reader()

while True:
    try:
        print("Please tap your NFC card...")
        reader.connect()
        uid = reader.get_uid()
        reader.print_data(uid)
        time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
        pass

    time.sleep(1)



print("Exiting...")