try:
    import UI.ui_config as uiConf
except ImportError:
    try:
        import ui_config as uiConf
    except ImportError as e:
        raise ImportError("Neither UI.ui_config nor ui_config is available") from e

def createIssuesBackUp(out_file=uiConf.ISSUES_FILE, out_back=uiConf.ISSUES_BACKUP_FILE):
    backup_text = ""    
    with open(out_file, mode="a+", encoding="utf-8") as read_file1:
        read_file1.seek(0)
        backup_text = read_file1.read()
    with open(out_back, mode="w", encoding="utf-8") as file2:
        file2.write(backup_text)
        
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


def issueCards_to_markup(issues: list[str], out_file=uiConf.ISSUES_FILE):
    
    text = ""
    
    for issue in issues:
        for key in issue:
            text += f"{uiConf.TOKEN_BEG} {key} {uiConf.TOKEN_END}\n"
            text += issue[key] + "\n"
        text += f"{uiConf.TOKEN_BEG} {uiConf.END_ISSUE_TOKEN} {uiConf.TOKEN_END}\n"
        
    text = text[:-1]                
    
    # print(text)        
    with open(out_file, mode="w", encoding="utf-8") as file1:
        file1.write(text)