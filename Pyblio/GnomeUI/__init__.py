# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
# 
# 

# Perform the first initialisation of Gnome, so that the options passed to the script
# are not passed to Gnome

import sys, string
import gettext

_ = gettext.gettext

files    = sys.argv [2:]
sys.argv = sys.argv [:2] + ['--'] + files

# correctly identify the program
from gi.repository import Gtk

from Pyblio import version

# prg = Gtk.Application (application_id='pybliographer') #, version.version)
# Gtk.init()
# prg.set_property (gnome.PARAM_APP_DATADIR, version.datadir)

def _vnum (t):
    return string.join (map (str, t), '.')

ui_version = _("This is Pybliographic %s [Python %s, Gtk %s]") % (
    version.version, _vnum (sys.version_info [:3]), Gtk._version)

# clean up our garbage
sys.argv = sys.argv [:2] + files

del sys, files
