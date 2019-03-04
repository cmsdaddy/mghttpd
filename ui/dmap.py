# -*- coding: UTF-8 -*-
__author__ = 'lijie'


def __unsigned_bin_to_float(fullmask, bits, times):
    """
        将按照n x 10倍率放大的无符号数据转换为实际使用的浮点数
        eg:
            64  为放大 10倍的浮点数
            6.4 = __u10times_to_float(64, 10)

            122  为放大 100倍的浮点数
            1.22 = __u10times_to_float(122, 100)
    """
    return (bits & fullmask) / (10 ** times)


def __signed_bin_to_float(absmask, signmask, bits, times):
    """
        将按照n x 10倍率放大的符号数据转换为实际使用的浮点数
        注： 一般最高位为符号位
        eg:
            1234  为放大 10倍的浮点数
            123.4 = __u10times_to_float(1234, 10)
    """
    sign = -1 if bits & signmask else 1
    return sign * (bits & absmask) / (10 ** times)


def __u8_to_float(u8, times):
    return __unsigned_bin_to_float(0xff, u8, times)


def __s8_to_float(s8, times):
    return __signed_bin_to_float(0x7f, 0x8f, s8, times)


def __u16_to_float(u8, times):
    return __unsigned_bin_to_float(0xffff, u8, times)


def __s16_to_float(s8, times):
    return __signed_bin_to_float(0x7fff, 0x8fff, s8, times)


def __u32_to_float(u8, times):
    return __unsigned_bin_to_float(0xffffffff, u8, times)


def __s32_to_float(s8, times):
    return __signed_bin_to_float(0x7fffffff, 0x8fffffff, s8, times)
