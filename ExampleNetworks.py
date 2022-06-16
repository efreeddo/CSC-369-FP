# Networking logic modified from https://www.codespeedy.com/connect-to-a-wifi-network-in-python/
# Configured to only work on Windows machines
import os
import getpass

def createNewConnection(name, SSID, key):
    # Write network config file
    config = """<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>"""+name+"""</name>
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
    with open(name+".xml", 'w') as file:
        file.write(config)
    # Connect to network
    command = "netsh wlan add profile filename=\""+name+".xml\""+" interface=Wi-Fi"
    os.system(command)
    # Clean up
    os.remove(name+".xml")

def connect(name, SSID):
    command = "netsh wlan connect name=\""+name+"\" ssid=\""+SSID+"\" interface=Wi-Fi"
    os.system(command)

def displayAvailableNetworks():
    command = "netsh wlan show networks interface=Wi-Fi"
    os.system(command)

if __name__ == "__main__":
    try:
        displayAvailableNetworks()
        # Always make a new connection
        #option = input("New connection (y/N)? ")
        #if option == "N" or option == "":
        #    name = input("Name: ")
        #    connect(name, name)
        #    print("If you aren't connected to this network, try connecting with correct credentials")
        #elif option == "y":
        name = input("Name: ")
        # Add default WiFi SSID
        if name == "": name = "SpectrumSetup-68"
        key = getpass.getpass("Password: ")
        createNewConnection(name, name, key)
        connect(name, name)
        os.system("netsh interface show interface | findstr Wi-Fi")
        print("If you aren't connected to this network, try connecting with correct credentials")
    except KeyboardInterrupt as e:
        # Clean up if early abort
        print("\nExiting...")
