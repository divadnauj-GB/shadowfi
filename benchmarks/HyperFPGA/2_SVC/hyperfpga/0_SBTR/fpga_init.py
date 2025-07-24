import asyncio
import os
import sys
sys.executable
sys.path.insert(0, os.path.expanduser("~"))
sys.path.insert(0, os.path.expanduser("~/Comblock/"))
from hyperfpga_conf.clusterconf import hyperfpga, get_nodes
import ipyparallel as ipp


class init_fpga:
    def __init__(self,configname='SVC_0_SBTR'):
        self.nodes = get_nodes()
        self.testnode = [self.nodes[1]]
        self.cluster = hyperfpga(self.testnode, configname ,n_engines = len(self.testnode), engines_per_node = 1)
        self.cluster.create_profile()
        async def myfunction():
            await self.cluster.configure()
        asyncio.run(myfunction())

        self.rc = self.cluster.start_and_connect_sync()   

    def shutdown_cluster(self):
        self.rc.shutdown()
        self.cluster.clean_cluster()
        self.cluster.stop_cluster()
        
    def reboot_cluster(self):
        self.shutdown_cluster()
        self.cluster.reboot_cluster()

FPGA_cluster = init_fpga()





