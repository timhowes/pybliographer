
encodings={}
decodings={}

encoding_functions={}
decoding_functions={}

aliases={}

ConvertError="wstrop.ConvertError"

def _not_implemented(*args):
    raise ConvertError,"This function is not implemented"

L=from_ucs2=from_ucs4=from_utf7=from_utf8=from_utf16=_not_implemented
