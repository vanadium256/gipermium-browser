import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

class GiperiumBrowser(Gtk.Window):
    def __init__(self):
        super().__init__(title="Giperium Browser")
        self.set_default_size(800, 600)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.tabs = []
        self.bookmarks = []  # Список закладок
        self.create_new_tab()

        self.show_all()

        # Создаем панель инструментов
        self.toolbar = Gtk.Toolbar()
        new_tab_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        bookmark_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        bookmark_view_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_JUMP_TO)

        new_tab_button.connect("clicked", self.create_new_tab)
        bookmark_button.connect("clicked", self.on_bookmark_button_clicked)
        bookmark_view_button.connect("clicked", self.show_bookmarks)

        self.toolbar.insert(new_tab_button, 0)
        self.toolbar.insert(bookmark_button, 1)
        self.toolbar.insert(bookmark_view_button, 2)

        self.notebook.set_show_tabs(True)
        self.notebook.set_show_border(True)

        # Добавляем панель инструментов в окно
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(self.notebook, True, True, 0)
        self.add(vbox)

    def create_new_tab(self, url="https://www.google.com"):
        tab_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        webview = WebKit2.WebView()
        webview.load_uri(url)

        # Ячейка для отображения текущего URL
        self.url_entry = Gtk.Entry()
        self.url_entry.set_text(url)
        self.url_entry.connect("activate", self.on_url_entry_activate, webview)

        # Создаем панель инструментов для вкладки
        toolbar = Gtk.Toolbar()
        back_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_BACK)
        forward_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_FORWARD)
        reload_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REFRESH)

        back_button.connect("clicked", self.on_back_button_clicked, webview)
        forward_button.connect("clicked", self.on_forward_button_clicked, webview)
        reload_button.connect("clicked", self.on_reload_button_clicked, webview)

        toolbar.insert(back_button, 0)
        toolbar.insert(forward_button, 1)
        toolbar.insert(reload_button, 2)

        # Добавляем виджет URL и панель инструментов в вкладку
        tab_box.pack_start(toolbar, False, False, 0)
        tab_box.pack_start(self.url_entry, False, False, 0)
        tab_box.pack_start(webview, True, True, 0)

        # Добавляем вкладку в Notebook
        tab_label = Gtk.Label("Tab {}".format(len(self.tabs) + 1))
        self.notebook.append_page(tab_box, tab_label)

        self.tabs.append(webview)

        # Обработчик изменения URL
        webview.connect("load-changed", self.on_load_changed, webview)

    def on_back_button_clicked(self, button, webview):
        if webview.can_go_back():
            webview.go_back()

    def on_forward_button_clicked(self, button, webview):
        if webview.can_go_forward():
            webview.go_forward()

    def on_reload_button_clicked(self, button, webview):
        webview.reload()

    def on_bookmark_button_clicked(self, button):
        # Получаем текущий веб-вью и его URL
        webview = self.tabs[self.notebook.get_current_page()]
        uri = webview.get_uri()
        if uri and uri not in self.bookmarks:
            self.bookmarks.append(uri)
            print("Bookmark added:", uri)  # Здесь можно добавить логику для сохранения закладок

    def show_bookmarks(self, button):
        dialog = Gtk.Dialog("Bookmarks", self, Gtk.DialogFlags.MODAL)
        dialog.set_default_size(300, 200)

        liststore = Gtk.ListStore(str)
        for bookmark in self.bookmarks:
            liststore.append([bookmark])

        treeview = Gtk.TreeView(model=liststore)
        renderer = Gtk.CellRendererText()
        # Добавляем TreeView в диалог
        column = Gtk.TreeViewColumn("Bookmarks", renderer, text=0)
        treeview.append_column(column)
        dialog.vbox.pack_start(treeview, True, True, 0)

        # Устанавливаем обработчик для выбора закладки
        treeview.connect("row-activated", self.on_bookmark_selected, dialog)

        dialog.show_all()

        # Устанавливаем обработчик закрытия диалога
        dialog.connect("response", lambda d, r: d.destroy())

    def on_bookmark_selected(self, treeview, path, column, dialog):
        model = treeview.get_model()
        selected_bookmark = model[path][0]
        self.create_new_tab(selected_bookmark)  # Открываем закладку в новой вкладке
        dialog.destroy()  # Закрываем диалог

    def on_url_entry_activate(self, entry, webview):
        url = entry.get_text()
        webview.load_uri(url)

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.COMMITTED:
            uri = webview.get_uri()
            self.url_entry.set_text(uri)  # Обновляем URL в ячейке

    def on_tab_switch(self, notebook, page, page_num):
        self.current_tab = self.tabs[page_num]

    def on_destroy(self, widget):
        Gtk.main_quit()

if __name__ == "__main__":
    browser = GiperiumBrowser()
    browser.connect("destroy", Gtk.main_quit)
    Gtk.main()

