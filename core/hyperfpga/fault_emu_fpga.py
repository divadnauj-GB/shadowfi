
import sys
import os
import shutil
import importlib.util
from warnings import warn
import asyncio
import time
import logging
from ipyparallel import require
import ipyparallel as ipp

from core.hyperfpga.fi_manager_fpga import *
#from core.hyperfpga.run import *



import core.hyperfpga.fpga_engine as fpga_engine





exec_ipp="""
import sys
import os
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

if os.path.expanduser("{path}") not in sys.path:
    sys.path.insert(0, os.path.expanduser("{path}"))
    
#from import apply_test_data
from core.hyperfpga.fi_manager_fpga import *
#from core.hyperfpga.run import *
import core.hyperfpga.fpga_engine as fpga_engine

"""


def write_sdc_data(args={},results_tasks=[]):
    project = args.get('project',{})
    emu_config = project.get('emu_config',{})
    write_args = emu_config.get('write_args',{})
    write_args['work_dir'] = f"{write_args['work_dir']}/tmp"

    work_dir_clean = os.path.abspath(project.get('work_dir', ''))
    os.system(f"mkdir -p {work_dir_clean}/logs")
    FPGA_ENGINE = emu_config.get('fpga_engine',fpga_engine)
    for results_task in results_tasks:
        for fault_result in results_task:
            if fault_result[1] == "SDC":
                fault_descriptor = fault_result[0].split(',')
                tmp_dir = f"{work_dir_clean}/C{int(fault_descriptor[0])}_B{int(fault_descriptor[5])}_F{int(fault_descriptor[6])}"
                os.system(f"mkdir -p {work_dir_clean}/tmp")
                FPGA_ENGINE.write_result(write_args,fault_result[2])
                shutil.rmtree(tmp_dir, True)
                os.system(f"mv {work_dir_clean}/tmp {tmp_dir}")
                shutil.make_archive(tmp_dir, "gztar", tmp_dir)  # archieve the outputs
                os.system(f"mv {work_dir_clean}/*.gz {work_dir_clean}/logs/")
                shutil.rmtree(tmp_dir, True)
    os.system(f"mv {work_dir_clean}/logs {work_dir_clean}/../logs/")

def write_golden_data(args={},result_sim=[]):
        project = args.get('project',{})
        emu_config = project.get('emu_config',{})
        write_args = emu_config.get('write_args',{})
        write_args['work_dir'] = f"{write_args['work_dir']}/golden"
        work_dir_clean = os.path.abspath(project.get('work_dir', ''))
        FPGA_ENGINE = emu_config.get('fpga_engine',fpga_engine)
        for result in result_sim:
            tmp_dir = f"{work_dir_clean}/golden"
            shutil.rmtree(tmp_dir, True)
            os.system(f"mkdir -p {work_dir_clean}/golden")
            FPGA_ENGINE.write_result(write_args,result)
            #os.system(f"mv {work_dir_clean}/tmp {tmp_dir}")
            shutil.make_archive(tmp_dir, "gztar", tmp_dir)  # archieve the outputs
            os.system(f"mv {work_dir_clean}/*.gz {work_dir_clean}/../logs/")
            shutil.rmtree(tmp_dir, True)

"""
def create_fault_descriptor(fi_structure):
    modules = fi_structure["modules"]
    sr_leght = fi_structure["sr_lenght"]
    component = fi_structure["component"]
    start_bit_pos = fi_structure["start_bit_pos"]
    end_bit_pos = fi_structure["end_bit_pos"]
    bit_pos = fi_structure["bit_pos"]
    f_cntrl = fi_structure["f_model"]
    seu_time = fi_structure["seu_time"]
    f_descriptor=[]
    f_descriptor.append(f_cntrl)
    f_descriptor.append(modules)
    f_descriptor.append(component)
    f_descriptor.append(sr_leght)
    f_descriptor.append(seu_time)
    f_descriptor.append(start_bit_pos)
    f_descriptor.append(end_bit_pos)
    for idx in range(fi_structure["sr_lenght"]):
        absolute_bit_pos = bit_pos + start_bit_pos
        if idx>= start_bit_pos and idx < end_bit_pos:
            if idx == absolute_bit_pos:
                f_descriptor.append(1)
            else:
                if idx == end_bit_pos-2:
                    f_descriptor.append(f_cntrl&1)
                    f_cntrl = f_cntrl >> 1
                elif idx == end_bit_pos -1:
                    f_descriptor.append(f_cntrl&1)
                    f_cntrl = f_cntrl >> 1
                else:
                    f_descriptor.append(0)                               
        else:
            f_descriptor.append(0)
    return(f_descriptor) 


def fi_sbtr_config(fault_descriptor):
    from comblock import Comblock
    def fi_port_conf(cb,RSTN=0, TFEN=0, SREN=0):
        FI_PORT = ((RSTN<<2)|(TFEN<<1)|(SREN))
        cb.write_reg(0,FI_PORT)
    def clk_gen(cb,PORT):
        PORT=PORT^(1<<3)
        cb.write_reg(0,PORT)
        PORT=PORT^(1<<3)
        cb.write_reg(0,PORT)
    cb1 = Comblock(1)
    # 0 -> SREN
    # 1 -> TFEN
    # 2 -> RSTN
    # 3 -> CLK not from here
    RSTN=0
    TFEN=0
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    cb1.write_reg(0,FI_PORT)
    clk_gen(cb1,FI_PORT)
    RSTN=1
    TFEN=0
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    for _ in range(10):
        clk_gen(cb1,FI_PORT)
    for element in fault_descriptor[7:]:
        RSTN=1
        TFEN=0
        SREN=1
        SI=element
        FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
        clk_gen(cb1,FI_PORT)
    RSTN=1
    TFEN=1
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    for _ in range(2):
        clk_gen(cb1,FI_PORT)   

"""

def run_one_task_fault_free_emulation(input_data={},fi_config={}):
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    num_target_components = int(emu_config.get('num_target_components', 0))
    total_bit_shift = int(emu_config.get('total_bit_shift', 0))
    fpga_engine_obj = emu_config.get('fpga_engine',fpga_engine)
    
    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }
    
    try:
        f_descriptor=create_fault_descriptor(fi_structure)
        fi_sbtr_config(f_descriptor)
        result_data=fpga_engine_obj.run(input_data)
    except Exception as error:
        raise(error)
    return result_data



def run_one_task_fault_emulation(fault_list_input: list, input_data={}, golden_results={},fi_config={}):
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    max_num_inj = emu_config.get('max_num_faults', -1)
    num_target_components = int(emu_config.get('num_target_components', 0))
    total_bit_shift = int(emu_config.get('total_bit_shift', 0))
    fpga_engine_obj = emu_config.get('fpga_engine',fpga_engine)

    sdc_count = 0
    masked = 0
    simulation_report = []
    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }
    
    with open(os.path.expanduser("~/stdout.txt"),"w") as fp:
        print(f"{len(fault_list_input)}",file=fp)
        print(fault_list_input,file=fp)
        for fault in fault_list_input:
            print(f"{fault}",file=fp)
            print(fault.strip().split(","), file=fp)
    
    if len(fault_list_input) > 0:
        fault_list = [fault.strip().split(",") for fault in fault_list_input]
    else:
        return ([[{},{},{}]])
        
    for idx, fault_info in enumerate(fault_list):
        # generate one fault descriptor
        # List_injections.append([idx, inst, module, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
        fi_structure["component"] = int(fault_info[0])
        fi_structure["start_bit_pos"] = int(fault_info[3])
        fi_structure["end_bit_pos"] = int(fault_info[4])
        fi_structure["bit_pos"] = int(fault_info[5])
        fi_structure["f_model"] = int(fault_info[6])
        fi_structure["seu_time"] = int(fault_info[7])

        f_descriptor=create_fault_descriptor(fi_structure)
        fi_sbtr_config(f_descriptor)
        try:
            result_data=fpga_engine_obj.run(input_data)
            fi_class=fpga_engine_obj.sdc_check(result_data,golden_results)
        except Exception as error:
            fi_class = "DUE"
            result_data={}

        result_fi = f"{fault_info[0]},{fault_info[1]},{fault_info[2]},{fault_info[3]},{fault_info[4]},{fault_info[5]},{fault_info[6]}"
        
        if fi_class == "Masked":
            masked += 1
            simulation_report.append([result_fi,fi_class,{}])
        else:
            sdc_count += 1
            simulation_report.append([result_fi,fi_class,result_data])
        if idx>=max_num_inj and max_num_inj>0:
            break
    return simulation_report



def progress_handler(from_file, to_file, bytes_copied, total_size):
    time_spent = time.perf_counter()
    print(f"{from_file} -> {to_file} {bytes_copied/time_spent:06.2f}", end='\r')

async def scp_handler(host: str, username: str, client_keys: str, src: str, dst:str, recursive=True):
    import asyncssh
    try:
        async with asyncssh.connect(host, username = username, client_keys = client_keys) as conn:
            await asyncssh.scp(src, (conn, f'{dst}'), recurse=recursive, progress_handler=progress_handler)
            print("tranfer file succesful")
            return True
    except(OSError, asyncssh.Error) as exc:
        warn(f'Error: SSH connection to host {host} failed. {str(exc)}', RuntimeWarning)
        return False

async def sshcmd(host, username: str, client_keys: str, cmd: str):
    import asyncssh
    try:
        async with asyncssh.connect(host, username = username, client_keys = client_keys) as conn:
            result = await conn.run(f'{cmd}')
            print(result)
            return result.stdout
    except(OSError, asyncssh.Error) as exc:
        warn(f'Error: SSH connection to host {host} failed. {str(exc)}.', RuntimeWarning)
        return 0


def run_golden_emulation(work_dir, fi_config={}):
    # import sys
    import os
    from core.hyperfpga.clusterconf.clusterconf import hyperfpga, get_nodes
    from core.hyperfpga.comblock.comblock import Comblock
    import importlib

    
    shadowfi_root = fi_config.get('shadowfi_root','')    
    
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    fault_list_name = fi_config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    fault_model = sbtr_config.get('fault_model', 'S@')
    fault_list_name = f"{fault_model}_{fault_list_name}"

    num_tasks = 1
    nodes_selected = emu_config.get('target_nodes',[1,2])
    work_dir_client = emu_config.get('work_dir_client', '~/work')
    design_name = emu_config.get('design_name', 'TCU_1_SBTR')
    module_path_file = os.path.abspath(emu_config.get('fpga_engine_module',"./config/fpga_engine.py"))
    os.system(f"cp {module_path_file} {shadowfi_root}/core/hyperfpga/")
    importlib.reload(fpga_engine)

    work_dir_clean = work_dir
    src_work_path_dir = os.path.abspath(os.path.join(work_dir_clean))
    # check if multiple tasks are required
    if num_tasks >= 1:
        CUT_engine = fpga_engine.fpga_engine()
        cut_test_data_info = CUT_engine.load_test_data(emu_config.get('load_args',{}))
        fi_config['project']['emu_config']['fpga_engine'] = CUT_engine
        input_data_list = []
        for _ in range(num_tasks):
            input_data_list.append(cut_test_data_info)
            
        # run the tasks

        nodes_config = get_nodes()
        testnode = [nodes_config[k] for k in nodes_selected]
        cluster = hyperfpga(testnode, design_name ,n_engines = len(testnode), engines_per_node = 1)
        cluster.create_profile()
        async def myfunction():
            await cluster.configure()
        asyncio.run(myfunction())
        with cluster.start_and_connect_sync() as rc:
            #rc = cluster.start_and_connect_sync() 
            print(cluster.NODE_USER_NAME)
            print(cluster.SSH_KEY_PATH)
            uname = cluster.NODE_USER_NAME
            sshkey = cluster.SSH_KEY_PATH
            for node in testnode:
                asyncio.run(sshcmd(node['ip'],uname, sshkey,f"rm -rf {work_dir_client}"))
                asyncio.run(sshcmd(node['ip'],uname, sshkey,f"rm -rf ~/core"))
                asyncio.run(scp_handler(node['ip'],uname, sshkey, src_work_path_dir,work_dir_client,True))
                asyncio.run(scp_handler(node['ip'],uname, sshkey, f"{shadowfi_root}/core","~",True))
                asyncio.run(sshcmd(node['ip'],uname, sshkey,f"mkdir -p {work_dir_client}"))
                asyncio.run(scp_handler(node['ip'],uname, sshkey, module_path_file,"~/core/hyperfpga",False))
 
            nodes = rc[:]
            with nodes.sync_imports():
                import os
                from struct import unpack
                from comblock import Comblock
            # Send and write the module to each engine
            logging.info(exec_ipp.format(path=work_dir_client))
            nodes.execute(exec_ipp.format(path=work_dir_client))
            asyncresult = nodes.map_async(run_one_task_fault_free_emulation,input_data_list,[fi_config])
            asyncresult.wait_interactive()
            results = asyncresult.get()
        logging.info(asyncresult)
        write_golden_data(fi_config,results)

    return(results[0])


def run_fault_emulation(work_dir, fi_config={}, golden_data={}):
    import os
    from core.hyperfpga.clusterconf.clusterconf import hyperfpga, get_nodes
    from core.hyperfpga.comblock.comblock import Comblock

    
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    fault_list_name = fi_config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    fault_model = sbtr_config.get('fault_model', 'S@')
    fault_list_name = f"{fault_model}_{fault_list_name}"

    F_sim_report = fi_config.get('project', {}).get('fault_sim_report', 'fsim_report.csv')
    num_tasks = emu_config.get('tasks', 2)
    nodes_selected = emu_config.get('target_nodes',[1,2])
    work_dir_client = emu_config.get('work_dir_client', '~/work')

    #work_dir_clean = os.path.abspath(fi_config.get('project', {}).get('work_dir', ''))
    work_dir_clean = work_dir
    src_work_path_dir = os.path.abspath(os.path.join(work_dir_clean))
    # check if multiple tasks are required
    if num_tasks >= 1:
        # read the fault list
        fault_list_task = []
        with open(f"{os.path.abspath(src_work_path_dir)}/{fault_list_name}", "r") as f:
            fault_list = f.readlines()
            if len(fault_list) == 0:
                print("No fault list found")
                return
            else:
                fault_list_task = [fault_list[task_id::num_tasks] for task_id in range(num_tasks)]

        # create hidden work directories  
        CUT_engine = fpga_engine.fpga_engine()
        cut_test_data_info = CUT_engine.load_test_data(emu_config.get('load_args',{}))
        input_data_list = []
        for _ in range(num_tasks):
            input_data_list.append(cut_test_data_info)
        # run the tasks
        """
        nodes_config = get_nodes()
        testnode = [nodes_config[k] for k in nodes_selected]
        cluster = hyperfpga(testnode, design_name ,n_engines = len(testnode), engines_per_node = 1)
        cluster.create_profile()
        async def myfunction():
            await cluster.configure()
        asyncio.run(myfunction())
        with cluster.start_and_connect_sync() as rc:
        """
        with ipp.Cluster(profile="ssh",n=len(nodes_selected)) as rc:
            nodes = rc[:]
            with nodes.sync_imports():
                import os
                from struct import unpack
                from comblock import Comblock
            # Send and write the module to each engine
            nodes.execute(exec_ipp.format(path=work_dir_client))
            asyncresult = nodes.map_async(run_one_task_fault_emulation,[flist_id for flist_id in fault_list_task],[cut_test_data_info for _ in range(num_tasks)],[golden_data for _ in range(num_tasks)], [fi_config for _ in range(num_tasks)])
            asyncresult.wait_interactive()
            logging.info(asyncresult)
            results_tasks = asyncresult.get()
        
        with open(f"{work_dir_clean}/{fault_model}_{F_sim_report}","w") as fp:
            for result_task in results_tasks:
                for fault_result in result_task:
                    fault_descriptor = fault_result[0]
                    fi_class = fault_result[1]
                    fp.write(f"{fault_descriptor},{fi_class}\n")
        fi_config['project']['emu_config']['fpga_engine'] = CUT_engine        
        write_sdc_data(fi_config,results_tasks)