### Task 1 MininetTopo

```shell
sudo python mininetTopo.py # expect to see exact number of devices are launched.
```

### Task 2 PingAll

```shell
pingall # expect to see all hosts ping each other successfully
```

### Task 3 Fault Tolerance

```shell
pingall # same
h1 ping h4 # connected
link s1 s2 down # drop the link
h1 ping h4 # there could be a timeout before reconnection
link s1 s2 up
```

### Task 4 Firewall

h4 on port 4001

```shell
h4 iperf -s -p 4001 & # start a iperf server on port 4001
h5 iperf -c h4 -p 4001 # no response
h1 iperf -c h4 -p 4001 # no response
```

```shell
h4 iperf -s -p 8080 & # start a iperf server on port 8080
h5 iperf -c h4 -p 8080 # local 10.0.0.5 port XXX connected with 10.0.0.4 port 8080
```

h2 to h5 on port 1000

```shell
h5 iperf -s -p 1000 & # start a iperf server on port 1000
h2 iperf -c h5 -p 1000 # no response
h1 iperf -c h5 -p 1000 # local 10.0.0.1 port XXX connected with 10.0.0.5 port 1000
h7 iperf -c h5 -p 1000 # local 10.0.0.7 port XXX connected with 10.0.0.5 port 1000
```

```shell
h5 iperf -s -p 8080 & # start a iperf server on port 8080
h2 iperf -c h5 -p 8080 # local 10.0.0.2 port XXX connected with 10.0.0.5 port 8080
```

### Task 5 Premium Traffic

premium to premium

```shell
iperf h1 h3 # Results: ~10Mbits
```

normal to premium

```shell
iperf h1 h2 # Results: ~5Mbits or ~10Mbits
iperf h2 h1 # Results: ~5Mbits or ~10Mbits
```

normal to normal 

```shell
iperf h2 h5 # Results: ~5Mbits
```

