
    
if __name__ == "__main__":
    from App import App
    from IssueSerializer import markup_to_issueCards, createIssuesBackUp
    import UI.ui_config as uiConf
    
    with open(uiConf.ISSUES_FILE, "r", encoding="utf-8") as f:
        text = f.read()
        issuesToDisplay = markup_to_issueCards(text)
        
    if(issuesToDisplay is not None):
        createIssuesBackUp(uiConf.ISSUES_FILE, uiConf.ISSUES_BACKUP_FILE)    
        app = App(issuesToDisplay, uiConf.ISSUES_FILE)
        app.mainloop()