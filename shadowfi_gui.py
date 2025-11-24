#import argparse
from core import fi_execute, fi_setup, project, elaboration, place_and_route, fi_fpga_exec, fi_fpga_setup
from utils.logger import setup_logger
from utils.config_loader import load_config,save_config, KeyValueAction
from core.shadowfi_utils.utils import (
    create_makefile_tb_sbtr,
    read_verilog_file,
    write_verilog_file,
    write_json,
    read_json,
)
from utils.parsers import CustomArgumenrParser, argparse
import pathlib
import asyncio

import os

import logging


from gui.local_file_picker import local_file_picker
from gui.SimWorkFlowSetup import SimWorkFlowSetup,FaultSimSetup
from nicegui import ui,run,app

import argparse

#os.system('cls' if os.name == 'nt' else 'clear')
os.environ['SHADOWFI_ROOT'] = os.path.dirname(os.path.abspath(__file__))  # export root directory

TEMPLATES_DICT = {
    'design_config': "design_config.yml",
    'emu_config': "emu_config.yml",
    'sim_config': "sim_config.yml",
    'target_modules': "target_modules.yml",
    'tb_config': "tb_config.yml",
}



class Project:
    def __init__(self, name="", path=""):
        self.shadowfi_root=os.environ['SHADOWFI_ROOT']
        self.name = name
        self.path = os.path.join(self.shadowfi_root, "projects") if path=="" else path

        self.t_design_config = load_config(os.path.join(self.shadowfi_root,"gui","config_templates",TEMPLATES_DICT['design_config']))
        self.t_emu_config = load_config(os.path.join(self.shadowfi_root,"gui","config_templates",TEMPLATES_DICT['emu_config']))
        self.t_sim_config = load_config(os.path.join(self.shadowfi_root,"gui","config_templates",TEMPLATES_DICT['sim_config']))
        self.t_target_modules = load_config(os.path.join(self.shadowfi_root,"gui","config_templates",TEMPLATES_DICT['target_modules']))
        self.t_tb_config = load_config(os.path.join(self.shadowfi_root,"gui","config_templates",TEMPLATES_DICT['tb_config']))
        self.file_design_config=""
        self.file_emu_config = ""
        self.file_sim_config = ""
        self.file_target_modules = ""
        self.file_tb_config = ""
        self.tmp_proj_dir=""
        self.config_template=""
        self.config_path=""

project_info = Project()

def uiResetAll(uiObjectsDict:dict):
    project_info=Project()


def uiCheckDialogToOpen(uiObjectsDict:dict):
    if app.storage.tab['uiPressedCreateProjBut']==1:
        uiObjectsDict['create_project_dialog'].open()
        app.storage.tab['uiPressedCreateProjBut']=0
    if app.storage.tab['uiPressedLoadProjBut']==1:
        uiObjectsDict['load_project_dialog'].open()
        app.storage.tab['uiPressedLoadProjBut']=0

def uiOnCreateProjButt(uiObjectsDict:dict):
    #ui.navigate.reload()
    uiResetAll(uiObjectsDict)
    #app.storage.tab['uiPressedCreateProjBut']=1
    uiObjectsDict['create_project_dialog'].open()


async def uiOnLoadProjButt(uiObjectsDict:dict):
    #ui.navigate.reload()
    uiResetAll(uiObjectsDict)
    #app.storage.tab['uiPressedLoadProjBut']=1
    uiObjectsDict['load_project_dialog'].open()
    
async def uiSelectProjDir(ui_projname):
    home = project_info.shadowfi_root
    result = await local_file_picker(home, multiple=False)
    if result:
        if len(result)!=0:
            project_dir=result[0]
            ui_projname.value = project_dir
            project_info.path=project_dir
            ui.notify(f'Project directory selected: {project_dir}') 
    else:
        ui.notify(f'No directory selected')



async def uiSelectDesignDir(uiObjectDict:dict):
    home = project_info.shadowfi_root
    result = await local_file_picker(home, multiple=False)
    if result:
        if len(result)!=0:
            project_dir=result[0]
            uiObjectDict['uiDesignRootInput'].value = project_dir
            project_info.t_design_config['design_config']['design_root_dir']=project_dir
            project_info.t_design_config['design_config']['src_path']=project_dir
            if(project_info.t_design_config['design_config']['design_root_dir']!=""):
                uiObjectDict['uiAddFilesButton'].enable()
                uiObjectDict['uiAddIncDirButton'].enable()
            ui.notify(f'Project directory selected: {project_dir}') 
    else:
        ui.notify(f'No directory selected')



async def uiSelectDesignFiles(uiTreeFiles:ui.tree):
    home = project_info.t_design_config['design_config']['design_root_dir']
    result = await local_file_picker(home, multiple=True)
    FilesList = project_info.t_design_config['design_config']['src_list_files']
    if not isinstance(FilesList,list):
        FilesList = []
    if result:
        if len(result)!=0:
            design_files=result
            for item in design_files: 
                if item not in FilesList:
                    FilesList.append(item)
            project_info.t_design_config['design_config']['src_list_files']=FilesList
            Files = [str(pathlib.Path(p.replace(project_info.design_root_dir,"/design_root_dir"))) for p in FilesList]
            nodes_data = build_tree_nodes(Files)
            uiTreeFiles.props['nodes']=nodes_data
            ui.notify(f'Design files selected: {design_files}') 
    else:
        ui.notify(f'No files selected')

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


def build_tree_components(paths):
    """
    Converts a list of absolute paths into a hierarchical data structure for ui.tree.
    """
    tree_root = {}
    sep = "@"
    inst_sep="->"
    for absolute_path in paths:
        # Use os.sep to split paths correctly for different OS
        [pathinfo,component]=absolute_path.split('->')
        parts = pathinfo.strip(sep).split(sep)
        print(parts)
        current_level = tree_root

        for i, part in enumerate(parts):
            # Create a unique ID for each node
            node_id = "@".join(parts[:i+1])
            node_id = node_id+'->'+component
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


def create_project_callback(uiObjectsDict:dict):
    print(project_info.name,project_info.path)
    if project_info.name=="" or project_info.path=="" or len(project_info.t_design_config['design_config']['src_list_files'])==0 or (project_info.t_design_config['design_config']['top_module'])=="":
        ui.notify(f'Error: Enter the required information (*)', color='negative')
        return
    project_info.tmp_proj_dir=f"{project_info.shadowfi_root}/.tmp-{project_info.name}"
    project_info.file_design_config=os.path.join(project_info.tmp_proj_dir,"design_config.yml")
    os.system(f"mkdir -p {project_info.tmp_proj_dir}")
    save_config(project_info.t_design_config,project_info.file_design_config)
    
    project_info.config_template=os.path.join(project_info.shadowfi_root,"gui","config_templates","project_config.yaml")
    project.create_project(project_info.name, 
                           base_dir=project_info.path,
                           template_config=project_info.config_template,
                           design_config=project_info.file_design_config)
    ui.notify(f'Project created succesfully at : {project_info.path}', color='positive')
    uiObjectsDict['uiProjMainNameInput'].value=project_info.name
    uiObjectsDict['uiProjMainPathInput'].value=os.path.join(project_info.path,project_info.name)
    uiObjectsDict['uiHDLElabButton'].enable()
    project_info.config_path=project.load_project_config(os.path.join(project_info.path,project_info.name))

    uiObjectsDict['create_project_dialog'].close()

async def uiSelectIncDirs(uiObjectDict:dict):
    home = project_info.t_design_config['design_config']['design_root_dir']
    result = await local_file_picker(home, multiple=True)
    DirsList = project_info.t_design_config['design_config']['inc_directories']
    if not isinstance(DirsList,list):
        DirsList = []
    if result:
        if len(result)!=0:
            inc_dirs=result
            for item in inc_dirs: 
                if item not in DirsList:
                    DirsList.append(item)
            
            project_info.t_design_config['design_config']['inc_directories']=DirsList
            Directories = [str(pathlib.Path(p.replace(project_info.design_root_dir,"/design_root_dir"))) for p in DirsList]
            nodes_data = build_tree_nodes(Directories)
            uiObjectDict['uiAddIncDirTree'].props['nodes']=nodes_data
            ui.notify(f'Design files selected: {Directories}') 
    else:
        ui.notify(f'No files selected')


def uiAddParam(uiObjectDict:dict):
    ParamsStr = uiObjectDict['uiAddParamInput'].value
    ParamsList = ParamsStr.split(',')
    ParamsList = [(p.strip()).lstrip() for p in ParamsList]
    project_info.t_design_config['design_config']['module_params']=ParamsList
    uiObjectDict['AddParamsDialog'].close()



def uiGetProjName(name):
    project_info.name=name
    ui.notify(f'Project name set to: {project_info.name}')

def uiGetTopModule(name):
    project_info.t_design_config['design_config']['top_module']=name

def uiGetProjPath(path):
    project_info.path=path

def uiGetDesignRoot(path):
    project_info.design_root_dir=path


def uiLoadProject(uiObjectsDict:dict):
    project_info.config_path=project.load_project_config(project_info.path)
    ProjectInfoDict = load_config(project_info.config_path)
    uiObjectsDict['uiProjMainNameInput'].value=ProjectInfoDict['project']['name']
    uiObjectsDict['uiProjMainPathInput'].value=ProjectInfoDict['project']['root_proj_dir']
    uiObjectsDict['uiHDLElabButton'].enable()
    ui.notify("Project created succesfully",color='positive')
    uiObjectsDict['load_project_dialog'].close()
    project_info.tmp_proj_dir=f"{project_info.shadowfi_root}/.tmp-{ProjectInfoDict['project']['name']}"
    os.system(f"mkdir -p {project_info.tmp_proj_dir}")
    

async def uiStartHDLElaboration(uiObjectsDict:dict):
    config = load_config(project_info.config_path)
    uiObjectsDict['uiHDLESpiner'].visible=True
    uiObjectsDict['uiHDLElabButton'].disable()
    uiObjectsDict['uiMainCreateProjButton'].disable()
    uiObjectsDict['uiMainLoadProjButton'].disable()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, elaboration.elaborate,config)
    uiObjectsDict['uiHDLESpiner'].visible=False
    uiObjectsDict['uiHDLElabButton'].enable()
    uiObjectsDict['uiCmpSelRadio'].enable()
    uiObjectsDict['uiPnRButton'].enable()
    uiObjectsDict['uiMainCreateProjButton'].enable()
    uiObjectsDict['uiMainLoadProjButton'].enable()
    ui.notify("HDL Elaboration finished!")



def uiComponentSelection(uiObjectsDict:dict):
    uiCmpSelRadio = uiObjectsDict['uiCmpSelRadio']
    uiObjectsDict['uiHierSelCard'].visible=False
    if uiCmpSelRadio.value=='Hierarchy':
        uiObjectsDict['uiDesignHierTree'].props['nodes']=[{}]
        config = load_config(project_info.config_path)
        sbtr_config = config.get('project', {}).get('sbtr_config', {})
        design_config = config.get('project', {}).get('design_config', {})
        file_name = os.path.join(sbtr_config['sbtr_dir'], f"{design_config['top_module']}_hierarchy.json")
        module_hierarchy=read_json(file_name)
        instances=place_and_route.get_list_of_instances(module_hierarchy)
        DesignHierPaths = [f"{design_config['top_module']}@{p[0]}->{p[1]}" for p in instances]
        nodes_data=build_tree_components(DesignHierPaths)
        uiObjectsDict['uiHierSelCard'].visible=True
        uiObjectsDict['uiDesignHierTree'].props['nodes']=nodes_data


async def uiGetTickedNodesFromTree(uiObjectsDict:dict):
    config = load_config(project_info.config_path)
    design_config = config.get('project', {}).get('design_config', {})
    NodesTree = uiObjectsDict['uiDesignHierTree']
    target_components = NodesTree._props['ticked']
    if not isinstance(target_components,list):
        target_components=[]

    hier_comp=set()
    targe_mod = set()
    for item in target_components:
        if "->" in item:
            [instance_path, component_name]=item.split('->')
            instance_path=instance_path.replace(f"{design_config['top_module']}","")
            instance_path = instance_path[1:] if instance_path.startswith('@') else instance_path
            hier_comp.add(f"{instance_path}->{component_name}_sbtr")
            targe_mod.add(f"{component_name}")
        else:
            ui.notify("The selected item does not have the correct format <inst_path:comp_name>",color='negative')

    project_info.t_target_modules['component_selection']['hierarchical_component']=list(hier_comp)
    project_info.t_target_modules['component_selection']['target_modules']=list(targe_mod)

    project_info.file_target_modules=os.path.join(project_info.tmp_proj_dir,"target_modules.yml")
    save_config(project_info.t_target_modules,project_info.file_target_modules)


async def uiStartSBTRPnR(uiObjectsDict:dict):
    uiObjectsDict['uiPnRButton'].disable()
    uiObjectsDict['uiPnRSpiner'].visible=True
    config = load_config(project_info.config_path)
    uiCmpSelRadio = uiObjectsDict['uiCmpSelRadio']
    uiFaultModelRadio = uiObjectsDict['uiFaultModelRadio']
    uiFIModeRadio = uiObjectsDict['uiFIModeRadio']

    CmSel=str(uiCmpSelRadio.value).lower()
    if uiFaultModelRadio.value=="Stuck-at":
        FM="S@"
    else:
        FM=uiFaultModelRadio.value
    FSampling = uiFIModeRadio.value

    pnr_args={
        "cmp_sel": CmSel,
        "fault_model":FM,
        "fault_sampling":FSampling,
        "user_cmp_sel": f"{project_info.file_target_modules}",
        "max_sel_cmp": 4
    }
    # Convert the dictionary to an argparse.Namespace object
    args = argparse.Namespace(**pnr_args)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, place_and_route.run_pnr,config,args)
    #uiObjectsDict['uiPnRButton'].enable()
    uiObjectsDict['uiPnRSpiner'].visible=False

async def uiOnWorkflowSetupButton(uiObjectsDict:dict):
    WorkflowOpt=uiObjectsDict['uiWorkFlowSelRadio']
    config = load_config(project_info.config_path)
    if WorkflowOpt.value=="Simulation Setup":
        Spinner = uiObjectsDict['uiWFValidSpinner']
        project_info.t_tb_config=await SimWorkFlowSetup(project_info.shadowfi_root)
        project_info.file_tb_config=os.path.join(project_info.tmp_proj_dir,"tb_config.yml")
        save_config(project_info.t_tb_config,project_info.file_tb_config)
        Spinner.visible=True
        pnr_args={'tb_config':project_info.file_tb_config}
        args = argparse.Namespace(**pnr_args)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, fi_setup.setup_testbench,config,args)
        Spinner.visible=False
    if WorkflowOpt.value=="Emulation Setup":
        pass
    

def uiOnWorkflowSaveButton(uiObjectsDict:dict):
    pass


async def uiOnFICStartButton(uiObjectsDict:dict):
    config = load_config(project_info.config_path)
    Spinner = uiObjectsDict['uiFICStartSpinner']
    Spinner.visible=True

    fsim_exec_args={'hpc':False,
                'fsim_config':project_info.file_sim_config}
    args = argparse.Namespace(**fsim_exec_args)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, fi_execute.execute_fault_injection,config,args)

    Spinner.visible=False


async def uiFICSetup(uiObjectsDict:dict):
    uiFICSelRadio=uiObjectsDict['uiFICSelRadio']
    uiFICNumFaultsInput=uiObjectsDict['uiFICNumFaultsInput']
    uiFICTimeoutInput=uiObjectsDict['uiFICTimeoutInput']
    config = load_config(project_info.config_path)
    if uiFICSelRadio.value=="Standalone":
        Spinner = uiObjectsDict['uiFICStartSpinner']
        Spinner.visible=True
        project_info.t_sim_config = await FaultSimSetup(project_info.config_path)
        project_info.file_sim_config=os.path.join(project_info.tmp_proj_dir,"sim_config.yml")
        save_config(project_info.t_sim_config,project_info.file_sim_config)
        uiFICNumFaultsInput.value=project_info.t_sim_config['sim_config']['max_num_faults']
        uiFICTimeoutInput.value=project_info.t_sim_config['sim_config']['tb_run_info']['tb_run_timeout']
        fsim_args={'fsim_config':project_info.file_sim_config,
                  'noset_run_scripts':True}
        args = argparse.Namespace(**fsim_args)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, fi_setup.setup_fault_injection,config,args)

        Spinner.visible=False

def uiFICSetNumFaults(uiObjectsDict:dict):
    uiFICNumFaultsInput=uiObjectsDict['uiFICNumFaultsInput']
    config = load_config(project_info.config_path)
    config['project']['sim_config']['max_num_faults']=int(uiFICNumFaultsInput.value)
    save_config(config,project_info.config_path)


@ui.page('/')
async def index():
    uiObjectsDict = {}
    await ui.context.client.connected()

    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-center'):
        ui.markdown('## **ShadowFi GUI Mode**')

    """Simulation workflow setup"""
    with ui.dialog() as SimWorkFlowSetupDiag, ui.card():
            uiObjectsDict['SimWorkFlowSetupDiag']=SimWorkFlowSetupDiag
            ui.markdown('#### **Simulation Workflow Setup**').classes('w-100')
            ui.button("close",on_click=SimWorkFlowSetupDiag.close)
            

    """Add module parameters"""
    with ui.dialog() as AddParamsDialog, ui.card():
            uiObjectsDict['AddParamsDialog']=AddParamsDialog
            uiAddParamInput = ui.input(label='Module Params', placeholder='Enter comma separated (e.g., N=10, M=25, PARAM=HELLO)').classes('w-72')
            uiObjectsDict['uiAddParamInput']=uiAddParamInput
            with ui.row().classes('w-full justify-between'):
                ui.button("Add",on_click=lambda:uiAddParam(uiObjectsDict))
                ui.button("Close",on_click=AddParamsDialog.close)
                
    """Create Project Dialog"""
    with ui.dialog() as create_project_dialog, ui.card():
            uiObjectsDict['create_project_dialog']=create_project_dialog
            ui.markdown('#### **New ShadowFi Project**').classes('w-100')
            uiProjNameInput=ui.input(label='Project Name (*)', placeholder='Enter project name here...',on_change=lambda e: uiGetProjName(e.value) ).classes('w-72')
            uiObjectsDict['uiProjNameInput']=uiProjNameInput
            with ui.row().classes('w-full items-center'):
                uiProjPathInput=ui.input('Select Project Path', on_change= lambda e:uiGetProjPath(e.value)).classes('w-72')
                uiProjPathInput.value=project_info.path
                uiProjPathButton = ui.button('Browse', on_click=lambda: uiSelectProjDir(uiProjPathInput))
                uiObjectsDict['uiProjPathInput']=uiProjPathInput
                uiObjectsDict['uiProjPathButton']=uiProjPathButton
                
            ui.separator()
            ui.markdown('##### **Design Settings**')

            with ui.row().classes('w-full items-center'):
                uiDesignRootInput=ui.input('Select Design Root (*)', on_change= lambda e:uiGetDesignRoot(e.value)).classes('w-72')
                uiDesignRootButton = ui.button('Browse', on_click=lambda: uiSelectDesignDir(uiObjectsDict))
                uiObjectsDict['uiDesignRootInput']=uiDesignRootInput
                uiObjectsDict['uiDesignRootButton']=uiDesignRootButton

            #ui.label("Design Files (*)")
            with ui.row().classes('w-full mt-2'): 
                uiAddFilesTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                uiAddFilesButton=ui.button('Add Design Files', on_click=lambda:uiSelectDesignFiles(uiAddFilesTree))
                uiAddFilesButton.disable()
                uiObjectsDict['uiAddFilesTree']=uiAddFilesTree
                uiObjectsDict['uiAddFilesButton']=uiAddFilesButton
            
            with ui.row().classes('w-full mt-2'): 
                uiAddIncDirTree = ui.tree({'id':0, 'label':'.', 'children':{}},node_key='id').classes('w-72')
                uiAddIncDirButton=ui.button('Add Include Directories', on_click=lambda:uiSelectIncDirs(uiObjectsDict))
                uiAddIncDirButton.disable()
                uiObjectsDict['uiAddIncDirTree']=uiAddIncDirTree
                uiObjectsDict['uiAddIncDirButton']=uiAddIncDirButton

            ui.input(label='Top module Name (*)', placeholder='Enter the name of the top module...',on_change=lambda e: uiGetTopModule(e.value) ).classes('w-72')
            with ui.row().classes('w-full mt-2'):
                uiAddParamButton = ui.button('Add Params', on_click=AddParamsDialog.open)
                uiObjectsDict['uiAddParamButton']=uiAddParamButton

            with ui.row().classes('w-full mt-4'):
                ui.label('(*) Required fields').classes('text-sm text-gray-500')
            with ui.row().classes('w-full justify-between'):
                #ui.button('Create Project', on_click=lambda: create_project_callback(create_project_dialog,uiProjMainNameInput,uiProjMainPathInput))
                ui.button('Create Project', on_click=lambda: create_project_callback(uiObjectsDict))

                ui.button('Cancel', on_click=create_project_dialog.close)
    
    """Load Project Dialog"""
    with ui.dialog() as load_project_dialog, ui.card():
            uiObjectsDict['load_project_dialog']=load_project_dialog
            ui.markdown('### **Load An Existing Project**').classes('w-100')
            with ui.row().classes('w-full items-center'):
                uiProjLoadPathInput=ui.input('Select Project Path', on_change= lambda e:uiGetProjPath(e.value)).classes('w-72')
                uiProjLoadPathInput.value=project_info.path
                uiProjLoadPathButton = ui.button('Browse', on_click=lambda: uiSelectProjDir(uiProjLoadPathInput))
                uiObjectsDict['uiProjLoadPathInput']=uiProjLoadPathInput
                uiObjectsDict['uiProjLoadPathButton']=uiProjLoadPathButton

            with ui.row().classes('w-full justify-between'):
                ui.button('Open Project', on_click=lambda: uiLoadProject(uiObjectsDict))
                ui.button('Cancel', on_click=load_project_dialog.close)
    

    
    """Create/Load Project section"""
    with ui.card().classes('w-full items-center'):
        ui.markdown('#### **1. Create/Load  project**') 
        with ui.row().classes('w-full justify-center'):
            #ui.label('Project Name:')
            uiProjMainNameInput=ui.input(label='Project Name:', placeholder='Enter project name here...').props("readonly").classes('w-50')
            uiObjectsDict['uiProjMainNameInput']=uiProjMainNameInput
            #ui.label('Project Path:')
            uiProjMainPathInput=ui.input(label='Project Path:', placeholder='Enter project name here...').props("readonly").classes('w-200')
            uiObjectsDict['uiProjMainPathInput']=uiProjMainPathInput

            #ui.label('Shadowfi root path:')
            ui_shadowfi_root=ui.input(label='Shadowfi root dir:', placeholder='Enter project name here...').props("readonly").classes('w-110')
            ui_shadowfi_root.value=project_info.shadowfi_root

        with ui.row().classes('w-full justify-center'):
            uiMainCreateProjButton = ui.button('Create project', on_click=lambda: uiOnCreateProjButt(uiObjectsDict))
            uiMainLoadProjButton = ui.button('Load project', on_click=lambda:(uiOnLoadProjButt(uiObjectsDict)))
            uiObjectsDict['uiMainCreateProjButton']=uiMainCreateProjButton
            uiObjectsDict['uiMainLoadProjButton']=uiMainLoadProjButton

    """HDL Elaboration section"""
    with ui.card().classes('w-full items-center'):
        ui.markdown('#### **2. HDL elaboration**') 
        with ui.row():
            uiHDLElabButton=ui.button('Start', on_click= lambda : uiStartHDLElaboration(uiObjectsDict))
            uiHDLElabButton.disable()
            uiHDLESpiner = ui.spinner(size='lg')
            uiHDLESpiner.visible=False
            uiObjectsDict['uiHDLElabButton']=uiHDLElabButton
            uiObjectsDict['uiHDLESpiner']=uiHDLESpiner

    """SBTR Place & Route section"""
    with ui.card().classes('w-full items-center'):
        ui.markdown('#### **3. SBTR Place & Route**') 
        with ui.row():
            with ui.card():
                ui.label("Component Selection")
                uiCmpSelRadio = ui.radio(['Random', 'Top', 'Hierarchy'], value='Random', on_change=lambda:uiComponentSelection(uiObjectsDict))
                uiCmpSelRadio.disable()
                uiObjectsDict['uiCmpSelRadio']=uiCmpSelRadio
            with ui.card() as uiHierSelCard:
                uiHierSelCard.visible=False
                ui.label("Select the target components")
                uiDesignHierTree = ui.tree([{}],node_key='id',tick_strategy='strict',on_tick=lambda : uiGetTickedNodesFromTree(uiObjectsDict))
                uiObjectsDict['uiDesignHierTree']=uiDesignHierTree
                uiObjectsDict['uiHierSelCard']=uiHierSelCard
                #uiDesignHierTree
            with ui.card():
                ui.label("Fault Model")
                uiFaultModelRadio = ui.radio(['Stuck-at', 'SET', 'SEU', "MEU"], value='Stuck-at')
                uiObjectsDict['uiFaultModelRadio']=uiFaultModelRadio
            with ui.card():
                ui.label("Fault Injection")
                uiFIModeRadio = ui.radio(['Full', 'Statistical'], value='Full')
                uiObjectsDict['uiFIModeRadio']=uiFIModeRadio
        with ui.row():
            uiPnRButton=ui.button('Start SBTR PnR', on_click= lambda : uiStartSBTRPnR(uiObjectsDict))
            uiPnRSpiner = ui.spinner(size='lg')
        uiPnRSpiner.visible=False
        uiObjectsDict['uiPnRButton']=uiPnRButton
        uiObjectsDict['uiPnRSpiner']=uiPnRSpiner
        uiPnRButton.disable()

    """Fault Injection Setup Section"""
    with ui.card().classes('w-full items-center'):
        ui.markdown('#### **4. Fault injection Setup**') 
        with ui.row():
            with ui.card():
                ui.label("Setup Type")
                uiWorkFlowSelRadio = ui.radio(['Simulation Setup', 'Emulation Setup'], value='Simulation Setup')
                uiObjectsDict['uiWorkFlowSelRadio']=uiWorkFlowSelRadio
            with ui.card():
                ui.label("Testbench Setup")
                uiTBConfigText=ui.textarea("Configuration",placeholder="Configure testbench parameters...")
                uiObjectsDict['uiTBConfigText']=uiTBConfigText
        with ui.row():
            uiWorkFlowSetBut = ui.button("Validate Setup",on_click=lambda:uiOnWorkflowSetupButton(uiObjectsDict))
            uiWorkFlowSaveBut = ui.button("Save configuration",on_click=lambda:uiOnWorkflowSaveButton(uiObjectsDict))
            uiWFValidSpinner = ui.spinner(size='lg')
            uiWFValidSpinner.visible=False
            uiObjectsDict['uiWorkFlowSetBut']=uiWorkFlowSetBut
            uiObjectsDict['uiWFValidSpinner']=uiWFValidSpinner
            uiObjectsDict['uiWorkFlowSaveBut']=uiWorkFlowSaveBut

    """Fault Injection Campaign execution"""
    with ui.card().classes('w-full items-center'):
        ui.markdown('#### **5. Fault injection Campaign**') 
        with ui.row():
            with ui.card():
                ui.label("Campaign Type")
                uiFICSelRadio = ui.radio(['Standalone', 'HPC'], value='Standalone', on_change=lambda:uiFICSetup(uiObjectsDict))
                uiObjectsDict['uiFICSelRadio']=uiFICSelRadio
            with ui.card():
                ui.label("Campaign Settings")
                uiFICNumFaultsInput = ui.input('Number of Faults', on_change=lambda:uiFICSetNumFaults(uiObjectsDict))
                uiFICTimeoutInput = ui.input('Timeout (seconds)')
                uiObjectsDict['uiFICNumFaultsInput']=uiFICNumFaultsInput
                uiObjectsDict['uiFICTimeoutInput']=uiFICTimeoutInput

        with ui.row():
            uiFICStartBut = ui.button("Start Campaign",on_click=lambda:uiOnFICStartButton(uiObjectsDict))
            uiFICScheduleBut = ui.button("Schedule Campaign")
            uiFICPreviewBut = ui.button("Preview Configuration")
            uiFICStartSpinner = ui.spinner(size='lg')
            uiFICStartSpinner.visible=False
            uiFICScheduleBut.disable()
            uiFICPreviewBut.disable()
            uiWFValidSpinner.visible=False
            uiObjectsDict['uiFICStartBut']=uiFICStartBut
            uiObjectsDict['uiFICScheduleBut']=uiFICScheduleBut
            uiObjectsDict['uiFICPreviewBut']=uiFICPreviewBut
            uiObjectsDict['uiFICStartSpinner']=uiFICStartSpinner

    app.storage.tab['uiPressedCreateProjBut'] = app.storage.tab.get('uiPressedCreateProjBut', 0)
    app.storage.tab['uiPressedLoadProjBut'] = app.storage.tab.get('uiPressedLoadProjBut', 0)

    #uiCheckDialogToOpen(uiObjectsDict)

if __name__ in {"__main__", "__mp_main__"}:
    #ui.run(host="127.0.0.1",port=8001)
    #os.environ['SHADOWFI_ROOT'] = os.path.dirname(os.path.abspath(__file__))  # export root directory
    setup_logger()
    logging.basicConfig(level=logging.INFO)
    ui.run(favicon="./doc/SHADOWFI-logo.ico", title="ShadowFI",
        uvicorn_reload_dirs='./gui')
