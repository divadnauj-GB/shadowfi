
from fpga_init import FPGA_cluster
import ipyparallel as ipp
import numpy as np
from PIL import Image
import math
import time

dview = FPGA_cluster.rc[:]
with dview.sync_imports():
    import os
    from struct import unpack
    from comblock import Comblock



@dview.remote(block=True)
def sim_cb(image):
    cb0 = Comblock(0)
    
    def reset_SVC(cb):
        cb.write_reg(0,0)  # Reset the accelerator and clear the Comblock FIFO
        cb.write_reg(0,0xffffffff)  # Release reset 
    
    def reset_fifo_in_out(cb):
        cb.fifo_in_clear()
        cb.fifo_out_clear()

    def read_check_fifo_output(cb,list_inout):
        rd_fl= cb.fifo_in_elements()
        if rd_fl!=0:
            list_inout.append(cb.read_fifo(rd_fl))
        (data, elements, bit_over_flow, bit_almost_full, bit_full)=cb.fifo_out_status()
        return(elements, bit_almost_full)

    Read_fifo=[]
    cnt=0
    b=0;
    e=0
    t=len(image)
    try:
        reset_SVC(cb0)
        reset_fifo_in_out(cb0)
        for pixels in image:
            (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
            while(bit_almost_full):
                (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
            b=e
            e=b+(1024-elements)
            if e<t and b<t:
                cb0.write_fifo(image[b:e])
            elif b<t and e>=t:
                cb0.write_fifo(image[b:t])
            else:
                (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                break
    finally:
        print("got here")
        
    return Read_fifo


@dview.remote(block=True)
def fi_config(fault_descriptor):
    listd=[]
    cb1 = Comblock(1)
    cb1.write_reg(0,0xAAAA)
    listd.append(cb1.read_reg(0))

    for element in fault_descriptor:
        cb1.write_reg(0,element)
        listd.append(cb1.read_reg(0))
    return(listd)


def main():    
    D=64
    Wc=7
    Wh=13
    M=450
    
    start_time = time.time()    
    image="Cones"
    
    Left_image = np.array(Image.open(f"./dataset/{image}L.png").convert('L'))
    Right_image = np.array(Image.open(f"./dataset/{image}R.png").convert('L'))
    
    im_shape=Left_image.shape
    if len(im_shape)<3:
        (N_filas, N_columnas)=im_shape
        num_channels = 0
    else:
        (N_filas, N_columnas, num_channels)=im_shape
    
    print(im_shape)
    
    concat_images = []

    EN=1
    
    for i in range(0,N_filas):
        for j in range(0,M):
            if j<N_columnas:
                if num_channels!=0:
                    comp_pixel = (int(EN)<<16) | (int(Right_image[(i,j,0)])<<8) | int(Left_image[(i,j,0)])
                    concat_images.append(comp_pixel)
                else:
                    comp_pixel = (int(EN)<<16) | (int(Right_image[(i,j)])<<8) | int(Left_image[(i,j)])
                    concat_images.append(comp_pixel)
            else:
                concat_images.append((int(EN)<<16) | 0)
                
        
    for i in range(0,30*M): #(10*N_columnas+N_columnas*N_filas):(10*N_columnas+N_columnas*N_filas+10*N_columnas)
        concat_images.append((int(EN)<<16) | 0)
    #print(concat_images)
    
    latency=math.floor(((M+1)*(Wc+Wh+2))/2)-2*M+math.floor(math.log2(Wc*Wc/2))+2*D+11
    
    for idx in range(2):
        start_time = time.time()
        resp = sim_cb(concat_images) # Call the accelerator operation
        print("--- %s seconds ---" % (time.time() - start_time))
    Output_image=np.zeros((N_filas, M, 3))
    
    flat_list = []
    for xs in resp:
        for xx in xs:
            for x in xx:
                flat_list.append(x)
    csv_out=[]
    i=0
    j=0
    for k in range(0,len(flat_list)):
        tmp=flat_list[k]
        valid_pixel = ((tmp & 0x80)>>7)
        val=tmp & 0x7f
        if valid_pixel==1:
            Output_image[(i,j,0)]=(val)
            Output_image[(i,j,1)]=(val)
            Output_image[(i,j,2)]=(val)
            csv_out.append(val)
            j=j+1
            if j==M:
                j=0
                i=i+1
                if i==N_filas:
                    i=N_filas-1
    print(Output_image.max())
    
    Output_image[Output_image>=64]=0
    result=Output_image*255/(Output_image.max())
    output_file=result.astype(np.uint8)
    im = Image.fromarray(output_file, mode="RGB")
    im.save(f"Disparity_map_FPGA_{idx}.png")
    print("done")
    print("--- %s seconds ---" % (time.time() - start_time))
    with open(f"Disparity_file_{idx}.csv","w") as fileo:
        for item in csv_out:
            fileo.write(f"{item}\n")

    start_time = time.time()
    res=fi_config(csv_out)
    print(len(csv_out))
    print("--- %s seconds ---" % (time.time() - start_time))
    
    FPGA_cluster.reboot_cluster()

if __name__=='__main__':
    main()