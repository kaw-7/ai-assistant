    
if __name__ == "__main__":
    from App import App
    from IssueFormatter import formatIssues
    file_path = "../output/VS2022/final_risk_report.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        issuesToDisplay = formatIssues(text)
        app = App(issuesToDisplay)
        app.mainloop()