import tkinter as tk
try:
    from UI.IssueCard import IssueCard
except ImportError:
    try:
        from IssueCard import IssueCard
    except ImportError as e:
        raise ImportError("Neither UI.IssueCard nor IssueCard is available") from e

try:
    import UI.ui_config as uiConf
except ImportError:
    try:
        import ui_config as uiConf
    except ImportError as e:
        raise ImportError("Neither UI.ui_config nor ui_config is available") from e


class App(tk.Tk):
    def __init__(self, items):
        super().__init__()
        self.title("Issue Items Viewer")
        self.geometry(uiConf.GEOMETRY)
        self.items = items
        
        # --- UI Construction ---
        top = tk.Frame(self, pady=uiConf.PADY)
        top.pack(fill="x")
        tk.Label(top, text="Filter:", font=(uiConf.FONT, 10, "bold")).pack(side="left", padx=(uiConf.PADX, uiConf.PADX))
        
        self.filter_var = tk.StringVar(value="All")
        options = [uiConf.ALL, uiConf.RISK_EXISTS, uiConf.NO_RISK, uiConf.NOT_EVALUATED]
        for opt in options:
            rb = tk.Radiobutton(top, text=opt, variable=self.filter_var, 
                                value=opt, command=self.apply_filter)
            rb.pack(side="left", padx=uiConf.PADX)
            
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable = tk.Frame(self.canvas)
        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        self.card_widgets = []
        for it in items:
            c = IssueCard(self.scrollable, it)
            c.pack(fill="x", expand=False, pady=uiConf.PADY, padx=uiConf.PADX)
            self.card_widgets.append(c)
        
        self.apply_filter()

    def on_resize(self, event):
        # Ensure only the main window resize triggers this
        if event.widget == self:
            # Adjust canvas content width
            new_width = self.canvas.winfo_width()
            self.canvas.itemconfigure(self.canvas_window, width=new_width)

    def apply_filter(self):
        mode = self.filter_var.get()
        for c in self.card_widgets:
            if c.matches_filter(mode):
                c.pack(fill="x", pady=uiConf.PADY, padx=uiConf.PADX)
            else:
                c.pack_forget()