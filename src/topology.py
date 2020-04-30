#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink
from functools import partial
from time import time

class LinearTopo(Topo):
    # Linear Topology with 2 hosts and n switchs
    def build(self, n=2, controller_ip="127.0.0.1"):
        host = self.addHost('h0')
        old_switch = self.addSwitch('s0')
        self.addLink(host, old_switch)

        for sw in range(1,n):
            switch = self.addSwitch('s%d' % sw)
            if sw < n:
                self.addLink(old_switch, switch)
            old_switch = switch

        host = self.addHost('h1')
        self.addLink(host, switch)

def performanceTest(n=4, suffix=""):
    "Create and test a network"
    topo = LinearTopo(n)
    link = partial( TCLink, bw=10 )
    net = Mininet(topo=topo, controller=RemoteController("c0") , switch=OVSKernelSwitch, link=link)
    net.start()

    print "Simulating network with %d switchs" % n

    print "Controller to Switch"
    f = open('out-c-s-'+suffix,'a+')
    print >>f, "switch size = %d" % n
    c = net.get("c0")
    for s in range(n):
        sw = net.get("s%d" %s)
        throughput0, throughput1 = net.iperf((c, sw))[0] ,net.iperf((c, sw))[1]
        _,_, latency_c_to_s = (net.pingFull((c, sw)))[0]
        _,_, mi, av, ma, mdev = latency_c_to_s
        print "s%d" %s, throughput0, throughput1, av
        print >>f, "s%d, %s, %s , %f" % (s, throughput0, throughput1, av)
    f.close()

    print "End to End with %d switchs" % n

    # print "Dumping host connections"
    # dumpNodeConnections(net.hosts)

    # print "Testing network connectivity"
    # net.pingAll()

    # print "Testing bandwidth between h1 and h2"
    h0, h1 = net.get( 'h0', 'h1' )
    
    throughput = net.iperf((h0, h1))
    ping = h0.cmd('ping -c 5 ' + h1.IP() + ' | grep rtt')

    f = open('out-n-n-'+suffix,'a+')
    print throughput, ping
    print >>f, "%d -> %s %s %s" % (n, throughput[0], throughput[1], ping)
    f.close()
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    start = time()
    setLogLevel('warning')
    for j in range(3):
        for i in [50, 100, 150]:
            performanceTest(i, suffix="LongNet-"+str(j))