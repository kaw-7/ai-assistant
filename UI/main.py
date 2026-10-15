def _sharp_on_high_dpi():
    """Without this Windows scales the window up as a bitmap - blurry text."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):    # not Windows, or older than 8.1
        pass


if __name__ == "__main__":
    from App import App
    from IssueSerializer import markup_to_issueCards, createIssuesBackUp
    import ui_config as uiConf

    with open(uiConf.ISSUES_FILE, "r", encoding="utf-8") as f:
        text = f.read()
        issuesToDisplay = markup_to_issueCards(text)

    if(issuesToDisplay is not None):
        createIssuesBackUp(uiConf.ISSUES_FILE, uiConf.ISSUES_BACKUP_FILE)
        _sharp_on_high_dpi()
        app = App(issuesToDisplay, uiConf.ISSUES_FILE)
        app.mainloop()
