typedef union{
    gchar * text;
    BibtexStruct * body;
} YYSTYPE;
#define	end_of_file	257
#define	L_NAME	258
#define	L_DIGIT	259
#define	L_COMMAND	260
#define	L_BODY	261
#define	L_SPACE	262
#define	L_UBSPACE	263


extern YYSTYPE bibtex_parser_lval;
