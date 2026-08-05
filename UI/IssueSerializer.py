try:
    import UI.ui_config as uiConf
except ImportError:
    try:
        import ui_config as uiConf
    except ImportError as e:
        raise ImportError("Neither UI.ui_config nor ui_config is available") from e
        
# Parsing function for the simplified format
def markup_to_issueCards(text):
    items = []
    cur = {}
    key = None
    for line in text.strip().splitlines():
        line = line.rstrip()
        if line.startswith(uiConf.TOKEN_BEG) and line.endswith(uiConf.TOKEN_END):
            sz = len(uiConf.TOKEN_BEG)
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
        

def issueCards_to_markup(issues: list[str]):
    
    text = ""
    
    for issue in issues:
        for key in issue:
            text += f"{uiConf.TOKEN_BEG} {key} {uiConf.TOKEN_END}\n"
            text += issue[key] + "\n"
        text += f"{uiConf.TOKEN_BEG} {uiConf.END_ISSUE_TOKEN} {uiConf.TOKEN_END}\n"
        
    text = text[:-1]                
    
    # print(text)
    backup_text = ""    
    with open(uiConf.ISSUES_FILE, mode="a+", encoding="utf-8") as read_file1:
        read_file1.seek(0)
        backup_text = read_file1.read()
    with open(uiConf.ISSUES_BACKUP_FILE, mode="w", encoding="utf-8") as file2:
        file2.write(backup_text)
        
    with open(uiConf.ISSUES_FILE, mode="w", encoding="utf-8") as file1:
        file1.write(text)