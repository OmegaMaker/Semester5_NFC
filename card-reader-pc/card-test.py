from py122u import nfc
import time

reader = nfc.Reader()

try:
    print("Please tap your NFC card...")
    reader.connect()
    reader.set_auto_polling(True)
    uid = reader.get_uid()
    reader.print_data(uid)
    reader.info()
except Exception as e:
    print(f"Error: {e}")

print("Exiting...")