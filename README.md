# CSC-369-FP
Easy, Medium, and Hard lists contains a unique password on each line. Easy contains less than 100 entries, Medium contains 1000, and Hard 
contains 1000000. The full list of all possible passwords is available online and is over 20GB: https://oxagast.org/wordlists/adjective_noun_3_digits_router.lst.gz

The ExampleNetworks program lists all available networks, then attemps to connect to one with the SSID and password provided by the user.

The RayTest program creates 20 threads which run the echo command on the command line to test if ray and subprocess.run work together.

PasswordCracker takes a path to a password list file, the SSID of the network to connect to, and the number of threads to run the program with. 
Each thread attempts to connect to the provided network with a password from the list, all threads terminating when a connection is made. All
passwords that could have caused the connection are tested individually, returning the correct password. There are some issues with threading
such that the correct password may not be tested if several threads test a password at the same time.

PasswordCrackerSim takes a path to a password list file and the number of threads to run the program with. It picks a random password from the
password list to try and find, then creates a number of threads to search the password list for a match. Each time a thread checks a password,
it waits for the average amount of time it takes PasswordChecker to test a WiFi password to simulate the work needed to crack a WiFi password
without needing to connect to a real network.
