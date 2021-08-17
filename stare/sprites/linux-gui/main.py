#!/usr/bin/env python

"""
 Copyright (C) 2003-2008 by the Battle for Wesnoth Project <www.wesnoth.org>
 Copyright (C) 2008, 2009, 2010 by Ignacio R. Morelle <shadowm2006@gmail.com>

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

APP_NAME = "Wesnoth-TC"
APP_VERSION = '1.5.0'

import sys

try:
    import pygtk
    import gtk
    a = gtk.check_version(2, 10, 0)
    if a:
        print a
        sys.exit(1)
except:
    print "Please install pyGTK version 2.10 or later"
    sys.exit(1)
try:
    import gtk.glade
    import gobject
    import cairo
    import os
except ImportError, error_message:
    error_dialog = gtk.MessageDialog(None
                      , gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
                      , gtk.MESSAGE_ERROR
                      , gtk.BUTTONS_CLOSE,
                      "Bah, Humbug.")
    error_dialog.format_secondary_text(str(error_message) + "\nPlease install the missing modules")
    error_dialog.run()
    error_dialog.destroy()
    sys.exit(1)

class WesnothTC:
    
    def __init__(self):
        self.local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
        self.filename=None
        self.rcfilename=None
        self.colour = 0
        
        #Initialise the Glade GUI environment
        self.wTree = gtk.glade.XML("gui.glade", "MainWindow")
        self.window = self.wTree.get_widget("MainWindow")
        self.wTree.signal_autoconnect(self)
        self.window.set_title("WesnothTC")
        
        if self.window:
            self.window.connect("destroy", gtk.main_quit)
        
        #Set up the team colour chooser box
        self.ColourPickerWidget = self.wTree.get_widget("colourpicker1")
        self.wTree.get_widget("colourpicker1").connect("changed", self.on_colourpicker1_changed)
        self.ColourPickerWidget.set_active(0)
        
        #Hook up some signals
        self.wTree.get_widget("fileloader").connect("clicked", self.on_filechooser_clicked)
        
        self.draw_original()
    
    def open_dialogue(self):
        """Opens the open file dialogue"""
        
        #Initialise the dialog
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        chooser = gtk.FileChooserDialog("Choose file", self.window, 
                                        gtk.FILE_CHOOSER_ACTION_OPEN, buttons)
        filter = gtk.FileFilter()
        #Create the file filters
        filter.set_name("PNG files")
        filter.add_pattern("*.png")
        chooser.add_filter(filter)
        if self.filename:
            self.oimage = cairo.ImageSurface.create_from_png(self.filename)
            chooser.set_filename(self.filename)
        #Run the dialog
        if chooser.run() == gtk.RESPONSE_OK:
            self.new_filename = chooser.get_filename()
            self.filename=self.new_filename
            
            self.colourize()
            
            chooser.destroy()
            self.draw_original()
            return True
        else:
            chooser.destroy()
            return None
    
    def colourize(self):
        os.system("wesnoth-tc " + str(self.filename) + " --tc " + str(self.colour+1) + " > /dev/null")
        self.rcfilename=self.new_filename[:-4]+"-RC-magenta-"+str(self.colour+1)+".png"
        #print self.new_filename[:-4]+"-RC-magenta-"+str(self.colour+1)+".png"
        #print "wesnoth-tc " + str(self.filename) + " --tc " + str(self.colour+1) + " > /dev/null"
        self.oimage = cairo.ImageSurface.create_from_png(self.filename)
        self.rcimage = cairo.ImageSurface.create_from_png(self.rcfilename)
        os.system("rm -f " + self.rcfilename)
        self.draw_recoloured()
    
    def draw_original(self):
        original_cairo_widget = self.wTree.get_widget("original")
        surface = original_cairo_widget.window.cairo_create()
        size_x, size_y = original_cairo_widget.window.get_size()
        
        surface.move_to(0, 0)
        surface.set_source_rgb(1, 1, 1)
        surface.rectangle(0, 0, size_x, size_y)
        surface.fill()
        
        if self.filename:
            surface.set_source_surface(self.oimage, 69, 69)
            surface.paint()
    
    def draw_recoloured(self):
        recoloured_cairo_widget = self.wTree.get_widget("recoloured")
        surface = recoloured_cairo_widget.window.cairo_create()
        size_x, size_y = recoloured_cairo_widget.window.get_size()
        
        surface.move_to(0, 0)
        surface.set_source_rgb(1, 1, 1)
        surface.rectangle(0, 0, size_x, size_y)
        surface.fill()
        
        if self.filename:
            surface.set_source_surface(self.rcimage, 69, 69)
            surface.paint()
            #print self.rcfilename
    
    #Signal Handlers
    def on_colourpicker1_changed(self, widget):
        self.colour = self.ColourPickerWidget.get_active()
        #print self.ColourPickerWidget.get_active()
        if self.filename:
            self.colourize()
    
    def on_filechooser_clicked(self, widget):
        self.open_dialogue()
    
    def on_original_expose_event(self, widget, signal):
        self.draw_original()
    
    def on_recoloured_expose_event(self, widget, signal):
        self.draw_recoloured()

"""
***********************************************************
*                                                         *
* Main Loop                                               *
*                                                         *
***********************************************************
"""
if __name__ == "__main__":
    main = WesnothTC()
    gtk.main()