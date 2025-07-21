import random
import myFunctions as mf
import numpy as np
import os
import subprocess

def absolute_error(real,actual):
    eabs=[]
    for i in range(0,len(real)):
        eabs.append(abs(real[i]-actual[i]))
    return eabs

def relative_error(real,actual):
    rerr=[]
    for i in range(0,len(real)):
        if real[i]==0:
            rerr.append(abs(abs((real[i]+1)-actual[i])/(real[i]+1)))
        else:
            rerr.append(abs(abs((real[i])-actual[i])/(real[i])))
    return rerr

print("verifing data in progress.........")

output_sin=mf.read_files("./output_sin.csv")
output_cos=mf.read_files("./output_cos.csv")
output_rsqrt=mf.read_files("./output_rsqrt.csv")
output_log2=mf.read_files("./output_log2.csv")
output_ex2=mf.read_files("./output_ex2.csv")

Tmp_in_oper=[]
Tmp_out_oper=[]
for index in output_sin[:-8]:
    W=index.split(',')
    Tmp_in_oper.append(W[0])
    Tmp_out_oper.append(W[1])

sine_data_in=np.float32(mf.hex2float(Tmp_in_oper))
sine_SFU_result=np.float32(mf.hex2float(Tmp_out_oper))

Tmp_in_oper=[]
Tmp_out_oper=[]
for index in output_cos[:-8]:
    W=index.split(',')
    Tmp_in_oper.append(W[0])
    Tmp_out_oper.append(W[1])

cosine_data_in=np.float32(mf.hex2float(Tmp_in_oper))
cosine_SFU_result=np.float32(mf.hex2float(Tmp_out_oper))

Tmp_in_oper=[]
Tmp_out_oper=[]
for index in output_rsqrt[:-9]:
    W=index.split(',')
    Tmp_in_oper.append(W[0])
    Tmp_out_oper.append(W[1])

rsqrt_data_in=np.float32(mf.hex2float(Tmp_in_oper))
rsqrt_SFU_result=np.float32(mf.hex2float(Tmp_out_oper))

Tmp_in_oper=[]
Tmp_out_oper=[]
for index in output_log2[:-8]:
    W=index.split(',')
    Tmp_in_oper.append(W[0])
    Tmp_out_oper.append(W[1])

log2_data_in=np.float32(mf.hex2float(Tmp_in_oper))
log2_SFU_result=np.float32(mf.hex2float(Tmp_out_oper))

Tmp_in_oper=[]
Tmp_out_oper=[]
for index in output_ex2[:-8]:
    W=index.split(',')
    Tmp_in_oper.append(W[0])
    Tmp_out_oper.append(W[1])

ex2_data_in=np.float32(mf.hex2float(Tmp_in_oper))
ex2_SFU_result=np.float32(mf.hex2float(Tmp_out_oper))


##calculates absolute error
abs_err_sin=absolute_error(np.float32(np.sin(sine_data_in)),sine_SFU_result)
abs_err_cos=absolute_error(np.float32(np.cos(cosine_data_in)),cosine_SFU_result)
abs_err_rsqrt=absolute_error(np.float32(1/np.sqrt(rsqrt_data_in)),rsqrt_SFU_result)
abs_err_log2=absolute_error(np.float32(np.log2(log2_data_in)),log2_SFU_result)
abs_err_ex2=absolute_error(np.float32(2**(ex2_data_in)),ex2_SFU_result)

## calculates relative error
rel_err_sin=relative_error(np.float32(np.sin(sine_data_in)),sine_SFU_result)
rel_err_cos=relative_error(np.float32(np.cos(cosine_data_in)),cosine_SFU_result)
rel_err_rsqrt=relative_error(np.float32(1/np.sqrt(rsqrt_data_in)),rsqrt_SFU_result)
rel_err_log2=relative_error(np.float32(np.log2(log2_data_in)),log2_SFU_result)
rel_err_ex2=relative_error(np.float32(2**(ex2_data_in)),ex2_SFU_result)

Rdata=[]
Rdata.append("sin abs mean error=   "+str(np.mean((abs_err_sin)))+"   Std="+str(np.std((abs_err_sin)))+"  sin rel mean error=   "+str(np.mean((rel_err_sin)))+"   Std="+str(np.std((rel_err_sin))))
Rdata.append("cos abs mean error=   "+str(np.mean((abs_err_cos)))+"   Std="+str(np.std((abs_err_cos)))+"  cos rel mean error=   "+str(np.mean((rel_err_cos)))+"  Std="+str(np.std((rel_err_cos))))
Rdata.append("rsqrt abs mean error= "+str(np.mean((abs_err_rsqrt)))+"   Std="+str(np.std((abs_err_rsqrt)))+"  rsqrt rel mean error= "+str(np.mean((rel_err_rsqrt)))+"  Std="+str(np.std((rel_err_rsqrt))))
Rdata.append("log2 abs mean error=  "+str(np.mean((abs_err_log2)))+"   Std="+str(np.std((abs_err_log2)))+"  log2 rel mean error=  "+str(np.mean((rel_err_log2)))+"  Std="+str(np.std((rel_err_log2))))
Rdata.append("ex2 abs mean error=   "+str(np.mean((abs_err_ex2)))+"   Std="+str(np.std((abs_err_ex2)))+"  ex2 rel mean error=   "+str(np.mean((rel_err_ex2)))+"  Std="+str(np.std((rel_err_ex2))))

mf.write_files("./Error_analysis.txt",Rdata)
print("\r\n\r\n\r\n\r\n\r\n")

print(Rdata[0])
print(Rdata[1])
print(Rdata[2])
print(Rdata[3])
print(Rdata[4])