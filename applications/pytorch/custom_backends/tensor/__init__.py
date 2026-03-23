from .RTLConv2dWrapper import RTLConv2dWrapper
from .RTLLinearWrapper import RTLLinearWrapper

wrapper = {
    "linear": RTLLinearWrapper,
    "conv2d": RTLConv2dWrapper
}
