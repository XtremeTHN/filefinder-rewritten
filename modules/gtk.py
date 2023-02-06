import gi, sys
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class gtk():
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("GUI/.FRONTEND/gui.ui")
        main_win = builder.get_object("main_window")
        input1 = builder.get_object("input")
        input2 = builder.get_object("input2")
        combobox = builder.get_object("combobox")

        main_win.set_title("FileFinder")
    class funcs:

        def combo_on_changed(combo):
            print(combo.get_active_id())

    def on_activate(self, app):
        data = []
        for x in jsonEx.get("../modules/exts.json"):
            data.append(x)
        builder = Gtk.Builder.new_from_file('.FRONTEND/gui.ui')
        main_win = builder.get_object('main_window')
        input1 = builder.get_object("input")
        combobox = builder.get_object("combo")
        btt1 = builder.get_object("exam_bt")
        btt2 = builder.get_object("other_btt")
        archive = Gtk.ListStore(str)
        archive.append(data)
        combobox.set_model(archive)
        combobox.connect('changed', self.funcs.combo_on_changed)
        app.add_window(main_win)
        main_win.present()
    def init(self):
        app = Gtk.Application(application_id='com.example.GtkApplication')
        app.connect('activate', self.on_activate)
        app.run()