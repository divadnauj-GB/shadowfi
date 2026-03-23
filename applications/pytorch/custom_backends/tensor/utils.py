import torch


def quantize_tensor(tensor, num_bits=8, dtype=None):
    """
    Quantize a float tensor symmetrically.

    Quantization model:
        q = round(x / scale)
        x ~= q * scale
    """
    if num_bits < 2 or num_bits > 32:
        raise ValueError("num_bits must be between 2 and 32")

    qmax = 2 ** (num_bits - 1) - 1
    qmin = -qmax

    max_val = tensor.abs().max()
    scale = 1.0 if max_val == 0 else max_val / qmax

    if dtype is None:
        if num_bits <= 8:
            dtype = torch.int8
        elif num_bits <= 16:
            dtype = torch.int16
        else:
            dtype = torch.int32

    qtensor = (tensor / scale).round().clamp(qmin, qmax).to(dtype)
    return qtensor, scale


def quantize_bias(bias, input_scale, weight_scale):
    """
    Quantize bias to accumulator scale.

    If:
        x ~= qx * sx
        w ~= qw * sw

    then:
        y = x@w + b
        y ~= (qx@qw + qb) * (sx * sw)

    where:
        qb = round(b / (sx * sw))
    """
    if bias is None:
        return None

    acc_scale = input_scale * weight_scale
    if acc_scale == 0:
        raise ValueError("Accumulator scale is zero")

    qbias = torch.round(bias / acc_scale).to(torch.int32)
    return qbias
