import asyncssh
import re
import os
import time
import asyncio
#import serial
import json
import pwd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from re import findall
from subprocess import Popen, PIPE, run, CalledProcessError
from ipyparallel import Cluster
from pathlib import Path
from warnings import warn
from PIL import Image
from typing import Union

#fpga configuration
start_time = 0
IMAGE_PATH = "/srv/data/hyperfpga_conf/hyperfpga.jpg"
NODES_PATH = "/srv/data/hyperfpga_conf/.nodes_assig/"

class hyperfpga(Cluster):
    # Configuration Constants
    CONTROLLER_IP = '192.168.0.42'
    SSH_KEY_PATH = '/srv/data/hyperfpga_conf/.ssh/id_rsa'
    NODE_USER_NAME = 'mlabadm'
    XSA_2_BIT_PATH = '/tools/xsa2bit/xsa2bins.py'
    VIVADO_PATH = '/tools/Xilinx/'
    DTS_PATH = '/tools/xsa2bit/device-tree-xlnx/'
    BITSTREAM_PATH = '/bitstreams/'
    
    def __init__(self, nodes: dict, firmware: Union[str, list], n_engines: int = None, engines_per_node: int = 1, profile: str = 'ssh'):
        self.home_dir = os.path.expanduser("~")
        self.nodes = nodes
        self.firmware = firmware
        self.engines_per_node = engines_per_node
        self.profile = profile
        self.n_engines = n_engines

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        if isinstance(nodes, list):
            self._nodes = nodes
        else:
            raise TypeError("Nodes must be a list.")

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        if isinstance(profile, str):
            self._profile = profile
        else:
            raise TypeError("Profile name must be a string.")

    @property
    def engines_per_node(self):
        return self._engines_per_node

    @engines_per_node.setter
    def engines_per_node(self, engines_per_node):
        if isinstance(engines_per_node, int) and engines_per_node > 0 and engines_per_node <= 4:
            self._engines_per_node = engines_per_node
        else:
            raise TypeError(f"Engines per node must be an integer bigger than 0 and less than 4.")

    @property
    def n_engines(self):
        return self.n_engines

    @n_engines.setter
    def n_engines(self, n_engines):
        if isinstance(n_engines, int) and n_engines > 0 and n_engines <= len(self._nodes) * self._engines_per_node:
            self._n_engines = n_engines
        else:
            raise TypeError(f"Engines must be an integer bigger than 0 and less than {len(self._nodes) * self._engines_per_node}.")

    @property
    def firmware(self):
        return self._firmware

    def __check_config_files(self, firmware):
        bit  = Path(f"{self.home_dir}{self.BITSTREAM_PATH}{firmware}-{self._nodes[0]['fpga']['model']}.bit.bin").expanduser()
        dtbo  = Path(f"{self.home_dir}{self.BITSTREAM_PATH}{firmware}-{self._nodes[0]['fpga']['model']}.dtbo").expanduser()
        xsafile = Path(f"{self.home_dir}{self.BITSTREAM_PATH}{firmware}-{self._nodes[0]['fpga']['model']}.xsa").expanduser()
        return bit, dtbo, xsafile

    def __exec_xsa2bin(self, xsafilename):
        try:
            workdir = f"{self.home_dir}{self.BITSTREAM_PATH}"
            xsafile = f"{workdir}{xsafilename}-{self._nodes[0]['fpga']['model']}.xsa"
            dtsifile = f"{workdir}{xsafilename}-{self._nodes[0]['fpga']['model']}.dtsi"
            cm_exec = ["python3", self.XSA_2_BIT_PATH, f"-x={xsafile}", f"-V={self.VIVADO_PATH}", f"-dts={self.DTS_PATH}"]
            file_create = run(cm_exec, check=True, stdout=PIPE, stderr=PIPE, cwd=workdir)
            if os.path.exists(dtsifile):
                os.remove(dtsifile)
            if os.path.exists(xsafile):
                os.remove(xsafile)
            print(f".bit and .dtbo files where created from {xsafilename}-{self._nodes[0]['fpga']['model']}.xsa")
        except CalledProcessError as e:
            raise RuntimeError(f"XSA to BIT conversion failed: {e.stderr.decode()}") from e
        
    @firmware.setter
    def firmware(self, firmware):
        if isinstance(firmware, str):
            bit, dtbo, xsafile = self.__check_config_files(firmware)
            if not bit.is_file() and not dtbo.is_file():
                if not  xsafile.is_file():
                    raise ValueError(f"Error: missing specified configuration files {xsafile} for FPGA in bitstreams folder.", RuntimeWarning)
                else:
                    print("Warning: missing configuration files .bit and .dtbo in bitstreams folder. They will be created, which may take a few minutes.")
                    self.__exec_xsa2bin(firmware)
            else:    
                if not bit.is_file():
                    raise ValueError(f"Error: missing specified configuration files {bit} for FPGA in bitstreams folder.", RuntimeWarning)
                if not  dtbo.is_file():
                    raise ValueError(f"Error: missing specified configuration files {dtbo} for FPGA in bitstreams folder.", RuntimeWarning)
            self._firmware = [firmware] * len(self._nodes)
        elif isinstance(firmware, list):
            if len(firmware) != len(self._nodes):
                raise ValueError(f"Error: missing configuration specification for all node in the cluster. Firmware count: {len(firmware)} for {len(self.nodes)} nodes.", RuntimeWarning)
            for f in firmware:
                bit, dtbo, xsafile = self.__check_config_files(f)
                if not bit.is_file() and not dtbo.is_file():
                    if not  xsafile.is_file():
                        raise ValueError(f"Error: missing specified configuration files {xsafile} for FPGA in bitstreams folder.", RuntimeWarning)
                    else:
                        print("Warning: missing configuration files .bit and .dtbo in bitstreams folder. They will be created, which may take a few minutes.")
                        self.__exec_xsa2bin(f)
                else:    
                    if not bit.is_file():
                        raise ValueError(f"Error: missing specified configuration files {bit} for FPGA in bitstreams folder.", RuntimeWarning)
                    if not  dtbo.is_file():
                        raise ValueError(f"Error: missing specified configuration files {dtbo} for FPGA in bitstreams folder.", RuntimeWarning)
            self._firmware = firmware

    def __progress_handler(self, from_file, to_file, bytes_copied, total_size):
        time_spent = time.perf_counter()
        print(f"{from_file} -> {to_file} {bytes_copied/time_spent:06.2f}", end='\r')

    async def clean_cluster(self):
        for node in self._nodes:
            await self.__sshcmd(node['ip'], f'sudo rmmod comblock')
            await self.__fpgautil_handler(node['ip'])
            node['fpga']['firmware'] = ''

    async def reboot_cluster(self):
        for node in self._nodes:
            await self.__sshcmd(node['ip'], 'sudo reboot')

    async def shutdown_cluster(self):
        for node in self._nodes:
            await self.__sshcmd(node['ip'], 'sudo shutdown')    
    
    async def configure(self):
        await self.clean_cluster()
        print('Uploading firmware...')
        await self.__upload_firmware()
        print('\n Programming fpgas...')
        await self.__program_fpgas()
        print('\n Node Status')
        await self.__load_driver()
        node_view(self._nodes, 'program')
        await self.print_state()
        super().__init__(profile = self._profile, n = self._n_engines)

    def create_profile(self, mpi: bool = False) -> dict :
        username = pwd.getpwuid(os.getuid()).pw_name
        if mpi:
            warn("Check that MPI is available in the nodes.", RuntimeWarning)
            engine_args = ["--engines=mpi", f"--profile-dir=/home/mlabadm/.ipython/profile_{self._profile}"]
        else: 
            engine_args = [f"--profile-dir=/home/mlabadm/.ipython/profile_{self._profile}"]
        profile = self.__ipy_profile({f'{self.NODE_USER_NAME}@{node["ip"]}': self._engines_per_node for node in self._nodes}, engine_args, self.CONTROLLER_IP)
        profile_folder = f"/home/{os.environ.get('USER')}/.ipython/profile_{self._profile}"
        if os.path.isdir(profile_folder):
            print("Profile exists, rewritting configuration.")
        else:
            print("Profile does not exist, creating new profile.")
            os.mkdir(profile_folder)
        with open(profile_folder + "/ipcluster_config.py", 'w') as file:
            file.write(profile)

    #ipython profile
    def __ipy_profile(self, hosts, engine_args: str, controller_ip: str) -> str :
        return f"""
c = get_config()
c.Cluster.controller_ip = '{controller_ip}'
c.Cluster.engine_launcher_class = 'ssh'
c.SSHEngineSetLauncher.engine_args = {engine_args}
c.SSHEngineSetLauncher.engines = {hosts}
"""

    async def __scp_handler(self, host: str, filename: str):
        try:
            async with asyncssh.connect(host, username = self.NODE_USER_NAME, client_keys = self.SSH_KEY_PATH) as conn:
                await asyncssh.scp(filename, (conn, '/tmp/'), progress_handler = self.__progress_handler)
                return True
        except(OSError, asyncssh.Error) as exc:
            warn(f'Error: SSH connection to host {host} failed. {str(exc)}', RuntimeWarning)
            return False

    async def __sshcmd(self, host, cmd: str):
        try:
            async with asyncssh.connect(host, username = self.NODE_USER_NAME, client_keys = self.SSH_KEY_PATH) as conn:
                result = await conn.run(f'sudo {cmd}')
                return result.stdout
        except(OSError, asyncssh.Error) as exc:
            warn(f'Error: SSH connection to host {host} failed. {str(exc)}.', RuntimeWarning)
            return 0

    def __ping (self, host, ping_count = 4):
        data = ""
        output = Popen(f"ping {host} -n {ping_count}", stdout=PIPE, encoding="utf-8")
        for line in output.stdout:
            if findall("TTL", line):
                return 1
            else:
                return 0

    async def __load_driver(self, driver : str = 'comblock'):
        # check that the destination nodes have valid ips
        # collect targetted fpgas to validate the files
        for node in self._nodes:
            if not( 'ip' in node):
                warn(f'Error: missing ip in node {node}', RuntimeWarning)
                return
            if not('fpga' in node):
                warn(f'Error: missing fpga in node {node}', RuntimeWarning)
                return
            await self.__sshcmd(node['ip'], f'sudo insmod {driver}.ko')
    
    async def __upload_firmware(self):
        # check that the destination nodes have valid ips
        # collect targetted fpgas to validate the files
        for node, firmware in zip(self._nodes, self._firmware):
            if not('ip' in node.keys()):
                warn(f'Error: missing ip in node {node}', RuntimeWarning)
                return
            if not('fpga' in node.keys()):
                warn(f'Error: missing fpga in node {node}', RuntimeWarning)
                return
            # check that the both filename.bin and filename.dtsi files are available is present in ~/bitstreams and both
            bit  = Path(f"{self.home_dir}{self.BITSTREAM_PATH}{firmware}-{node['fpga']['model']}.bit.bin").expanduser()
            dtbo  = Path(f"{self.home_dir}{self.BITSTREAM_PATH}{firmware}-{node['fpga']['model']}.dtbo").expanduser()
            if not (bit.is_file() and dtbo.is_file()):
                warn(f"Error: missing configuration files for FPGA {node['fpga']['model']}", RuntimeWarning)
                return
            if not await self.__scp_handler(node['ip'], bit):
                warn(f"Error: failed to copy {bit} to {node['ip']}.", RuntimeWarning)
                return
            if not await self.__scp_handler(node['ip'], dtbo):
                warn(f"Error: failed to copy {dtbo} to {node['ip']}.", RuntimeWarning)
                return
        
    async def __fpgautil_handler(self, host: str, firmware: str =  None):
        try:       
            if firmware:
                op = f"-b /tmp/{firmware}.bit.bin -o /tmp/{firmware}.dtbo"
            else:
                op = "-R"
            result = await self.__sshcmd(host, f'sudo fpgautil {op}')
            print(result, end = '')
            return 1
        except (OSError, asyncssh.Error) as exc:
            warn(f'Error: SSH connection failed {str(exc)}', RuntimeWarning)
            return 0

    async def __program_fpgas(self):
        # check that the destination nodes have valid ips
        # collect targetted fpgas to validate the files
        for node, firmware in zip(self._nodes, self._firmware):
            if not( 'ip' in node.keys()):
                warn(f'Error: missing ip in node {node}', RuntimeWarning)
                return
            if not('fpga' in node.keys()):
                warn(f'Error: missing fpga in node {node}', RuntimeWarning)
                return
            if not await self.__fpgautil_handler(node['ip'], f"{firmware}-{node['fpga']['model']}"):
                warn(f"Error: failed to program {node['ip']}.", RuntimeWarning)
                return
            else:
                node['fpga']['firmware'] = firmware

    async def __fpga_state(self, host: str):
        try:
            async with asyncssh.connect(host, username=self.NODE_USER_NAME, client_keys=self.SSH_KEY_PATH) as conn:
                result = await conn.run(f'sudo cat /sys/class/fpga_manager/fpga0/state')
                return result.stdout
        except (OSError, asyncssh.Error) as exc:
            warn(f'Error: SSH connection failed {str(exc)}', RuntimeWarning)
            return 0

    async def print_state(self):
        await self.__read_state()
        for node in self._nodes:
            hostname = node['hostname']
            firmware = node['fpga']['firmware']
            state = node['fpga']['state']
            comblock = node['comblock']['devs']
            print(f' host: {hostname} state: {state} firmware: {firmware} comblock: {comblock}\n')

    async def __read_state(self):
        # check that the destination nodes have valid ips
        # collect targetted fpgas to validate the files
        for node in self._nodes:
            if not( 'ip' in node.keys()):
                warn(f'Error: missing ip in node {node}', RuntimeWarning)
                return
            if not('fpga' in node.keys()):
                warn(f'Error: missing fpga in node {node}', RuntimeWarning)
                return
            result = await self.__fpga_state(node['ip'])          
            if not result:
                break
            else:
                node['fpga']['state'] = result

            result = await self.__sshcmd(node['ip'], 'ls /dev/ComBlock*')
            node['comblock']['devs'] =  re.findall(r'_\d+_([a-z_]+)', result)

#    def get_power(self, stage: str = "init", number_of_samples = 100, f_opt = "w", port = '/dev/ttyUSB0', baudrate = 115200, timeout = 1):
#        ser = serial.Serial(port = port, baudrate = baudrate, timeout = timeout)

#        with open(f"pw_{stage}.txt", f_opt) as pw_file:
#            for i in range(number_of_samples):
#                pw_file.write(ser.readline().decode())

def get_nodes():
    user = os.environ.get("USER")
    nodesFile = f"{NODES_PATH}{user}_nodes.json"
    with open(nodesFile) as nodes_file:
        nodes = json.load(nodes_file)['nodes']
    print("Assigned Nodes:")
    node_view(nodes)
    return nodes
    


def node_view(nodes,state='view'):
    image = np.array(Image.open(IMAGE_PATH))
    square_size = 123
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.axis('off')
    for i in range(len(nodes)):
        x = nodes[i]['x']
        y = nodes[i]['y']
        ip = nodes[i]['ip']
        model = nodes[i]['fpga']['model']
        hostname = f"{model}-{x}-{y}"
        x_position = x * square_size
        y_position = y * square_size
        if state == 'view':
            rect = patches.Rectangle((y_position, x_position), square_size, square_size, linewidth=3, edgecolor='r', facecolor='none')
        else:
            rect = patches.Rectangle((y_position, x_position), square_size, square_size, linewidth=3, edgecolor='b', facecolor='none')
        ax.add_patch(rect)
        center_x = x_position + square_size / 2
        center_y = y_position + square_size / 2
        if state == 'view':
            ax.text(center_y, center_x, f'node: {i} \n model: {model}\n ip: {ip}', color='r', ha='center', va='center', fontsize=6.5, bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.5'))
        else:
            ax.text(center_y, center_x, f'hostname: \n {hostname}', color='r', ha='center', va='center', fontsize=7, bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.5'))
    plt.show()
