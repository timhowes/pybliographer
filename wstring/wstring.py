"Main module for the wide string support."

try:
    from  wstrop import *
except ImportError:
    from wstremul import *

def install_encoding_map(name,dict):
    """Insert a new mapping for 10646 characters. Parameters are the name
    of the mapping and the dictionary from encoded characters 
    to 10646 characters."""
    encoding = {}
    for code8,uni in dict.items():
	encoding[uni]=code8
    encodings[name]=encoding
    decodings[name]=dict

def install_encoding_function(name,encoding,decoding):
    """Install a new pair of encoding and decoding functions. First parameter
    is the name, followed by both functions."""
    encoding_functions[name]=encoding
    decoding_functions[name]=decoding

def install_alias(alias,name):
    """Install an alias for a mapping. Parameters are the alias and 
    the mapping."""
    aliases[alias]=name

def _to_utf7(string,flags):
    return string.utf7(flags)
def _to_utf8(string,flags):
    return string.utf8(flags)
def _to_utf16(string,flags):
    return string.utf16(flags)
def _to_ucs2(string,flags):
    return string.ucs2(flags)
def _to_ucs4(string,flags):
    return string.ucs4(flags)

install_encoding_function("UTF-7",_to_utf7,from_utf7)
install_encoding_function("UTF-8",_to_utf8,from_utf8)
install_encoding_function("UTF-16",_to_utf16,from_utf16)
install_encoding_function("UCS-2",_to_ucs2,from_ucs2)
install_encoding_function("UCS-4",_to_ucs4,from_ucs4)
