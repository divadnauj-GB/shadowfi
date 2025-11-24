import platform
import pathlib
from pathlib import Path
import os
from typing import Optional

from nicegui import events, ui
from gui.local_file_picker import local_file_picker
from utils.config_loader import load_config,save_config, KeyValueAction


def build_tree_nodes(paths):
    """
    Converts a list of absolute paths into a hierarchical data structure for ui.tree.
    """
    tree_root = {}

    for absolute_path in paths:
        # Use os.sep to split paths correctly for different OS
        parts = absolute_path.strip(os.sep).split(os.sep)
        current_level = tree_root

        for i, part in enumerate(parts):
            # Create a unique ID for each node
            node_id = os.sep + os.path.join(*parts[:i+1])
            if part not in current_level:
                current_level[part] = {
                    'id': node_id,
                    'label': part,
                    'children': {}
                }
            current_level = current_level[part]['children']
            
    # Convert the nested dictionary structure to the list format expected by ui.tree
    def convert_dict_to_list(node_dict):
        result = []
        for key, value in node_dict.items():
            item = {'id': value['id'], 'label': value['label']}
            if value['children']:
                item['children'] = convert_dict_to_list(value['children'])
            result.append(item)
        return result

    return convert_dict_to_list(tree_root)

class SimWorkFlowSetup(ui.dialog):

    def __init__(self, ShadowfiPath="~") -> None:
        super().__init__()
        self.shadowfi_root = ShadowfiPath
        self.tb_path=""
        self.tb_working_dir=""
        self.tb_inc_directories=[]
        self.tb_list_files=[]
        self.tb_verilator_params=""
        self.tb_top=""
        self.tb_params=[]
        self.tb_target_file=""
        self.tb_build_cmd=[]
        self.external_tb_build=False

        with self, ui.card():
            self.uiObjectsDict=dict()
            ui.markdown('#### **TestBench Settings**').classes('w-100')
            self.uiTBExtCheckBox=ui.checkbox("External TestBench Build settings (*)",on_change=self.uiExtTBBuild)
            with ui.card() as self.TBExternal:
                self.TBExternal.visible=False
                with ui.row().classes('w-full mt-2'): 
                    self.uiTBExtCMDInput = ui.input(label='TestBench Parameters', placeholder='Enter TB build commands, comma separated (e.g., make -f Makefile_sbtr clean, make -f Makefile_sbtr)',on_change=self.uiTBExtCMD).classes('w-72')
                
            with ui.card() as self.TBInternal:
                self.TBInternal.visible=True
                with ui.row().classes('w-full items-center'):
                    self.uiProjPathInput=ui.input('Select TestBench Path (*)', on_change= lambda e:self.uiGetProjPath(e.value)).classes('w-72')
                    self.uiProjPathInput.value=""
                    self.uiProjPathButton = ui.button('Browse', on_click=lambda: self.uiSelectProjDir())
                
                with ui.row().classes('w-full mt-2'): 
                    self.uiTBIncDirTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                    self.uiTBIncDirButton=ui.button('TestBench Inc Directories', on_click=self.uiSelectIncDirs)
                    self.uiTBIncDirButton.disable()
                
                with ui.row().classes('w-full mt-2'): 
                    self.uiTBFilesTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                    self.uiTBFilesButton=ui.button('TestBench Files (*)', on_click=self.uiSelTBFiles)
                    self.uiTBFilesButton.disable()

                with ui.row().classes('w-full mt-2'): 
                    self.uiTBParamInput = ui.input(label='TestBench Parameters', placeholder='Enter comma separated (e.g., N=10, M=25, PARAM=HELLO)',on_change=self.uiAddParam).classes('w-72')
                
                with ui.row().classes('w-full mt-2'): 
                    self.uiTBVerilatorParamsInput = ui.input(label='TestBench Verilator Params', placeholder='Enter additional verilator CLI params',on_change=self.uiTBVerilatorParams).classes('w-72')  
                
                with ui.row().classes('w-full mt-2'): 
                    self.uiTBTopModuleInput = ui.input(label='TestBench Top module (*)', placeholder='Enter the top module name',on_change=self.uiTBTopModule).classes('w-72')  


                with ui.row().classes('w-full items-center'):
                    self.uiTBTargetFileInput=ui.input('Select Target TestBench File (*)', on_change= lambda e:self.uiGetTBTargetFile(e.value)).classes('w-72')
                    self.uiTBTargetFileInput.value=""
                    self.uiTBTargetFileButton = ui.button('Browse', on_click=self.uiOnTBTargetFile)

            with ui.row().classes('w-full items-center'):
                self.uiTBWorkDirInput=ui.input('TestBench Working Directory (*)', on_change= lambda e:self.uiGetTBWorkDir(e.value)).classes('w-72')
                self.uiTBWorkDirInput.value=""
                self.uiTBWorkDirButton = ui.button('Browse', on_click=lambda: self.uiSelTBWorkDirDir())
                    

            with ui.row().classes('w-full mt-4'):
                ui.label('(*) Required fields').classes('text-sm text-gray-500')
            with ui.row().classes('w-full justify-between'):
                #ui.button('Create Project', on_click=lambda: create_project_callback(create_project_dialog,uiProjMainNameInput,uiProjMainPathInput))
                ui.button('OK', on_click=self._handle_ok)

                ui.button('Cancel', on_click=self.close)

    def uiExtTBBuild(self):
        if self.uiTBExtCheckBox.value:
            self.TBExternal.visible=True
            self.TBInternal.visible=False
        else:
            self.TBExternal.visible=False
            self.TBInternal.visible=True
        self.external_tb_build=self.uiTBExtCheckBox.value

    def uiTBExtCMD(self):
        ParamsStr=self.uiTBExtCMDInput.value
        ParamsList = ParamsStr.split(',')
        ParamsList = [(p.strip()).lstrip() for p in ParamsList]
        self.tb_build_cmd=ParamsList

    def uiAddParam(self):
        ParamsStr=self.uiTBParamInput.value
        ParamsList = ParamsStr.split(',')
        ParamsList = [(p.strip()).lstrip() for p in ParamsList]
        self.tb_params=ParamsList
        

    def uiTBTopModule(self):
        self.tb_top = self.uiTBTopModuleInput.value

    def uiTBVerilatorParams(self):
        self.tb_verilator_params=self.uiTBVerilatorParamsInput.value

    def uiGetTBTargetFile(self,file):
        self.tb_target_file=file

    async def uiOnTBTargetFile(self):
        home = self.shadowfi_root
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                self.uiTBTargetFileInput.value=project_dir
                self.tb_target_file=project_dir
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')


    def uiGetProjPath(self,path):
        self.tb_path=path

    def uiGetTBWorkDir(self,path):
        self.tb_working_dir=path

    async def uiSelectProjDir(self):
        home = self.shadowfi_root
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                self.uiProjPathInput.value=project_dir
                self.tb_path=project_dir
                self.uiTBIncDirButton.enable()
                self.uiTBFilesButton.enable()
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')

    async def uiSelTBWorkDirDir(self):
        home = self.shadowfi_root
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                self.uiTBWorkDirInput.value=project_dir
                self.tb_working_dir=project_dir
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')

    async def uiSelTBFiles(self):
        home = self.tb_path
        result = await local_file_picker(home, multiple=True)
        DirsList = self.tb_list_files
        if not isinstance(DirsList,list):
            DirsList = []
        if result:
            if len(result)!=0:
                inc_dirs=result
                for item in inc_dirs: 
                    if item not in DirsList:
                        DirsList.append(item)
                
                self.tb_list_files=DirsList
                Directories = [str(pathlib.Path(p.replace(self.tb_path,"/tb_root_dir"))) for p in DirsList]
                nodes_data = build_tree_nodes(Directories)
                self.uiTBFilesTree.props['nodes']=nodes_data
                ui.notify(f'TB files selected: {Directories}') 
        else:
            ui.notify(f'No TB files selected')

    async def uiSelectIncDirs(self):
        home = self.tb_path
        result = await local_file_picker(home, multiple=True)
        DirsList = self.tb_inc_directories
        if not isinstance(DirsList,list):
            DirsList = []
        if result:
            if len(result)!=0:
                inc_dirs=result
                for item in inc_dirs: 
                    if item not in DirsList:
                        DirsList.append(item)
                
                self.tb_inc_directories=DirsList
                Directories = [str(pathlib.Path(p.replace(self.tb_path,"/tb_root_dir"))) for p in DirsList]
                nodes_data = build_tree_nodes(Directories)
                self.uiTBIncDirTree.props['nodes']=nodes_data
                ui.notify(f'TB dirs selected: {Directories}') 
        else:
            ui.notify(f'No TB dirs selected')

    async def _handle_ok(self):
        
        tb_config ={
            'testbench_config': {
                'external_tb_build': False,
                'external_tb_config': {
                    'tb_build_cmd':  self.tb_build_cmd,
                    'tb_working_dir': self.tb_working_dir
                },
                'internal_tb_config': {
                    'tb_list_files': self.tb_list_files,
                    'tb_path': self.tb_path,
                    'tb_working_dir': self.tb_working_dir,
                    'tb_target_file': self.tb_target_file,
                    'tb_top': self.tb_top,
                    'tb_inc_directories':  self.tb_inc_directories,
                    'tb_params': self.tb_params,
                    'tb_verilator_params': self.tb_verilator_params
                }
            }
        }
        
        self.submit(tb_config)




class FaultSimSetup(ui.dialog):

    def __init__(self, config_file) -> None:
        super().__init__()
        self.shadowfi_root  = os.getenv('SHADOWFI_ROOT', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")))
        self.config = load_config(config_file)
        self.sim_config_dict={}
        self.sim_config_dict['sim_config'] = self.config['project'].get('sim_config',{})
     
        #self.sim_config_dict = load_config(os.path.join(self.shadowfi_root,"gui","config_templates","sim_config.yml"))


        with self, ui.card():
            self.uiObjectsDict=dict()
            ui.markdown('#### **Fault Simulation Settings**').classes('w-100')
            with ui.row():
                self.FITasksInput=ui.input('Tasks (*)', on_change= lambda e:self.uiGetFITasks(e.value)).classes('w-20')
                self.FIEnginesInput=ui.input('Engines (*)', on_change= lambda e:self.uiGetFIEngines(e.value)).classes('w-20')
                self.FINFaultsInput=ui.input('Max Num Faults (*)', on_change= lambda e:self.uiGetFINFaults(e.value)).classes('w-30')
                self.FIRunTimeInput=ui.input('Simulation Runtime (s) (*)', on_change= lambda e:self.uiGetRunTime(e.value)).classes('w-30')
                self.FITasksInput.value=self.sim_config_dict['sim_config'].get('tasks',1)
                self.FIEnginesInput.value=self.sim_config_dict['sim_config'].get('engines',1)
                self.FINFaultsInput.value=self.sim_config_dict['sim_config'].get('max_num_faults',1)
                self.FIRunTimeInput.value=self.sim_config_dict['sim_config'].get('sim_runtime',200000)

            with ui.row().classes('w-full items-center'):
                self.FIWorkRootDirInput=ui.input('Work Root Dir (*)', on_change= lambda e:self.uiGetProjPath(e.value)).classes('w-72')
                self.FIWorkRootDirInput.value=self.sim_config_dict['sim_config'].get('work_sim_root_dir',"")
                self.FIWorkRootDirButton = ui.button('Browse', on_click=lambda: self.uiSelectProjDir())

            with ui.row().classes('w-full items-center'):
                self.FIWorkSimDirInput=ui.input('Work Sim Dir (*)', on_change= lambda e:self.GetWorkSimDir(e.value)).classes('w-72')
                self.FIWorkSimDirInput.value=self.sim_config_dict['sim_config'].get('work_sim_dir',"")
                self.FIWorkSimDirButton = ui.button('Browse', on_click=self.SelWorkSimDir)

            with ui.row().classes('w-full items-center'):
                self.FITBBuildDirInput=ui.input('TesteBench Build Dir (*)', on_change= lambda e:self.GetTBBuildDir(e.value)).classes('w-72')
                self.FITBBuildDirInput.value=self.sim_config_dict['sim_config'].get('tb_build_dir',"")
                self.FITBBuildDirButton = ui.button('Browse', on_click=self.SelTBBuildDir)
            ui.separator()
            ui.markdown('##### **TestBench Run Script**').classes('w-100')
            with ui.row().classes('w-full items-center'):
                self.RunScriptInput=ui.input('Path to run.sh (*)', on_change= lambda e:self.GetRunScript(e.value)).classes('w-72')
                self.RunScriptInput.value=self.sim_config_dict['sim_config']['tb_run_info'].get('tb_run_script',"")

                self.RunScriptButton = ui.button('Browse', on_click=self.SelRunScript)

            self.RunArgsInput=ui.input('run.sh args ', on_change= lambda e:self.uiGetRunArgs(e.value)).classes('w-72')
            self.RunTimeoutInput=ui.input('run.sh timeot ', on_change= lambda e:self.uiGetRunTimeout(e.value)).classes('w-72')
            self.RunEnvVarsInput=ui.input('run.sh Env Vars (;) separated ', on_change= lambda e:self.uiGetRunEnvVars(e.value)).classes('w-72')

            ui.markdown('##### **TestBench SDC Check Script**').classes('w-100')
            with ui.row().classes('w-full items-center'):
                self.SDCScriptInput=ui.input('Path to sdc_check.sh (*)', on_change= lambda e:self.GetSDCScript(e.value)).classes('w-72')
                self.SDCScriptInput.value=self.sim_config_dict['sim_config']['tb_sdc_check_info'].get('tb_sdc_check_script',"")
                self.SDCScriptButton = ui.button('Browse', on_click=self.SelSDCScript)

            self.SDCArgsInput=ui.input('sdc_check.sh args ', on_change= lambda e:self.uiGetSDCArgs(e.value)).classes('w-72')
            self.SDCEnvVarsInput=ui.input('sdc_check.sh Env Vars (;) separated ', on_change= lambda e:self.uiGetSDCEnvVars(e.value)).classes('w-72')

            ui.markdown('##### **TestBench TestApp Settings**').classes('w-100')
            with ui.row().classes('w-full items-center'):
                self.uiTestAppDirsTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                self.uiTestAppDirsButton=ui.button('TestApp Inc Directories', on_click=self.uiSelectTestAppDirs)
                
                
            with ui.row().classes('w-full items-center'):
                self.uiTestAppFilesTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                self.uiTestAppFilesButton=ui.button('TesApp Source Files', on_click=self.uiSelectTestAppFiles)
                

            self.TestAppInput=ui.input('TestApp', on_change= lambda e:self.uiGetTestApp(e.value)).classes('w-72')
            self.TestAppArgsInput=ui.input('TestApp args ', on_change= lambda e:self.uiGetTestAppArgs(e.value)).classes('w-72')
            self.TestAppEnvVarsInput=ui.input('TestApp Env Vars (;) separated ', on_change= lambda e:self.uiGetTestAppEnvVars(e.value)).classes('w-72')


            with ui.row().classes('w-full mt-4'):
                ui.label('(*) Required fields').classes('text-sm text-gray-500')
            with ui.row().classes('w-full justify-between'):
                #ui.button('Create Project', on_click=lambda: create_project_callback(create_project_dialog,uiProjMainNameInput,uiProjMainPathInput))
                ui.button('OK', on_click=self._handle_ok)

                ui.button('Cancel', on_click=self.close)

    def uiGetFITasks(self,val):
        self.sim_config_dict['sim_config']['tasks']=int(val)

    def uiGetFIEngines(self,val):
        self.sim_config_dict['sim_config']['engines']=int(val)

    def uiGetFINFaults(self,val):
        self.sim_config_dict['sim_config']['max_num_faults']=int(val)

    def uiGetRunTime(self,val):
        self.sim_config_dict['sim_config']['sim_runtime']=int(val)
    
    def uiGetProjPath(self,path):
        self.tb_path=path

    async def uiSelectProjDir(self):
        home = self.shadowfi_root
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                self.FIWorkRootDirInput.value=project_dir
                self.sim_config_dict['sim_config']['work_sim_root_dir']=project_dir
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')

    def GetWorkSimDir(self,path):
        self.sim_config_dict['sim_config']['work_sim_dir']=path

    async def SelWorkSimDir(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                NewPath=os.path.relpath(project_dir,home)
                self.FIWorkSimDirInput.value=NewPath
                self.sim_config_dict['sim_config']['work_sim_dir']=NewPath
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')

    def GetTBBuildDir(self,path):
        self.sim_config_dict['sim_config']['tb_build_dir']=path

    async def SelTBBuildDir(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                NewPath=os.path.relpath(project_dir,home)
                self.FITBBuildDirInput.value=NewPath
                self.sim_config_dict['sim_config']['tb_build_dir']=NewPath
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')

    def GetRunScript(self,path):
        path=path.replace('/run.sh',"")
        self.sim_config_dict['sim_config']['tb_run_info']['tb_run_script']=f"{path}/run.sh"

    async def SelRunScript(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                NewPath=os.path.relpath(project_dir,home)
                self.RunScriptInput.value=f"{NewPath}/run.sh"
                self.sim_config_dict['sim_config']['tb_run_info']['tb_run_script']=f"{NewPath}/run.sh"
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')


    def uiGetRunArgs(self,val):
        self.sim_config_dict['sim_config']['tb_run_info']['tb_run_args']=val

    def uiGetRunTimeout(self,val):
        self.sim_config_dict['sim_config']['tb_run_info']['tb_run_timeout']=int(val)

    def uiGetRunEnvVars(self,val):
        Items = val.split(';')
        self.sim_config_dict['sim_config']['tb_run_info']['tb_run_env_vars']=Items

    def GetSDCScript(self,path):
        path=path.replace('/sdc_check.sh',"")
        self.sim_config_dict['sim_config']['tb_sdc_check_info']['tb_sdc_check_script']=f"{path}/sdc_check.sh"

    async def SelSDCScript(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=False)
        if result:
            if len(result)!=0:
                project_dir=result[0]
                NewPath=os.path.relpath(project_dir,home)
                self.SDCScriptInput.value=f"{NewPath}/sdc_check.sh"
                self.sim_config_dict['sim_config']['tb_sdc_check_info']['tb_sdc_check_script']=f"{NewPath}/sdc_check.sh"
                ui.notify(f'Project directory selected: {project_dir}') 
        else:
            ui.notify(f'No directory selected')


    def uiGetSDCArgs(self,val):
        self.sim_config_dict['sim_config']['tb_run_info']['tb_sdc_check_args']=val

    def uiGetSDCEnvVars(self,val):
        Items = val.split(';')
        self.sim_config_dict['sim_config']['tb_run_info']['tb_sdc_check_env_vars']=Items

    async def uiSelectTestAppDirs(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=True)
        DirsList = self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_dirs']
        if not isinstance(DirsList,list):
            DirsList = []
        if result:
            if len(result)!=0:
                inc_dirs=result
                for item in inc_dirs: 
                    if item not in DirsList:
                        DirsList.append(os.path.relpath(item,home))
                ui.notify(f'TB dirs selected: {DirsList}') 
        else:
            ui.notify(f'No TB dirs selected')
        self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_dirs']=DirsList
        Directories = [str(pathlib.Path(p.replace(home,"/TestApp_root_dir"))) for p in DirsList]
        nodes_data = build_tree_nodes(Directories)
        self.uiTestAppDirsTree.props['nodes']=nodes_data

    async def uiSelectTestAppFiles(self):
        home = self.sim_config_dict['sim_config']['work_sim_root_dir']
        result = await local_file_picker(home, multiple=True)
        DirsList = self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_files']
        if not isinstance(DirsList,list):
            DirsList = []
        if result:
            if len(result)!=0:
                inc_dirs=result
                for item in inc_dirs: 
                    if item not in DirsList:
                        DirsList.append(os.path.relpath(item,home))
                
                ui.notify(f'TB dirs selected: {DirsList}') 
        else:
            ui.notify(f'No TB dirs selected')
        self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_files']=DirsList
        Directories = [str(pathlib.Path(p.replace(home,"/TestApp_root_dir"))) for p in DirsList]
        nodes_data = build_tree_nodes(Directories)
        self.uiTestAppFilesTree.props['nodes']=nodes_data

    def uiGetTestApp(self,val):
        self.sim_config_dict['sim_config']['tb_test_app_info']['test_app']=val

    def uiGetTestAppArgs(self,val):
        self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_args']=val

    def uiGetTestAppEnvVars(self,val):
        Items = val.split(';')
        self.sim_config_dict['sim_config']['tb_test_app_info']['test_app_env_vars']=Items

    async def _handle_ok(self):
        self.submit(self.sim_config_dict)

