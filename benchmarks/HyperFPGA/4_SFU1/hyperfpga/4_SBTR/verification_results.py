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

output_result=mf.read_files("./output_dot_product.csv")


sim_results=output_result[::2]
golden_results=output_result[1::2]


sim_results_float=[]
golden_results_float=[]
for index in sim_results:
    values=index.split(',')
    nmm = []
    for item in values:
        nmm.append(np.float32(mf.hex_to_float(item)))
    sim_results_float.append(nmm)

for index in golden_results:
    values=index.split(',')
    nmm = []
    for item in values:
        nmm.append(np.float32(mf.hex_to_float(item)))
    golden_results_float.append(nmm)


abs_error_results = []
rel_error_results = []
for i,val in enumerate(sim_results_float):
    g_mm = golden_results_float[i]
    abs_err_tot = 0
    rel_err_tot = 0
    for j,v2 in enumerate(val):
        g_item = g_mm[j]
        abs_err = abs(v2 - g_item)
        rel_err = abs(abs((g_item)-v2)/(g_item))
        abs_err_tot += abs_err
        rel_err_tot += rel_err  
    abs_err_tot = abs_err_tot / len(val)
    rel_err_tot = rel_err_tot / len(val)
    abs_error_results.append(abs_err_tot)
    rel_error_results.append(rel_err_tot)

Rdata=[]
Rdata.append("sin abs mean error=   "+str(np.mean((abs_error_results)))+"   Std="+str(np.std((abs_error_results)))+"  sin rel mean error=   "+str(np.mean((rel_error_results)))+"   Std="+str(np.std((rel_error_results))))

mf.write_files("./Error_analysis.txt",Rdata)
print("\r\n\r\n\r\n\r\n\r\n")

print(Rdata[0])