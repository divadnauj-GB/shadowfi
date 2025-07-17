import re

# ========== REGEX PATTERNS ==========
MODULE_PATTERN = re.compile(
    r"module\s+([^\s]+)\s*\(.*?\)\s*;([\s\S]*?)endmodule", re.DOTALL
)
MODULE_PATTERN_WITH_DETAILS = re.compile(
    r"module\s+(\w+)\s*\((.*?)\)\s*;([\s\S]*?)endmodule", re.DOTALL
)
COMPONENT_PATTERN = re.compile(
    r"([^\s]+)\s+(\\?[\w\d\[?\]?.?:?]+)\s*\(\s*((\.\w+\(.*?\),?\s*))\s*\);",
    re.DOTALL,
)
PORTS_PATTERN = re.compile(r"\.(\w+)\((.*?)\)", re.DOTALL)

# ========== STRING TEMPLATES ==========
MODULE_TEMPLATE = (
    """module {module_name} ({module_ports});{module_implementation}endmodule"""
)
SABOTEOUR_MODULE_NAME_TEMPLATE = "_sbtr"
SABOTEOUR_MODULE_PORTS_TEMPLATE = ", i_FI_CONTROL_PORT, i_SI, o_SI"
SABOTEOUR_MODULE_PORTS_DEFINITION_TEMPLATE = """
  input [3:0] i_FI_CONTROL_PORT;
  wire [3:0] i_FI_CONTROL_PORT;
  input i_SI;
  wire {saboteur_input_bits} SIwire;
  output o_SI;
  wire o_SI;
"""
SABOTEOUR_MODULE_ADD_PORTS_TEMPLATE = (
    """, .i_FI_CONTROL_PORT(i_FI_CONTROL_PORT), .i_SI({saboteur_si}), .o_SI({saboteur_so})"""
)

SBTR_SI_NAME = "i_SI"
SBTR_CNTRL_NAME = "i_FI_CONTROL_PORT"
SBTR_SO_NAME = "o_SI"

UPDATE_TOP_MODULE = """
module {top} ({ports});
{description}
endmodule
"""
