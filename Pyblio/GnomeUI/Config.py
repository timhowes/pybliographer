# This file is part of pybliographer
# 
# Copyright (C) 1998,1999,2000 Frederic GOBRY
# Email : gobry@idiap.ch
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

from gtk import *
from gnome.ui import *

import string, gettext, re, copy

_ = gettext.gettext

from Pyblio.GnomeUI import Utils
from Pyblio import Config
from Pyblio.Utils import format

_map = string.maketrans ('\t\n', '  ')
_cpt = re.compile ('\s+')

class ConfigDialog:

    def __init__ (self, parent = None):

        tooltips = GtkTooltips ()
        tooltips.enable ()
        
        self.w = GnomePropertyBox ()
        self.w.set_parent (parent)
        self.w.set_title (_("Choose you preferences"))
        self.w.connect ('apply', self.apply)
        self.w.set_policy (TRUE, TRUE, FALSE)

        self.warning = 0
        self.parent = parent
        
        domains = Config.domains ()
        domains = map (lambda x: string.capitalize (x), domains)
        domains.sort ()

        self.page = []
        
        for dom in domains:
            
            cw    = {}
            keys  = Config.keys_in_domain (string.lower (dom))
            keys.sort ()
            
            table = GtkVBox ()
            
            for item in keys:
                data  = Config.get (item)
                if data.type is None or not hasattr (data.type, 'w'):
                    continue

                nice  = string.capitalize (string.split (item, '/') [1])
                label = GtkFrame (nice)
                label.set_border_width (5)
                
                desc  = data.description
                desc  = string.translate (desc, _map)
                desc  = string.strip (_cpt.sub (' ', desc))

                hbox = GtkHBox (spacing = 5)
                hbox.set_border_width (5)
                
                # Create the edition widget...
                edit = data.type.w (data.type, self.w, item)
                cw [item] = edit
                hbox.pack_start (edit.w)

                # helper button
                help = GnomeStock (STOCK_PIXMAP_HELP)
                button = GtkButton ()
                button.add (help)
                button.set_relief (RELIEF_NONE)
                button.connect ('clicked', self.display_help,
                                (self.w, _("Item `%s':\n\n%s") % (item, desc)))
                hbox.pack_start (button, FALSE, FALSE)
                tooltips.set_tip (button, desc)

                label.add (hbox)
                table.pack_start (label,
                                  expand = edit.resize,
                                  fill   = edit.resize)

            if cw:
                self.w.append_page (table, GtkLabel (dom))
                self.page.append (cw)
            
        self.w.show_all ()
        return

    def display_help (self, w, data):
        (w, help) = data
        d = GnomeOkDialog (format (help, 40, 0, 0), w)
        d.show_all ()
        return

    def apply (self, w, page):
        if page == -1: return

        changed = {}
        cw = self.page [page]
        for item in cw.keys ():
            if cw [item].update ():
                changed [item] = Config.get (item).data

        Config.save_user (changed)

        if not self.warning:
            self.warning = 1
            self.parent.warning (_("Some changes require to restart Pybliographic\n"
                                   "to be correctly taken into account"))
        return


class BaseConfig:
    def __init__ (self, dtype, props, key):
        self.type    = dtype
        self.key     = key
        self.prop    = props
        self._state  = 0
        self.frozen  = 0
        return

    def state (self):
        return self._state
    
    def changed (self, * arg):
        if self.frozen: return
        
        self.prop.changed ()
        self._state = 1
        return

    def freeze (self):
        self.frozen = 1
        return

    def thaw (self):
        self.frozen = 0
        return

    def update (self):
        if not self.state (): return 0

        if self.key:
            Config.set (self.key, self.get ())
        return 1


class StringConfig (BaseConfig):

    resize = FALSE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)
        
        self.w = GtkEntry ()
        
        if self.key:
            text = Config.get (key).data
            if text: self.w.set_text (text)
        
        self.w.connect ('changed', self.changed)
        self.w.show_all ()
        return


    def get (self):
        return self.w.get_text ()


    def set (self, value):
        self.freeze ()
        self.w.set_text (value)
        self.thaw ()
        return
    

class IntegerConfig (StringConfig):

    resize = FALSE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        if self.key:
            value = Config.get (key).type
            
            vmin = value.min or 0
            vmax = value.max or +100
        else:
            vmin = 0
            vmax = +100
            
        adj = GtkAdjustment (0, vmin, vmax, 1, 10, 1)
        self.w = GtkSpinButton (adj, 1, 0)
        
        if self.key:
            value = Config.get (key).data
            if value is not None: self.w.set_value (value)
        
        self.w.connect ('changed', self.changed)
        self.w.show_all ()
        return


    def get (self):
        value = self.w.get_value_as_int ()
        type = Config.get (self.key).type
        if type.min and value < type.min: return None
        if type.max and value > type.max: return None

        return value


    def set (self, value):
        self.freeze ()
        self.w.set_value (value)
        self.thaw ()
        return
    

class BooleanConfig (BaseConfig):

    resize = FALSE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = GtkHBox ()
        self.true  = GtkRadioButton (label = _("True"))
        self.false = GtkRadioButton (group = self.true, label = _("False"))
        
        self.w.pack_start (self.true)
        self.w.pack_start (self.false)
        
        if self.key:
            value = Config.get (key).data
            
            if value: self.true.set_active (TRUE)
            else:     self.false.set_active (TRUE)
        
        self.true.connect  ('clicked', self.changed)
        self.false.connect ('clicked', self.changed)
        
        self.w.show_all ()
        return

    def get (self):
        return self.true.get_active ()

    def set (self, value):
        self.freeze ()
        if value: self.true.set_active (TRUE)
        else:     self.false.set_active (TRUE)
        self.thaw ()
        return
    

class ElementConfig (BaseConfig):
    
    resize = TRUE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = GtkScrolledWindow ()
        self.w.set_policy (POLICY_NEVER, POLICY_AUTOMATIC)
        self.list = GtkCList (1)
        self.w.add (self.list)
        
        self.items = dtype.get ()
            
        self.list.freeze ()
        for i in self.items:
            self.list.append ((str (i),))
        self.list.thaw ()

        if key:
            data = Config.get (key).data
            self.list.select_row (self.items.index (data), 0)
            
        self.list.connect ('select-row', self.changed)
        self.w.show_all ()
        return

    def get (self):
        return self.items [self.list.selection [0]]


    def set (self, value):
        self.freeze ()
        self.list.select_row (self.items.index (value), 0)
        self.thaw ()
        return

    
class TupleConfig (BaseConfig):

    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = GtkVBox (spacing = 5)
        self.sub = []

        self.resize = FALSE

        for sub in dtype.subtypes:
            w = sub.w (sub, props)
            self.sub.append (w)
            
            if w.resize:
                self.resize = TRUE

        for w in self.sub:
            self.w.pack_start (w.w,
                               expand = w.resize,
                               fill   = w.resize)
        
        if key:
            data = Config.get (key).data
            i = 0
            for item in data:
                self.sub [i].set (item)
                i = i + 1
        self.w.show_all ()
        return

    def state (self):
        for item in self.sub:
            if item.state (): return 1
        return 0
    
    def get (self):
        ret = []
        for item in self.sub:
            ret.append (item.get ())
        return ret


    def set (self, value):
        self.freeze ()
        i = 0
        for item in value:
            self.sub [i].set (item)
            i = i + 1
        self.thaw ()
        return


class ListConfig (BaseConfig):

    resize = TRUE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = GtkVBox (spacing = 5)
        h = GtkHBox (spacing = 5)
        scroll = GtkScrolledWindow ()
        scroll.set_policy (POLICY_NEVER, POLICY_AUTOMATIC)

        self.list = GtkCList (1)
        self.list.connect ('select-row', self.select_cb)
        self.list.set_reorderable (TRUE)
        self.list.connect ('row_move', self.changed)
        scroll.add (self.list)
        h.pack_start (scroll)

        bbox = GtkVButtonBox ()

        button = GtkButton (_("Add"))
        bbox.pack_start (button)
        button.connect ('clicked', self.add_cb)
        button = GtkButton (_("Update"))
        bbox.pack_start (button)
        button.connect ('clicked', self.update_cb)
        button = GtkButton (_("Remove"))
        bbox.pack_start (button)
        button.connect ('clicked', self.remove_cb)

        h.pack_start (bbox, FALSE, FALSE)
        self.w.pack_start (h)

        # Bottom
        self.subw = dtype.subtype.w (dtype.subtype, props)
        self.w.pack_start (self.subw.w,
                           expand = self.subw.resize,
                           fill   = self.subw.resize)

        if self.key:
            data = Config.get (self.key).data
            i = 0
            for item in data:
                self.list.append ((str (item),))
                self.list.set_row_data (i, item)
                i = i + 1
            
        self.w.show_all ()
        return

    def add_cb (self, * arg):
        self.changed ()
        data = self.subw.get ()
        self.list.append ((str (data),))
        self.list.set_row_data (self.list.rows - 1, data)
        return

    def remove_cb (self, * arg):
        if not self.list.selection: return

        self.changed ()
        self.list.remove (self.list.selection [0])
        return

    def update_cb (self, * arg):
        if not self.list.selection: return
        self.changed ()
        data = self.subw.get ()
        row  = self.list.selection [0]
        self.list.set_text (row, 0, str (data))
        self.list.set_row_data (row, data)
        pass
    

    def select_cb (self, w, row, col, event):
        data = self.list.get_row_data (self.list.selection [0])
        self.subw.set (data)
        return

    def set (self, data):
        self.freeze ()
        self.list.freeze ()
        self.list.clear  ()
        i = 0
        for item in data:
            self.list.append ((str (item),))
            self.list.set_row_data (i, item)
            i = i + 1
        self.list.thaw ()
        self.thaw ()
        return

    def get (self):
        ret = []
        for i in range (0, self.list.rows):
            data = self.list.get_row_data (i)
            ret.append (data)
        return ret
    
    
class DictConfig (BaseConfig):

    resize = TRUE
    
    def __init__ (self, dtype, props, key = None):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = GtkVBox (spacing = 5)
        h = GtkHBox (spacing = 5)
        scroll = GtkScrolledWindow ()
        scroll.set_policy (POLICY_NEVER, POLICY_AUTOMATIC)

        self.list = GtkCList (2, (_("Key"), _("Value")))
        self.list.connect ('select-row', self.select_cb)
        self.list.set_column_auto_resize (0, TRUE)
        
        scroll.add (self.list)
        h.pack_start (scroll)

        bbox = GtkVButtonBox ()

        button = GtkButton (_("Set"))
        bbox.pack_start (button)
        button.connect ('clicked', self.update_cb)
        button = GtkButton (_("Remove"))
        bbox.pack_start (button)
        button.connect ('clicked', self.remove_cb)

        h.pack_start (bbox, FALSE, FALSE)
        self.w.pack_start (h)

        self.w.pack_start (GtkHSeparator (), expand = FALSE, fill = FALSE)
        
        # Bottom
        table = GtkTable (2, 2, homogeneous = FALSE)
        table.set_row_spacings (5)
        table.set_col_spacings (5)
        table.attach (GtkLabel (_("Key:")), 0, 1, 0, 1,
                      xoptions = 0, yoptions = 0)
        table.attach (GtkLabel (_("Value:")), 0, 1, 1, 2,
                      xoptions = 0, yoptions = 0)

        self.keyw   = dtype.key.w (dtype.key, props)
        if self.keyw.resize:
            table.attach (self.keyw.w, 1, 2, 0, 1)
        else:
            table.attach (self.keyw.w, 1, 2, 0, 1,
                          yoptions = 0)
            
        self.valuew = dtype.value.w (dtype.value, props)
        if self.valuew.resize:
            table.attach (self.valuew.w, 1, 2, 1, 2)
        else:
            table.attach (self.valuew.w, 1, 2, 1, 2,
                          yoptions = 0)
            
        self.w.pack_start (table)
        self.dict = {}
        
        if self.key:
            data = Config.get (self.key).data
            self.dict = copy.copy (data)
            keys = data.keys ()
            keys.sort ()
            for k in keys:
                v = data [k]
                self.list.append ((str (k), str (v)))
                self.list.set_row_data (self.list.rows - 1,
                                        (k, v))
        self.w.show_all ()
        return

    def remove_cb (self, * arg):
        if not self.list.selection: return

        self.changed ()
        key = self.list.get_row_data (self.list.selection [0]) [0]
        del self.dict [key]
        self.set (self.dict)
        return

    def update_cb (self, * arg):
        self.changed ()
        self.dict [self.keyw.get ()] = self.valuew.get ()
        self.set (self.dict)
        pass
    

    def select_cb (self, w, row, col, event):
        data = self.list.get_row_data (self.list.selection [0])
        self.keyw.set   (data [0])
        self.valuew.set (data [1])
        return

    def set (self, data):
        self.freeze ()
        self.list.freeze ()
        self.list.clear ()
        
        self.dict = copy.copy (data)
        keys = data.keys ()
        keys.sort ()
        for k in keys:
            v = data [k]
            self.list.append ((str (k), str (v)))
            self.list.set_row_data (self.list.rows - 1,
                                    (k, v))
        self.list.thaw ()
        self.thaw ()
        return

    def get (self):
        return self.dict
    
    
Config.Boolean.w = BooleanConfig
Config.String.w  = StringConfig
Config.Integer.w = IntegerConfig
Config.Element.w = ElementConfig
Config.Tuple.w   = TupleConfig
Config.List.w    = ListConfig
Config.Dict.w    = DictConfig
