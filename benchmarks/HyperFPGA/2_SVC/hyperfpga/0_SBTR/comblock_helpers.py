from fpga_init import FPGA_cluster

dview = FPGA_cluster.rc[:]
with dview.sync_imports():
    import os
    from struct import unpack
    from comblock import Comblock
     
@dview.remote(block=True)
        
def sim_cb(image):
    cb0 = Comblock(0)

    Read_fifo=[]
    cnt=0
    try:
        cb0.write_reg(0,0)  # Reset the accelerator and clear the Comblock FIFO
        cb0.write_reg(0,0xffffffff)  # Release reset       
        for pixels in image:
            cb0.write_fifo(pixels)
            Read_fifo.append(cb0.read_fifo())
    finally:
        cb0.close()
        
    return Read_fifo
