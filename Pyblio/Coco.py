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
    def __init__(self, window=None, title=None,
                 *args, **argh):

        self.window = window
        self.progress = None
        self.title = title

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



    
class Importer (Base):
    """Import class -- to be developped."""

    def __init__(self, file=None, data=None, *args, **argh):
 
        Base.__init__(self, *args, **argh)
        return

    
