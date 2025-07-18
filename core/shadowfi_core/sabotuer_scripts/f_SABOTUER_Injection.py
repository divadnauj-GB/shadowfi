from .class_wire_extraction import WireInfo
from .f_define_new_wire import define_new_wire
from .f_find_wire_name import find_wire_name
from .f_insert_sabouter import insert_instances
from .f_create_detailed_report import create_detailed_report
import shutil
import math
import re

def module_in_one_line(file_path):
    with open(file_path, 'r') as file:
        verilog_code = file.read()
    signals = []
    #print(verilog_code)
    # Regular expression to match always blocks with posedge/negedge sensitivity list
    #always_pattern = re.compile(r'module\s+[^\s*]\s*\(?(.*?)\)?\s*\((.*\s*)\);$', re.DOTALL)
    #always_pattern = re.compile(r'[^\n\s]*(module)\s+(\S+)\s*\((.*[^\n\s]*\n*.*\s*)\);')
    #always_pattern = re.compile(r'[^\n\s]*module\s+\S+\s+#\(.*[^\n\s]*\n*.*\s*\)\s*\(.*[^\n\s]*\n*.*\s*\);|[^\n\s]*module\s+\S+\s*\(.*[^\n\s]*\n*.*\s*\);')
    always_pattern = re.compile(r'[^\n\s]*module\s+[^\s]+\s*#?\s*?\(?[^)]+?\)?\s*\([^)]+\);', re.DOTALL)
    matches = always_pattern.findall(verilog_code)    
    if matches:
        for match in matches:
            verilog_code=verilog_code.replace(match,match.replace("\n",""))
        with open(file_path,"w") as fp:
            fp.write(verilog_code)


def inject_sabotuer(i_file, module):
    module_in_one_line(i_file)
    wire_list = []          # holds wire names and their bit number
    temp_wire_list = []     # holds new temporary wire names and their number of bits
    input_list = []         # list for input signals

# WRITE YOUR FILENAMES HERE (MODIFY ACCORDING TO YOUR DESIGN):
    filename = i_file                                    # the netlist
    new_filename = i_file.replace(".v", "_sbtr.v")        # output: new netlist

# read line by line and save wire and input names with their number of bits into the list:
    lineNum = 0
    with open(filename, 'r') as file:
        for line_design in file:
            lineNum += 1
            line_info = WireInfo(line_design)
            if line_info.type:
                if 'wire' in line_info.type:        # get signals defined as wire
                    #wire_info = WireInfo(line_design)         # send to class and get wire name and number of bits
                    line_info.lineNum = lineNum
                    wire_list.append(line_info)                       # append the list
                elif 'input' in line_info.type:    # get signals defined as input
                    #input_info = WireInfo(line_design)        # send to class and get input name and number of bits
                    input_list.append(line_info)                     # append the list

    file.close()

    # delete input signals from the wire list. input signals will not be used for new signal definitions
    for x in input_list:
        for y in wire_list:
            if x.get_name() == y.get_name():
                wire_list.remove(y)
   
    for x in wire_list:
        print(f"Name: {x.get_name()} - Number of Bits: {x.get_numBit()}")

    # send each wire to the function to create new wire definitions
    for w in wire_list:
        new_wire_info = define_new_wire(w)
        temp_wire_list.append(new_wire_info)    # save them in a new list

    total_enables = 0   # counts total number of bits
    index = 0           # index number for the list
    number_of_super_sabouter = 0    # needed when inserting sabouters. sabouter-1, sabouter-2...
    # print to see wires and their new definitions
    for x in wire_list:
    #    print(f"Name: {x.get_name()} - Number of Bits: {x.get_numBit()}")
    #    print(f"New Definition: {temp_wire_list[index]}")
        total_enables = total_enables + x.get_numBit()  
        index = index + 1
        number_of_super_sabouter = number_of_super_sabouter + 1

    # copy the original file:
    shutil.copy(filename,new_filename)

    with open(new_filename, 'r') as file:
        lines = file.readlines()    #  returns the contents of the entire file 

    # insert new wires and _ace wire names after "assign"
    break_line=""
    with open(new_filename, 'w') as file:
        for idx,line in enumerate(lines):                                       # insert my new temporary wires
            if 'module' in line and 'endmodule' not in line:           # Check if the current line contains 'module'
                file.write(line)
                if ";" not in line:                    
                    file.write(lines[idx+1])
                    break_line=lines[idx+1]
                file.writelines(temp_wire_list)                        # Insert new lines after the line containing 'module'
            elif 'assign' in line:                                     
                wire_name_assign = find_wire_name(line)
                if "\\" in wire_name_assign:
                    replace_wire_with = "\\temp_" + wire_name_assign.replace("\\","")         # exp: replace "_000_" with "temp__000_"
                else:
                    replace_wire_with = "temp_" + wire_name_assign.replace("\\","_")         # exp: replace "_000_" with "temp__000_"
                line_parts = line.split("=")
                new_line = line_parts[0].replace(wire_name_assign, replace_wire_with)+" = "+line_parts[1]  
                file.write(new_line)          
            else:
                if break_line!=line:
                    file.write(line)
    file.close()

    # insert components before "endmodule":
    # find line number for "endmodule"
    with open(new_filename, 'r') as file:
        lines = file.readlines()    #  returns the contents of the entire file 

    endmodule_line_number = None
    for i, line in enumerate(lines):
        if 'endmodule' in line:
            endmodule_line_number = i   # find line number containing "endmodule". with that i will insert components before endmodule
            break
    
    numBit_SS = math.floor(math.log2(number_of_super_sabouter)) + 1
    WIDTH = total_enables + 2
    COMPONENTS1 = insert_instances(wire_list, "i_TFEn", "EN_CTRL", WIDTH)

    new_lines = lines[:endmodule_line_number]  + COMPONENTS1 + lines[endmodule_line_number:]

    with open(new_filename, 'w') as file:
        file.writelines(new_lines)
    file.close()

    # insert new ports for inputs and outputs
    new_ports       = ", i_FI_CONTROL_PORT, i_SI, o_SI"
    parameter       = f" #(parameter WIDTH_SR = {WIDTH})"
    def_si          =  "  input i_SI;\n"
    def_new_port    =  "  input [3:0] i_FI_CONTROL_PORT;\n"        # control signals definition (CLK,  RST, TFEn and EN_SR)
    def_o_si        =  "  output o_SI;\n"                       # the only output controled by Fault Injection framework
    def_wire        = f"  wire [WIDTH_SR-1:0] o_SR;\n"
    assign_o_SI     =  "  assign o_SI = o_SR[0];\n"             # enable signals which will be shifted in the shift register


    with open(new_filename, 'r') as file:
        lines = file.readlines()
    with open(new_filename, 'w') as file:
        new_file_lines=[]
        break_line=""
        for idx,line in enumerate(lines):
            if 'module' in line and 'endmodule' not in line:
                x = line.find("(")
                str1 = line[:x] + parameter + line[x:]
                if ";" in str1:
                    y = str1.find(";")
                    new_line = str1[:y-1] + new_ports + str1[y-1:]                    
                else:
                    y = str1.find("\n")
                    new_line = str1[:y] + new_ports + str1[y:]
                    break_line=lines[idx+1]
                file.write(new_line)
                file.write(break_line)                                
                file.write(def_si)
                file.write(def_new_port)
                file.write(def_o_si)
                file.write(def_wire)
                file.write(assign_o_SI)
            else:
                if break_line!=line:
                    file.write(line)
            
    file.close()

    total = total_enables + 2
    print("Total number of bits for shift register:")
    print(f"[Enable Signals ({total_enables})] + [Control (2)] = {total}")

    print("Super Sabouters' lengths respectively (0 to N):")
    for x in wire_list:      
        print(x.get_numBit(), end=' ')

    print("\nNumber of Super Sabouter:", number_of_super_sabouter)
    print("Number of bits to represent Super Sabouter Number:", numBit_SS)

    create_detailed_report(wire_list, filename, f"SABOTUER_{module}")