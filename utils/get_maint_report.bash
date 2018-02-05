source utils/env.sh
report_path='issue_report.html'
~/.virtualenvs/github_issues_report/bin/python report.py $GITHUB_TOKEN $GITHUB_REPO $GITHUB_ORG maintenance > $report_path
