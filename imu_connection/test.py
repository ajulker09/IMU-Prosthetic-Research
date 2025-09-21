import asyncio
import bleak
import device_model
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

last_time = time.time()
count = 0
devices = []
BLEDevice = []
selected_devices = []

#3 3 axis gorups. 9 channels.
groups = {
    "Accelerometer": ["AccX", "AccY", "AccZ"],
    "Gyroscope": ["AsX", "AsY", "AsZ"],
    "Magnetometer": ["HX", "HY", "HZ"]
}

MAX_POINTS = 40
buffers = {}    
figs = {}       
axes_dict = {}  

def init_plot(device_name):
    buffers[device_name] = {}
    for vars in groups.values():
        for var in vars:
            buffers[device_name][var] = deque(maxlen=MAX_POINTS)

    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 8), sharex=True)
    fig.suptitle(f"{device_name} (9-DOF Data)")
    figs[device_name] = fig
    axes_dict[device_name] = axes

#This function scans and determines how many IMUS will be connected and used. Works for varying number of IMUS. 
async def scan():
    global devices
    global BLEDevice
    find = []
    print("Searching for Bluetooth devices......")
    devices = await bleak.BleakScanner.discover(timeout=20.0)
    print("Search ended")
    for d in devices:
        if d.name is not None and "WT" in d.name:
            find.append(d)
            print(d)
    if len(find) == 0:
        print("No devices found in this search!")
    else:
        #we will allow the user to select how many IMUs they want to connect 
        print("Number of IMUS in Network: "+str(len(find)))
        num_imus=int(input("Please enter how many IMU you want to connect to: "))
        if num_imus>len(find):
            print("Invalid number of IMUs. ")
            return

        for i in range(num_imus):
            BLEDevice.append(find[i])      
        
async def startIMUs(BlEDdevice):
    #iterates over the BLEDevice list and starts them all by creating seperate device_model objects 
    imu_devices=[]
    for i, dev in enumerate(BLEDevice, start=1):
        device = device_model.DeviceModel(f"IMU{i}", dev, updateData)
        imu_devices.append(device)
        asyncio.create_task(device.openDevice())

    while True:
        await asyncio.sleep(1)


def updateData(DeviceModel):
    name = DeviceModel.deviceName
    data = DeviceModel.deviceData

    if name not in buffers:
        init_plot(name)

    for key in data:
        if key in buffers[name]:
            buffers[name][key].append(data[key])


def animate(frame):
    for name, buf in buffers.items():
        axes = axes_dict[name]
        for ax, (group, vars) in zip(axes, groups.items()):
            ax.clear()
            for var in vars:
                ax.plot(list(buf[var]), label=var)
            ax.set_title(group)
            ax.legend(loc="upper right")
        axes[-1].set_xlabel("Samples (last 40)")

async def main():
    await scan()
    if BLEDevice:
        # startIMUs runs forever, so start it as a background task
        asyncio.create_task(startIMUs(BLEDevice))
    else:
        print("No IMUs Selected!")
        return

    # now that figures will exist once data arrives, attach animation
    ani = animation.FuncAnimation(plt.gcf(), animate, interval=100)

    # non-blocking plot loop
    plt.show(block=False)
    while True:
        await asyncio.sleep(0.1)
        plt.pause(0.001)

if __name__ == "__main__":
    asyncio.run(main())
