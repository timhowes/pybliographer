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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_STDBOOL_H
#include <stdbool.h>
#else /* ! HAVE_STDBOOL_H */

/* stdbool.h for GNU.  */

/* The type `bool' must promote to `int' or `unsigned int'.  The constants
   `true' and `false' must have the value 0 and 1 respectively.  */
typedef enum
  {
    false = 0,
    true = 1
  } bool;

/* The names `true' and `false' must also be made available as macros.  */
#define false	false
#define true	true

/* Signal that all the definitions are present.  */
#define __bool_true_false_are_defined	1

#endif /* HAVE_STDBOOL_H */

#include <stdio.h>

#ifdef USE_RECODE
#include <recode.h>
#endif

#include "bibtex.h"

static BibtexStruct * 
text_to_struct (gchar * string) {
    BibtexEntry * entry;
    BibtexStruct * s;
    static BibtexSource * source = NULL;

    if (source == NULL) source = bibtex_source_new ();

    /* parse as a string */
    if (! bibtex_source_string (source, "internal string", string)) {
	g_error ("can't create string");
    }
	
    entry = bibtex_source_next_entry (source, FALSE);

    if (entry == NULL) {
	bibtex_error ("can't parse entry `%s'", string);
	return NULL;
    }

    s = bibtex_struct_copy (entry->preamble);
    
    bibtex_entry_destroy (entry, TRUE);

/*      bibtex_source_destroy (source, TRUE); */

    return s;
}

BibtexField * 
bibtex_reverse_field (BibtexField * field) {
#ifdef USE_RECODE
    BibtexStruct * s;
    gchar * string, * tmp, c;
    gboolean has_upper, is_upper;
    gint start, stop, last, i;
    BibtexAuthor * author;

    static GString *      st      = NULL;
    static RECODE_OUTER   outer   = NULL;
    static RECODE_REQUEST request = NULL;

    g_return_val_if_fail (field != NULL, NULL);

    if (st == NULL) st = g_string_sized_new (16);
	
    if (outer == NULL) {
	outer = recode_new_outer (false);
	g_assert (outer != NULL);
    }

    if (request == NULL) {
	request = recode_new_request (outer);
	g_assert (request != NULL);
	if (! recode_scan_request (request, "latin1..latex")) {
	    g_error ("can't create recoder");
	}
    }

    if (field->structure) {
	bibtex_struct_destroy (field->structure, TRUE);
	field->structure = NULL;
    }

    field->loss = FALSE;

    switch (field->type) {
    case BIBTEX_OTHER:
	g_return_val_if_fail (field->text != NULL, NULL);

	g_string_truncate (st, 0);

	tmp = recode_string (request, field->text);

	g_string_append (st, "@preamble{{");
	g_string_append (st, tmp);
	g_free (tmp);
	g_string_append (st, "}}");
	
	s = text_to_struct (st->str);
	break;

    case BIBTEX_TITLE:
	g_return_val_if_fail (field->text != NULL, NULL);

	g_string_truncate (st, 0);
	
	tmp = recode_string (request, field->text);

	g_string_append (st, "@preamble{{");

	/* Put the upper cases between {} */
	string   = tmp;
	is_upper = false;
	while (* tmp) {
	    if (* tmp >= 'A' && * tmp <= 'Z') {
		if (! is_upper) {
		    g_string_append_c (st, '{');
		    is_upper = true;
		}
		g_string_append_c (st, * tmp);
	    }
	    else {
		if (is_upper) {
		    g_string_append_c (st, '}');
		    is_upper = false;
		}

		g_string_append_c (st, * tmp);
	    }
	    tmp ++;
	}
	if (is_upper) {
	    g_string_append_c (st, '}');
	    is_upper = false;
	}
	g_free (string);
	g_string_append (st, "}}");
	
	s = text_to_struct (st->str);
	break;

    case BIBTEX_AUTHOR:
	g_return_val_if_fail (field->field.author != NULL, NULL);

	g_string_truncate (st, 0);

	for (i = 0 ; i < field->field.author->len; i ++) {
	    author = & g_array_index (field->field.author, BibtexAuthor, i);

	    if (i != 0) {
		g_string_append (st, " and ");
	    }

	    g_string_append_c (st, '{');
	    if (author->last) {
		g_string_append (st, author->last);
	    }

	    if (author->lineage) {
		g_string_append (st, "}, {");
		g_string_append (st, author->lineage);
	    }
	    g_string_append_c (st, '}');

	    if (author->first) {
		g_string_append (st, ", ");
		g_string_append_c (st, '{');
		g_string_append (st, author->first);
		g_string_append_c (st, '}');
	    }
	}

	/* Create a simple preamble to parse */
	g_string_append  (st, "}}");
	g_string_prepend (st, "@preamble{{");

	s = text_to_struct (st->str);

	break;

    case BIBTEX_DATE:
	s = bibtex_struct_new (BIBTEX_STRUCT_TEXT);
	s->value.text = g_strdup_printf ("%d", field->field.date.year);
	break;

    default:
	g_assert_not_reached ();
    }

    field->structure = s;

    /* remove text field */
    if (field->text) {
	g_free (field->text);

	field->text = NULL;
	field->converted = FALSE;
    }

    return field;

#else  /* ! USE_RECODE */
    bibtex_warning ("bibtex_reverse_field () is disabled");
    bibtex_warning ("to enable it, install GNU Recode and recompile");

    return NULL;
#endif /* USE_RECODE */
}
