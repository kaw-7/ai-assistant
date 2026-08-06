    
if __name__ == "__main__":
    from App import App
    from IssueSerializer import markup_to_issueCards
    file_path = "output/Rider/final_risk_report.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        issuesToDisplay = markup_to_issueCards(text)
        app = App(issuesToDisplay)
        app.mainloop()