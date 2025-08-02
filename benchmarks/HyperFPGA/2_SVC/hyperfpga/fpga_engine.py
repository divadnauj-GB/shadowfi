import os
from PIL import Image
import numpy as np
import sys
import json

from core.hyperfpga.comblock.comblock import *


class fpga_engine():
    FILENAME="values_dot_product.csv"
    DEFAULWORKPATH="~/work"
    def __init__(self):
        self.load_result_struct = {'data':[]}
        self.input_run_struct = {'data':[]}
        self.run_out_struct = {'resp':[]}
        self.N_filas = 0
        self.N_columnas = 0  
        self.num_channels = 0

    def load_test_data(self, input_args={}):
        data_set_work_dir=input_args.get('work_dir',self.DEFAULWORKPATH)
        image=input_args.get('input_image','Cones')
        
        stereo_image_left = f"{os.path.abspath(data_set_work_dir)}/dataset/{image}L.png"
        stereo_image_right = f"{os.path.abspath(data_set_work_dir)}/dataset/{image}R.png"
        
        D=64
        Wc=7
        Wh=13
        M=450
        
        Left_image = np.array(Image.open(stereo_image_left).convert('L'))
        Right_image = np.array(Image.open(stereo_image_right).convert('L'))
        
        im_shape=Left_image.shape
        if len(im_shape)<3:
            (self.N_filas, self.N_columnas)=im_shape
            self.num_channels = 0
        else:
            (self.N_filas, self.N_columnas, self.num_channels)=im_shape
        
        print(im_shape)
        
        concat_images = []

        EN=1
        
        for i in range(0,self.N_filas):
            for j in range(0,M):
                if j<self.N_columnas:
                    if self.num_channels!=0:
                        comp_pixel = (int(EN)<<16) | (int(Right_image[(i,j,0)])<<8) | int(Left_image[(i,j,0)])
                        concat_images.append(comp_pixel)
                    else:
                        comp_pixel = (int(EN)<<16) | (int(Right_image[(i,j)])<<8) | int(Left_image[(i,j)])
                        concat_images.append(comp_pixel)
                else:
                    concat_images.append((int(EN)<<16) | 0)
                    
            
        for i in range(0,30*M): #(10*N_columnas+N_columnas*N_filas):(10*N_columnas+N_columnas*N_filas+10*N_columnas)
            concat_images.append((int(EN)<<16) | 0)
       
        self.load_result_struct['data']=concat_images
        return(self.load_result_struct)

    def write_result(self,write_args={},write_data={}):
        mode = write_args.get('mode','golden')
        work_dir = write_args.get('work_dir',"~/work")
        resp = write_data.get('resp',[])
        
        D=64
        Wc=7
        Wh=13
        M=450
        Output_image=np.zeros((self.N_filas, M, 3))
        
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
                    if i==self.N_filas:
                        i=self.N_filas-1
        
        Output_image[Output_image>=64]=0
        result=Output_image*255/(Output_image.max())
        output_file=result.astype(np.uint8)
        im = Image.fromarray(output_file, mode="RGB")
        path_to_save_png = os.path.join(os.path.abspath(work_dir), f"Disparity_map_FPGA_{mode}.png")
        path_to_save_csv = os.path.join(os.path.abspath(work_dir), f"Disparity_map_FPGA_{mode}.csv")
        im.save(path_to_save_png)
        with open(path_to_save_csv,"w") as fileo:
            for item in csv_out:
                fileo.write(f"{item}\n")


    def run(self,input_args={}):
        self.input_run_struct = input_args
        image = self.input_run_struct.get('data',[])
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
        b=0
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
        self.run_out_struct['resp']=Read_fifo
        return (self.run_out_struct)


    def sdc_check(self,results, golden):
        """sdc_check
        Args:
            results (dict): Dictionary with the results 
            golden (dict): Dictionary with the golden results

        Returns:
            str: return an string indicating whether the inputs match
        """
        if results != golden:
            result = "SDC"
        else:
            result = "Masked"
        return result