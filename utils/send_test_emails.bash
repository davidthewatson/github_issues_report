source utils/env.sh
~/.virtualenvs/github_issues_report/bin/python issue_update_prompter.py $GITHUB_TOKEN $GITHUB_REPO $GITHUB_ORG --send_to_test_target $TEST_EMAIL_TARGET
