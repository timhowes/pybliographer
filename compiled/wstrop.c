/***********************************************************
Copyright (C) 1997 Martin von Löwis

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies.

This software comes with no warranty. Use at your own risk.
******************************************************************/


#include <stdio.h>
#include <errno.h>

#include "pyblioconf.h"

#ifdef HAVE_WCHAR_H
#  include <wchar.h>
#else
#  define unsigned int wchar_t;
#endif

#include "Python.h"


static char PyWStrop_Doc[]=
"Support for wide character strings\n"
"This module defines a new type wstring, which represents strings as\n"
"defined in ISO 10646 and Unicode. Some of it is in C, some in Python,\n"
"and some comes from the underlying C library, so the level of support\n"
"can differ among platforms.\n"
"Wide strings should behave like normal strings for most operations.\n"
"If they don't, there should be replacement operations. If there aren't\n"
"report it as a bug.\n"
"Many functions deal with the conversion from and to various character\n"
"sets and encodings. Those functions take an optional flags argument,\n"
"which is a combination of the following values:\n"
"SKIP_INVALID          Illegal characters should be treated gracefully\n"
"                      rather than raising ConvertError\n"
"UTF7_QUOTE_OPTIONALS  Characters not legal in some places of an RFC 822\n"
"                      message should be quoted in utf7()\n"
"UCS_SWITCH_BYTEORDER  The UCS-2 and -4 strings should be considered\n"
"                      little endian.\n"
"UCS2_DO_UTF16         When processing UCS2 (e.g. inside UTF7), honor\n"
"                      cells reserved for UTF-16.";


#define SKIP_INVALID               1
#define UTF7_QUOTE_OPTIONALS       2
#define UCS_SWITCH_BYTEORDER       4
#define UCS2_DO_UTF16              8

typedef struct{
  PyObject_VAR_HEAD
  wchar_t string[1];
} PyWString;

staticforward PyTypeObject PyWString_Type;

static PyObject* ConvertError;

static PyObject* Encodings;
static PyObject* Decodings;
static PyObject* EncodingFunctions;
static PyObject* DecodingFunctions;
static PyObject* Aliases;

#define PyWString_Check(v)	((v)->ob_type == &PyWString_Type)

static PyObject* PyWString_Slice(PyWString* a,int i,int j);

/* allocates new WString. Possible optimization: share empty strings */
static PyWString*
PyWString_New(int len)
{
  PyWString *wstr;
  /* this gives len+1 wchar_t elements */
  wstr = (PyWString*)malloc(sizeof(PyWString)+len*sizeof(wchar_t));
  if(!wstr)
    return (PyWString*)PyErr_NoMemory(); /* return value is 0, anyway */
  wstr->ob_type = &PyWString_Type;
  wstr->ob_size = len;
  /* always zero-terminated */
  wstr->string[len]=0;
  _Py_NewReference(wstr);
  return wstr;
}

/* deletes the string */
static void
PyWString_Free(PyWString *self)
{
  PyMem_DEL(self);
}

/* Converts a single wide character to a sequence of utf8 bytes.
   Returns the number of bytes, or 0 on error. */
static int
to_utf8(wchar_t c,unsigned char* buf)
{
  if(c<0x80){
    if(buf)buf[0]=c;
    return 1;
  }
  if(c<0x800){
    if(buf){
      buf[0] = 0xc0 | (c>>6);
      buf[1] = 0x80 | (c & 0x3f);
    }
    return 2;
  }
  if(c<0x10000){
    if(buf){
      buf[0] = 0xe0 | (c>>12);
      buf[1] = 0x80 | ((c>>6) & 0x3f);
      buf[2] = 0x80 | (c & 0x3f);
    }
    return 3;
  }
  if(c<0x200000){
    if(buf){
      buf[0] = 0xf0 | (c>>18);
      buf[1] = 0x80 | ((c>>12) & 0x3f);
      buf[2] = 0x80 | ((c>>6) & 0x3f);
      buf[3] = 0x80 | (c & 0x3f);
    }
    return 4;
  }
  if(c<0x4000000){
    if(buf){
      buf[0] = 0xf8 | (c>>24);
      buf[1] = 0x80 | ((c>>18) & 0x3f);
      buf[2] = 0x80 | ((c>>12) & 0x3f);
      buf[3] = 0x80 | ((c>>6) & 0x3f);
      buf[4] = 0x80 | (c & 0x3f);
    }
    return 5;
  }
  if(c<0x8000000U){
    if(buf){
      buf[0] = 0xfc | (c>>30);
      buf[1] = 0x80 | ((c>>24) & 0x3f);
      buf[2] = 0x80 | ((c>>18) & 0x3f);
      buf[3] = 0x80 | ((c>>12) & 0x3f);
      buf[4] = 0x80 | ((c>>6) & 0x3f);
      buf[5] = 0x80 | (c & 0x3f);
    }
    return 6;
  }
      
  /* not encodable */
  return 0;
}

/* Decodes a sequence of utf8 bytes into a single wide character.
   Returns the number of bytes consumed, or 0 on error */
static int
from_utf8(const unsigned char* str,wchar_t *c)
{
  int l=0,i;
  if(*str<0x80){
    *c = *str;
    return 1;
  }
  if(*str<0xc0) /* lead byte must not be 10xxxxxx */
    return 0;   /* is c0 a possible lead byte? */
  if(*str<0xe0){         /* 110xxxxx */
    *c = *str & 0x1f;
    l=2;
  }else if(*str<0xf0){   /* 1110xxxx */
    *c = *str & 0xf;
    l=3;
  }else if(*str<0xf8){   /* 11110xxx */
    *c = *str & 7;
    l=4;
  }else if(*str<0xfc){   /* 111110xx */
    *c = *str & 3;
    l=5;
  }else if(*str<0xfe){   /* 1111110x */
    *c = *str & 1;
    l=6;
  }else return 0;

  for(i=1;i<l;i++){
    if((str[i] & 0xc0) != 0x80) /* all other bytes must be 10xxxxxx */
      return 0;
    *c <<= 6;
    *c |= str[i] & 0x3f;
  }
  return l;
}

/* characterize ASCII character with regard to their UTF-7 type */
enum utf7_type{SET_D,SET_O,SET_C,SET_B};
static int
get_utf7_type(char c,enum utf7_type t)
{
  /* The zero byte is in none of the sets (but strchr will say so) */
  if(!c)
    return 0;
  /* This assumes the C compiler is ASCII */
  switch(t){
  case SET_D:
    if(c>='A' && c<='Z')
      return 1;
    if(c>='a' && c<='z')
      return 1;
    if(c>='0' && c<='9')
      return 1;
    if(strchr("'(),-./:?",c))
      return 1;
    return 0;
  case SET_O:
    if(get_utf7_type(c,SET_D))
      return 1;
    if(strchr("!\"#$%&*;<=>@[]^_`{|}",c))
      return 1;
    return 0;
    /* Set D plus characters that need not to be quoted according to Rule 3 */
  case SET_C:
    if(get_utf7_type(c,SET_O))
      return 1;
    if(strchr("\n\r\t ",c))
      return 1;
    return 0;
  case SET_B:
    if(c>='A' && c<='Z')
      return 1;
    if(c>='a' && c<='z')
      return 1;
    if(c>='0' && c<='9')
      return 1;
    if(strchr("+/",c))
      return 1;    
    return 0;
  }
  return 0;
}

/* Converts a natural in the range 0..63 to the 
   corresponding base64 character */
static char
to_base64(int i)
{
  static char map[]=
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";
  if(i<64)
    return map[i];
  return ' ';
}

/* Converts a base64 character to the corresponding integer */
static int
from_base64(char c)
{
  if(c>='A' && c<='Z')
    return c-'A';
  if(c>='a' && c<='z')
    return c-'a'+26;
  if(c>='0' && c<='9')
    return c-'0'+52;
  if(c=='+')
    return 62;
  if(c=='/')
    return 63;
  return -1;
}

/* Converts a UCS-2 string to UTF-7.
   Returns the length of the UTF-7 string, or -1 on error.
   If the destination buffer is 0, it only counts the length. */
static int
ucs2_to_utf7(char* utf7,unsigned char* ucs2,int len2,enum utf7_type optionals)
{
  int len7=0;
  int carry=0,ccount=0;
  int quoted=0;
  int b64;
#define PUT7(c)  do{if(utf7)*utf7++=c;len7++;}while(0)
#define FLUSH_CARRY \
      while(ccount>=6){              \
	b64=carry>>(ccount-6);       \
	PUT7(to_base64(b64));        \
	ccount-=6;                   \
	carry &= (1<<ccount)-1;      \
      }
  if(len2 & 1)  /* UCS-2 strings should have even numbers of bytes */
    return -1;
  while(len2){
    if(*ucs2 || !get_utf7_type(*(ucs2+1),optionals)){
      if(!quoted && !*ucs2 && *(ucs2+1)=='+'){
	/* a single + is quoted as +- */
	PUT7('+');PUT7('-');
      }else{
	/* need quoting */
	if(!quoted){
	  PUT7('+');
	  quoted=1;
	}
	carry<<=16;
	carry|=(*ucs2<<8)|*(ucs2+1);
	ccount+=16;
	FLUSH_CARRY;
      }
    }else{
      if(quoted){
	/* Fill with 0 bits */
	if(ccount%6){
	  carry<<=6-ccount%6;
	  ccount=(ccount+5)/6*6;
	}
	FLUSH_CARRY;
	/* quote stop if next character is base64 */
	if(get_utf7_type(*(ucs2+1),SET_B))
	  PUT7('-');
	quoted=0;
      }
      PUT7(*(ucs2+1));
      /* FIXME: optional quoting of CR, LF and FF */
    }
    len2-=2;
    ucs2+=2;
  }
  if(quoted){
    if(ccount%6){
      carry<<=6-ccount%6;
      ccount=(ccount+5)/6*6;
    }
    FLUSH_CARRY;
    PUT7('-'); /* just to be on the safe side */
  }
  return len7;
}      

/* Converst a UTF-7 sequence to an UCS-2 sequence.
   Returns the length of the UCS-2 string in shorts.
   On error, raises exception and returns -1. */
static int
utf7_to_ucs2(unsigned char* ucs2,unsigned char* utf7,int len2,int flags)
{
  int quoted=0;
  int len=0;
  int carry=0,ccount=0;
#define PUT2(c1,c2) {if(ucs2){*ucs2++=c1;*ucs2++=c2;};len++;}
#define FLUSH_CACHE							\
    if(ccount>=16){							\
      PUT2((carry>>(ccount-8))&0xFF,(carry>>(ccount-16)) & 0xFF);	\
      ccount-=16;							\
      carry&=(1<<ccount)-1;						\
    }
    /* The quoted sequence MUST have an even number of octets.
     * This would have meant that we need to check for ccount>8
     * The current test also detects +A- as ill-formed sequence
     */
#define UNQUOTE								\
    if(!(flags & SKIP_INVALID) && ccount>6){				\
      PyErr_SetString(ConvertError,					\
		      "odd number of octets in quoted sequence");	\
      return -1;							\
    }									\
    carry=0;ccount=0;quoted=0;
  while(len2){
    if(!quoted && *utf7!='+'){
      /* FIXME: check for invalid UTF-7 characters */
      PUT2(0,*utf7);
      utf7++;len2--;
      continue;
    }
    if(!quoted && *utf7=='+'){
      utf7++;len2--;
      /* + must be followed either by - or a SET_B character */
      if((!(flags & SKIP_INVALID) && 
	  (!len2 || (*utf7!='-' && !get_utf7_type(*utf7,SET_B))))){
	PyErr_SetString(ConvertError,"Invalid escape in UTF-7");
	return -1;
      }
      if(len2 && *utf7=='-'){ /* +- */
	PUT2(0,'+');
	utf7++;len2--;
      }else
	quoted=1;
      continue;
    }
    /* handle base 64 string */
    if(!get_utf7_type(*utf7,SET_B)){
      /* not a base64 character, done */
      if(*utf7=='-'){
	/* final '-', skip it */
	utf7++;len2--;
      }
      FLUSH_CACHE;
      /* check and clear remaining bits */
      UNQUOTE;
      continue;
    }
    carry=(carry<<6)|from_base64(*utf7);
    utf7++;len2--;
    ccount+=6;
    FLUSH_CACHE;
  }
  FLUSH_CACHE;
  /* check and clear remaining bits */
  UNQUOTE;
  return len;
}

static char PyWString_FromUtf8_Doc[]=      
"Creates a wide string from an UTF-8 string";

static PyWString*
PyWString_FromUtf8(PyObject* self,PyObject *args)
{
  char *string;
  char *tmp;
  PyWString *wstr = 0;
  wchar_t wtmp;
  int len,i,l1,newlen;

  if(!PyArg_ParseTuple(args,"s#",&string,&len))
    return NULL;
  for(i=0,newlen=0;i<len;i+=l1,newlen++){
    l1=from_utf8(string+i,&wtmp);
    if(!l1){
      PyErr_SetString(ConvertError,"Illegal byte sequence");
      return 0;
    }
  }
  wstr = PyWString_New(newlen);
  if(!wstr)return 0;
  for(tmp=string,i=0;tmp<string+len;i++)
    tmp+=from_utf8(tmp,wstr->string+i);
  return wstr;
}

static char PyWString_Decode_Doc[]=
"Decodes a wide string when given an encoding and a string.\n"
"The encoding must be an alias, a mapping table, a function or built-in.\n"
"Optional flags have encoding-dependent semantics.\n";

static PyWString*
PyWString_Decode(PyObject* self,PyObject* args)
{
  char* type;
  unsigned char* string;
  PyObject *val;
  int len;
  int flags=0;

  if(!PyArg_ParseTuple(args,"ss#|i",&type,&string,&len,&flags))
    return NULL;
  /* Alias processing, allow one level of indirection */
  val=PyDict_GetItemString(Aliases,type);
  if(val && PyString_Check(val))
    type=PyString_AsString(val);
  /* 8859-1 is builtin */
  if(!strcmp(type,"ISO_8859-1:1987")){
    PyWString *result = PyWString_New(len);
    int i;
    if(!result)return 0;
    for(i=0;i<len;i++){
      result->string[i] = (wchar_t)string[i];
    }
    return result;
  }

  /* Dictionary mappings always use 8bit characters */
  val=PyDict_GetItemString(Decodings,type);
  if(val && PyDict_Check(val)){
    PyWString *result = PyWString_New(len);
    int i;
    PyObject *I,*C;
    if(!result)return 0;
    for(i=0;i<len;i++){
      I=PyInt_FromLong(string[i]);
      if(!I)return 0;
      C=PyDict_GetItem(val,I);Py_DECREF(I);
      if(!C){
	if(flags && SKIP_INVALID){
	  result->string[i]=string[i];
	  continue;
	}
	PyErr_SetString(ConvertError,"Invalid character in source");
	PyWString_Free(result);
	return NULL;
      }
      result->string[i] = (wchar_t)PyInt_AsLong(C);
    }
    return result;
  }

  /* Mapping functions do everything */
  val=PyDict_GetItemString(DecodingFunctions,type);
  if(val && PyCallable_Check(val)){
    PyWString *result;
    PyObject *args=Py_BuildValue("s#i",string,len,flags);
    if(!args)return 0;
    result=(PyWString*)PyEval_CallObject(val,args);
    Py_DECREF(args);
    if(!PyWString_Check(result)){
      PyErr_SetString(PyExc_TypeError,"conversion function did not return a wide string");
      return 0;
    }
    return result;
  }
  PyErr_SetString(ConvertError,"Unknown character set");
  return NULL;
}

static char PyWString_Encode_Doc[]=
"Encodes a wide string when given an encoding name.\n"
"The encoding must be an alias, a mapping table, a function or built-in.\n"
"Optional flags have encoding-dependent semantics.\n";

static PyObject*
PyWString_Encode(PyWString* self,PyObject *args)
{
  char *type;
  int flags=0;
  char *s;
  PyObject *val;
  if(!PyArg_ParseTuple(args,"s|i",&type,&flags))return 0;
  /* Alias processing, allow one level of indirection */
  val=PyDict_GetItemString(Aliases,type);
  if(val && PyString_Check(val))
    type=PyString_AsString(val);
  /* 8859-1 is builtin */
  if(!strcmp(type,"ISO_8859-1:1987")){
    PyObject *result = PyString_FromStringAndSize(0,self->ob_size);
    int i;
    int skipped=0;
    if(!result)return 0;
    s=PyString_AsString(result);
    for(i=0;i<self->ob_size;i++){
      if(self->string[i]>=256){
	if(flags && SKIP_INVALID){
	  skipped++;
	  continue;
	}
	Py_DECREF(result);
	PyErr_SetString(ConvertError,"Unconvertible wide character");
	return 0;
      }
      s[i-skipped] = (char)self->string[i];
    }
    if(skipped){
      PyObject *s1=PySequence_GetSlice(result,0,self->ob_size-skipped);
      Py_DECREF(result);
      result=s1;
    }
    return result;
  }
  
  /* Dictionary mappings always use 8bit characters */
  val=PyDict_GetItemString(Encodings,type);
  if(val && PyDict_Check(val)){
    PyObject *result = PyString_FromStringAndSize(0,self->ob_size);
    int i;
    int skipped=0;
    PyObject *I,*C;
    if(!result)return 0;
    s=PyString_AsString(result);
    for(i=0;i<self->ob_size;i++){
      I=PyInt_FromLong(self->string[i]);
      if(!I)return 0;
      C=PyDict_GetItem(val,I);Py_DECREF(I);
      if(!C){
	if(flags && SKIP_INVALID){
	  skipped++;
	  continue;
	}
	PyErr_SetString(ConvertError,"Unconvertible wide character");
	Py_DECREF(result);
	return NULL;
      }
      s[i-skipped] = (char)PyInt_AsLong(C);
    }
    if(skipped){
      PyObject *s1=PySequence_GetSlice(result,0,self->ob_size-skipped);
      Py_DECREF(result);
      result=s1;
    }
    return result;
  }

  /* Mapping functions do everything */
  val=PyDict_GetItemString(EncodingFunctions,type);
  if(val && PyCallable_Check(val)){
    PyObject *result;
    PyObject *args=Py_BuildValue("Oi",self,flags);
    if(!args)return 0;
    result=PyEval_CallObject(val,args);
    Py_DECREF(args);
    if(!PyString_Check(result)){
      PyErr_SetString(PyExc_TypeError,"conversion function did not return a string");
      return 0;
    }
    return result;
  }
  
  PyErr_SetString(ConvertError,"Unknown character set");
  return NULL;
}

static char PyWString_ToUtf8_Doc[]=
"Converts a wide string to UTF-8.";

static PyObject*
PyWString_ToUtf8(PyWString* self,PyObject* args)
{
  PyObject *string;
  int len,l1,i;
  char *str;

  if(!PyArg_NoArgs(args))return 0;

  for(len=i=0;i<self->ob_size;i++){
    l1=to_utf8(self->string[i],0);
    if(!l1){
      len=-1;
      break;
    }
    len+=l1;
  }
  if(len==-1){
    PyErr_SetString(ConvertError,"Illegal 10646 character");
	return 0;
  }
  string = PyString_FromStringAndSize(0,len);
  if(!string)return 0;
  str=PyString_AsString(string);
  for(i=0;i<self->ob_size;i++)
    str+=to_utf8(self->string[i],str);
  return string;
}

static char PyWString_FromUcs2_Doc[]=
"Creates a wide string when given an UCS-2 string.\n"
"The optional flag UCS2_DO_UTF16 combines S-zone characters appropriately.\n"
"Raises ConvertError for invalid strings unless SKIP_INVALID is given.\n";

static PyWString*
PyWString_FromUcs2(PyObject* self,PyObject* args)
{
  PyWString *result;
  int flags=0;
  unsigned char *string;
  int len;
  int skipped=0;
  char *error=0;
  int i;
  
  if(!PyArg_ParseTuple(args,"s#|i",&string,&len,&flags))return 0;
  if((len & 1) && !(flags & SKIP_INVALID)){
    PyErr_SetString(ConvertError,"odd number of UCS-2 bytes");
    return 0;
  }
  result=PyWString_New(len/2);
  if(!result)return 0;
  for(i=0;i<len;i+=2){
    wchar_t c = (string[i]<<8) | string[i+1];
    /* check for S-zone */
    if((c & 0xF800) != 0xD800){
      result->string[i/2-skipped]=c;
      continue;
    }
    /* check for UTF-16 support */
    if(flags & UCS2_DO_UTF16){
      wchar_t next;
      /* not in high-half zone: coding error*/
      if((c & 0xFC00) != 0xD800)
	if(flags & SKIP_INVALID){
	  skipped++;
	  continue;
	}else{
	  error="unpaired low-half UTF-16 cell";
	  break;
	}
      i+=2;
      if(i>=len){
	if(flags & SKIP_INVALID)
	  skipped++;
	else
	  error="unpaired high-half UTF-16 cell";
	break;
      }
      next=(string[i]<<8)|(string[i+1]);
      /* not in low-half zone: coding error */
      if((next & 0xFC00) != 0xDC00)
	if(flags & SKIP_INVALID){
	  skipped++;i-=2; /*process next again*/
	  continue;
	}else{
	  error="unpaired high-half UTF-16 cell";
	  break;
	}
      /* construct cell */
      skipped++;
      result->string[i/2-skipped] = ((c & 0x3FF)<<10) | (next & 0x3FF);
      continue;
    }
    /* no UTF-16 support requested */
    if(flags & SKIP_INVALID){
      skipped++;
      continue;
    }
    error="UTF-16 cells in UCS-2 string";
    break;
  }
  if(error){
    Py_DECREF(result);
    PyErr_SetString(ConvertError,error);
    return 0;
  }
  if(skipped){
    PyObject *s=PyWString_Slice(result,0,result->ob_size-skipped);
    Py_DECREF(result);
    result=(PyWString*)s;
  }
  return result;
}

static char PyWString_ToUcs2_Doc[]=
"Returns the UCS-2 encoding for the wide string, or UTF-16 if.\n"
"UCS2_DO_UTF16 is given. Raises ConvertError if characters are not\n"
"in the supported range.";
 
static PyObject*
PyWString_ToUcs2(PyWString* self,PyObject *args)
{
  PyObject *string;
  char *s;
  int i;
  int flags=0;
  int newlen,newindex;
  wchar_t tmp;
  char* error=0;

  if(!PyArg_ParseTuple(args,"|i",&flags))return 0;
  if(flags & UCS2_DO_UTF16){
    for(i=newlen=0;i<self->ob_size;i++){
      tmp=self->string[i];
      /* cells in the range supported by UTF-16 will need 4 bytes */
      newlen += (tmp>=0x10000 && tmp<0x110000) ? 2:1;
    }
  }else
    newlen=self->ob_size;
  string = PyString_FromStringAndSize(NULL,2*newlen);
  if(!string) return 0;
  s=PyString_AsString(string);
  for(i=newindex=0;i<self->ob_size;i++){
    tmp=self->string[i];
    if(tmp<0x10000){
      s[newindex++] = (self->string[i]>>8) & 0xFF;
      s[newindex++] = self->string[i] & 0xFF;
      continue;
    }
    if(tmp<0x110000){
      if(flags & UCS2_DO_UTF16){
	int high=0xD800|(tmp>>10);
	int low=0xDC00|(tmp & 0x3FF);
	s[newindex++]=high >> 8;
	s[newindex++]=high & 0xFF;
	s[newindex++]=low >> 8;
	s[newindex++]=low & 0xFF;
	continue;
      }
      /* no UTF-16 support */
      if(flags & SKIP_INVALID)
	continue;
      error="character out of range for UCS-2, try UTF-16";
      break;
    }
    if(flags & SKIP_INVALID)
      continue;
    error=(flags & UCS2_DO_UTF16)?
      "character out of range for UTF-16":
      "character out of range for UCS-2";
    break;
  }
  if(error){
    Py_DECREF(string);
    PyErr_SetString(ConvertError,error);
    return 0;
  }
  if(2*newlen != newindex){ /* some cells were skipped */
    PyObject *s=PySequence_GetSlice(string,0,newindex);
    Py_DECREF(string);
    string=s;
  }
  return string;
}

char PyWString_FromUtf7_Doc[]=
"Creates a wide string from an UTF-7 encoding. Supports UTF-16\n"
"in the intermediate UCS-2 encoding if the flag says UCS2_DO_UTF16.\n"
"SKIP_INVALID in the flags avoids ConvertError being raised.";

static PyWString*
PyWString_FromUtf7(PyObject*self,PyObject* args)
{
  unsigned char* string;
  int len,len2;
  int flags=0;
  PyObject *ucs2;
  PyWString *result;

  if(!PyArg_ParseTuple(args,"s#|i",&string,&len,&flags))return 0;
  len2=utf7_to_ucs2(0,string,len,flags);
  if(len2<0)return 0;
  ucs2=PyString_FromStringAndSize(0,2*len2);
  if(!ucs2)return 0;
  utf7_to_ucs2(PyString_AsString(ucs2),string,len,flags);
  args=Py_BuildValue("Oi",ucs2,flags);
  if(!args)return 0;
  result=PyWString_FromUcs2(0,args);
  Py_DECREF(args);
  return result;
}

char PyWString_ToUtf7_Doc[]=
"Returns the UTF-7 encoding for a wide string. Supports UTF-16\n"
"in the intermediate UCS-2 encoding if the flag says UCS2_DO_UTF16.\n"
"SKIP_INVALID in the flags avoids ConvertError being raised.";

static PyObject*
PyWString_ToUtf7(PyWString* self,PyObject *args)
{
  PyObject *ucs2,*utf7;
  int flags=0;
  int len;
  if(!PyArg_ParseTuple(args,"|i",&flags))return 0;
  ucs2=PyWString_ToUcs2(self,args);
  if(!ucs2)return 0;
  len=ucs2_to_utf7(0,PyString_AsString(ucs2),PyObject_Length(ucs2),
		   (flags & UTF7_QUOTE_OPTIONALS) ? SET_D : SET_C);
  if(len<0){
    Py_DECREF(ucs2);
    PyErr_SetString(ConvertError,"Invalid intermediate ucs2");
    return 0;
  }
  utf7=PyString_FromStringAndSize(NULL,len);
  if(!utf7)return 0;
  ucs2_to_utf7(PyString_AsString(utf7),PyString_AsString(ucs2),
	       PyObject_Length(ucs2),
	       (flags & UTF7_QUOTE_OPTIONALS) ? SET_D : SET_C);
  Py_DECREF(ucs2);
  return utf7;
}

static char PyWString_FromUcs4_Doc[]=
"Creates a wide string from an UCS-4 string.\n"
"Later versions will support byte swapping, if the string is not bigendian.";

static PyWString*
PyWString_FromUcs4(PyWString *self,PyObject *args)
{
  unsigned char *string;
  int len,i;
  int flags=0;
  PyWString *result;
  if(!PyArg_ParseTuple(args,"s#|i",&string,&len,&flags))return 0;
  if((len & 3) && !(flags & SKIP_INVALID)){
    PyErr_SetString(ConvertError,"Length of UCS-4 string not multiple of 4");
    return 0;
  }
  result=PyWString_New(len/4);
  if(!result)return 0;
  for(i=0;i<len/4;i++){
    wchar_t tmp;
    tmp=(wchar_t)((string[4*i]<<24)|(string[4*i+1]<<16)|
			 (string[4*i+2]<<8)|(string[4*i+3]));
    if(!(flags & SKIP_INVALID) && tmp>0xD8000 && tmp<0xE000){
      /* maybe we should consider UTF-16 processing in this case */
      PyErr_SetString(ConvertError,"Reserved UTF-16 cells in UCS-4 string");
      return 0;
    }
    result->string[i]=tmp;
  }
  return result;
}

static char PyWString_ToUcs4_Doc[]=
"Converts a wide string into UCS-4.\n"
"Later versions will support byte swapping on request.";

static PyObject*
PyWString_ToUcs4(PyWString *self,PyObject* args)
{
  int flags=0;
  PyObject* result;
  unsigned char *s;
  int i;
  /* this flags are ignored, anyways */
  if(!PyArg_ParseTuple(args,"|i",&flags))return 0;
  result=PyString_FromStringAndSize(0,4*self->ob_size);
  if(!result)return 0;
  s=PyString_AsString(result);
  for(i=0;i<self->ob_size;i++){
    wchar_t tmp=self->string[i];
    s[4*i]=tmp>>24;
    s[4*i+1]=(tmp>>16) & 0xFF;
    s[4*i+2]=(tmp>>8) & 0xFF;
    s[4*i+3]=tmp & 0xFF;
  }
  return result;
}

static char PyWString_FromUtf16_Doc[]=
"Creates a wide string from UTF-16.\n"
"This is a wrapper to from_ucs2.";

PyWString *
PyWString_FromUtf16(PyObject* self,PyObject *args)
{
  PyObject *string;
  PyWString *result;
  int flags=0;
  if(!PyArg_ParseTuple(args,"S|i",&string,&flags))return 0;
  flags|=UCS2_DO_UTF16;
  args=Py_BuildValue("Oi",string,flags);
  if(!args)return 0;
  result=PyWString_FromUcs2(self,args);
  Py_DECREF(args);
  return result;
}

static char PyWString_ToUtf16_Doc[]=
"Returns the UTF-16 coding for the wide string.\n"
"This is a wrapper for to_ucs2.";

PyObject *
PyWString_ToUtf16(PyWString* self,PyObject *args)
{
  PyObject *result;
  int flags=0;
  if(!PyArg_ParseTuple(args,"|i",&flags))return 0;
  flags|=UCS2_DO_UTF16;
  args=Py_BuildValue("(i)",flags);
  if(!args)return 0;
  result=PyWString_ToUcs2(self,args);
  Py_DECREF(args);
  return result;
}

/* return len(self) */
static int
PyWString_Length(PyWString* self)
{
  return self->ob_size;
}

/* return a+b */
static PyObject*
PyWString_Concat(PyWString* a,PyWString *b)
{
  PyWString *result;
  if(!PyWString_Check(b)){
    PyErr_BadArgument();
    return 0;
  }
  /* optimize len(a)==0 and len(b)==0 */
  if(a->ob_size==0){
    Py_INCREF(b);
    return (PyObject*)b;
  }
  if(b->ob_size==0){
    Py_INCREF(a);
    return (PyObject*)a;
  }
  result=PyWString_New(a->ob_size+b->ob_size);
  if(!result)return 0;
  memcpy(result->string,a->string,a->ob_size*sizeof(wchar_t));
  memcpy(result->string+a->ob_size,b->string,b->ob_size*sizeof(wchar_t));
  result->ob_size=a->ob_size+b->ob_size;
  /* New already set last field to 0 */
  return (PyObject*)result;
}

/* return a*n */
static PyObject*
PyWString_Repeat(PyWString* a,int n)
{
  int len,size;
  PyWString *result;
  if(n<0)n=0;
  len=a->ob_size*n;
  if(len==a->ob_size){
    Py_INCREF(a);
    return (PyObject*)a;
  }
  size=len*sizeof(wchar_t);
  result=PyWString_New(len);
  if(!result)return 0;
  for(n=0;n<len;n++)
    memcpy(result->string+n*size,a->string,size);
  return (PyObject*)result;
}

/* return a[i] */
static PyObject*
PyWString_Item(PyWString* a,int i)
{
  PyWString *result;
  if(i<0 || i>=a->ob_size){
    PyErr_SetString(PyExc_IndexError,"wstring index out of range");
    return 0;
  }
  result=PyWString_New(1);
  if(!result)return 0;
  result->string[0]=a->string[i];
  return (PyObject*)result;
}


/* return a[i:j] */
static PyObject*
PyWString_Slice(PyWString* a,int i,int j)
{
  PyWString *result;
  if(i<0)i=0;
  if(j<0)j=0;
  if(j>a->ob_size)j=a->ob_size;
  if(i==0 && j==a->ob_size){
    Py_INCREF(a);
    return (PyObject*)a;
  }
  if(j<i)j=i;
  result=PyWString_New(j-i);
  if(!result)return 0;
  memcpy(result->string,a->string+i,(j-i)*sizeof(wchar_t));
  return (PyObject*)result;
}

/* return "wstring.L("+repr(a.utf8())+")" */
static PyObject*
PyWString_Repr(PyWString* a)
{
  PyObject *result,*tmp;
  /* UTF-8 of the wide string */
  tmp=PyWString_ToUtf8(a,0);
  if(!tmp)return 0;
  /* character representation of it. This is necessary to quote quotes */
  result=PyObject_Repr(tmp);
  Py_DECREF(tmp);
  if(!result)return 0;
  tmp=result;
  /* surrounded by wstring.L() */
  result=PyString_FromStringAndSize(0,PyObject_Length(tmp)+11);
  if(!result){
    Py_DECREF(tmp);
    return 0;
  }
  sprintf(PyString_AsString(result),"wstring.L(%s)",PyString_AsString(tmp));
  return result;
}

/* return a<b
   Comparison is done lexicographically, ignoring any locales */
static int
PyWString_Compare(PyWString *a,PyWString *b)
{
  int a_len=a->ob_size,b_len=b->ob_size;
  int min_len=(a_len<b_len)?a_len:b_len;
  int i;
  for(i=0;i<min_len;i++){
    if(a->string[i]<b->string[i])
      return -1;
    if(a->string[i]>b->string[i])
      return 1;
  }
  return a_len<b_len? -1 : b_len<a_len ? 1 : 0;
}

/* return hash(a) */
static long
PyWString_Hash(PyWString *a)
{
  /* algorithm taken from stringobject.c */
  int len;
  wchar_t *p;
  long x;

  len = a->ob_size;
  p = a->string;
  x = *p << 7;
  while (--len >= 0)
    x = (1000003*x) ^ *p++;
  x ^= a->ob_size;
  if (x == -1)
    x = -2;
  return x;
}

static char PyWString_chr_Doc[]=
"Returns the one-character wide string at the given cell.\n";

static PyWString*
PyWString_chr(PyWString* self,PyObject *args)
{
  int val;
  PyWString *wval;
  if(!PyArg_ParseTuple(args,"l",&val))return 0;
  if(val<0){
    PyErr_SetString(PyExc_ValueError,"negative wide character");
    return 0;
  }
  if(val>0xD800 && val<0xE000){
    PyErr_SetString(ConvertError,"zone reserved for UTF-16");
    return 0;
  }
  wval=PyWString_New(1);
  if(!wval)return 0;
  wval->string[0]=val;
  return wval;
}

static char PyWString_ord_Doc[]=
"Return the cell value (code point) for the given one-character string.\n";
static PyObject*
PyWString_ord(PyObject *self,PyObject *args)
{
  PyWString *val;
  if(!PyArg_ParseTuple(args,"O!",&PyWString_Type,&val))return 0;
  return PyInt_FromLong(val->string[0]);
}
  
static struct PyMethodDef PyWString_Methods[] = {
  {"utf8", (PyCFunction)PyWString_ToUtf8, 0, PyWString_ToUtf8_Doc},
  {"ucs2", (PyCFunction)PyWString_ToUcs2, 1, PyWString_ToUcs2_Doc},
  {"ucs4", (PyCFunction)PyWString_ToUcs4, 1, PyWString_ToUcs4_Doc},
  {"utf7", (PyCFunction)PyWString_ToUtf7, 1, PyWString_ToUtf7_Doc},
  {"utf16", (PyCFunction)PyWString_ToUtf16, 1, PyWString_ToUtf16_Doc},
  {"encode", (PyCFunction)PyWString_Encode, 1, PyWString_Encode_Doc},
  {NULL,NULL}
};

static PyObject *
PyWString_GetAttr(PyWString* o,char *name)
{
  return Py_FindMethod(PyWString_Methods, (PyObject*)o, name);
}

statichere PySequenceMethods PyWString_AsSequence ={
  (inquiry)PyWString_Length, /*sq_length*/
  (binaryfunc)PyWString_Concat, /*sq_concat*/
  (intargfunc)PyWString_Repeat, /* sq_repeat*/
  (intargfunc)PyWString_Item,  /*sq_item*/
  (intintargfunc)PyWString_Slice, /*sq_slice*/
  (intobjargproc)0, /*sq_ass_item*/
  (intintobjargproc)0 /*sq_ass_slice*/
};
  

statichere PyTypeObject PyWString_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,                                /*ob_size*/
  "wstring",                        /*tp_name*/
  sizeof(PyWString),                /*tp_size*/
  sizeof(wchar_t),                  /*tp_itemsize*/
  (destructor)PyWString_Free,       /*tp_dealloc*/
  0,                                /*tp_print*/
  (getattrfunc)PyWString_GetAttr,   /*tp_getattr*/
  0,                                /*tp_setattr*/
  (cmpfunc)PyWString_Compare,       /*tp_compare*/
  (reprfunc)PyWString_Repr,         /*tp_repr*/
  0,                                /*tp_as_number*/
  &PyWString_AsSequence,            /*tp_as_sequence*/
  0,                                /*tp_as_mapping*/
  (hashfunc)PyWString_Hash,         /*tp_hash*/
  0,                   /*tp_call*/
  0,                   /*tp_str*/
  0,                   /*tp_getattro*/
  0,                   /*tp_setattro*/
};

static struct PyMethodDef PyWStrop_Methods[] = {
  {"L",(PyCFunction)PyWString_FromUtf8, 1, PyWString_FromUtf8_Doc},
  {"decode",(PyCFunction)PyWString_Decode, 1, PyWString_Decode_Doc},
  {"chr",(PyCFunction)PyWString_chr, 1, PyWString_chr_Doc},
  {"ord",(PyCFunction)PyWString_ord, 1, PyWString_ord_Doc},
  {"from_ucs2",(PyCFunction)PyWString_FromUcs2, 1, PyWString_FromUcs2_Doc},
  {"from_ucs4",(PyCFunction)PyWString_FromUcs4, 1, PyWString_FromUcs4_Doc},
  {"from_utf7",(PyCFunction)PyWString_FromUtf7, 1, PyWString_FromUtf7_Doc},
  {"from_utf8",(PyCFunction)PyWString_FromUtf8, 1, PyWString_FromUtf8_Doc},
  {"from_utf16",(PyCFunction)PyWString_FromUtf16, 1, PyWString_FromUtf16_Doc},
  {NULL, NULL}
};

void
initwstrop()
{
  PyObject *m,*d,*s;
  m=Py_InitModule4("wstrop",PyWStrop_Methods,PyWStrop_Doc,
		   0,PYTHON_API_VERSION);
  d = PyModule_GetDict(m);
  /* Where should I put documentation for the constants?
     For now, it goes into the module documentation... */
  ConvertError = PyString_FromString("wstrop.ConvertError");
  PyDict_SetItemString(d,"ConvertError",ConvertError);
  PyDict_SetItemString(d,"SKIP_INVALID",PyInt_FromLong(SKIP_INVALID));
  PyDict_SetItemString(d,"UTF7_QUOTE_OPTIONALS",
		       PyInt_FromLong(UTF7_QUOTE_OPTIONALS));
  PyDict_SetItemString(d,"UCS_SWITCH_BYTEORDER",
		       PyInt_FromLong(UCS_SWITCH_BYTEORDER));
  PyDict_SetItemString(d,"UCS2_DO_UTF16",
		       PyInt_FromLong(UCS2_DO_UTF16));
  PyDict_SetItemString(d,"encodings",Encodings=PyDict_New());
  PyDict_SetItemString(d,"decodings",Decodings=PyDict_New());
  PyDict_SetItemString(d,"encoding_functions",EncodingFunctions=PyDict_New());
  PyDict_SetItemString(d,"decoding_functions",DecodingFunctions=PyDict_New());
  PyDict_SetItemString(d,"aliases",Aliases=PyDict_New());
  /*8859-1 aliases are builtin*/
  s=PyString_FromString("ISO_8859-1:1987");
  PyDict_SetItemString(Aliases,"ISO-IR-100",s);
  Py_INCREF(s); /* the SetItemString ate the reference */
  PyDict_SetItemString(Aliases,"ISO_8859-1",s);
  Py_INCREF(s);
  PyDict_SetItemString(Aliases,"LATIN1",s);
  Py_INCREF(s);
  PyDict_SetItemString(Aliases,"L1",s);
  Py_INCREF(s);
  PyDict_SetItemString(Aliases,"IBM819",s);
  Py_INCREF(s);
  PyDict_SetItemString(Aliases,"CP819",s);  

  if(PyErr_Occurred())
    Py_FatalError("Can't initialize module wstrop");
}



