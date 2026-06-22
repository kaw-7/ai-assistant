if __name__ == "__main__":
    import ui_config as uiConf
else:
    import UI.ui_config as uiConf
        
# Parsing function for the simplified format
def formatIssues(text):
    items = []
    cur = {}
    key = None
    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith(uiConf.ISSUE_BEG) and line.endswith(uiConf.ISSUE_END):
            sz = len(uiConf.ISSUE_BEG)
            token = line[sz:-sz].strip()
            if token == uiConf.END_ISSUE_TOKEN:
                if cur:
                    items.append(cur)
                cur = {}
                key = None
            else:
                key = token
                cur[key] = ""
        else:
            if key:
                cur[key] = (cur.get(key, "") + ("\n" if cur.get(key) else "") + line)
    return items
        
if __name__ == "__main__":
    from App import App

    file_path = "../output/VS2022/final_risk_report.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        issuesToDisplay = formatIssues(text)
        app = App(issuesToDisplay)
        app.mainloop()

