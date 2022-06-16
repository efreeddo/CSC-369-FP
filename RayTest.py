# Networking logic modified from https://www.codespeedy.com/connect-to-a-wifi-network-in-python/
# Configured to only work on Windows machines
import os
import subprocess
import ray

@ray.remote
def echo(val):
    command = "echo"
    res = subprocess.run([command, str(val)], capture_output=True, shell=True).stdout
    print(str(res)+" : "+str(val))
    #os.system(command)

if __name__ == "__main__":
    print("Init start")
    ray.init()
    print("Init done")
    futures = []
    for i in range(20):
        futures += [echo.remote(i)]
    ray.get(futures)

