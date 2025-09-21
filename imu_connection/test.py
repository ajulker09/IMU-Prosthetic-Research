import asyncio
import bleak
import device_model

devices = []
BLEDevice =[]
selected_devices=[]

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
    print(f"[{DeviceModel.deviceName}] {DeviceModel.deviceData}")


async def main():
    await scan()
    if BLEDevice:
        await startIMUs(BLEDevice)
    else:
        print("No IMUs Selected!")

if __name__ == "__main__":
    asyncio.run(main())
