
from gi.repository import Gtk, Gio, Gdk, WebKit2, GLib
import requests
import os
import urllib

class DummyTab(Gtk.Box):
    def __init__(self):
        super().__init__()



class Tab(WebKit2.WebView):
    def __init__(self, mainWindow, url=None):
        super().__init__()
        
        self.NEWTABPATH = 'templates/newtab.html'
        self.CONTROLSPATH = 'templates/controls.html'
    

        if url is None:
            self.url = 'surfwd://newtab'
        else:
            self.url = url
            
        self.mainWindow = mainWindow
        self.navigate_to_url(self.url)

        

    def formulate_link(self, link):
        protocols = ('http://', 'https://', 'ftp://', 'swd://', 'surfwd://')
        
        if link.startswith(protocols):
            return link
        
        link = protocols[1] + link
        
        return link


    def handle_custom_uri(self, req_page):
        if req_page == 'newtab':
            with open(self.NEWTABPATH, 'r') as f:
                html = f.read()
            self.load_html(html, f'surfwd://{req_page}')
            
        if req_page == 'controls':
            with open(self.CONTROLSPATH, 'r') as f:
                html = f.read()
            self.load_html(html, f'surfwd://{req_page}')
            
            

        
    def navigate_to_url(self, query, *args):
        if self.isLink(query):
            link = self.formulate_link(query)
            self.load_uri(link)
            
        elif self.isCustomUri(query):

            req_page = query.lstrip('surfwd://')
            self.handle_custom_uri(req_page)
            link = self.formulate_link(query)
            
        else:
            link = f'{self.mainWindow.searchEngine}/search?q={query}'
            self.load_uri(link)
            
            
        self.set_url(link)
        self.mainWindow.remove_home_uri(self)


    def isLink(self, txt:str):
        domain_suffixes= self.get_domain_suffixes()

        ltext=txt.lower().split('/')[0]
        return ltext.startswith(('http','www','ftp', 'swd')) or ltext.endswith(domain_suffixes)

    def isCustomUri(self, txt:str):
        return txt.startswith('surfwd://')
            



    def set_url(self, url):
        self.mainWindow.urlbar.props.text = url
        
    def goback(self, *args):
        self.go_back()
        
    def goforward(self, *args):
        self.go_forward()
        
    def gohome(self, *args):
        self.navigate_to_url(self.mainWindow.homePage)
        
    def refresh(self, *args):
        print('done')
        self.navigate_to_url(self.get_uri())
        


    def get_domain_suffixes(self):
        try:
            req = requests.get('https://publicsuffix.org/list/public_suffix_list.dat')
            res = req.text
        except Exception as e:
            with open('public_suffix_list.dat', 'r') as f:
                res = f.read()
                
        lst=set()
        
        for line in res.split('\n'):
            if not line.startswith('//'):
                domains=line.split('.')
                cand=domains[-1]
                if cand:
                    lst.add('.' + cand)
                    
        return tuple(sorted(lst))



class MainWindow(Gtk.Window):
    def __init__(self):
        
        super().__init__(title="HeaderBar Demo")
        
        context = WebKit2.WebContext.get_default()


        self.cookies = context.get_cookie_manager()
        self.manager = WebKit2.UserContentManager()

        cookiesPath = '/tmp/cookies.txt'
        storage = WebKit2.CookiePersistentStorage.TEXT
        policy = WebKit2.CookieAcceptPolicy.ALWAYS

        self.cookies.set_accept_policy(policy)
        self.cookies.set_persistent_storage(cookiesPath, storage)


        self.cookies.connect("changed", self.cookies_change)
        
        self.set_border_width(10)
        self.set_default_size(900, 600)
        
        self.maximized = False
        
        self.tabCloseBtns = {} 
        
        self.searchEngine = 'https://www.google.com'
        self.homePage = 'surfwd://newtab'
       


        self.connect("window-state-event", self.on_window_state_event)
        self.connect("key-release-event", self.checkShortcuts) 
        
        self.style_context = Gtk.StyleContext()
        
        try: 
            
            self.bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL).to_string()
            print(self.bg_color)
            
            if self.bg_color is None:
                self.bg_color = "black"
            
        except:
            self.bg_color = "black"

        self.set_border_width(2)
        
        
        self.draw_header_bar()
        self.init_tabs()
        self.apply_css()
        
        
        
    def draw_header_bar(self):
                


        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hb.set_name("header")
        Gtk.StyleContext.add_class(hb.get_style_context(), "linked")

        
        #nav box
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")


        lbutton = Gtk.Button()
        lbutton.add(
            Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT, shadow_type=Gtk.ShadowType.NONE))
        
        lbutton.connect("clicked", self.goback)
        
        box.add(lbutton)

        rbutton = Gtk.Button()
        rbutton.add(
            Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT, shadow_type=Gtk.ShadowType.NONE))
        
        rbutton.connect("clicked", self.goforward)

        
        box.add(rbutton)
        
        rebutton = Gtk.Button()
        reicon = Gio.ThemedIcon(name="view-refresh")

        reimage = Gtk.Image.new_from_gicon(reicon, Gtk.IconSize.BUTTON)
        rebutton.add(reimage)

        rebutton.connect("clicked", self.reload)

        box.add(rebutton)
        
        hbutton = Gtk.Button()
        hicon = Gio.ThemedIcon(name="go-home")

        image = Gtk.Image.new_from_gicon(hicon, Gtk.IconSize.BUTTON)
        
        hbutton.connect("clicked", self.gohome)

        hbutton.add(image)

        box.add(hbutton)
        
        #url bar
        
        self.urlbar = Gtk.Entry()
        
        self.urlbar.set_name("urlbar")
        
        self.urlbar.props.placeholder_text = "Enter URL"

        self.urlbar.connect("activate", self.checkEnter)   
        self.urlbar.connect("button-press-event", self.selectAll) 


      
        # settings button

        setbutton = Gtk.Button()
        seticon = Gio.ThemedIcon(name="open-menu-symbolic")

        setimage = Gtk.Image.new_from_gicon(seticon, Gtk.IconSize.BUTTON)
        setbutton.add(setimage)
        
        setbutton.connect("clicked", self.settingspage)

        #window decorations
        
        closebutton = Gtk.Button()
        closeicon = Gio.ThemedIcon(name="window-close-symbolic")

        closeimage = Gtk.Image.new_from_gicon(closeicon, Gtk.IconSize.BUTTON)
        closebutton.add(closeimage)
        
        closebutton.set_name('closebtn')
        
        closebutton.connect("clicked", self.exit)
        
        minbutton = Gtk.Button()
        minicon = Gio.ThemedIcon(name="window-minimize-symbolic")

        minmage = Gtk.Image.new_from_gicon(minicon, Gtk.IconSize.BUTTON)
        minbutton.add(minmage)
        
        minbutton.set_name('minbtn')

        minbutton.connect("clicked", self.minimize)
        
        maxbutton = Gtk.Button()
        maxicon = Gio.ThemedIcon(name="window-maximize-symbolic")

        maximage = Gtk.Image.new_from_gicon(maxicon, Gtk.IconSize.BUTTON)
        maxbutton.add(maximage)

        maxbutton.connect("clicked", self.maxss)
        
        #pack

        hb.pack_start(box, False, False, 5)

        hb.pack_start(self.urlbar, True, True, 20)

        hb.pack_end(closebutton, False, False, 1)
        hb.pack_end(maxbutton,  False, False, 1)
        hb.pack_end(minbutton, False, False, 1)
        
        hb.pack_end(setbutton, False, False, 5)

        

        self.set_titlebar(hb)


    def on_window_state_event(self, widget, windowState, *args):
        mask = Gdk.WindowState.MAXIMIZED

        if widget.get_window().get_state() & mask == mask:
            if self.maximized == True:
                pass
            else:
                self.maximized = True
        else:
            if self.maximized == False:
                pass
            else:
                self.maximized = False

    def cookies_change(self, *args):
        pass
    
    def selectAll(self, *args):
        self.urlbar.select_region(0,-1)

        
    

    
    def make_tab(self, widget=None, url=None):
        newtab = Tab(self, url)
        newtab.connect('notify::uri', self.on_load)
        newtab.connect('notify::title', self.on_title_change)

       
        self.notebook.append_page(newtab, self.make_header_box("New Tab", newtab))
        self.notebook.set_tab_reorderable(newtab, True)
        self.notebook.set_tab_detachable(newtab, True)
        self.show_all()
        
        self.notebook.set_current_page(self.notebook.page_num(newtab))

        if url is None:
            self.urlbar.grab_focus()
        
        return newtab


    def get_active_tab(self):
        return self.notebook.get_nth_page(self.notebook.get_current_page())

    def init_tabs(self):
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    
        self.notebook = Gtk.Notebook()
        
        self.notebook.connect("switch-page", self.on_tab_change)
        self.notebook.connect("page-added", self.moveAddToEnd)
        self.notebook.connect("page-removed", self.moveAddToEnd)
        self.notebook.connect("page-reordered", self.moveAddToEnd)
        
        self.notebook.set_scrollable(True)


        newtabbtn = Gtk.Button(label='+')
        context = newtabbtn.get_style_context()
        context.add_class("newtab")

        newtabbtn.connect("clicked", self.make_tab)
        
        dummytab = DummyTab()
        
        self.newTabPage = dummytab

        self.notebook.append_page(dummytab, newtabbtn)


        self.make_tab()
        # new tab button
        
        
            
        vbox.pack_start(self.notebook, True , True, 0)

                
        self.add(vbox)

   
    def settingspage(self, *args):
        
        settingsAlreadyOpen = False
        
        for tab in self.notebook.get_children():
            if isinstance(tab, Tab):
                if tab.get_uri() == 'surfwd://controls':
                    self.notebook.set_current_page(self.notebook.page_num(tab))
                    settingsAlreadyOpen = True
                    break
        if not settingsAlreadyOpen:
            self.make_tab(url="surfwd://controls")

   
   
    def moveAddToEnd(self, *args):
        self.notebook.reorder_child(self.newTabPage, -1)

            
    def goback(self, *args):
        self.get_active_tab().goback()
        
    def goforward(self, *args):
        self.get_active_tab().goforward()
        
    def gohome(self, *args):
        self.get_active_tab().gohome()
        
    def reload(self, *args):
        self.get_active_tab().refresh()
        
    def nextab(self, *args):
        self.notebook.next_page()
        
    def prevtab(self, *args):
        self.notebook.prev_page()

            
        
    def checkEnter(self, urlbar, *args):
        
        self.get_active_tab().navigate_to_url(urlbar.get_text())

    def checkShortcuts(self, window, ev, data=None, *ars):
        if ev.state == Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK or ev.state== Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD2_MASK:

            if ev.keyval in [Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Tab]:
                self.prevtab()


        elif ev.state == Gdk.ModifierType.CONTROL_MASK or ev.state == Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD2_MASK:

            if ev.keyval in [Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Tab]:
                self.nextab()   


            elif ev.keyval in [Gdk.KEY_W, Gdk.KEY_w]:
                self.close_tab(self.tabCloseBtns[self.get_active_tab()])


            elif ev.keyval in [Gdk.KEY_R, Gdk.KEY_r]:
                self.reload()


            elif ev.keyval in [Gdk.KEY_T, Gdk.KEY_t]:
                self.make_tab()

                


        
            
    def on_load(self, tab, *args):
        self.set_url(self.get_active_tab().get_uri())
        
        
    def make_header_box(self, text, tab):
        
        header = Gtk.HBox()
        title_label = Gtk.Label(label=text)

        close_button = Gtk.Button(label="x")

        context = close_button.get_style_context()
        context.add_class("closetab")

        close_button.connect('clicked', self.close_tab)

        header.pack_start(title_label,True, True, 0)
        header.pack_end(close_button, False, False, 0)
        
        header.show_all()
        
        self.tabCloseBtns[tab] = close_button
        
        return header

        
    def on_title_change(self, tab, title, *args):

        heading = tab.get_title()
        if len(heading) > 12:
            heading = heading[:12] + '...'

        self.notebook.set_tab_label(tab, self.make_header_box(heading, tab))


    def remove_home_uri(self, tab):
        tab_uri = tab.get_uri()

        if tab_uri == 'surfwd://newtab':
            tab_uri = ''
        
        self.urlbar.props.text = tab_uri

        
    def on_tab_change(self, ntbk, tab, ind, *args):
        if isinstance(tab, DummyTab):
            self.notebook.stop_emission_by_name("switch-page")
            return
        
        self.remove_home_uri(tab)
        
        
        
    def close_tab(self, btn, *args):

        for tab, butn in self.tabCloseBtns.items():
            if butn == btn:
                break
        
        
        tabnum = self.notebook.page_num(tab)
        
        
        if len(self.tabCloseBtns) == 1: 
            self.tabCloseBtns.pop(tab)

            self.exit()
            
            return


        elif tabnum == len(self.tabCloseBtns)-1 and tabnum == self.notebook.get_current_page() :

            self.notebook.set_current_page(tabnum-1)


        
        self.tabCloseBtns.pop(tab)

        # print(self.tabCloseBtns)

        self.notebook.remove_page(self.notebook.page_num(tab))
        
        
        
        
    def set_url(self, url):
        self.urlbar.props.text = url

    def exit(self, *args):
        self.destroy()


    def maxss(self, *args):
        
        if self.maximized:
            self.unmaximize()
        else:
            self.maximize()
        


    def minimize(self, *args):
        self.iconify()


    
    def apply_css(self):
        
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        css = f"""
        
        *   {{
            outline: none;
            border: none;
            
        }}
        
        #header {{
            background-color: {self.bg_color};
            padding-top: 4px;
            padding-bottom: 2px;
        }}
        
        #urlbar{{
            border-radius: 10px;
        }}
        
        #closebtn{{
            margin-right: 5px;
        }}
        
        .closetab{{
            padding: 3px;
            background: none;
            border: none;   
            margin-left: 6px;

        }}
        
        .newtab{{
            background: none;
            padding: 0px;
            margin: 0px;

        }}
        
        

        """.encode()
        provider.load_from_data(css)




if __name__ == '__main__':
    
    window = MainWindow()


    window.connect("destroy", Gtk.main_quit)

    window.show_all()


    Gtk.main()


