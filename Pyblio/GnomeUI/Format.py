# -*- coding: utf-8 -*-
# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
# Copyright (C) 2013 Germán Poo-Caamaño
# Email : gpoo@gnome.org
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
# 

''' Defines a Dialog to format a subset of entries as a bibliography '''

from gi.repository import Gtk

import string, os

from Pyblio import Connector, version, Autoload
from Pyblio.GnomeUI import Utils


class FormatDialog(Connector.Publisher, Utils.GladeWindow):
    """ Class implementing the Format dialog. This class issues a

        'format-query'

        signal when the user applies its settings
    """

    gladeinfo = { 'file': 'format.ui',
                  'root': '_w_format',
                  'name': 'format'
                  }

    style  = os.path.join(version.pybdir, 'Styles', 'Alpha.xml')
    output = None
    
    def __init__(self, parent=None):
        Utils.GladeWindow.__init__(self, parent)
        
        outlist = Autoload.available('output')
        outlist.sort()
        
        for avail in outlist:
            self._w_menu.append_text(avail)

        self._w_menu.set_active(0)
        self.menu_item = outlist[0]

        self._w_style.set_filename(FormatDialog.style)

        if FormatDialog.output:
            self._w_output.set_filename(FormatDialog.output)
        
        self._w_format.show()

    def _menu_select (self, menu):
        self.menu_item = menu.get_active_text()

    def _set_output_file(self, widget):
        FormatDialog.output = self._w_output.get_filename()
        self._w_output.set_filename(FormatDialog.output)

    def _on_validate (self, * arg):
        style  = self._w_style.get_filename()
        output = self._w_output.get_filename()

        FormatDialog.style  = style
        FormatDialog.output = output
        
        format = Autoload.get_by_name ('output', self.menu_item).data

        # FIXME: We can't use GtkFileChooserButton for saving a file
        # So, now we are not saving anything
        if output is None:
            import inspect
            fname, lineno, funcname = inspect.getframeinfo(inspect.currentframe())[:3]
            print 'FIXME: Data not saved. %s:%d (%s)' % (fname, lineno, funcname)

        if style is None or output is None: return
        self._w_format.destroy ()

        self.issue ('format-query', style, format, output)
        return

    def _on_close (self, * arg):
        self.size_save()
        self._w_format.destroy()
