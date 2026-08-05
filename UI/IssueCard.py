import tkinter as tk
import re
try:
    import UI.ui_config as uiConf
    from UI.IssueCardHeader import IssueCardHeader
except ImportError:
    import ui_config as uiConf
    from IssueCardHeader import IssueCardHeader
    
        
class IssueCard(tk.Frame):
    def __init__(self, master, item, on_save=None, *args, **kwargs):
        super().__init__(master, bd=1, relief="solid", padx=uiConf.PADX, pady=uiConf.PADY, *args, **kwargs)
        self.item = item

        # Container for main content
        main_content = tk.Frame(self)
        main_content.pack(fill="both", expand=True)
        
        # Using Grid: 
        # Column 0: Descriptions (fills space)
        # Column 1: Metadata (fixed width or content-based)
        main_content.columnconfigure(0, weight=1) 
        
        # --- Left Column ---
        left_col = tk.Frame(main_content)
        left_col.grid(row=0, column=0, sticky="nsew")
        
        # Header
        tk.Label(left_col, text=item.get(uiConf.DESCRIPTION, "(no description)"), 
             font=(uiConf.FONT, uiConf.FONT_SIZE + 1, "bold")).pack(fill="x", pady=(0, uiConf.PADY))
        
        # Description area (wrap=word handles width resizing)
        from tkinter import scrolledtext
        self._edit = False
        self.header = IssueCardHeader(
            left_col,
            uiConf.DESCRIPTION,
            on_edit=self._on_edit,
            on_save=on_save
        )
        self.header.pack(fill="x")
        # tk.Label(left_col, text=uiConf.DEFECT_DESCRIPTION, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        self.desc_text = scrolledtext.ScrolledText(left_col, height=3, wrap="word")
        self.desc_text.insert("1.0", item.get(uiConf.DEFECT_DESCRIPTION, ""))
        self.desc_text.config(state="disabled")
        self.desc_text.pack(fill="x", pady=(0, uiConf.PADY))
        
        # Risk Assessment area
        tk.Label(left_col, text=uiConf.RISK_ASSESSMENT, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        self.risk_text = scrolledtext.ScrolledText(left_col, height=3, wrap="word")
        self.risk_text.insert("1.0", item.get(uiConf.RISK_ASSESSMENT, ""))
        self.risk_text.config(state="disabled")
        self.risk_text.pack(fill="x", pady=(0, uiConf.PADY))
        self._bind_sync(self.risk_text, uiConf.RISK_ASSESSMENT)
        
        # --- Right Column ---
        right_col = tk.Frame(main_content, padx=uiConf.PADX)
        right_col.grid(row=0, column=1, sticky="ne")
        
        # expand button
        self.expanded = False
        tk.Button(right_col, text="Expand", font=(uiConf.FONT, uiConf.FONT_SIZE, "bold"), command=self._toggle_expand).pack(anchor="w")
        
        # Metadata
        tk.Label(right_col, text=uiConf.DEFECT_ID, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        tk.Label(right_col, text=item.get(uiConf.DEFECT_ID, ""), bg="#eee").pack(fill="x", pady=(0, uiConf.PADY))
        
        tk.Label(right_col, text=uiConf.STATUS, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        tk.Label(right_col, text=item.get(uiConf.STATUS, ""), bg="#eee").pack(fill="x")

    def matches_filter(self, mode):
        # mode: "All", "Risk Exists", "No Risk", "NOT_EVALUATED"
        ra = (self.item.get(uiConf.RISK_ASSESSMENT) or "").strip()
        status_text = (self.item.get(uiConf.STATUS) or "").strip()
        
        if mode == uiConf.ALL:
            return True
        
        if mode == uiConf.NOT_EVALUATED:
            pattern = uiConf.NOT_EVALUATED.lower().replace("_", ".?")    # 'not.?evaluated'
            if re.search(pattern, status_text, re.IGNORECASE ):
                return True
            if re.search(pattern, ra, re.IGNORECASE ):
                return True
            return False
        
        if mode == uiConf.RISK_EXISTS:
            pattern = uiConf.RISK_EXISTS.lower().replace(" ", ".?")[:-1]    # 'risk.?exist'
            if re.search(pattern, status_text, re.IGNORECASE ):
                return True
            if re.search(pattern, ra, re.IGNORECASE ):
                return True
            return False
        
        if mode == uiConf.NO_RISK:
            pattern = uiConf.NO_RISK.lower().replace(" ", ".?")    # 'no.?risk'
            if re.search(pattern, status_text, re.IGNORECASE ):
                return True
            if re.search(pattern, ra, re.IGNORECASE ):
                return True
            return False
        
        return True
    
    def _toggle_expand(self):
        self.expanded = not self.expanded
        self._toggle_widget_expand(self.desc_text)
        self._toggle_widget_expand(self.risk_text)
        
    def _toggle_widget_expand(self, widget):
        MIN_LINES = 3
        MAX_LINES = 35
        widget.update_idletasks()
        if self.expanded == False:
            widget.config(height=MIN_LINES)
        else:              
            lines = widget.tk.call(widget._w, "count", "-displaylines", "1.0", "end")        
            widget.config(height=max(min(lines, MAX_LINES), MIN_LINES))
    
    def _on_edit(self):
        self._edit = not self._edit
        if(self._edit):
            self.risk_text.config(state="normal")
            self.desc_text.config(state="normal")
        else:
            self.risk_text.config(state="disabled")
            self.desc_text.config(state="disabled")

    def _bind_sync(self, widget, key):
        widget.bind("<<Modified>>", lambda e, k=key: self._sync(e.widget, k))
    
    def _sync(self, widget, key):
        if not widget.edit_modified():      # ignore the event from resetting the flag
            return
        self.item[key] = widget.get("1.0", "end-1c")
        widget.edit_modified(False)            
            