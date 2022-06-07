# from gi.repository import Gtk, Gio, Gdk, WebKit2
# import requests


# class Tab(WebKit2.WebView):
#     def __init__(self, mainWindow, url=None):
#         super().__init__()
#         if url is None:
#             self.url = 'https://www.google.com'
#         else:
#             self.url = url
        
#         self.mainWindow = mainWindow
#         self.navigate_to_url(self.url)
        
        

#     def formulate_link(self, link):
#         protocols = ('http://', 'https://', 'ftp://', 'swd://')
        
#         if link.startswith(protocols):
#             return link
        
#         link = protocols[1] + link
        
#         return link

        
#     def navigate_to_url(self, query, *args):

#         if self.isLink(query):
#             link = self.formulate_link(query)
#             self.load_uri(link)
#         else:
#             link = f'https://www.bing.com/search?q={query}'
#             self.load_uri(link)
            
            
#         self.set_url(link)


#     def isLink(self, txt:str):
#         domain_suffixes= self.get_domain_suffixes()

#         ltext=txt.lower().split('/')[0]
#         return ltext.startswith(('http','www','ftp', 'swd')) or ltext.endswith(domain_suffixes)

#     def set_url(self, url):
#         self.mainWindow.urlbar.props.text = url
        
#     def goback(self, *args):
#         self.set_url(self.get_uri())
        
#     def goforward(self, *args):
#         self.set_url(self.get_uri())
        
#     def gohome(self, *args):
#         self.navigate_to_url('https://www.google.com')
        
#     def reload(self, *args):
#         self.set_url(self.get_uri())
        
#         self.mainWindow.tabstack.get_child_by_name('tab1').title='google'
#         self.mainWindow.show_all()

#     def get_domain_suffixes(self):
#         try:
#             req = requests.get('https://publicsuffix.org/list/public_suffix_list.dat')
#             res = req.text
#         except Exception as e:
#             with open('public_suffix_list.dat', 'r') as f:
#                 res = f.read()
                
#         lst=set()
        
#         for line in res.split('\n'):
#             if not line.startswith('//'):
#                 domains=line.split('.')
#                 cand=domains[-1]
#                 if cand:
#                     lst.add('.' + cand)
                    
#         return tuple(sorted(lst))



# class MainWindow(Gtk.Window):
#     def __init__(self):
        
#         super().__init__(title="HeaderBar Demo")
        
        
#         self.set_border_width(10)
#         self.set_default_size(900, 600)
        
#         self.maximized = False
        
                
#         self.tabs = []
        

#         self.connect("window-state-event", self.on_window_state_event)
#         self.connect("key-release-event", self.checkShortcuts) 
        
#         self.style_context = Gtk.StyleContext()
        
#         try: 
            
#             self.bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL).to_string()
#             print(self.bg_color)
            
#             if self.bg_color is None:
#                 self.bg_color = "black"
            
#         except:
#             self.bg_color = "black"

#         self.set_border_width(4)
        
#         self.draw_header_bar()
#         self.init_tabs()
#         self.apply_css()
        
        
        
#     def draw_header_bar(self):
                


#         hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
#         hb.set_name("header")
#         Gtk.StyleContext.add_class(hb.get_style_context(), "linked")

        
#         #nav box
        
#         box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
#         Gtk.StyleContext.add_class(box.get_style_context(), "linked")


#         lbutton = Gtk.Button()
#         lbutton.add(
#             Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT, shadow_type=Gtk.ShadowType.NONE))
        
#         lbutton.connect("clicked", self.goback)
        
#         box.add(lbutton)

#         rbutton = Gtk.Button()
#         rbutton.add(
#             Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT, shadow_type=Gtk.ShadowType.NONE))
        
#         rbutton.connect("clicked", self.goforward)

        
#         box.add(rbutton)
        
#         rebutton = Gtk.Button()
#         reicon = Gio.ThemedIcon(name="view-refresh")

#         reimage = Gtk.Image.new_from_gicon(reicon, Gtk.IconSize.BUTTON)
#         rebutton.add(reimage)

#         rebutton.connect("clicked", self.reload)

#         box.add(rebutton)
        
#         hbutton = Gtk.Button()
#         hicon = Gio.ThemedIcon(name="go-home")

#         image = Gtk.Image.new_from_gicon(hicon, Gtk.IconSize.BUTTON)
        
#         hbutton.connect("clicked", self.gohome)

#         hbutton.add(image)

#         box.add(hbutton)
        
#         #url bar
        
#         self.urlbar = Gtk.Entry()
        
#         self.urlbar.set_name("urlbar")
        
#         self.urlbar.props.placeholder_text = "Enter URL"

#         self.urlbar.connect("key-release-event", self.checkEnter)   



#         # settings button
      
        
        
#         setbutton = Gtk.Button()
#         seticon = Gio.ThemedIcon(name="open-menu-symbolic")

#         setimage = Gtk.Image.new_from_gicon(seticon, Gtk.IconSize.BUTTON)
#         setbutton.add(setimage)
        
#         #window decorations
        
#         closebutton = Gtk.Button()
#         closeicon = Gio.ThemedIcon(name="window-close-symbolic")

#         closeimage = Gtk.Image.new_from_gicon(closeicon, Gtk.IconSize.BUTTON)
#         closebutton.add(closeimage)
        
#         closebutton.set_name('closebtn')
        
#         closebutton.connect("clicked", self.exit)
        
#         minbutton = Gtk.Button()
#         minicon = Gio.ThemedIcon(name="window-minimize-symbolic")

#         minmage = Gtk.Image.new_from_gicon(minicon, Gtk.IconSize.BUTTON)
#         minbutton.add(minmage)
        
#         minbutton.set_name('minbtn')

#         minbutton.connect("clicked", self.minimize)
        
#         maxbutton = Gtk.Button()
#         maxicon = Gio.ThemedIcon(name="window-maximize-symbolic")

#         maximage = Gtk.Image.new_from_gicon(maxicon, Gtk.IconSize.BUTTON)
#         maxbutton.add(maximage)

#         maxbutton.connect("clicked", self.maxss)
        
#         #pack

#         hb.pack_start(box, False, False, 5)

#         hb.pack_start(self.urlbar, True, True, 20)

#         hb.pack_end(closebutton, False, False, 1)
#         hb.pack_end(maxbutton,  False, False, 1)
#         hb.pack_end(minbutton, False, False, 1)
        
#         hb.pack_end(setbutton, False, False, 5)
        
        

#         self.set_titlebar(hb)


#     def on_window_state_event(self, widget, windowState, *args):
#         mask = Gdk.WindowState.MAXIMIZED

#         if widget.get_window().get_state() & mask == mask:
#             if self.maximized == True:
#                 pass
#             else:
#                 self.maximized = True
#         else:
#             if self.maximized == False:
#                 pass
#             else:
#                 self.maximized = False


    
#     def make_tab(self, widget=None, url=None):
#         newtab = Tab(self, url)
#         newtab.connect('notify::uri', self.on_load)
        
#         self.tabs.append(newtab)
#         self.tabstack.add_titled(newtab, 'tab' + str(len(self.tabs)), f'Tab{str(len(self.tabs))}')
        
#         self.stack_switcher.set_stack(self.tabstack)
        
#         self.show_all()
        
#         self.tabstack.set_visible_child(newtab)

#         return newtab


#     def get_active_tab(self):
#         return self.tabstack.get_visible_child()

#     def init_tabs(self):
        
#         vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
#         hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
#         self.newtabbtn = Gtk.Button()
#         nicon = Gio.ThemedIcon(name="new-symbolic")

#         image = Gtk.Image.new_from_gicon(nicon, Gtk.IconSize.BUTTON)
        
#         self.newtabbtn.connect("clicked", self.make_tab)

#         self.newtabbtn.add(image)


#         self.tabstack = Gtk.Stack()
#         # self.tabstack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
#         self.tabstack.set_transition_duration(100)


#         self.stack_switcher = Gtk.StackSwitcher()
        
#         self.stack_switcher.set_stack(self.tabstack)


#         self.make_tab()
        
        
            
#         hbox.pack_start(self.stack_switcher, True, True, 0)
#         hbox.pack_start(self.newtabbtn, False, False, 0)
#         vbox.pack_start(hbox, False, True, 0)

#         vbox.pack_start(self.tabstack, True, True, 0)
        
        
#         self.add(vbox)


            
#     def goback(self, *args):
#         self.get_active_tab().goback()
        
#     def goforward(self, *args):
#         self.get_active_tab().goforward()
        
#     def gohome(self, *args):
#         self.get_active_tab().gohome()
        
#     def reload(self, *args):
#         self.get_active_tab().reload()

            
        
#     def checkEnter(self, urlbar, ev, data=None, *args):
#         if ev.keyval == Gdk.KEY_Return:
#             self.navigate_to_url(urlbar.get_text())

#     def checkShortcuts(self, window, ev, data=None, *ars):
#         if ev.state == Gdk.ModifierType.CONTROL_MASK:
#             if ev.keyval in [Gdk.KEY_W, Gdk.KEY_w]:
#                 print('close tab')
#             if ev.keyval in [Gdk.KEY_R, Gdk.KEY_r]:
#                 print('reload tab')

        
            
#     def on_load(self, tab, *args):
#         self.set_url(self.webview.get_uri())
        
        

#     def exit(self, *args):
#         self.destroy()


#     def maxss(self, *args):
        
#         if self.maximized:
#             self.unmaximize()
#         else:
#             self.maximize()
        


#     def minimize(self, *args):
#         self.iconify()


    
#     def apply_css(self):
        
#         screen = Gdk.Screen.get_default()
#         provider = Gtk.CssProvider()
#         self.style_context.add_provider_for_screen(
#             screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
#         )
#         css = f"""
#         #header {{
#             background-color: {self.bg_color};
#             padding-top: 4px;
#             padding-bottom: 2px;
#         }}
        
#         #urlbar{{
#             border-radius: 10px;
#         }}
        
#         #closebtn{{
#             margin-right: 5px;
#         }}
        
        

#         """.encode()
#         provider.load_from_data(css)




# if __name__ == '__main__':
    
#     window = MainWindow()


#     window.connect("destroy", Gtk.main_quit)

#     window.show_all()


#     Gtk.main()


# #tabs
# #cookies
# #settings
# #newtab
# #load