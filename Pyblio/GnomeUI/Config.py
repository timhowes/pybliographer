# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

# TO DO:
# Pixmap instead of text label for help button
# Parent for dialogue
# Only close button needed -- instantly apply changes
# improve the layout & placement of help text


import pygtk
pygtk.require("2.0")

import gtk, gtk.glade
import gnome.ui 

import copy, gettext, os.path, re, string   

_ = gettext.gettext

from Pyblio.GnomeUI import Utils
from Pyblio import Config, version
from Pyblio.Utils import format

_map = string.maketrans ('\t\n', '  ')
_cpt = re.compile ('\s+')



class ConfigDialog:

    def __init__ (self, parent = None):


        gp = os.path.join (version.prefix, 'glade', 'config1.glade')
        
        self.xml = gtk.glade.XML (gp, 'config1')
        self.xml.signal_autoconnect (self)

        self.dialog = self.xml.get_widget ('config1')
        self.dialog_vbox = self.xml.get_widget ('dialog-vbox1')
        self.w = gtk.Notebook ()

        self.dialog_vbox.pack_start(self.w)

        tooltips = gtk.Tooltips ()
        tooltips.enable ()
        
        #self.dialog.set_parent (parent) ####
        self.dialog.set_title (_("Choose your preferences"))
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

            table = gtk.VBox ()
            
            for item in keys:
                data  = Config.get (item)
                if data.type is None or not hasattr (data.type, 'w'):
                    continue

                nice  = string.capitalize (string.split (item, '/') [1])
                label = gtk.Label()
                label.set_use_markup(gtk.TRUE)

                label.set_markup('   <b>%s</b>' % (nice))
                label.set_alignment(xalign=0.5, yalign=0.5)
                table.pack_start (label,False)
                
                desc  = data.description
                desc  = string.translate (desc, _map)
                desc  = string.strip (_cpt.sub (' ', desc))
                
                hbox = gtk.HBox (spacing = 5)
                hbox.set_border_width (5)
                
                # Create the edition widget...
                edit = data.type.w (data.type, self.w, item, help_text=desc)
                cw [item] = edit
                hbox.pack_start (edit.w)

                # helper button
                #help = gnome.ui.Pixmap (gtk.STOCK_HELP) XXX
                if edit.allow_help:
                    help = gtk.Label('HELP!')
                    button = gtk.Button ()
                    button.add (help)
                    button.set_relief (gtk.RELIEF_NONE)
                    button.connect ('clicked', self.display_help,
                                (self.w, _("Item `%s':\n\n%s") % (item, desc)))
                    hbox.pack_start (button, False, False)
                    tooltips.set_tip (button, desc)

                table.pack_start (hbox,
                                  expand = edit.resize,
                                  fill   = edit.resize)

            if cw:
                self.w.append_page (table, gtk.Label (dom))
                self.page.append (cw)
            
        self.dialog.show_all ()
        return

    def on_applybutton1_clicked(self, w):
        print 'ON_APPLY_BUTTON_CLICKED:', self, w
        page = self.w.get_current_page()
        
        if page == -1: return
        changed = {}

        cw = self.page [page]
        for item in cw.keys ():
            print 'ITEM:', item,
            if cw [item].update ():
                print 'UPDATE:', Config.get (item).data
                changed [item] = Config.get (item).data
            print changed.get(item, '*unchanged*')
        Config.save_user (changed)

        if not self.warning:
            self.warning = 1
            self.parent.warning (
                _("Some changes require to restart Pybliographic\n"
                  "to be correctly taken into account"))
        self.dialog.response(gtk.RESPONSE_APPLY)
        self.dialog.destroy()
        return
        
    def on_okbutton1_clicked(self, w, *data):
        print 'ON_OK_BUTTON_CLICKED:', self, w, data
        #self.apply (w, page)
        self.dialog.response(gtk.RESPONSE_OK)
        self.dialog.hide()
       
    def on_helpbutton1_clicked(self, w, *data):
        print 'ON_HELP_BUTTON_CLICKED:',self, w, data

        self.dialog.response(gtk.RESPONSE_HELP)
        self.dialog.destroy()
        
    def on_cancelbutton1_clicked(self, w, *data):
        print 'ON_CANCEL_BUTTON_CLICKED:',self, w, data
        self.dialog.response(gtk.RESPONSE_CANCEL)
        self.dialog.destroy()
       
       
    def display_help (self, w, data):
        (w, help) = data
        d = gnome.ui.OkDialog (format (help, 40, 0, 0), w)
        d.show_all ()
        
        return

    def apply (self, w, page):
        page = self.w.get_current_page()
        
        if page == -1: return

        changed = {}
        cw = self.page [page]
        for item in cw.keys ():
            if cw [item].update ():
                changed [item] = Config.get (item).data

        Config.save_user (changed)

        if not self.warning:
            self.warning = 1
            self.parent.warning (
                _("Some changes require to restart Pybliographic\n"
                  "to be correctly taken into account"))
        return


class BaseConfig:
    def __init__ (self, dtype, props, key, help_text=''):
        print 'INIT CONFIG:', self, dtype, props, key
        self.type    = dtype
        self.key     = key
        self.prop    = props
        self._state  = 0
        self.frozen  = 0
        self.allow_help = 1
        return

    def state (self):
        return self._state
    
    def changed (self, * arg):
        if self.frozen: return
        
        #self.prop.changed () XXX
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

    resize = False
    
    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)
        
        self.w = gtk.Entry ()
        
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

    resize = False
    
    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)

        if self.key:
            value = Config.get (key).type
            
            vmin = value.min or 0
            vmax = value.max or +100
        else:
            vmin = 0
            vmax = +100
            
        adj = gtk.Adjustment (0, vmin, vmax, 1, 10, 1)
        self.w = gtk.SpinButton (adj, 1, 0)
        
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

    resize = False

    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)
        self.allow_help = False
        self.w = gtk.HBox ()
        self.button = gtk.CheckButton ()
        self.w.pack_start (self.button, False)

        if self.key:
            value = Config.get (key).data
            self.button.set_active(value)
        
        self.button.connect  ('clicked', self.clicked)
        description = gtk.Label()
        description.set_use_markup(gtk.TRUE)
        description.set_line_wrap(True)
        description.set_justify(gtk.JUSTIFY_LEFT) #default?
        description.set_markup('%s' % (help_text))
        description.set_alignment(xalign=0.5, yalign=0.5)
        self.w.pack_start (description, False, True)
        
        self.w.show_all ()
        return
    
    def clicked(self, *args):
        print 'CLICKED:', args
        self.changed()
        self.update()

    def get (self):
        return self.button.get_active ()

    def set (self, value):
        self.freeze ()
        self.button.set_active(value)
        self.thaw ()
        return
    

class ElementConfig (BaseConfig):
    
    resize = True
    
    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = gtk.ScrolledWindow ()
        self.w.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.list = gtk.CList (1)
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

    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = gtk.VBox (spacing = 5)
        self.sub = []

        self.resize = False

        for sub in dtype.subtypes:
            w = sub.w (sub, props)
            self.sub.append (w)
            
            if w.resize:
                self.resize = True

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

    resize = True
    
    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = gtk.VBox (spacing = 5)
        h = gtk.HBox (spacing = 5)
        scroll = gtk.ScrolledWindow ()
        scroll.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.list = gtk.CList (1)
        self.list.connect ('select-row', self.select_cb)
        self.list.set_reorderable (True)
        self.list.connect ('row_move', self.changed)
        scroll.add (self.list)
        h.pack_start (scroll)

        bbox = gtk.VButtonBox ()

        button = gtk.Button (_("Add"))
        bbox.pack_start (button)
        button.connect ('clicked', self.add_cb)
        button = gtk.Button (_("Update"))
        bbox.pack_start (button)
        button.connect ('clicked', self.update_cb)
        button = gtk.Button (_("Remove"))
        bbox.pack_start (button)
        button.connect ('clicked', self.remove_cb)

        h.pack_start (bbox, False, False)
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

    resize = True
    
    def __init__ (self, dtype, props, key = None, help_text=''):
        BaseConfig.__init__ (self, dtype, props, key)

        self.w = gtk.VBox (spacing = 5)
        h = gtk.HBox (spacing = 5)
        scroll = gtk.ScrolledWindow ()
        scroll.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.list = gtk.CList (2, (_("Key"), _("Value")))
        self.list.connect ('select-row', self.select_cb)
        self.list.set_column_auto_resize (0, True)
        
        scroll.add (self.list)
        h.pack_start (scroll)

        bbox = gtk.VButtonBox ()

        button = gtk.Button (_("Set"))
        bbox.pack_start (button)
        button.connect ('clicked', self.update_cb)
        button = gtk.Button (_("Remove"))
        bbox.pack_start (button)
        button.connect ('clicked', self.remove_cb)

        h.pack_start (bbox, False, False)
        self.w.pack_start (h)

        self.w.pack_start (gtk.HSeparator (), expand = False, fill = False)
        
        # Bottom
        table = gtk.Table (2, 2, homogeneous = False)
        table.set_row_spacings (5)
        table.set_col_spacings (5)
        table.attach (gtk.Label (_("Key:")), 0, 1, 0, 1,
                      xoptions = 0, yoptions = 0)
        table.attach (gtk.Label (_("Value:")), 0, 1, 1, 2,
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


# Local Variables:
# py-master-file: "tConfig.py"
# End:

