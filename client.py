import requests
import platform
import uuid
import socket
import sys
import time
from datetime import datetime

class LicenseClient:
    def __init__(self, license_key, api_url):
        self.license_key = license_key
        self.api_url = api_url
        self.machine_id = self._get_machine_id()
        self.verified = False
        self.expiry_date = None
    
    def _get_machine_id(self):
        """สร้าง ID เครื่องที่ไม่ซ้ำกัน"""
        machine_id = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_id))
    
    def _get_ip_address(self):
        """รับ IP address ของเครื่อง"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def verify_license(self):
        """ตรวจสอบ license กับเซิร์ฟเวอร์"""
        try:
            response = requests.post(
                f"{self.api_url}/licenses/verify",
                json={
                    "license_key": self.license_key,
                    "machine_id": self.machine_id,
                    "ip_address": self._get_ip_address()
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.verified = data.get("valid", False)
                self.expiry_date = datetime.fromisoformat(data.get("expires_at").replace("Z", "+00:00"))
                return True
            else:
                print(f"License verification failed: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Error verifying license: {str(e)}")
            return False
    
    def is_valid(self):
        """ตรวจสอบว่า license ยังใช้งานได้หรือไม่"""
        if not self.verified:
            return self.verify_license()
        
        # ตรวจสอบวันหมดอายุ
        if self.expiry_date and datetime.now().astimezone() > self.expiry_date:
            self.verified = False
            return False
        
        return self.verified

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    LICENSE_KEY = "YOUR_LICENSE_KEY"
    API_URL = "https://your-license-api.render.com"
    
    license_client = LicenseClient(LICENSE_KEY, API_URL)
    
    if not license_client.is_valid():
        print("Invalid license. Exiting...")
        sys.exit(1)
    
    print("License verified successfully!")
    print(f"License expires on: {license_client.expiry_date}")
    
    # ตัวอย่างการตรวจสอบ license เป็นระยะ
    try:
        while True:
            # โค้ดโปรแกรมของคุณ...
            print("Program is running...")
            
            # ตรวจสอบ license ทุก 1 ชั่วโมง
            if not license_client.is_valid():
                print("License has expired or is no longer valid. Exiting...")
                sys.exit(1)
            
            time.sleep(10)  # ในตัวอย่างนี้ตรวจสอบทุก 10 วินาที
    except KeyboardInterrupt:
        print("Program terminated by user")