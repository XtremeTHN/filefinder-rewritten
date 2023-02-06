import gi, sys, os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Pango
from modules.funcs import jsonEx, files_handler, finder
Adw.init()
class DialogSelecFolder(Gtk.FileChooserDialog):
    # Definindo o diretório padrão.
    def __init__(self, parent, inputx=None, folder=True):
        self.input = inputx
        self.folder = folder
        super().__init__(transient_for=parent, use_header_bar=True)
        if folder:
            self.set_action(action=Gtk.FileChooserAction.SELECT_FOLDER)
            title = 'Selecciona la carpeta en donde se buscaran los archivos'
        else:
            self.set_action(action=Gtk.FileChooserAction.SAVE)
            title = 'Selecciona en donde quieres guardar los resultados'
        self.set_title(title=title)
        self.set_modal(modal=True)
        self.connect('response', self.dialog_response)

        self.add_buttons(
            '_Cancelar', Gtk.ResponseType.CANCEL,
            '_Seleccionar', Gtk.ResponseType.OK
        )

        self.show()

    def dialog_response(self, widget, response):
        print(response)
        if response == Gtk.ResponseType.OK:
            if self.folder:
                glocalfile = self.get_file()
                self.input.set_text(glocalfile.get_path())
            else:
                print(self.get_file().get_path, self.get_file().get_basename)
        widget.close()

class ResultsWindow(Gtk.Dialog):

    # Variável auxiliar que armazena o valor do filtro.
    current_filter_language = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(title='Resultados')
        self.set_default_size(width=int(1366 / 2), height=int(768 / 2))
        self.set_size_request(width=int(1366 / 2), height=int(768 / 2))

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        menu_button_model = Gio.Menu()
        menu_button_model.append('Preferências', 'app.preferences')

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name(icon_name='open-menu-symbolic')
        menu_button.set_menu_model(menu_model=menu_button_model)
        menu_button.connect('activate', self.headerbtt_clicked)
        menu_button.activate()
        headerbar.pack_end(child=menu_button)

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
        self.list_store = Gtk.ListStore(str, str, str, str, float, int)

        find_obj = finder(input1.get_text(),combo_selected)
        finded = find_obj.find()
        
        # Adicionando os dados no `Gtk.ListStore()`.
        for x in find_obj.all:
            print(files_handler.stat(x))
            self.list_store.append(files_handler.stat(x))

        # Criando um `Gtk.TreeView()`.
        tree_view = Gtk.TreeView.new_with_model(model=self.list_store)
        tree_view.set_vexpand(expand=True)
        scrolled_window.set_child(child=tree_view)

        # Nome das colunas (title)

        cols = ('Nombre', 'Directorio', 'Extension', 'Fecha de modificacion', 'Tamaño', 'UID')
        for i, col in enumerate(cols):
            # Criando um rederizador com para o tipo de dado que será exibido.
            cell_render = Gtk.CellRendererText.new()

            # Configurando o rederizador da primeira coluna.
            if i == 0:
                cell_render.set_property('weight_set', True)
                cell_render.set_property('weight', Pango.Weight.BOLD)

            # Criando a coluna.
            treeviewcolumn = Gtk.TreeViewColumn(
                # Titulo da coluna.
                title=col,
                # Rederizador que será utilizado na coluna.
                cell_renderer=cell_render,
                # Posição (index) da coluna.
                text=i,
            )

            # Adicionando a coluna no `Gtk.TreeView()`.
            tree_view.append_column(column=treeviewcolumn)

        hbuton_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        vbox.append(child=hbuton_box)
    def headerbtt_clicked(self, btt):
        DialogSelecFolder(self.get_parent(),folder=False)

class CustomDialog(Gtk.Dialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title='Informacion')
        self.use_header_bar = True
        self.connect('response', self.dialog_response)

        self.set_width = 600
        self.set_height = 300

        self.add_buttons(
            '_Aceptar', Gtk.ResponseType.OK,
        )

        btn_ok = self.get_widget_for_response(
            response_id=Gtk.ResponseType.OK,
        )
        btn_ok.get_style_context().add_class(class_name='suggested-action')

        content_area = self.get_content_area()
        content_area.set_orientation(orientation=Gtk.Orientation.VERTICAL)
        content_area.set_spacing(spacing=24)
        content_area.set_margin_top(margin=12)
        content_area.set_margin_end(margin=12)
        content_area.set_margin_bottom(margin=12)
        content_area.set_margin_start(margin=12)

        label = Gtk.Label.new(str=msg)
        content_area.append(child=label)
    def dialog_response(self,dialog,response):
        dialog.close()

class gtk(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.run()

    def combo_on_changed(self,combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.combo_selected = model[tree_iter][:2][0]

    def exam_clicked(self,btt):
        DialogSelecFolder(self.main_win, self.input1)

    def open_response(self,dialog, response):
        print(dialog.get_filename(), response)

    def find(self,btt):
        global msg
        if self.input1.get_text() == '':
            msg = 'Porfavor escribe una direccion en donde se buscaran los archivos'
            CustomDialog().present()
            return None
        elif not self.combo_selected:
            msg = 'Porfavor selecciona una extension de la lista'
            CustomDialog().present()
            return None
        global input1, combo_selected
        combo_selected = self.combo_selected
        input1 = self.input1
        ResultsWindow().present()
    def others_clicked(self,btt):
        print("Debug other")
    def on_activate(self,app):  
        # Definicion de objetos      
        self.builder = Gtk.Builder.new_from_file('GUI/.FRONTEND/gui.ui')
        self.main_win = self.builder.get_object('main_window')
        self.organizator = self.builder.get_object('organizator')
        self.input1 = self.builder.get_object("input1")
        self.combobox = self.builder.get_object("combo")
        self.btt1 = self.builder.get_object("exam_bt")
        self.btt2 = self.builder.get_object("other_btt")
        self.find_btt = self.builder.get_object("find")
        self.combo_selected = None

        #Agregando elementos a el ComboBox
        self.archive = Gtk.ListStore(str)
        for v in jsonEx.get('modules/exts.json'):
            self.archive.append([v])
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_model(self.archive)

        # Conectando señales
        self.combobox.connect('changed', self.combo_on_changed)
        self.btt1.connect('clicked', self.exam_clicked)
        self.btt2.connect('clicked', self.others_clicked)
        self.find_btt.connect('clicked', self.find)
        self.add_window(self.main_win)
        self.main_win.present()