# This file is part of pybliographer
# 
# Copyright (C) 2002, Peter Schulte-Stracke
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

"""Collection of Control Objects for Pybliographer --

      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

Classes in this module represent user interface object and in addition
serve to decouple the components of Pybliographer from each other.

Class Base provides for title and progress indications.
Class Folder provides for classifiaction of entries.
Classes Import, Query, Scan maintain information about
        current or recent activity.
Class Connection decribes an external ressource.

"""

class Base:

    """Central Control Object for Pybliographer.


    """
    _typ = 'any'
    
    def __init__(self, title='unnamed', window=None, 
                 *args, **argh):
        

        self.dict = argh

        self.title = title
        self.window = window

        self.progress = 0


    def __getitem__ (self, key):
	''' Returns the property named  key '''
	return self.dict [key]

    def __setitem__ (self, key, value):
	''' Sets a proerty '''
        self.dict [key] = value
	return

    def __delitem__ (self, key):
	''' Removes a Property'''
	del self.dict [key]
    

    def start (self, *args, **argh): pass
    
    def set_progress (self, position=None, target=None, add=None):
        """set_progress ([position,] [target=maximum] add=increment)
        either adjusts the rogress bar, if a window is assigned,
        or stores the possible maximum (= 100 %) of its value.

        Set target to -1 to indicate that it is unknown.
        Set position to 0 to indicate completion.
        Call set_position () to clear the position bar.
        """

        
        if target:
            self.progress_max = target
        if add:
            print add, type(add)
            self.progress = self.progress + add
        if position:
            self.progress = position
        try:
            if self.position_max:
                if position == 0:
                    percentage = 100.0
                    return
                if self.position_max > 0:
                    percentage = 100.0 * self.position_max / self.position
                else:
                    percentage = -100.0 * self.position_max / self.position
                    if percentage > 100.0 :
                        percentage = 30.0
                        self.position_max = 3*self.position
                    elif percentage > 90.0:
                        percentage = .7 * percentage
                        self.position_max = 1.4 * self.position_max
            else: percentage = 0
            if self.window:
                self.window.set_position(percentage)
        except:
            pass
        return


    def set_title (self, title):
        """set_title (title) sets the (window) title """

        if title:
            self.title = title
        return

    def set_window (self, window):
        """set_window (window) (re)sets the associated window.
        Note that it is possible to remove the association with
        set_window (None)."""

        
        self.window = window
        return



class RecordSet (Base):
    _typ='rs'

class DataBase (Base):
    _type='DB'
    
class Importer (RecordSet):
    """Import class -- to be developped."""
    _typ='im'
    
    def __init__(self, file=None, data=None, *args, **argh):
 
        Base.__init__(self, *args, **argh)
        return

class InputFile(Importer):
    _typ = 'in'


    
def save_configuration():
    
    return

def reset_configuration(db):
    
    return

