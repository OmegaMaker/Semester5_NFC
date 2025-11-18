from py122u import nfc
import requests
import time

API_URL = "http://34.51.214.84:8000/receive_uid"  # Receiver endpoint

def main():
    reader = nfc.Reader()
    print("[SCAN] Connecting to NFC reader...")
    reader.connect()

    while True:
        uid = reader.get_uid()
        if uid:
            print(f"[SCAN] UID scanned: {uid}")

            payload = {"uid": uid}

            try:
                r = requests.post(API_URL, json=payload, timeout=2)
                print(f"[SCAN] Sent UID → Status {r.status_code}")
            except Exception as e:
                print(f"[SCAN] Failed to send UID: {e}")

        time.sleep(5)  # Prevent busy-looping

if __name__ == "__main__":
    
    main()
