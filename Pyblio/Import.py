# This file is part of pybliographer
# 
# Copyright (C) 2002 Peter Schulte-Stracke
# Email : peter.schulte-stracke@t-online.de
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# $Id$

"""Import functions for Pybliographer
 
      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

Class ImportReader -- Base class for various Import modules.

importer  -- convenience function to import from a file or in-core data.

   See also GnomeUI/Import.py for related dialogues.

   XXX Update discussion in Todo. 
"""
import os, stat, string, types
from  Pyblio import Base, Coco, Fields, Iterator

_default_options = {'preserve_input':1}

class ImportReader (Iterator.Iterator):

    """Base class for all import reader classes.

    Support for input methods, encodings, database and GUI connections, 

    Iterator interface: first/next -- return an entry or None

    Subclass Interface: * means: must implement

    start_file     read file prologue 
    * read_next    return next input record
    * parse        parse input record, return entry
    begin_record   called for each record upon start of parse
    end_record     called after parse (use for clean up)
    next_entry     called to obtain new empty entry 
    
    """

    def __init__ (self, control=None, options=None,
                  interactive=0, 
                  file=None, data=None, iter=None,
                  *argv, **argh):
        
        """Input sources:
        -- file   a file name (url) or an open file *or*
        -- data   a sequence of lines *or*
        -- iter   an iterator

        Interactive means:  
        
        """

        self.interactive = interactive
        self.entry = None
        self.jentry = None
        self.control = control or Coco.Importer(
            title='Unspecified Import', options=options)
        self.options = options or _default_options

        assert ((file != None) + (data != None) + (iter != None)
                ) == 1, "Zero or more than one input source"

        if file:
            if type(file) == types.FileType:
                self.source = file
            else:
                self.control.set_title('Unspecified Import from %s' % file)
                self.source = open(file)
            self.control.set_progress(0, os.fstat(self.source.fileno()
                                                  )[stat.ST_SIZE])
        elif data:
            import StringIO
            self.source = StringIO.StringIO(data)
            self.control.set_progress(0, len(data))
        else:
            self.source = None
            self.control.set_progress(0, -1)

        if iter:
            self.read_first = iter.first
            self.read_next = iter.next
        
        self.control.start()

        # file_position
        self.start_pos, self.end_pos = 0, 0
        
        return

### The following need no change as a rule:

    def first (self):
        self.start_file()
        return self.next()

    def start_file(self, *args, **argh): pass

    def next (self, entry=None, data=None):
        """Process the next entry from the input source. Both
        entry and data argument are provided for easy testing.
        For interactive use, self.parse is the right interface
        to use.


        """
        
        entry = entry or self.next_entry()
        self.jentry = self.jentry or self.next_entry()
        data = data or self.read_next(self.source)
        
        if data :
            if self.options.has_key('preserve_input'):
                entry.lines = data
            self.entry = entry
            return self.parse(entry, data)
        else:
            return None
     
    
    def begin_record (self, *args, **argh):
        """Subclass overridable routine."""
        pass

    def end_record (self, entry, lines, *args, **argh):
        """Subclass overridable routine."""
        pass

    def next_entry (self):
        """Create a new empty entry for use by import routine."""
        entry = Base.Entry2(key=None)
        #print  'NEXT ENTRY: ', dir(entry), entry.__class__, entry.key
        
        return entry
    
### The following must be provided (if needed) by the derived class:

# Main routine:

    def parse (self, entry, data):
        """Major routine. Must always be subclass implemented."""
        raise NotImplementedError

    def unpack (self, data): # needed if unpacked data is used
        """Unsure about this routine ***
        It could unpack the data object, setup a memory file
        and return this, but alternatively could return the data,
        and setup read_next in a suitable way.

        XXXX
        
        """
        raise NotImplementedError

    def read_first (self):
        return self.read_next()

    def read_next (self):

        """Read input data for one record. Subclass implemented.
        Return the data as either a sequence of lines or (e.g., for
        tagged input) a sequence of sequences, starting with the tag
        (or the empty string for the leader).

        Note: some formats within the scope of TaggedReader delimit
        information with newlines (e.g., ISI), others do not break
        lines at all (e.g., MARC), but are often given in a
        convenience format with line breaks. To accomodate them all,
        use the following rules: If the input field comes in several
        lines, respect the line breaks but remove the newline
        characters. If a reader uses both, broken and unbroken
        input, it is to implement prepare_data to join the lines.
        
        For interactive use, we need an indication of the text
        reletive to the input as a whole, if the limits are in any way
        subject to manual intervention.  For that purpose, we have
        start_pos, end_pos with both set to zero in the trivial case.

        So the interactive applicaton has to check end_pos to determine
        if it is posssible to change the boundries of the input data.

        The parsing routines are shielded from the input, they must
        never access the input directly.
        

        """

        


        raise NotImplementedError

    def read_next_indent(self, source):

        """Read data with indented continuation lines."""

        if not line :
            line = source.readline()
            self.line_counter += 1
        lines = [line]
        self.line_number = self.line_counter        
        line = source.readline()
        self.line_counter += 1
        while line and line[0] in string.whitespace:
            lines.append(line)
            line = source.readline()
            self.line_counter += 1
            
        
        return lines

    def prepare_data(self, data):
        """Subclass overridable. Joins lines that were input broken."""
        return data

def importer (name=None, control=None):
    """ Import from a file or an internal result set. Both
    are modelled as an iterator. ???

    from:       Iterator (or Scan) to be imported.
    control:    Coco object associated

    Returns:    a coco object An inport object) ?"""

    pass
    
