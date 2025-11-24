#!/usr/bin/env python3
from gui.local_file_picker import local_file_picker
from gui.SimWorkFlowSetup import SimWorkFlowSetup, FaultSimSetup

from nicegui import ui


async def pick_file() -> None:
    result = await FaultSimSetup()
    ui.notify(f'You chose {result}')


@ui.page('/')
def index():
    ui.button('Choose file', on_click=pick_file, icon='folder')


ui.run()