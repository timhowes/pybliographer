/* A Bison parser, made by GNU Bison 1.875a.  */

/* Skeleton parser for Yacc-like parsing with Bison,
   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003 Free Software Foundation, Inc.

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

/* Written by Richard Stallman by simplifying the original so called
   ``semantic'' parser.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Using locations.  */
#define YYLSP_NEEDED 0

/* If NAME_PREFIX is specified substitute the variables and functions
   names.  */
#define yyparse bibtex_parser_parse
#define yylex   bibtex_parser_lex
#define yyerror bibtex_parser_error
#define yylval  bibtex_parser_lval
#define yychar  bibtex_parser_char
#define yydebug bibtex_parser_debug
#define yynerrs bibtex_parser_nerrs


/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     end_of_file = 258,
     L_NAME = 259,
     L_DIGIT = 260,
     L_COMMAND = 261,
     L_BODY = 262,
     L_SPACE = 263,
     L_UBSPACE = 264
   };
#endif
#define end_of_file 258
#define L_NAME 259
#define L_DIGIT 260
#define L_COMMAND 261
#define L_BODY 262
#define L_SPACE 263
#define L_UBSPACE 264




/* Copy the first part of user declarations.  */
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

#include <string.h>
#include "bibtex.h"

extern void bibtex_parser_initialize (BibtexSource *);
extern void bibtex_parser_continue (BibtexSource *);
extern void bibtex_parser_finish (BibtexSource *);

extern int bibtex_parser_lex (void);

int bibtex_parser_parse (void);

extern gboolean bibtex_parser_is_content;

extern int bibtex_parser_debug;

static BibtexEntry *	entry	= NULL;
static int		start_line, entry_start;
static BibtexSource *	current_source;
static gchar *	        error_string = NULL;
static gchar *	        warning_string = NULL;
static GString *        tmp_string = NULL;

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



/* Enabling traces.  */
#ifndef YYDEBUG
# define YYDEBUG 1
#endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

#if ! defined (YYSTYPE) && ! defined (YYSTYPE_IS_DECLARED)
#line 193 "bibparse.y"
typedef union YYSTYPE {
    gchar * text;
    BibtexStruct * body;
} YYSTYPE;
/* Line 191 of yacc.c.  */
#line 300 "y.tab.c"
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif



/* Copy the second part of user declarations.  */


/* Line 214 of yacc.c.  */
#line 312 "y.tab.c"

#if ! defined (yyoverflow) || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# if YYSTACK_USE_ALLOCA
#  define YYSTACK_ALLOC alloca
# else
#  ifndef YYSTACK_USE_ALLOCA
#   if defined (alloca) || defined (_ALLOCA_H)
#    define YYSTACK_ALLOC alloca
#   else
#    ifdef __GNUC__
#     define YYSTACK_ALLOC __builtin_alloca
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning. */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
# else
#  if defined (__STDC__) || defined (__cplusplus)
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   define YYSIZE_T size_t
#  endif
#  define YYSTACK_ALLOC malloc
#  define YYSTACK_FREE free
# endif
#endif /* ! defined (yyoverflow) || YYERROR_VERBOSE */


#if (! defined (yyoverflow) \
     && (! defined (__cplusplus) \
	 || (YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  short yyss;
  YYSTYPE yyvs;
  };

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (short) + sizeof (YYSTYPE))				\
      + YYSTACK_GAP_MAXIMUM)

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  register YYSIZE_T yyi;		\
	  for (yyi = 0; yyi < (Count); yyi++)	\
	    (To)[yyi] = (From)[yyi];		\
	}					\
      while (0)
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T yynewbytes;						\
	YYCOPY (&yyptr->Stack, Stack, yysize);				\
	Stack = &yyptr->Stack;						\
	yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
	yyptr += yynewbytes / sizeof (*yyptr);				\
      }									\
    while (0)

#endif

#if defined (__STDC__) || defined (__cplusplus)
   typedef signed char yysigned_char;
#else
   typedef short yysigned_char;
#endif

/* YYFINAL -- State number of the termination state. */
#define YYFINAL  5
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   57

/* YYNTOKENS -- Number of terminals. */
#define YYNTOKENS  19
/* YYNNTS -- Number of nonterminals. */
#define YYNNTS  13
/* YYNRULES -- Number of rules. */
#define YYNRULES  33
/* YYNRULES -- Number of states. */
#define YYNSTATES  53

/* YYTRANSLATE(YYLEX) -- Bison symbol number corresponding to YYLEX.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   264

#define YYTRANSLATE(YYX) 						\
  ((unsigned int) (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[YYLEX] -- Bison symbol number corresponding to YYLEX.  */
static const unsigned char yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,    18,    17,     2,     2,     2,     2,
      13,    14,     2,     2,    15,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,    16,     2,     2,    10,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,    11,     2,    12,     2,     2,     2,     2,
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
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9
};

#if YYDEBUG
/* YYPRHS[YYN] -- Index of the first RHS symbol of rule number YYN in
   YYRHS.  */
static const unsigned char yyprhs[] =
{
       0,     0,     3,     9,    15,    17,    23,    29,    35,    41,
      45,    48,    50,    54,    56,    60,    62,    63,    68,    69,
      74,    76,    78,    80,    82,    84,    88,    90,    92,    94,
      95,    98,   101,   102
};

/* YYRHS -- A `-1'-separated list of the rules' RHS. */
static const yysigned_char yyrhs[] =
{
      20,     0,    -1,    10,     4,    11,    21,    12,    -1,    10,
       4,    13,    21,    14,    -1,     3,    -1,    10,     4,    13,
       1,    14,    -1,    10,     4,    11,     1,    12,    -1,    10,
       4,    13,     1,     3,    -1,    10,     4,    11,     1,     3,
      -1,    22,    15,    21,    -1,    22,    15,    -1,    22,    -1,
       4,    16,    23,    -1,    23,    -1,    28,    17,    23,    -1,
      28,    -1,    -1,    11,    25,    30,    12,    -1,    -1,    18,
      27,    31,    18,    -1,     5,    -1,     4,    -1,    24,    -1,
      26,    -1,     6,    -1,    11,    30,    12,    -1,     8,    -1,
       9,    -1,     7,    -1,    -1,    18,    30,    -1,    29,    30,
      -1,    -1,    29,    31,    -1
};

/* YYRLINE[YYN] -- source line where rule number YYN was defined.  */
static const unsigned short yyrline[] =
{
       0,   222,   222,   231,   240,   247,   273,   299,   306,   320,
     326,   332,   344,   392,   410,   416,   429,   429,   445,   445,
     458,   465,   474,   480,   490,   497,   505,   511,   518,   531,
     536,   545,   557,   562
};
#endif

#if YYDEBUG || YYERROR_VERBOSE
/* YYTNME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals. */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "end_of_file", "L_NAME", "L_DIGIT", 
  "L_COMMAND", "L_BODY", "L_SPACE", "L_UBSPACE", "'@'", "'{'", "'}'", 
  "'('", "')'", "','", "'='", "'#'", "'\"'", "$accept", "entry", "values", 
  "value", "content", "content_brace", "@1", "content_quote", "@2", 
  "simple_content", "text_part", "text_brace", "text_quote", 0
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[YYLEX-NUM] -- Internal token number corresponding to
   token YYLEX-NUM.  */
static const unsigned short yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
      64,   123,   125,    40,    41,    44,    61,    35,    34
};
# endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const unsigned char yyr1[] =
{
       0,    19,    20,    20,    20,    20,    20,    20,    20,    21,
      21,    21,    22,    22,    23,    23,    25,    24,    27,    26,
      28,    28,    28,    28,    29,    29,    29,    29,    29,    30,
      30,    30,    31,    31
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN.  */
static const unsigned char yyr2[] =
{
       0,     2,     5,     5,     1,     5,     5,     5,     5,     3,
       2,     1,     3,     1,     3,     1,     0,     4,     0,     4,
       1,     1,     1,     1,     1,     3,     1,     1,     1,     0,
       2,     2,     0,     2
};

/* YYDEFACT[STATE-NAME] -- Default rule to reduce with in state
   STATE-NUM when YYTABLE doesn't specify something else to do.  Zero
   means the default is an error.  */
static const unsigned char yydefact[] =
{
       0,     4,     0,     0,     0,     1,     0,     0,     0,    21,
      20,    16,    18,     0,    11,    13,    22,    23,    15,     0,
       0,     8,     6,     0,    29,    32,     2,    10,     0,     7,
       5,     3,    21,    12,    24,    28,    26,    27,    29,    29,
      29,     0,    32,     0,     9,    14,     0,    30,    31,    17,
      33,    19,    25
};

/* YYDEFGOTO[NTERM-NUM]. */
static const yysigned_char yydefgoto[] =
{
      -1,     3,    13,    14,    15,    16,    24,    17,    25,    18,
      40,    41,    43
};

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
#define YYPACT_NINF -24
static const yysigned_char yypact[] =
{
      30,   -24,    -1,    37,    34,   -24,     0,     5,    10,    32,
     -24,   -24,   -24,    38,    36,   -24,   -24,   -24,    39,    12,
      40,   -24,   -24,     3,    21,    35,   -24,    20,     3,   -24,
     -24,   -24,   -24,   -24,   -24,   -24,   -24,   -24,    21,    21,
      21,    41,    35,    31,   -24,   -24,    43,   -24,   -24,   -24,
     -24,   -24,   -24
};

/* YYPGOTO[NTERM-NUM].  */
static const yysigned_char yypgoto[] =
{
     -24,   -24,    -7,   -24,   -11,   -24,   -24,   -24,   -24,   -24,
     -23,    -4,    15
};

/* YYTABLE[YYPACT[STATE-NUM]].  What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule which
   number is the opposite.  If zero, do what YYDEFACT says.
   If YYTABLE_NINF, syntax error.  */
#define YYTABLE_NINF -1
static const unsigned char yytable[] =
{
      20,     8,    42,     4,     9,    10,    19,    32,    10,     9,
      10,    11,    33,    21,    11,    29,    11,    45,    12,    42,
      44,    12,    22,    12,     9,    10,    30,    34,    35,    36,
      37,    11,    38,     1,    46,    47,    48,     5,    12,    39,
       2,    34,    35,    36,    37,     6,    38,     7,    23,    51,
      26,    27,     0,    49,    31,    52,    28,    50
};

static const yysigned_char yycheck[] =
{
       7,     1,    25,     4,     4,     5,     1,     4,     5,     4,
       5,    11,    23,     3,    11,     3,    11,    28,    18,    42,
      27,    18,    12,    18,     4,     5,    14,     6,     7,     8,
       9,    11,    11,     3,    38,    39,    40,     0,    18,    18,
      10,     6,     7,     8,     9,    11,    11,    13,    16,    18,
      12,    15,    -1,    12,    14,    12,    17,    42
};

/* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
   symbol of state STATE-NUM.  */
static const unsigned char yystos[] =
{
       0,     3,    10,    20,     4,     0,    11,    13,     1,     4,
       5,    11,    18,    21,    22,    23,    24,    26,    28,     1,
      21,     3,    12,    16,    25,    27,    12,    15,    17,     3,
      14,    14,     4,    23,     6,     7,     8,     9,    11,    18,
      29,    30,    29,    31,    21,    23,    30,    30,    30,    12,
      31,    18,    12
};

#if ! defined (YYSIZE_T) && defined (__SIZE_TYPE__)
# define YYSIZE_T __SIZE_TYPE__
#endif
#if ! defined (YYSIZE_T) && defined (size_t)
# define YYSIZE_T size_t
#endif
#if ! defined (YYSIZE_T)
# if defined (__STDC__) || defined (__cplusplus)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# endif
#endif
#if ! defined (YYSIZE_T)
# define YYSIZE_T unsigned int
#endif

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		(-2)
#define YYEOF		0

#define YYACCEPT	goto yyacceptlab
#define YYABORT		goto yyabortlab
#define YYERROR		goto yyerrlab1


/* Like YYERROR except do call yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */

#define YYFAIL		goto yyerrlab

#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)					\
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    {								\
      yychar = (Token);						\
      yylval = (Value);						\
      yytoken = YYTRANSLATE (yychar);				\
      YYPOPSTACK;						\
      goto yybackup;						\
    }								\
  else								\
    { 								\
      yyerror ("syntax error: cannot back up");\
      YYERROR;							\
    }								\
while (0)

#define YYTERROR	1
#define YYERRCODE	256

/* YYLLOC_DEFAULT -- Compute the default location (before the actions
   are run).  */

#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)         \
  Current.first_line   = Rhs[1].first_line;      \
  Current.first_column = Rhs[1].first_column;    \
  Current.last_line    = Rhs[N].last_line;       \
  Current.last_column  = Rhs[N].last_column;
#endif

/* YYLEX -- calling `yylex' with the right arguments.  */

#ifdef YYLEX_PARAM
# define YYLEX yylex (YYLEX_PARAM)
#else
# define YYLEX yylex ()
#endif

/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (yydebug)					\
    YYFPRINTF Args;				\
} while (0)

# define YYDSYMPRINT(Args)			\
do {						\
  if (yydebug)					\
    yysymprint Args;				\
} while (0)

# define YYDSYMPRINTF(Title, Token, Value, Location)		\
do {								\
  if (yydebug)							\
    {								\
      YYFPRINTF (stderr, "%s ", Title);				\
      yysymprint (stderr, 					\
                  Token, Value);	\
      YYFPRINTF (stderr, "\n");					\
    }								\
} while (0)

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (cinluded).                                                   |
`------------------------------------------------------------------*/

#if defined (__STDC__) || defined (__cplusplus)
static void
yy_stack_print (short *bottom, short *top)
#else
static void
yy_stack_print (bottom, top)
    short *bottom;
    short *top;
#endif
{
  YYFPRINTF (stderr, "Stack now");
  for (/* Nothing. */; bottom <= top; ++bottom)
    YYFPRINTF (stderr, " %d", *bottom);
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)				\
do {								\
  if (yydebug)							\
    yy_stack_print ((Bottom), (Top));				\
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

#if defined (__STDC__) || defined (__cplusplus)
static void
yy_reduce_print (int yyrule)
#else
static void
yy_reduce_print (yyrule)
    int yyrule;
#endif
{
  int yyi;
  unsigned int yylineno = yyrline[yyrule];
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %u), ",
             yyrule - 1, yylineno);
  /* Print the symbols being reduced, and their result.  */
  for (yyi = yyprhs[yyrule]; 0 <= yyrhs[yyi]; yyi++)
    YYFPRINTF (stderr, "%s ", yytname [yyrhs[yyi]]);
  YYFPRINTF (stderr, "-> %s\n", yytname [yyr1[yyrule]]);
}

# define YY_REDUCE_PRINT(Rule)		\
do {					\
  if (yydebug)				\
    yy_reduce_print (Rule);		\
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YYDSYMPRINT(Args)
# define YYDSYMPRINTF(Title, Token, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   SIZE_MAX < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#if YYMAXDEPTH == 0
# undef YYMAXDEPTH
#endif

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif



#if YYERROR_VERBOSE

# ifndef yystrlen
#  if defined (__GLIBC__) && defined (_STRING_H)
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
static YYSIZE_T
#   if defined (__STDC__) || defined (__cplusplus)
yystrlen (const char *yystr)
#   else
yystrlen (yystr)
     const char *yystr;
#   endif
{
  register const char *yys = yystr;

  while (*yys++ != '\0')
    continue;

  return yys - yystr - 1;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined (__GLIBC__) && defined (_STRING_H) && defined (_GNU_SOURCE)
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
#   if defined (__STDC__) || defined (__cplusplus)
yystpcpy (char *yydest, const char *yysrc)
#   else
yystpcpy (yydest, yysrc)
     char *yydest;
     const char *yysrc;
#   endif
{
  register char *yyd = yydest;
  register const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

#endif /* !YYERROR_VERBOSE */



#if YYDEBUG
/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

#if defined (__STDC__) || defined (__cplusplus)
static void
yysymprint (FILE *yyoutput, int yytype, YYSTYPE *yyvaluep)
#else
static void
yysymprint (yyoutput, yytype, yyvaluep)
    FILE *yyoutput;
    int yytype;
    YYSTYPE *yyvaluep;
#endif
{
  /* Pacify ``unused variable'' warnings.  */
  (void) yyvaluep;

  if (yytype < YYNTOKENS)
    {
      YYFPRINTF (yyoutput, "token %s (", yytname[yytype]);
# ifdef YYPRINT
      YYPRINT (yyoutput, yytoknum[yytype], *yyvaluep);
# endif
    }
  else
    YYFPRINTF (yyoutput, "nterm %s (", yytname[yytype]);

  switch (yytype)
    {
      default:
        break;
    }
  YYFPRINTF (yyoutput, ")");
}

#endif /* ! YYDEBUG */
/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

#if defined (__STDC__) || defined (__cplusplus)
static void
yydestruct (int yytype, YYSTYPE *yyvaluep)
#else
static void
yydestruct (yytype, yyvaluep)
    int yytype;
    YYSTYPE *yyvaluep;
#endif
{
  /* Pacify ``unused variable'' warnings.  */
  (void) yyvaluep;

  switch (yytype)
    {

      default:
        break;
    }
}


/* Prevent warnings from -Wmissing-prototypes.  */

#ifdef YYPARSE_PARAM
# if defined (__STDC__) || defined (__cplusplus)
int yyparse (void *YYPARSE_PARAM);
# else
int yyparse ();
# endif
#else /* ! YYPARSE_PARAM */
#if defined (__STDC__) || defined (__cplusplus)
int yyparse (void);
#else
int yyparse ();
#endif
#endif /* ! YYPARSE_PARAM */



/* The lookahead symbol.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;

/* Number of syntax errors so far.  */
int yynerrs;



/*----------.
| yyparse.  |
`----------*/

#ifdef YYPARSE_PARAM
# if defined (__STDC__) || defined (__cplusplus)
int yyparse (void *YYPARSE_PARAM)
# else
int yyparse (YYPARSE_PARAM)
  void *YYPARSE_PARAM;
# endif
#else /* ! YYPARSE_PARAM */
#if defined (__STDC__) || defined (__cplusplus)
int
yyparse (void)
#else
int
yyparse ()

#endif
#endif
{
  
  register int yystate;
  register int yyn;
  int yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int yyerrstatus;
  /* Lookahead token as an internal (translated) token number.  */
  int yytoken = 0;

  /* Three stacks and their tools:
     `yyss': related to states,
     `yyvs': related to semantic values,
     `yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack.  */
  short	yyssa[YYINITDEPTH];
  short *yyss = yyssa;
  register short *yyssp;

  /* The semantic value stack.  */
  YYSTYPE yyvsa[YYINITDEPTH];
  YYSTYPE *yyvs = yyvsa;
  register YYSTYPE *yyvsp;



#define YYPOPSTACK   (yyvsp--, yyssp--)

  YYSIZE_T yystacksize = YYINITDEPTH;

  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;


  /* When reducing, the number of symbols on the RHS of the reduced
     rule.  */
  int yylen;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss;
  yyvsp = yyvs;

  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed. so pushing a state here evens the stacks.
     */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyss + yystacksize - 1 <= yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
	/* Give user a chance to reallocate the stack. Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *yyvs1 = yyvs;
	short *yyss1 = yyss;


	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  This used to be a
	   conditional around just the two extra args, but that might
	   be undefined if yyoverflow is a macro.  */
	yyoverflow ("parser stack overflow",
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),

		    &yystacksize);

	yyss = yyss1;
	yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyoverflowlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
	goto yyoverflowlab;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
	yystacksize = YYMAXDEPTH;

      {
	short *yyss1 = yyss;
	union yyalloc *yyptr =
	  (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
	if (! yyptr)
	  goto yyoverflowlab;
	YYSTACK_RELOCATE (yyss);
	YYSTACK_RELOCATE (yyvs);

#  undef YYSTACK_RELOCATE
	if (yyss1 != yyssa)
	  YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;


      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) yystacksize));

      if (yyss + yystacksize - 1 <= yyssp)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  goto yybackup;

/*-----------.
| yybackup.  |
`-----------*/
yybackup:

/* Do appropriate processing given the current state.  */
/* Read a lookahead token if we need one and don't already have one.  */
/* yyresume: */

  /* First try to decide what to do without reference to lookahead token.  */

  yyn = yypact[yystate];
  if (yyn == YYPACT_NINF)
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid lookahead symbol.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = YYLEX;
    }

  if (yychar <= YYEOF)
    {
      yychar = yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YYDSYMPRINTF ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yyn == 0 || yyn == YYTABLE_NINF)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Shift the lookahead token.  */
  YYDPRINTF ((stderr, "Shifting token %s, ", yytname[yytoken]));

  /* Discard the token being shifted unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  *++yyvsp = yylval;


  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  yystate = yyn;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
        case 2:
#line 224 "bibparse.y"
    {
    entry->type = g_strdup (yyvsp[-3].text);
    g_strdown (entry->type);

    YYACCEPT; 
}
    break;

  case 3:
#line 233 "bibparse.y"
    { 
    entry->type = g_strdup (yyvsp[-3].text);
    g_strdown (entry->type);

    YYACCEPT; 	
}
    break;

  case 4:
#line 242 "bibparse.y"
    { 
    current_source->eof = TRUE; 
    YYABORT; 
}
    break;

  case 5:
#line 249 "bibparse.y"
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
}
    break;

  case 6:
#line 275 "bibparse.y"
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
}
    break;

  case 7:
#line 301 "bibparse.y"
    {
    bibtex_parser_start_error ("end of file during processing");
    YYABORT;
}
    break;

  case 8:
#line 308 "bibparse.y"
    {
    bibtex_parser_start_error ("end of file during processing");
    YYABORT;
}
    break;

  case 9:
#line 322 "bibparse.y"
    {
    nop ();
}
    break;

  case 10:
#line 328 "bibparse.y"
    {
    nop ();
}
    break;

  case 11:
#line 334 "bibparse.y"
    {
    nop ();
}
    break;

  case 12:
#line 346 "bibparse.y"
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
}
    break;

  case 13:
#line 394 "bibparse.y"
    { 
    entry_start = start_line + entry->length;

    if (entry->preamble) {
	bibtex_parser_start_error ("entry already contains a preamble");
	YYABORT;
    }

    entry->preamble = yyvsp[0].body;
}
    break;

  case 14:
#line 412 "bibparse.y"
    { 
    yyval.body = bibtex_struct_append (yyvsp[-2].body, yyvsp[0].body);
}
    break;

  case 15:
#line 418 "bibparse.y"
    {
    yyval.body = yyvsp[0].body;
}
    break;

  case 16:
#line 429 "bibparse.y"
    { bibtex_parser_is_content = TRUE; }
    break;

  case 17:
#line 432 "bibparse.y"
    { 
    bibtex_parser_is_content = FALSE; 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);

    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_BRACE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
}
    break;

  case 18:
#line 445 "bibparse.y"
    { bibtex_parser_is_content = TRUE; }
    break;

  case 19:
#line 448 "bibparse.y"
    { 
    bibtex_parser_is_content = FALSE; 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);

    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_QUOTE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
}
    break;

  case 20:
#line 460 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup (yyvsp[0].text);
}
    break;

  case 21:
#line 467 "bibparse.y"
    {
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_REF);
    yyval.body->value.ref = g_strdup (yyvsp[0].text);

    /* g_strdown ($$->value.ref); */
}
    break;

  case 22:
#line 476 "bibparse.y"
    { 
    yyval.body = yyvsp[0].body;
}
    break;

  case 23:
#line 482 "bibparse.y"
    { 
    yyval.body = yyvsp[0].body;
}
    break;

  case 24:
#line 492 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_COMMAND);
    yyval.body->value.com = g_strdup (yyvsp[0].text + 1);
}
    break;

  case 25:
#line 499 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SUB);
    yyval.body->value.sub->encloser = BIBTEX_ENCLOSER_BRACE;
    yyval.body->value.sub->content  = yyvsp[-1].body;
}
    break;

  case 26:
#line 507 "bibparse.y"
    {
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SPACE);
}
    break;

  case 27:
#line 513 "bibparse.y"
    {
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_SPACE);
    yyval.body->value.unbreakable = TRUE;
}
    break;

  case 28:
#line 520 "bibparse.y"
    {
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup (yyvsp[0].text);
}
    break;

  case 29:
#line 531 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("");
}
    break;

  case 30:
#line 538 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("\"");

    yyval.body = bibtex_struct_append (yyval.body, yyvsp[0].body);
}
    break;

  case 31:
#line 547 "bibparse.y"
    { 
    yyval.body = bibtex_struct_append (yyvsp[-1].body, yyvsp[0].body);
}
    break;

  case 32:
#line 557 "bibparse.y"
    { 
    yyval.body = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
    yyval.body->value.text = g_strdup ("");
}
    break;

  case 33:
#line 564 "bibparse.y"
    { 
    yyval.body = bibtex_struct_append (yyvsp[-1].body, yyvsp[0].body);
}
    break;


    }

/* Line 999 of yacc.c.  */
#line 1567 "y.tab.c"

  yyvsp -= yylen;
  yyssp -= yylen;


  YY_STACK_PRINT (yyss, yyssp);

  *++yyvsp = yyval;


  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTOKENS] + *yyssp;
  if (0 <= yystate && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTOKENS];

  goto yynewstate;


/*------------------------------------.
| yyerrlab -- here on detecting error |
`------------------------------------*/
yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
#if YYERROR_VERBOSE
      yyn = yypact[yystate];

      if (YYPACT_NINF < yyn && yyn < YYLAST)
	{
	  YYSIZE_T yysize = 0;
	  int yytype = YYTRANSLATE (yychar);
	  char *yymsg;
	  int yyx, yycount;

	  yycount = 0;
	  /* Start YYX at -YYN if negative to avoid negative indexes in
	     YYCHECK.  */
	  for (yyx = yyn < 0 ? -yyn : 0;
	       yyx < (int) (sizeof (yytname) / sizeof (char *)); yyx++)
	    if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR)
	      yysize += yystrlen (yytname[yyx]) + 15, yycount++;
	  yysize += yystrlen ("syntax error, unexpected ") + 1;
	  yysize += yystrlen (yytname[yytype]);
	  yymsg = (char *) YYSTACK_ALLOC (yysize);
	  if (yymsg != 0)
	    {
	      char *yyp = yystpcpy (yymsg, "syntax error, unexpected ");
	      yyp = yystpcpy (yyp, yytname[yytype]);

	      if (yycount < 5)
		{
		  yycount = 0;
		  for (yyx = yyn < 0 ? -yyn : 0;
		       yyx < (int) (sizeof (yytname) / sizeof (char *));
		       yyx++)
		    if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR)
		      {
			const char *yyq = ! yycount ? ", expecting " : " or ";
			yyp = yystpcpy (yyp, yyq);
			yyp = yystpcpy (yyp, yytname[yyx]);
			yycount++;
		      }
		}
	      yyerror (yymsg);
	      YYSTACK_FREE (yymsg);
	    }
	  else
	    yyerror ("syntax error; also virtual memory exhausted");
	}
      else
#endif /* YYERROR_VERBOSE */
	yyerror ("syntax error");
    }



  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
	 error, discard it.  */

      /* Return failure if at end of input.  */
      if (yychar == YYEOF)
        {
	  /* Pop the error token.  */
          YYPOPSTACK;
	  /* Pop the rest of the stack.  */
	  while (yyss < yyssp)
	    {
	      YYDSYMPRINTF ("Error: popping", yystos[*yyssp], yyvsp, yylsp);
	      yydestruct (yystos[*yyssp], yyvsp);
	      YYPOPSTACK;
	    }
	  YYABORT;
        }

      YYDSYMPRINTF ("Error: discarding", yytoken, &yylval, &yylloc);
      yydestruct (yytoken, &yylval);
      yychar = YYEMPTY;

    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*----------------------------------------------------.
| yyerrlab1 -- error raised explicitly by an action.  |
`----------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;	/* Each real token shifted decrements this.  */

  for (;;)
    {
      yyn = yypact[yystate];
      if (yyn != YYPACT_NINF)
	{
	  yyn += YYTERROR;
	  if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYTERROR)
	    {
	      yyn = yytable[yyn];
	      if (0 < yyn)
		break;
	    }
	}

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
	YYABORT;

      YYDSYMPRINTF ("Error: popping", yystos[*yyssp], yyvsp, yylsp);
      yydestruct (yystos[yystate], yyvsp);
      yyvsp--;
      yystate = *--yyssp;

      YY_STACK_PRINT (yyss, yyssp);
    }

  if (yyn == YYFINAL)
    YYACCEPT;

  YYDPRINTF ((stderr, "Shifting error token, "));

  *++yyvsp = yylval;


  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

#ifndef yyoverflow
/*----------------------------------------------.
| yyoverflowlab -- parser overflow comes here.  |
`----------------------------------------------*/
yyoverflowlab:
  yyerror ("parser stack overflow");
  yyresult = 2;
  /* Fall through.  */
#endif

yyreturn:
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
  return yyresult;
}


#line 571 "bibparse.y"
     
	

