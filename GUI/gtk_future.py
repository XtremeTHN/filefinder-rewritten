import gi, threading, time
gi.require_versions({'Adw':'1','Gtk':'4.0'})
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from modules.funcs import jsonEx, finder, files_handler, compress
from shutil import move
Adw.init()

config = jsonEx.get('modules/configs.json')
class NotIterableError(Exception):
    pass

class SelcFolder(Gtk.FileChooserDialog):
    def __init__(self, **kwargs):
        super().__init__(transient_for=kwargs.get("parent"), use_header_bar=kwargs.get("use_header_bar"))
        try:
            self.callback = kwargs.get("callback")
            self.args = kwargs.get("args")
        except:
            self.callback = self.placeholder
            self.args = []
        self.type = kwargs.get("dialog_type")
        if type(self.args) not in [list,tuple]:
            raise NotIterableError("No es iterable")
        self.set_action(action=self.type)
        self.set_title(title=kwargs.get("title"))
        self.set_modal(modal=True)

        self.connect('response', self.response)
        self.add_buttons('_Cancelar', Gtk.ResponseType.CANCEL,
                         '_Seleccionar', Gtk.ResponseType.OK)
        self.show()
    
    def response(self, widget, response_w):
        if response_w == Gtk.ResponseType.OK:
            if self.args:
                temp_list = ['"{}"'.format(elem) for elem in self.args]
                exec("self.callback(self.get_file().get_path(), {})".format(', '.join(temp_list)))
            else:
                self.callback(self.get_file().get_path())
        widget.close()
    
    def placeholder(self, file):
        pass

class ResultsWindow(Gtk.Dialog):
    def __init__(self, **kwargs):
        path = kwargs.get("path")
        ext = kwargs.get("ext")
        del kwargs["path"], kwargs["ext"]
        super().__init__(**kwargs)

        self.set_title(title='Resultados')
        self.set_default_size(width=600, height=400)
        self.set_size_request(width=600, height=400)

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        self.set_child(child=vbox)

        # Janela com rolagem onde será adicionado o Gtk.TreeView().
        scrolled_window = Gtk.ScrolledWindow.new()
        vbox.append(child=scrolled_window)

        # Criando um modelo com `Gtk.ListStore()`.
        self.list_store = Gtk.ListStore.new(
            [GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_INT, GObject.TYPE_INT],
        )

        self.find_obj = finder(path, ext)
        self.files = self.find_obj.find()
        for x in self.find_obj.generalize():
            self.list_store.append(files_handler.stat(x))

        # Criando um `Gtk.TreeView()`.
        tree_view = Gtk.TreeView.new_with_model(model=self.list_store)
        tree_view.set_vexpand(expand=True)
        scrolled_window.set_child(child=tree_view)

        # Nome das colunas (title).
        cols = ('Nombre', 'Directorio', 'Extension', 'Fecha de modificacion', 'Tamaño', 'UID')
        for i, col in enumerate(cols):
            # Renderizador
            cell_render = Gtk.CellRendererText.new()

            treeviewcolumn = Gtk.TreeViewColumn(
                title=col,
                cell_renderer=cell_render,
                text=i,
            )

            # Agregando al Gtk.TreeView
            tree_view.append_column(column=treeviewcolumn)

        hbuton_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.progressbar = Gtk.ProgressBar()
        self.files_btt = Gtk.Button.new()
        self.comp_btt = Gtk.Button.new()
        self.mv_btt = Gtk.Button.new()

        self.progressbar.set_show_text(True)
        self.progressbar.set_pulse_step(1 / len(self.find_obj.generalize()))

        self.files_btt.set_label("Guardar resultados")
        self.comp_btt.set_label("Comprimir")
        self.mv_btt.set_label("Mover")

        self.files_btt.connect('clicked', self.on_files_btt_clicked)
        self.comp_btt.connect('clicked', self.on_comp_btt_clicked)
        self.mv_btt.connect('clicked', self.on_mv_btt_clicked)

        hbuton_box.set_homogeneous(True)
        hbuton_box.append(self.files_btt)
        hbuton_box.append(self.comp_btt)
        hbuton_box.append(self.mv_btt)
        vbox.append(child=hbuton_box)
        vbox.append(child=self.progressbar)
    
    def disable_buttons(self):
        self.mv_btt.set_sensitive(False)
        self.comp_btt.set_sensitive(False)
        self.files_btt.set_sensitive(False)
    
    def enable_buttons(self):
        self.mv_btt.set_sensitive(True)
        self.comp_btt.set_sensitive(True)
        self.files_btt.set_sensitive(True)
    
    def on_files_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona en donde quieres guardar el archivo",
                   dialog_type=Gtk.FileChooserAction.SAVE, callback=self.files_btt_callback, args=[])

    def files_btt_callback(self, filepath):
        files_handler.save(filepath,self.find_obj.generalize())
    
    def on_comp_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona como quieres guardar tu archivo comprimido",
                   dialog_type=Gtk.FileChooserAction.SAVE, callback=self.comp_btt_callback, args=())
    
    def comp_btt_callback(self, filename):
        self.comp_obj = compress(filename, format='zip')
        threading.Thread(target=self.compress_thread).start()
    
    def compress_thread(self):
        self.disable_buttons()
        for x,v in enumerate(self.find_obj.generalize()):
            self.comp_obj.add_single(v)
            GLib.idle_add(self.progressbar.set_fraction, x / len(self.find_obj.generalize()))
            GLib.idle_add(self.progressbar.set_text, v)
            if config['delay_progress_bar']:
                time.sleep(config['seconds_delay'])

        self.comp_obj.finish()
        self.enable_buttons()
    
    def on_mv_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona la carpeta en donde quieras mover los archivos",
                   dialog_type=Gtk.FileChooserAction.SELECT_FOLDER, callback=self.mv_btt_callback, args=[])
    
    def mv_btt_callback(self, filepath):
        for x,v in enumerate(self.find_obj.generalize()):
            try:
                move(v, filepath)
                GLib.idle_add(self.progressbar.set_fraction, x / len(self.find_obj.generalize()))
                GLib.idle_add(self.progressbar.set_text, v)
            except:
                continue

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(title='PyFileFinder')
        self.set_default_size(width=500, height=100)
        self.set_size_request(width=500, height=100)

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        self.box = Gtk.Box()
        self.button_box = Gtk.Box()
        self.center_box = Gtk.CenterBox()
        self.center_box2 = Gtk.CenterBox()
        self.label_input = Gtk.Label()
        self.label_combo = Gtk.Label()
        self.input = Gtk.Entry()
        self.button1 = Gtk.Button()
        self.button2 = Gtk.Button()
        self.button3 = Gtk.Button()
        self.combobox = Gtk.ComboBox()

        self.label_input.set_label("Directorio a buscar")
        self.label_combo.set_label("Extensiones por filtrar")
        self.button1.set_label("...")
        self.button2.set_label("Otra extension")
        self.button3.set_label("Buscar")
        self.center_box.set_start_widget(child=self.label_input)
        self.center_box.set_center_widget(child=self.input)
        self.center_box.set_end_widget(child=self.button1)

        self.button1.connect('clicked', self.on_exam_clicked)
        self.button2.connect('clicked', self.on_other_ext_clicked)
        self.button3.connect('clicked', self.on_find_clicked)

        

        self.center_box2.set_start_widget(child=self.label_combo)
        self.center_box2.set_center_widget(child=self.combobox)
        self.center_box2.set_end_widget(child=self.button2)

        self.center_box.set_margin_top(margin=12)
        self.center_box.set_margin_end(margin=12)
        self.center_box.set_margin_bottom(margin=12)
        self.center_box.set_margin_start(margin=12)
        self.center_box2.set_margin_top(margin=12)
        self.center_box2.set_margin_end(margin=12)
        self.center_box2.set_margin_bottom(margin=12)
        self.center_box2.set_margin_start(margin=12)

        self.button_box.set_margin_top(margin=10)
        self.button_box.set_margin_start(margin=20)
        self.button_box.set_margin_end(margin=20)
        self.button_box.set_margin_bottom(margin=20)
        self.box.set_margin_top(margin=10)

        self.archive = Gtk.ListStore(str)
        for v in jsonEx.get('modules/exts.json'):
            self.archive.append([v])
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_model(self.archive)

        self.combobox.connect('changed', self.combo_on_changed)

        self.combo_selected = None

        self.box.append(child=self.center_box)
        self.box.append(child=self.center_box2)
        self.button_box.append(child=self.button3)
        self.button_box.set_homogeneous(True)
        self.box.append(child=self.button_box)
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_child(child=self.box)
    
    def combo_on_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.combo_selected = model[tree_iter][:2][0]
    
    def on_exam_clicked(self,btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona la carpeta en donde quieras buscar los archivos", 
                   dialog_type=Gtk.FileChooserAction.SELECT_FOLDER, callback=self.exam_callback, args=[])
        
    def exam_callback(self,filename):
        self.input.set_text(filename)

    def on_other_ext_clicked(self, btt):
        pass

    def on_find_clicked(self, btt):
        if self.combo_selected:
            ResultsWindow(path=self.input.get_text(), ext=self.combo_selected, transient_for=self).present()
        else:
            print("Error debug")

class MainApplication(Adw.Application):

    def __init__(self):
        super().__init__(application_id="com.github.FileFinder.XtremeTHN",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.create_action('quit', self.exit_app, ['<primary>q'])
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_preferences_action(self, action, param):
        print('Ação app.preferences foi ativa.')

    def exit_app(self, action, param):
        self.quit()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)

MainApplication().run()