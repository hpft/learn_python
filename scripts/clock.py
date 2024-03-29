#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gobject
import pango
import gtk
import math
import time
from gtk import gdk
try:
    import cairo
except ImportError:
    pass

if gtk.pygtk_version < (2,3,93):
    print "PyGtk 2.3.93 or later required"
    raise SystemExit

TEXT = 'PFT: cairo'
BORDER_WIDTH = 10

def progress_timeout(object):
    x, y, w, h = object.allocation
    object.window.invalidate_rect((0,0,w,h),False)
    return True

class PyGtkWidget(gtk.Widget):
    __gsignals__ = { 'realize': 'override',
                     'expose-event' : 'override',
                     'size-allocate': 'override',
                     'size-request': 'override',}

    def __init__(self):
        gtk.Widget.__init__(self)
        self.draw_gc = None
        self.layout = self.create_pango_layout(TEXT)
        self.layout.set_font_description(pango.FontDescription("sans serif 8"))
        self.timer = gobject.timeout_add (1000, progress_timeout, self)
                                           
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=self.get_events() | gdk.EXPOSURE_MASK)
        if not hasattr(self.window, "cairo_create"):
            self.draw_gc = gdk.GC(self.window,
                                  line_width=5,
                                  line_style=gdk.SOLID,
                                  join_style=gdk.JOIN_ROUND)

	self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)

    def do_size_request(self, requisition):
	width, height = self.layout.get_size()
	requisition.width = (width // pango.SCALE + BORDER_WIDTH*4)* 1.45
	requisition.height = (3 * height // pango.SCALE + BORDER_WIDTH*4) * 1.2

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def _expose_gdk(self, event):
        x, y, w, h = self.allocation
        self.layout = self.create_pango_layout('no cairo')
        fontw, fonth = self.layout.get_pixel_size()
        self.style.paint_layout(self.window, self.state, False,
                                event.area, self, "label",
                                (w - fontw) / 2, (h - fonth) / 2,
                                self.layout)

    def _expose_cairo(self, event, cr):
        
        # time 

        hours = time.localtime().tm_hour
        minutes = time.localtime().tm_min
        secs = time.localtime().tm_sec

        sec_arc= (2*math.pi / 60) * secs
        minute_arc = (2*math.pi / 60) * minutes
        if hours > 12:
            hours = hours - 12       
        hour_arc = (2*math.pi / 12) * hours + minute_arc / 12
       
        # clock background

        x, y, w, h = self.allocation
        cr.set_source_rgba(1, 0.2, 0.2, 0.6)
        cr.arc(w/2, h/2, min(w,h)/2 - 8 , 0, 2 * 3.14) 
        cr.fill()
        cr.stroke()

        # center arc

        cr.set_source_color(self.style.fg[self.state])
        cr.arc ( w/2, h/2, (min(w,h)/2 -20) / 5, 0, 2 * math.pi)
        cr.fill()
        cr.line_to(w/2,h/2)
        cr.stroke()

        # pointer hour

        cr.set_source_color(self.style.fg[self.state])
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5) 
        cr.set_line_width ((min(w,h)/2 -20)/6 )
        cr.move_to(w/2,h/2)
        cr.line_to(w/2 + (min(w,h)/2 -20) * 0.6 * math.cos(hour_arc - math.pi/2),
            h/2 + (min(w,h)/2 -20) * 0.6 * math.sin(hour_arc - math.pi/2))
        cr.stroke()

        # pointer minute

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5) 
        cr.set_line_width ((min(w,h)/2 -20)/6 * 0.8)
        cr.move_to(w/2,h/2)
        cr.line_to(w/2 + (min(w,h)/2 -20) * 0.8 * math.cos(minute_arc - math.pi/2), 
            h/2 + (min(w,h)/2 -20) * 0.8 * math.sin(minute_arc - math.pi/2))
        cr.stroke()

        # pointer second

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5) 
        cr.set_line_width ((min(w,h)/2 -20)/6 * 0.6)
        cr.move_to(w/2,h/2)
        cr.line_to(w/2 + (min(w,h)/2 -20) * 0.9 * math.cos(sec_arc - math.pi/2), 
            h/2 + (min(w,h)/2 -20) * 0.9 * math.sin(sec_arc - math.pi/2))
        cr.stroke()


        # pango layout 
        
        fontw, fonth = self.layout.get_pixel_size()
        cr.move_to((w - fontw - 4), (h - fonth ))
        cr.update_layout(self.layout)
        cr.show_layout(self.layout)
        
    def do_expose_event(self, event):
        self.chain(event)
        try:
            cr = self.window.cairo_create()
        except AttributeError:
            return self._expose_gdk(event)
        return self._expose_cairo(event, cr)

win = gtk.Window()
win.set_title('clock')
win.connect('delete-event', gtk.main_quit)

event_box = gtk.EventBox()
event_box.connect("button_press_event", lambda w,e: win.set_decorated(not win.get_decorated()))

win.add(event_box)

w = PyGtkWidget()
event_box.add(w)

win.move(gtk.gdk.screen_width() - 120, 40)
win.show_all()

gtk.main()
    
