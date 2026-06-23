try:
    import UI.ui_config as uiConf
except ImportError:
    try:
        import ui_config as uiConf
    except ImportError as e:
        raise ImportError("Neither UI.ui_config nor ui_config is available") from e
        
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
        


