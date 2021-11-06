## Prerequisite

1. Installed a Mininet VM.

2. Can open a Mininet console using SSH to Mininet VM:

   ```shell
   ssh mininet@MININET_IP_ADDRESS # password is also mininet
   ```

## Set up

Copy examples folder from your local host to Mininet VM root path i.e. `~/examples`. 

1. Find the IP_ADDRESS of your Mininet VM using: `ifconfig`.
2. Find the the absolute path EXAMPLE_FOLDER of examples folder in your local host i.e. E.g. `/home/cs4226/examples`.

```shell
scp -r EXAMPLE_FOLDER mininet@MININET_IP_ADDRESS:
```

**Launch POX Controller**: Open one console of Mininet VM, run following commands:

```shell
mv controller-*.py ~/pox
cd ~/pox
# run hub controller.
./pox.py controller-hub
# run example controller
# ./pox.py controller-example
```

**Launch Mininet Topology**: Open another console of Mininet VM, run following commands:

```shell
cd ~/examples
sudo python mininetTopo-example.py
```

## Issues

If you have the error message when launch your POX controller:

```
Error 98 while binding socket: Address already in use
```

Try to clean the old Mininet topologies and restart the POX controller again:

```
sudo mn -c
```

