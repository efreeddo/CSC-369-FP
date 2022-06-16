# Networking logic modified from https://www.codespeedy.com/connect-to-a-wifi-network-in-python/
# Configured to only work on Windows machines
import os
import subprocess
import ray
import random
import sys
from time import time, sleep

# From findAvrTime(30)
TEST_DELAY = 0.7505173
TARGET_PASSWORD = ""

def createProfile(SSID, key):
    # Write network config file
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+SSID+"""</name>
    <SSIDConfig>
        <SSID>
            <name>"""+SSID+"""</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>"""+key+"""</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    with open(SSID+key+".xml", 'w') as file:
        file.write(config)

def connect(SSID, key):
    # Add network profile
    command = "netsh wlan add profile filename=\""+SSID+key+".xml\""+" interface=Wi-Fi"
    os.system(command)
    # Connect with network profile
    command = "netsh wlan connect name=\""+SSID+"\" ssid=\""+SSID+"\" interface=Wi-Fi"
    os.system(command)

def clearProfile(SSID, key):
    # Remove profile from directory
    os.remove(SSID+key+".xml")

def testConnection():
    command = "netsh interface show interface | findstr Wi-Fi"
    result = subprocess.run(command.split(), capture_output=True, shell=True).stdout
    return str(result).find("Connected") != -1

'''
@ray.remote
def passwordRange(filename, SSID, start, end):
    # Open password list
    file = open(filename, "r")
    # Move to starting position
    if start != 0:
        file.seek(start)
        file.readline()
    # Save previous key
    lastkey = ""
    # Check all passwords in range
    while file.tell() < end or testConnection():
        # Get password & try to connect
        key = file.readline().rstrip()
        createProfile(SSID, key)
        connect(SSID, key)
        # Check connection
        if testConnection():
            return (key, lastkey)
        # Cleanup profile
        clearProfile(SSID, key)
        # Double-Check connection
        if testConnection():
            return (key, lastkey)
        lastkey = key
    
    # Either at end of range, or found key
    if file.tell() < end:
        return (lastkey)
    else:
        return ()
'''

# Pull a random password from a password list
def getRandomPassword(password_list):
    with open(password_list, "r") as f:
        # Seek random valid position
        length = f.seek(0,2)
        index = random.randrange(0, length-30)
        f.seek(index)
        # Burn the rest of the current line
        f.readline()
        # Strip and return password
        return f.readline().rstrip()

@ray.remote
class PasswordCrackerManager:
    def __init__(self):
        self.CONNECTED = False

    def setConnection(self, status):
        self.CONNECTED = status

    # Simulate testing a WiFi password. Sets CONNECTED to true if correct
    def testPassword(self, password):
        # Wait average time to test a connection
        sleep(TEST_DELAY)
        # Check password
        if password == TARGET_PASSWORD:
            self.CONNECTED = True
        return self.CONNECTED

    def passwordRangeSim(self, filename, start, end):
        # Open password list
        file = open(filename, "r")
        # Move to starting position
        if start != 0:
            file.seek(start)
            file.readline()
        # Check all passwords in range
        while file.tell() < end or self.CONNECTED == False:
            # Get password & try to connect
            key = file.readline().rstrip()
            # Test the key
            if self.testPassword(key):
                return key
        
        # Either at end of range
        if file.tell() < end:
            return ""

# Find the average time it takes to test one WiFi password
def findAvrTime(rounds):
    start_time = time()
    SSID = "SpectrumSetup-68"
    key = "123456789ABCDEF"
    for i in range(rounds):
        createProfile(SSID, key)
        connect(SSID, key)
        testConnection()
        clearProfile(SSID, key)
        testConnection()
    avr_time = (time() - start_time) / rounds
    print("Average time per connection test: "+str(avr_time)+"s")
    return avr_time

if __name__ == "__main__":
    futures = []
    try:
        # Arg formatting
        if len(sys.argv) != 3:
            print("Format: python PasswordCrackerSim.py password_list thread_count")
            exit()
        
        # Get args
        _, password_list, thread_count = sys.argv
        thread_count = int(thread_count)

        # Find password_list length
        list_len = 0
        try:
            with open(password_list) as f:
                list_len = f.seek(0,2)
        except:
            print("Error opening "+password_list)
            exit()

        # Select a random target password
        TARGET_PASSWORD = getRandomPassword(password_list)
        print("The target password is",TARGET_PASSWORD)

        # Start rays
        ray.init()
        manager = PasswordCrackerManager.remote()
        print("Threads started...")
        for i in range(thread_count):
            start = list_len // thread_count * i
            end = list_len // thread_count * (i+1)
            futures += [manager.passwordRangeSim.remote(password_list, start, end)]
        
        # Get results from rays
        results = ray.get(futures)
        passwords = []
        for password in results:
            if password != "":
                passwords += [password]
        
        print("Finding correct password from",passwords)

        # Disconnect from WiFi
        ray.get(manager.setConnection.remote(False))

        for password in passwords:
            if ray.get(manager.testPassword.remote(password)):
                print("The correct password is", password)
                exit()

    except KeyboardInterrupt as e:
        # Clean up if early abort
        print("\nExiting...")
        exit()