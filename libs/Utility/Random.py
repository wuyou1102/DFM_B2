import random as __random

__whitespace = ' \t\n\r\v\f'
__lowercase = 'abcdefghijklmnopqrstuvwxyz'
__uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
__letters = __lowercase + __uppercase
__digits = '0123456789'
__hexdigits = __digits + 'abcdef'
__octdigits = '01234567'
__punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
__printable = __digits + __letters + __punctuation + __whitespace


def code(bit=32):
    return ''.join([__random.choice(__lowercase) for x in xrange(bit)])


def integer(min, max):
    return __random.randint(min, max)
