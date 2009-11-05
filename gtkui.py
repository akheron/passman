import random

import pygtk
try:
    pygtk.require('2.0')
except AssertionError, err:
    raise ImportError("gtk: %s" % err.message)
import gtk
import gobject


class EntryDialog(gtk.Dialog):
    def __init__(self, title=None, parent=None):
        gtk.Dialog.__init__(self, title=title, parent=parent)
        self.set_modal(True)
        self.set_has_separator(False)
        self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                           gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)

        table = gtk.Table(rows=3, columns=2)
        table.set_col_spacing(0, 5)
        table.set_row_spacings(5)
        table.attach(gtk.Label('Entry ID'), 0, 1, 0, 1)
        table.attach(gtk.Label('Username'), 0, 1, 1, 2)
        table.attach(gtk.Label('Password'), 0, 1, 2, 3)
        table.attach(gtk.Label('URL'), 0, 1, 3, 4)
        table.attach(gtk.Entry(), 1, 2, 0, 1)
        table.attach(gtk.Entry(), 1, 2, 1, 2)
        table.attach(gtk.Entry(), 1, 2, 2, 3)
        table.attach(gtk.Entry(), 1, 2, 3, 4)
        table.show_all()
        self.vbox.pack_start(table)


class GtkUI(object):
    def _delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def _treeview_button_press(self, treeview, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            _, treeiter = treeview.get_selection().get_selected()
            dialog = EntryDialog(title='Entry', parent=self.main_window)
            print dialog.run()
            dialog.destroy()
            # kesken


    def msg(self, text):
        pass

    def run(self, passdb):
        # Model
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for entry in passdb:
            model.set(model.append(),
                      0, entry.name,
                      1, entry.desc)

        # Main window
        self.main_window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Password Manager")
        window.connect("delete_event", self._delete_event)
        window.set_default_size(500, 350)
        window.set_border_width(5)

        sw = gtk.ScrolledWindow()
        window.add(sw)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        treeview = gtk.TreeView(model)
        sw.add(treeview)
        treeview.set_rules_hint(True)
        treeview.connect('button-press-event', self._treeview_button_press)

        renderer = gtk.CellRendererText()
        name_column = gtk.TreeViewColumn('Name', renderer, text=0)
        name_column.set_resizable(True)
        name_column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        name_column.set_sort_column_id(0)
        treeview.append_column(name_column)

        renderer = gtk.CellRendererText()
        desc_column = gtk.TreeViewColumn('Short description', renderer, text=1)
        desc_column.set_resizable(True)
        desc_column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        desc_column.set_sort_column_id(1)
        treeview.append_column(desc_column)

        # Sort initially by the 'Name' column
        name_column.emit("clicked")

        # Run
        self.main_window.show_all()
        gtk.main()


if __name__ == '__main__':
    class Entry:
        def __init__(self, a, b):
            self.name = a
            self.desc = b

    GtkUI().run([
        Entry('foo', 'bar'),
        Entry('bar', 'baz'),
        Entry('baz', 'buzz')]*3)
