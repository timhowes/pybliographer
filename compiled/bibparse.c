
/*  A Bison parser, made from bibparse.y
    by GNU Bison version 1.28  */

#define YYBISON 1  /* Identify Bison output.  */

#define yyparse bibtex_parser_parse
#define yylex bibtex_parser_lex
#define yyerror bibtex_parser_error
#define yylval bibtex_parser_lval
#define yychar bibtex_parser_char
#define yydebug bibtex_parser_debug
#define yynerrs bibtex_parser_nerrs
#define	end_of_file	257
#define	L_NAME	258
#define	L_DIGIT	259
#define	L_COMMAND	260
#define	L_BODY	261
#define	L_SPACE	262
#define	L_UBSPACE	263

#line 1 "bibparse.y"


/*
 This file is part of pybliographer
 
 Copyright (C) 1998-1999 Frederic GOBRY
 Email : gobry@idiap.ch
 	   
 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2 
 of the License, or (at your option) any later version.
   
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details. 
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 
 $Id$
*/

/*  #include "parsername.h" */
#include "bibtex.h"

extern void bibtex_parser_initialize (BibtexSource *);
extern void bibtex_parser_continue (BibtexSource *);
extern void bibtex_parser_finish (BibtexSource *);

extern gboolean bibtex_parser_is_content;

extern int bibtex_parser_debug;

static BibtexEntry *	entry	= NULL;
static int		start_line, entry_start;
static BibtexSource *	current_source;
static gchar *	        error_string = NULL;
static gchar *	        warning_string = NULL;
static GString *        tmp_string = NULL;

static gboolean recovering = FALSE;

static void 
nop (void) { 
    return ;
}

void 
bibtex_next_line (void) { 
    entry->length ++; 
}

void 
bibtex_analyzer_initialize (BibtexSource * source)  {
    bibtex_parser_initialize (source);
}

void 
bibtex_analyzer_finish (BibtexSource * source)  {
    g_return_if_fail (source != NULL);

    bibtex_parser_finish (source);
    
    current_source = NULL;
}
 
BibtexEntry * 
bibtex_analyzer_parse (BibtexSource * source) {
  int ret;
  gboolean is_comment;

  g_return_val_if_fail (source != NULL, NULL);

  if (! tmp_string) {
      tmp_string = g_string_new (NULL);
  }

  current_source = source;

  bibtex_parser_debug = source->debug;

  start_line  = source->line;
  entry_start = source->line + 1;

  entry = bibtex_entry_new ();

  bibtex_parser_continue (source);
  bibtex_parser_is_content = FALSE;

  ret = bibtex_parser_parse ();

  entry->start_line = entry_start;

  bibtex_tmp_string_free ();

  is_comment = (entry->type && (strcasecmp (entry->type, "comment") == 0));

  if (warning_string && ! is_comment) {
      bibtex_warning (warning_string);
  }
  
  if (ret != 0) {
      source->line += entry->length;
      
      if (error_string && ! is_comment) {
	  bibtex_error (error_string);
      }

      bibtex_entry_destroy (entry, TRUE);
      entry = NULL;
  }

  if (error_string) {
      g_free (error_string);
      error_string = NULL;
  }

  if (warning_string) {
      g_free (warning_string);
      warning_string = NULL;
  }

  return entry;
}

void 
bibtex_parser_error (char * s) {
    if (error_string) {
	g_free (error_string);
    }

    if (current_source) {
	error_string = g_strdup_printf ("%s:%d: %s", current_source->name,
					start_line + entry->length, s);
    }
    else {
	error_string = g_strdup_printf ("%d: %s", 
					start_line + entry->length, s);

    }
}

void 
bibtex_parser_warning (char * s) {
    if (current_source) {
	warning_string = g_strdup_printf ("%s:%d: %s", current_source->name,
					  start_line + entry->length, s);
    }
    else {
	warning_string = g_strdup_printf ("%d: %s", 
					  start_line + entry->length, s);

    }
}

static void 
bibtex_parser_start_error (char * s) {
    if (error_string) {
	g_free (error_string);
    }

    if (current_source) {
	error_string = g_strdup_printf ("%s:%d: %s", current_source->name,
					entry_start, s);
    }
    else {
	error_string = g_strdup_printf ("%d: %s", 
					entry_start, s);
    }
}

static void 
bibtex_parser_start_warning (char * s) {
    if (current_source) {
	warning_string = g_strdup_printf ("%s:%d: %s", current_source->name,
					  entry_start, s);
    }
    else {
	warning_string = g_strdup_printf ("%d: %s", 
					  entry_start, s);
    }
}


#line 189 "bibparse.y"
typedef union{
    gchar * text;
    BibtexStruct * body;
} YYSTYPE;
#ifndef YYDEBUG
#define YYDEBUG 1
#endif

#include <stdio.h>

#ifndef __cplusplus
#ifndef __STDC__
#define const
#endif
#endif



#define	YYFINAL		53
#define	YYFLAG		-32768
#define	YYNTBASE	19

#define YYTRANSLATE(x) ((unsigned)(x) <= 263 ? yytranslate[x] : 31)

static const char yytranslate[] = {     0,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,    18,    17,     2,     2,     2,     2,    13,
    14,     2,     2,    15,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
    16,     2,     2,    10,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,    11,     2,    12,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
     2,     2,     2,     2,     2,     1,     3,     4,     5,     6,
     7,     8,     9
};

#if YYDEBUG != 0
static const short yyprhs[] = {     0,
     0,     6,    12,    14,    20,    26,    32,    38,    42,    45,
    47,    51,    53,    57,    59,    60,    65,    66,    71,    73,
    75,    77,    79,    81,    85,    87,    89,    91,    92,    95,
    98,    99
};

static const short yyrhs[] = {    10,
     4,    11,    20,    12,     0,    10,     4,    13,    20,    14,
     0,     3,     0,    10,     4,    13,     1,    14,     0,    10,
     4,    11,     1,    12,     0,    10,     4,    13,     1,     3,
     0,    10,     4,    11,     1,     3,     0,    21,    15,    20,
     0,    21,    15,     0,    21,     0,     4,    16,    22,     0,
    22,     0,    27,    17,    22,     0,    27,     0,     0,    11,
    24,    29,    12,     0,     0,    18,    26,    30,    18,     0,
     5,     0,     4,     0,    23,     0,    25,     0,     6,     0,
    11,    29,    12,     0,     8,     0,     9,     0,     7,     0,
     0,    18,    29,     0,    28,    29,     0,     0,    28,    30,
     0
};

#endif

#if YYDEBUG != 0
static const short yyrline[] = { 0,
   218,   227,   236,   243,   269,   295,   302,   316,   322,   328,
   340,   388,   406,   412,   425,   426,   441,   442,   454,   461,
   470,   476,   486,   493,   501,   507,   514,   525,   532,   541,
   551,   558
};
#endif


#if YYDEBUG != 0 || defined (YYERROR_VERBOSE)

static const char * const yytname[] = {   "$","error","$undefined.","end_of_file",
"L_NAME","L_DIGIT","L_COMMAND","L_BODY","L_SPACE","L_UBSPACE","'@'","'{'","'}'",
"'('","')'","','","'='","'#'","'\\\"'","entry","values","value","content","content_brace",
"@1","content_quote","@2","simple_content","text_part","text_brace","text_quote", NULL
};
#endif

static const short yyr1[] = {     0,
    19,    19,    19,    19,    19,    19,    19,    20,    20,    20,
    21,    21,    22,    22,    24,    23,    26,    25,    27,    27,
    27,    27,    28,    28,    28,    28,    28,    29,    29,    29,
    30,    30
};

static const short yyr2[] = {     0,
     5,     5,     1,     5,     5,     5,     5,     3,     2,     1,
     3,     1,     3,     1,     0,     4,     0,     4,     1,     1,
     1,     1,     1,     3,     1,     1,     1,     0,     2,     2,
     0,     2
};

static const short yydefact[] = {     0,
     3,     0,     0,     0,     0,     0,    20,    19,    15,    17,
     0,    10,    12,    21,    22,    14,     0,     0,     7,     5,
     0,    28,    31,     1,     9,     0,     6,     4,     2,    20,
    11,    23,    27,    25,    26,    28,    28,    28,     0,    31,
     0,     8,    13,     0,    29,    30,    16,    32,    18,    24,
     0,     0,     0
};

static const short yydefgoto[] = {    51,
    11,    12,    13,    14,    22,    15,    23,    16,    38,    39,
    41
};

static const short yypact[] = {    30,
-32768,    -1,    34,     0,     5,    10,    32,-32768,-32768,-32768,
    25,    36,-32768,-32768,-32768,    33,    12,    38,-32768,-32768,
     3,    21,    35,-32768,    20,     3,-32768,-32768,-32768,-32768,
-32768,-32768,-32768,-32768,-32768,    21,    21,    21,    37,    35,
    39,-32768,-32768,    41,-32768,-32768,-32768,-32768,-32768,-32768,
    54,    55,-32768
};

static const short yypgoto[] = {-32768,
    -5,-32768,    -9,-32768,-32768,-32768,-32768,-32768,   -21,    -2,
    16
};


#define	YYLAST		57


static const short yytable[] = {    18,
     6,    40,     3,     7,     8,    17,    30,     8,     7,     8,
     9,    31,    19,     9,    27,     9,    43,    10,    40,    42,
    10,    20,    10,     7,     8,    28,    32,    33,    34,    35,
     9,    36,     1,    44,    45,    46,    24,    10,    37,     2,
    32,    33,    34,    35,     4,    36,     5,    21,    47,    26,
    25,    29,    50,    52,    53,    48,    49
};

static const short yycheck[] = {     5,
     1,    23,     4,     4,     5,     1,     4,     5,     4,     5,
    11,    21,     3,    11,     3,    11,    26,    18,    40,    25,
    18,    12,    18,     4,     5,    14,     6,     7,     8,     9,
    11,    11,     3,    36,    37,    38,    12,    18,    18,    10,
     6,     7,     8,     9,    11,    11,    13,    16,    12,    17,
    15,    14,    12,     0,     0,    40,    18
};
/* -*-C-*-  Note some compilers choke on comments on `#line' lines.  */
#line 3 "//usr/lib/bison.simple"
/* This file comes from bison-1.28.  */

/* Skeleton output parser for bison,
   Copyright (C) 1984, 1989, 1990 Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330,
   Boston, MA 02111-1307, USA.  */

/* As a special exception, when this file is copied by Bison into a
   Bison output file, you may use that output file without restriction.
   This special exception was added by the Free Software Foundation
   in version 1.24 of Bison.  */

/* This is the parser code that is written into each bison parser
  when the %semantic_parser declaration is not specified in the grammar.
  It was written by Richard Stallman by simplifying the hairy parser
  used when %semantic_parser is specified.  */

#ifndef YYSTACK_USE_ALLOCA
#ifdef alloca
#define YYSTACK_USE_ALLOCA
#else /* alloca not defined */
#ifdef __GNUC__
#define YYSTACK_USE_ALLOCA
#define alloca __builtin_alloca
#else /* not GNU C.  */
#if (!defined (__STDC__) && defined (sparc)) || defined (__sparc__) || defined (__sparc) || defined (__sgi) || (defined (__sun) && defined (__i386))
#define YYSTACK_USE_ALLOCA
#include <alloca.h>
#else /* not sparc */
/* We think this test detects Watcom and Microsoft C.  */
/* This used to test MSDOS, but that is a bad idea
   since that symbol is in the user namespace.  */
#if (defined (_MSDOS) || defined (_MSDOS_)) && !defined (__TURBOC__)
#if 0 /* No need for malloc.h, which pollutes the namespace;
	 instead, just don't use alloca.  */
#include <malloc.h>
#endif
#else /* not MSDOS, or __TURBOC__ */
#if defined(_AIX)
/* I don't know what this was needed for, but it pollutes the namespace.
   So I turned it off.   rms, 2 May 1997.  */
/* #include <malloc.h>  */
 #pragma alloca
#define YYSTACK_USE_ALLOCA
#else /* not MSDOS, or __TURBOC__, or _AIX */
#if 0
#ifdef __hpux /* haible@ilog.fr says this works for HPUX 9.05 and up,
		 and on HPUX 10.  Eventually we can turn this on.  */
#define YYSTACK_USE_ALLOCA
#define alloca __builtin_alloca
#endif /* __hpux */
#endif
#endif /* not _AIX */
#endif /* not MSDOS, or __TURBOC__ */
#endif /* not sparc */
#endif /* not GNU C */
#endif /* alloca not defined */
#endif /* YYSTACK_USE_ALLOCA not defined */

#ifdef YYSTACK_USE_ALLOCA
#define YYSTACK_ALLOC alloca
#else
#define YYSTACK_ALLOC malloc
#endif

/* Note: there must be only one dollar sign in this file.
   It is replaced by the list of actions, each action
   as one case of the switch.  */

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		-2
#define YYEOF		0
#define YYACCEPT	goto yyacceptlab
#define YYABORT 	goto yyabortlab
#define YYERROR		goto yyerrlab1
/* Like YYERROR except do call yyerror.
   This remains here temporarily to ease the
   transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */
#define YYFAIL		goto yyerrlab
#define YYRECOVERING()  (!!yyerrstatus)
#define YYBACKUP(token, value) \
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    { yychar = (token), yylval = (value);			\
      yychar1 = YYTRANSLATE (yychar);				\
      YYPOPSTACK;						\
      goto yybackup;						\
    }								\
  else								\
    { yyerror ("syntax error: cannot back up"); YYERROR; }	\
while (0)

#define YYTERROR	1
#define YYERRCODE	256

#ifndef YYPURE
#define YYLEX		yylex()
#endif

#ifdef YYPURE
#ifdef YYLSP_NEEDED
#ifdef YYLEX_PARAM
#define YYLEX		yylex(&yylval, &yylloc, YYLEX_PARAM)
#else
#define YYLEX		yylex(&yylval, &yylloc)
#endif
#else /* not YYLSP_NEEDED */
#ifdef YYLEX_PARAM
#define YYLEX		yylex(&yylval, YYLEX_PARAM)
#else
#define YYLEX		yylex(&yylval)
#endif
#endif /* not YYLSP_NEEDED */
#endif

/* If nonreentrant, generate the variables here */

#ifndef YYPURE

int	yychar;			/*  the lookahead symbol		*/
YYSTYPE	yylval;			/*  the semantic value of the		*/
				/*  lookahead symbol			*/

#ifdef YYLSP_NEEDED
YYLTYPE yylloc;			/*  location data for the lookahead	*/
				/*  symbol				*/
#endif

int yynerrs;			/*  number of parse errors so far       */
#endif  /* not YYPURE */

#if YYDEBUG != 0
int yydebug;			/*  nonzero means print parse trace	*/
/* Since this is uninitialized, it does not stop multiple parsers
   from coexisting.  */
#endif

/*  YYINITDEPTH indicates the initial size of the parser's stacks	*/

#ifndef	YYINITDEPTH
#define YYINITDEPTH 200
#endif

/*  YYMAXDEPTH is the maximum size the stacks can grow to
    (effective only if the built-in stack extension method is used).  */

#if YYMAXDEPTH == 0
#undef YYMAXDEPTH
#endif

#ifndef YYMAXDEPTH
#define YYMAXDEPTH 10000
#endif

/* Define __yy_memcpy.  Note that the size argument
   should be passed with type unsigned int, because that is what the non-GCC
   definitions require.  With GCC, __builtin_memcpy takes an arg
   of type size_t, but it can handle unsigned int.  */

#if __GNUC__ > 1		/* GNU C and GNU C++ define this.  */
#define __yy_memcpy(TO,FROM,COUNT)	__builtin_memcpy(TO,FROM,COUNT)
#else				/* not GNU C or C++ */
#ifndef __cplusplus

/* This is the most reliable way to avoid incompatibilities
   in available built-in functions on various systems.  */
static void
__yy_memcpy (to, from, count)
     char *to;
     char *from;
     unsigned int count;
{
  register char *f = from;
  register char *t = to;
  register int i = count;

  while (i-- > 0)
    *t++ = *f++;
}

#else /* __cplusplus */

/* This is the most reliable way to avoid incompatibilities
   in available built-in functions on various systems.  */
static void
__yy_memcpy (char *to, char *from, unsigned int count)
{
  register char *t = to;
  register char *f = from;
  register int i = count;

  while (i-- > 0)
    *t++ = *f++;
}

#endif
#endif

#line 217 "//usr/lib/bison.simple"

/* The user can define YYPARSE_PARAM as the name of an argument to be passed
   into yyparse.  The argument should have type void *.
   It should actually point to an object.
   Grammar actions can access the variable by casting it
   to the proper pointer type.  */

#ifdef YYPARSE_PARAM
#ifdef __cplusplus
#define YYPARSE_PARAM_ARG void *YYPARSE_PARAM
#define YYPARSE_PARAM_DECL
#else /* not __cplusplus */
#define YYPARSE_PARAM_ARG YYPARSE_PARAM
#define YYPARSE_PARAM_DECL void *YYPARSE_PARAM;
#endif /* not __cplusplus */
#else /* not YYPARSE_PARAM */
#define YYPARSE_PARAM_ARG
#define YYPARSE_PARAM_DECL
#endif /* not YYPARSE_PARAM */

/* Prevent warning if -Wstrict-prototypes.  */
#ifdef __GNUC__
#ifdef YYPARSE_PARAM
int yyparse (void *);
#else
int yyparse (void);
#endif
#endif

int
yyparse(YYPARSE_PARAM_ARG)
     YYPARSE_PARAM_DECL
{
  register int yystate;
  register int yyn;
  register short *yyssp;
  register YYSTYPE *yyvsp;
  int yyerrstatus;	/*  number of tokens to shift before error messages enabled */
  int yychar1 = 0;		/*  lookahead token as an internal (translated) token number */

  short	yyssa[YYINITDEPTH];	/*  the state stack			*/
  YYSTYPE yyvsa[YYINITDEPTH];	/*  the semantic value stack		*/

  short *yyss = yyssa;		/*  refer to the stacks thru separate pointers */
  YYSTYPE *yyvs = yyvsa;	/*  to allow yyoverflow to reallocate them elsewhere */

#ifdef YYLSP_NEEDED
  YYLTYPE yylsa[YYINITDEPTH];	/*  the location stack			*/
  YYLTYPE *yyls = yylsa;
  YYLTYPE *yylsp;

#define YYPOPSTACK   (yyvsp--, yyssp--, yylsp--)
#else
#define YYPOPSTACK   (yyvsp--, yyssp--)
#endif

  int yystacksize = YYINITDEPTH;
  int yyfree_stacks = 0;

#ifdef YYPURE
  int yychar;
  YYSTYPE yylval;
  int yynerrs;
#ifdef YYLSP_NEEDED
  YYLTYPE yylloc;
#endif
#endif

  YYSTYPE yyval;		/*  the variable used to return		*/
				/*  semantic values from the action	*/
				/*  routines				*/

  int yylen;

#if YYDEBUG != 0
  if (yydebug)
    fprintf(stderr, "Starting parse\n");
#endif

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss - 1;
  yyvsp = yyvs;
#ifdef YYLSP_NEEDED
  yylsp = yyls;
#endif

/* Push a new state, which is found in  yystate  .  */
/* In all cases, when you get here, the value and location stacks
   have just been pushed. so pushing a state here evens the stacks.  */
yynewstate:

  *++yyssp = yystate;

  if (yyssp >= yyss + yystacksize - 1)
    {
      /* Give user a chance to reallocate the stack */
      /* Use copies of these so that the &'s don't force the real ones into memory. */
      YYSTYPE *yyvs1 = yyvs;
      short *yyss1 = yyss;
#ifdef YYLSP_NEEDED
      YYLTYPE *yyls1 = yyls;
#endif

      /* Get the current used size of the three stacks, in elements.  */
      int size = yyssp - yyss + 1;

#ifdef yyoverflow
      /* Each stack pointer address is followed by the size of
	 the data in use in that stack, in bytes.  */
#ifdef YYLSP_NEEDED
      /* This used to be a conditional around just the two extra args,
	 but that might be undefined if yyoverflow is a macro.  */
      yyoverflow("parser stack overflow",
		 &yyss1, size * sizeof (*yyssp),
		 &yyvs1, size * sizeof (*yyvsp),
		 &yyls1, size * sizeof (*yylsp),
		 &yystacksize);
#else
      yyoverflow("parser stack overflow",
		 &yyss1, size * sizeof (*yyssp),
		 &yyvs1, size * sizeof (*yyvsp),
		 &yystacksize);
#endif

      yyss = yyss1; yyvs = yyvs1;
#ifdef YYLSP_NEEDED
      yyls = yyls1;
#endif
#else /* no yyoverflow */
      /* Extend the stack our own way.  */
      if (yystacksize >= YYMAXDEPTH)
	{
	  yyerror("parser stack overflow");
	  if (yyfree_stacks)
	    {
	      free (yyss);
	      free (yyvs);
#ifdef YYLSP_NEEDED
	      free (yyls);
#endif
	    }
	  return 2;
	}
      yystacksize *= 2;
      if (yystacksize > YYMAXDEPTH)
	yystacksize = YYMAXDEPTH;
#ifndef YYSTACK_USE_ALLOCA
      yyfree_stacks = 1;
#endif
      yyss = (short *) YYSTACK_ALLOC (yystacksize * sizeof (*yyssp));
      __yy_memcpy ((char *)yyss, (char *)yyss1,
		   size * (unsigned int) sizeof (*yyssp));
      yyvs = (YYSTYPE *) YYSTACK_ALLOC (yystacksize * sizeof (*yyvsp));
      __yy_memcpy ((char *)yyvs, (char *)yyvs1,
		   size * (unsigned int) sizeof (*yyvsp));
#ifdef YYLSP_NEEDED
      yyls = (YYLTYPE *) YYSTACK_ALLOC (yystacksize * sizeof (*yylsp));
      __yy_memcpy ((char *)yyls, (char *)yyls1,
		   size * (unsigned int) sizeof (*yylsp));
#endif
#endif /* no yyoverflow */

      yyssp = yyss + size - 1;
      yyvsp = yyvs + size - 1;
#ifdef YYLSP_NEEDED
      yylsp = yyls + size - 1;
#endif

#if YYDEBUG != 0
      if (yydebug)
	fprintf(stderr, "Stack size increased to %d\n", yystacksize);
#endif

      if (yyssp >= yyss + yystacksize - 1)
	YYABORT;
    }

#if YYDEBUG != 0
  if (yydebug)
    fprintf(stderr, "Entering state %d\n", yystate);
#endif

  goto yybackup;
 yybackup:

/* Do appropriate processing given the current state.  */
/* Read a lookahead token if we need one and don't already have one.  */
/* yyresume: */

  /* First try to decide what to do without reference to lookahead token.  */

  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* yychar is either YYEMPTY or YYEOF
     or a valid token in external form.  */

  if (yychar == YYEMPTY)
    {
#if YYDEBUG != 0
      if (yydebug)
	fprintf(stderr, "Reading a token: ");
#endif
      yychar = YYLEX;
    }

  /* Convert token to internal form (in yychar1) for indexing tables with */

  if (yychar <= 0)		/* This means end of input. */
    {
      yychar1 = 0;
      yychar = YYEOF;		/* Don't call YYLEX any more */

#if YYDEBUG != 0
      if (yydebug)
	fprintf(stderr, "Now at end of input.\n");
#endif
    }
  else
    {
      yychar1 = YYTRANSLATE(yychar);

#if YYDEBUG != 0
      if (yydebug)
	{
	  fprintf (stderr, "Next token is %d (%s", yychar, yytname[yychar1]);
	  /* Give the individual parser a way to print the precise meaning
	     of a token, for further debugging info.  */
#ifdef YYPRINT
	  YYPRINT (stderr, yychar, yylval);
#endif
	  fprintf (stderr, ")\n");
	}
#endif
    }

  yyn += yychar1;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != yychar1)
    goto yydefault;

  yyn = yytable[yyn];

  /* yyn is what to do for this token type in this state.
     Negative => reduce, -yyn is rule number.
     Positive => shift, yyn is new state.
       New state is final state => don't bother to shift,
       just return success.
     0, or most negative number => error.  */

  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrlab;

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Shift the lookahead token.  */

#if YYDEBUG != 0
  if (yydebug)
    fprintf(stderr, "Shifting token %d (%s), ", yychar, yytname[yychar1]);
#endif

  /* Discard the token being shifted unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  *++yyvsp = yylval;
#ifdef YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  /* count tokens shifted since error; after three, turn off error status.  */
  if (yyerrstatus) yyerrstatus--;

  yystate = yyn;
  goto yynewstate;

/* Do the default action for the current state.  */
yydefault:

  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;

/* Do a reduction.  yyn is the number of a rule to reduce with.  */
yyreduce:
  yylen = yyr2[yyn];
  if (yylen > 0)
    yyval = yyvsp[1-yylen]; /* implement default value of the action */

#if YYDEBUG != 0
  if (yydebug)
    {
      int i;

      fprintf (stderr, "Reducing via rule %d (line %d), ",
	       yyn, yyrline[yyn]);

      /* Print the symbols being reduced, and their result.  */
      for (i = yyprhs[yyn]; yyrhs[i] > 0; i++)
	fprintf (stderr, "%s ", yytname[yyrhs[i]]);
      fprintf (stderr, " -> %s\n", yytname[yyr1[yyn]]);
    }
#endif


  switch (yyn) {

case 1:
#line 220 "bibparse.y"
{
    entry->type = g_strdup (yyvsp[-3].text);
    g_strdown (entry->type);

    YYACCEPT; 
;
    break;}
case 2:
#line 229 "bibparse.y"
{ 
    entry->type = g_strdup (yyvsp[-3].text);
    g_strdown (entry->type);

    YYACCEPT; 	
;
    break;}
case 3:
#line 238 "bibparse.y"
{ 
    current_source->eof = TRUE; 
    YYABORT; 
;
    break;}
case 4:
#line 245 "bibparse.y"
{
    if (strcasecmp (yyvsp[-3].text, "comment") == 0) {
	entry->type = g_strdup (yyvsp[-3].text);
	g_strdown (entry->type);

	yyclearin;
	YYACCEPT;
    }

    if (current_source->strict) {
	bibtex_parser_start_error ("perhaps a missing coma");
	YYABORT;
    }
    else {
	bibtex_parser_start_warning ("perhaps a missing coma.");

	entry->type = g_strdup (yyvsp[-3].text);
	g_strdown (entry->type);

	yyclearin;
	YYACCEPT;
    }
;
    break;}
case 5:
#line 271 "bibparse.y"
{
    if (strcasecmp (yyvsp[-3].text, "comment") == 0) {
	entry->type = g_strdup (yyvsp[-3].text);
	g_strdown (entry->type);

	yyclearin;
	YYACCEPT;
    }

    if (current_source->strict) {
	bibtex_parser_start_error ("perhaps a missing coma");
	YYABORT;
    }
    else {
	bibtex_parser_start_warning ("perhaps a missing coma");

	entry->type = g_strdup (yyvsp[-3].text);
	g_strdown (entry->type);

	yyclearin;
	YYACCEPT;
    }
;
    break;}
case 6:
#line 297 "bibparse.y"
{
    bibtex_parser_start_error ("end of file during processing");
    YYABORT;
;
    break;}
case 7:
#line 304 "bibparse.y"
{
    bibtex_parser_start_error ("end of file during processing");
    YYABORT;
;
    break;}
case 8:
#line 318 "bibparse.y"
{
    nop ();
;
    break;}
case 9:
#line 324 "bibparse.y"
{
    nop ();
;
    break;}
case 10:
#line 330 "bibparse.y"
{
    nop ();
;
    break;}
case 11:
#line 342 "bibparse.y"
{ 
    char * name;
    BibtexField * field;
    BibtexFieldType type = BIBTEX_OTHER;

    g_strdown (yyvsp[-2].text);
    field = g_hash_table_lookup (entry->table, yyvsp[-2].text);

    /* Get a new instance of a field name */
    if (field) {
	g_string_sprintf (tmp_string, "field `%s' is already defined", yyvsp[-2].text); 
	bibtex_parser_warning (tmp_string->str);

	bibtex_field_destroy (field, TRUE);
	name = yyvsp[-2].text;
    }
    else {
	name = g_strdup (yyvsp[-2].text);
    }

    /* Search its type */
    do {
	if (strcmp (name, "author") == 0) {
	    type = BIBTEX_AUTHOR;
	    break;
	}

	if (strcmp (name, "title") == 0) {
	    type = BIBTEX_TITLE;
	    break;
	}

	if (strcmp (name, "year") == 0) {
	    type = BIBTEX_DATE;
	    break;
	}
    } 
    while (0);

    /* Convert into the right field */
    field = bibtex_struct_as_field (bibtex_struct_flatten (yyvsp[0].body),
				    type);

    g_hash_table_insert (entry->table, name, field);
;
    break;}
case 12:
#line 390 "bibparse.y"
{ 
    entry_start = start_line + entry->length;

    if (entry->preamble) {
	bibtex_parser_start_error ("entry already contains a preamble");
	YYABORT;
    }

    entry->preamble = yyvsp[0].body;
;
    break;}
case 13:
#line 408 "bibparse.y"
{ 
    yyval.body = bibtex_struct_append (yyvsp[-2].body, yyvsp[0].body);
;
    break;}
case 14:
#line 414 "bibparse.y"
{
    yyval.body = yyvsp[0].body;
;
    break;}
case 15:
#line 425 "bibparse.y"
{ bibtex_parser_is_content = TRUE; ;
    break;}
case 16:
#line 428 "bibparse.y"
{ 
    bibtex_parser_is_content = FALSE; 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);

    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_BRACE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
;
    break;}
case 17:
#line 441 "bibparse.y"
{ bibtex_parser_is_content = TRUE; ;
    break;}
case 18:
#line 444 "bibparse.y"
{ 
    bibtex_parser_is_content = FALSE; 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);

    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_QUOTE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
;
    break;}
case 19:
#line 456 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup (yyvsp[0].text);
;
    break;}
case 20:
#line 463 "bibparse.y"
{
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_REF);
    yyval.body->value.ref = g_strdup (yyvsp[0].text);

    /* g_strdown ($$->value.ref); */
;
    break;}
case 21:
#line 472 "bibparse.y"
{ 
    yyval.body = yyvsp[0].body;
;
    break;}
case 22:
#line 478 "bibparse.y"
{ 
    yyval.body = yyvsp[0].body;
;
    break;}
case 23:
#line 488 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_COMMAND);
    yyval.body->value.com = g_strdup (yyvsp[0].text + 1);
;
    break;}
case 24:
#line 495 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);
    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_BRACE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
;
    break;}
case 25:
#line 503 "bibparse.y"
{
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SPACE);
;
    break;}
case 26:
#line 509 "bibparse.y"
{
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SPACE);
    yyval.body->value.unbreakable = TRUE;
;
    break;}
case 27:
#line 516 "bibparse.y"
{
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup (yyvsp[0].text);
;
    break;}
case 28:
#line 527 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("");
;
    break;}
case 29:
#line 534 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("\"");

    yyval.body = bibtex_struct_append (yyval.body, yyvsp[0].body);
;
    break;}
case 30:
#line 543 "bibparse.y"
{ 
    yyval.body = bibtex_struct_append (yyvsp[-1].body, yyvsp[0].body);
;
    break;}
case 31:
#line 553 "bibparse.y"
{ 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("");
;
    break;}
case 32:
#line 560 "bibparse.y"
{ 
    yyval.body = bibtex_struct_append (yyvsp[-1].body, yyvsp[0].body);
;
    break;}
}
   /* the action file gets copied in in place of this dollarsign */
#line 543 "//usr/lib/bison.simple"

  yyvsp -= yylen;
  yyssp -= yylen;
#ifdef YYLSP_NEEDED
  yylsp -= yylen;
#endif

#if YYDEBUG != 0
  if (yydebug)
    {
      short *ssp1 = yyss - 1;
      fprintf (stderr, "state stack now");
      while (ssp1 != yyssp)
	fprintf (stderr, " %d", *++ssp1);
      fprintf (stderr, "\n");
    }
#endif

  *++yyvsp = yyval;

#ifdef YYLSP_NEEDED
  yylsp++;
  if (yylen == 0)
    {
      yylsp->first_line = yylloc.first_line;
      yylsp->first_column = yylloc.first_column;
      yylsp->last_line = (yylsp-1)->last_line;
      yylsp->last_column = (yylsp-1)->last_column;
      yylsp->text = 0;
    }
  else
    {
      yylsp->last_line = (yylsp+yylen-1)->last_line;
      yylsp->last_column = (yylsp+yylen-1)->last_column;
    }
#endif

  /* Now "shift" the result of the reduction.
     Determine what state that goes to,
     based on the state we popped back to
     and the rule number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTBASE] + *yyssp;
  if (yystate >= 0 && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTBASE];

  goto yynewstate;

yyerrlab:   /* here on detecting error */

  if (! yyerrstatus)
    /* If not already recovering from an error, report this error.  */
    {
      ++yynerrs;

#ifdef YYERROR_VERBOSE
      yyn = yypact[yystate];

      if (yyn > YYFLAG && yyn < YYLAST)
	{
	  int size = 0;
	  char *msg;
	  int x, count;

	  count = 0;
	  /* Start X at -yyn if nec to avoid negative indexes in yycheck.  */
	  for (x = (yyn < 0 ? -yyn : 0);
	       x < (sizeof(yytname) / sizeof(char *)); x++)
	    if (yycheck[x + yyn] == x)
	      size += strlen(yytname[x]) + 15, count++;
	  msg = (char *) malloc(size + 15);
	  if (msg != 0)
	    {
	      strcpy(msg, "parse error");

	      if (count < 5)
		{
		  count = 0;
		  for (x = (yyn < 0 ? -yyn : 0);
		       x < (sizeof(yytname) / sizeof(char *)); x++)
		    if (yycheck[x + yyn] == x)
		      {
			strcat(msg, count == 0 ? ", expecting `" : " or `");
			strcat(msg, yytname[x]);
			strcat(msg, "'");
			count++;
		      }
		}
	      yyerror(msg);
	      free(msg);
	    }
	  else
	    yyerror ("parse error; also virtual memory exceeded");
	}
      else
#endif /* YYERROR_VERBOSE */
	yyerror("parse error");
    }

  goto yyerrlab1;
yyerrlab1:   /* here on error raised explicitly by an action */

  if (yyerrstatus == 3)
    {
      /* if just tried and failed to reuse lookahead token after an error, discard it.  */

      /* return failure if at end of input */
      if (yychar == YYEOF)
	YYABORT;

#if YYDEBUG != 0
      if (yydebug)
	fprintf(stderr, "Discarding token %d (%s).\n", yychar, yytname[yychar1]);
#endif

      yychar = YYEMPTY;
    }

  /* Else will try to reuse lookahead token
     after shifting the error token.  */

  yyerrstatus = 3;		/* Each real token shifted decrements this */

  goto yyerrhandle;

yyerrdefault:  /* current state does not do anything special for the error token. */

#if 0
  /* This is wrong; only states that explicitly want error tokens
     should shift them.  */
  yyn = yydefact[yystate];  /* If its default is to accept any token, ok.  Otherwise pop it.*/
  if (yyn) goto yydefault;
#endif

yyerrpop:   /* pop the current state because it cannot handle the error token */

  if (yyssp == yyss) YYABORT;
  yyvsp--;
  yystate = *--yyssp;
#ifdef YYLSP_NEEDED
  yylsp--;
#endif

#if YYDEBUG != 0
  if (yydebug)
    {
      short *ssp1 = yyss - 1;
      fprintf (stderr, "Error: state stack now");
      while (ssp1 != yyssp)
	fprintf (stderr, " %d", *++ssp1);
      fprintf (stderr, "\n");
    }
#endif

yyerrhandle:

  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yyerrdefault;

  yyn += YYTERROR;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != YYTERROR)
    goto yyerrdefault;

  yyn = yytable[yyn];
  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrpop;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrpop;

  if (yyn == YYFINAL)
    YYACCEPT;

#if YYDEBUG != 0
  if (yydebug)
    fprintf(stderr, "Shifting error token, ");
#endif

  *++yyvsp = yylval;
#ifdef YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  yystate = yyn;
  goto yynewstate;

 yyacceptlab:
  /* YYACCEPT comes here.  */
  if (yyfree_stacks)
    {
      free (yyss);
      free (yyvs);
#ifdef YYLSP_NEEDED
      free (yyls);
#endif
    }
  return 0;

 yyabortlab:
  /* YYABORT comes here.  */
  if (yyfree_stacks)
    {
      free (yyss);
      free (yyvs);
#ifdef YYLSP_NEEDED
      free (yyls);
#endif
    }
  return 1;
}
#line 567 "bibparse.y"
     
	
