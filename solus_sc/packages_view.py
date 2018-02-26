#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GLib, GdkPixbuf
from gi.repository import AppStreamGlib as As

""" enum for the model fields """
INDEX_FIELD_DISPLAY = 0
INDEX_FIELD_NAME = 1
INDEX_FIELD_ICON = 2
INDEX_FIELD_ARROW = 3


class LoadingPage(Gtk.VBox):
    """ Simple loading page, nothing fancy. """

    spinner = None

    def __init__(self, message=""):
        Gtk.VBox.__init__(self)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(-1, 64)
        self.spinner.start()
        # Loading available packages (witty loading screen)
        self.label = Gtk.Label()
        self.set_message(message)

        self.pack_start(self.spinner, True, True, 0)
        self.pack_start(self.label, False, False, 0)
        self.label.set_property("margin", 20)

    def set_message(self, message):
        self.label.set_markup(u"<big>{}…</big>".format(message))


def render_plain(input_string):
    """ Render a plain version of the description, no markdown """
    plain = As.markup_convert_simple(input_string)
    plain = plain.replace("&quot;", "\"").replace("&apos;", "'").replace("&amp;", "&")
    return plain


class ScPackagesView(Gtk.VBox):
    appsystem = None
    basket = None
    owner = None
    stack = None
    scroll = None
    tview = None
    load_page = None

    def __init__(self, owner, basket, appsystem):
        Gtk.VBox.__init__(self, 0)
        self.basket = basket
        self.appsystem = appsystem
        self.owner = owner

        self.stack = Gtk.Stack()
        t = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.stack.set_transition_type(t)
        self.pack_start(self.stack, True, True, 0)

        self.load_page = LoadingPage()
        self.stack.add_named(self.load_page, "loading")

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroll.set_overlay_scrolling(False)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_property("kinetic-scrolling", True)
        self.stack.add_named(self.scroll, "packages")

        # Main treeview where it's all happening. Single click activate
        self.tview = Gtk.TreeView()
        self.tview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.tview.connect_after('row-activated', self.on_row_activated)
        self.tview.set_activate_on_single_click(True)

        # Defugly
        self.tview.set_property("enable-grid-lines", False)
        self.tview.set_property("headers-visible", False)
        self.scroll.add(self.tview)

        # Installed
        ren = Gtk.CellRendererPixbuf()
        ren.set_padding(5, 5)
        ren.set_property("icon-name", "object-select-symbolic")
        column = Gtk.TreeViewColumn("Installed", ren, visible=4)
        # set to true by 'display-installed 'tview option
        column.set_visible(False)
        self.tview.append_column(column)

        # img view
        ren = Gtk.CellRendererPixbuf()
        ren.set_property("stock-size", Gtk.IconSize.DIALOG)
        ren.set_padding(5, 2)
        column = Gtk.TreeViewColumn("Icon", ren, pixbuf=2)
        self.tview.append_column(column)

        # Set up display columns
        ren = Gtk.CellRendererText()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Name", ren, markup=0)
        self.tview.append_column(column)
        self.tview.set_search_column(1)

        # Details
        ren = Gtk.CellRendererPixbuf()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Details", ren, icon_name=3)
        self.tview.append_column(column)
        ren.set_property("xalign", 1.0)

        self.tview_options = {}
        # Must be called after creating columns
        self.set_tview_option("display-installed", True)

    def get_tview_option(self, key):
        return self.tview_options[key]

    def refresh_tview(self):
        if self.get_tview_option("display-installed"):
            self.tview.get_column(0).set_visible(True)

    def set_tview_option(self, key, val):
        self.tview_options[key] = val
        self.refresh_tview()

    @staticmethod
    def get_pkg_name_from_path(tview, path):
        model = tview.get_model()
        row = model[path]

        return row[INDEX_FIELD_NAME]

    @staticmethod
    def get_model():
        # name and description, name, icon, details (icon), install state
        return Gtk.ListStore(str, str, GdkPixbuf.Pixbuf, str, bool)

    def get_pkg_model(self, pkg):
        summary = self.appsystem.get_summary(pkg)
        summary = render_plain(str(summary))

        if len(summary) > 76:
            summary = "%s…" % summary[0:76]

        name = self.appsystem.get_name(pkg)
        p_print = "<b>%s</b> - %s\n%s" % (name, str(pkg.version),
                                          summary)

        pbuf = self.appsystem.get_pixbuf_only(pkg)

        installed = False
        if self.get_tview_option("display-installed") and self.basket.installdb.has_package(pkg.name):
            installed = True

        return [p_print, pkg.name, pbuf, "go-next-symbolic", installed]

    def reset(self):
        self.tview.set_model(None)
        self.stack.set_visible_child_name("loading")
        self.load_page.spinner.start()
        self.queue_draw()
