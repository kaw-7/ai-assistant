import tkinter as tk 

try:
    import UI.ui_config as uiConf
except ImportError:
    import ui_config as uiConf
        
class IssueCardHeader(tk.Frame):
    def __init__(self, master, title, on_edit=None, on_save=None):
        super().__init__(master, padx=uiConf.PADX, pady=uiConf.PADY) 
        header = tk.Frame(master)
        header.pack(fill="x")
        
        tk.Label(header, text=title,
             font=(uiConf.FONT, uiConf.FONT_SIZE, "bold"), anchor="w").pack(
             side="left", fill="x", expand=True)
        
        self.edit_btn = tk.Button(header, text="Edit", command=on_edit, padx=uiConf.PADX, pady=uiConf.PADY)
        self.edit_btn.pack(side="right")
        
        self.save_btn = tk.Button(header, text="Save", command=on_save, padx=uiConf.PADX, pady=uiConf.PADY)
        self.save_btn.pack(side="right")