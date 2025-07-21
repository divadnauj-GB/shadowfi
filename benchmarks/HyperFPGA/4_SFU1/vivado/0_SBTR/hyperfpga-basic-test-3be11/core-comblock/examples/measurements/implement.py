"""Implementation of the block design to get measurements."""

import logging

from fpga.project import Project

logging.basicConfig()
logging.getLogger('fpga.project').level = logging.DEBUG

prj = Project('vivado')
prj.set_part('xc7z020clg484-1')

prj.add_files('../../src/helpers/fifo_loop.vhdl')
prj.add_include('../../src')
prj.add_design('zed.tcl')

prj.add_postimp_cmd('report_utilization -hierarchical -file utilization.rpt')

try:
    prj.generate(to_task='imp')
except Exception as e:
    logging.warning('{} ({})'.format(type(e).__name__, e))
