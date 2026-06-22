import tkinter as tk
try:
    import UI.ui_config as uiConf
except ImportError:
    try:
        import ui_config as uiConf
    except ImportError as e:
        raise ImportError("Neither UI.ui_config nor ui_config is available") from e
        
class IssueCard(tk.Frame):
    def __init__(self, master, item, *args, **kwargs):
        super().__init__(master, bd=1, relief="solid", padx=uiConf.PADX, pady=uiConf.PADY, *args, **kwargs)
        self.item = item
        
        # Header
        tk.Label(self, text=item.get(uiConf.DESCRIPTION, "(no description)"), 
                 font=(uiConf.FONT, uiConf.FONT_SIZE, "bold"), anchor="w").pack(fill="x")
        
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
        
        # Description area (wrap=word handles width resizing)
        tk.Label(left_col, text=uiConf.DEFECT_DESCRIPTION, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        desc_text = tk.Text(left_col, height=3, wrap="word")
        desc_text.insert("1.0", item.get(uiConf.DEFECT_DESCRIPTION, ""))
        desc_text.config(state="disabled")
        desc_text.pack(fill="x", pady=(0, 5))
        
        # Risk Assessment area
        tk.Label(left_col, text=uiConf.RISK_ASSESSMENT, font=(uiConf.FONT, uiConf.FONT_SIZE, "bold")).pack(anchor="w")
        risk_text = tk.Text(left_col, height=3, wrap="word")
        risk_text.insert("1.0", item.get(uiConf.RISK_ASSESSMENT, ""))
        risk_text.config(state="disabled")
        risk_text.pack(fill="x")
        
        # --- Right Column ---
        right_col = tk.Frame(main_content, padx=uiConf.PADX)
        right_col.grid(row=0, column=1, sticky="ne")
        
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
            # treat empty or missing as NOT_EVALUATED
            if( status_text is None or status_text == uiConf.NOT_EVALUATED):
                return True
            else:
                return False
        if mode == uiConf.RISK_EXISTS:
            # consider "risk" keywords or non-empty and not explicitly "No risk"/"NO RISK"
            if ra == "":
                return False
            low = ra.lower()
            if uiConf.NO_RISK.lower() in low:
                return False
            if( status_text is None or status_text == uiConf.NOT_EVALUATED):
                return False
            return True
        if mode == uiConf.NO_RISK:
            low = ra.lower()
            return (status_text.strip().lower().startswith(uiConf.NO_RISK.lower())) or (ra.strip().lower().startswith(uiConf.NO_RISK.lower()))
        return True