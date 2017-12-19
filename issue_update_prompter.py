import dominate
import itertools
import copy
import yaml
from datetime import datetime
from github import Github
from clint import arguments
from dominate.tags import table, tbody, h3
import report
import smtplib
from email.mime.text import MIMEText


def make_email_body(issues):
    title = 'BETA:\nPlease update or close the following issues so Bianca and Spencer know what is going on.'
    d = dominate.document(title=title)
    with d.body:
        h3(title)
        with table(border='1', width='1024', cellpadding='10').add(tbody()):
            report.make_table_header()
            decorated_issues = report.build_decorated_issues(issues)
            decorated_issues.sort(key=lambda issue: issue.priority)
            for decorated_issue in decorated_issues:
                report.make_table_row(decorated_issue)
    return str(d)


def get_notification_from_repos(criteria, repos):
    notification_lists = [get_notification_from_issues(criteria, repo.get_issues()) for repo in repos]
    notifications = list(itertools.chain.from_iterable(notification_lists))
    return notifications


def time_to_notify(timeframe, last_updated):
    """I'm making this a seperate function, as I think we will eventually find some 
    odd edge cases that we will want to build into this logic (last updated 23.5 hours ago, etc). 
    target_days (int or float): number of days at which we want to notify
    last_updated (datetime): datetime object from github of last time issues was updated """
    day_delta = (datetime.now() - last_updated).days
    if 'catch-up' in timeframe and timeframe['catch-up']:
        return day_delta >= timeframe['days']
    else:
        return day_delta == timeframe['days']


def get_notification_from_issues(criteria, issues):
    notifications = []
    notification_labels = set(criteria.keys())
    for issue in issues:
        issue_labels = set(str(issue.name) for issue in issue.labels)
        target_labels = issue_labels & notification_labels
        for target_label in target_labels:
            # reversed sorted order so if there is a different notification level at 60 and one at 30, only the 60 is sent
            for timeframe in sorted(criteria[target_label], key=lambda x: x['days'], reverse=True):
                if time_to_notify(timeframe, issue.updated_at):
                    recipients = copy.deepcopy(timeframe['recipients'])
                    if 'AUTHORS' in recipients:
                        def debug_assignees(assignee):
                            if assignee.email is None:
                                print('''Github user {} can't be contacted as they don't 
                                      have a public email set. Found in issue {}.'''.format(assignee, issue))
                        list(map(debug_assignees, issue.assignees))
                        assignee_emails = [assignee.email for assignee in issue.assignees if assignee.email]
                        if not assignee_emails:
                            pass
                            # todo: what do we want to do with issues that are not assigned? PM or nothing?
                        recipients.remove('AUTHORS')
                        recipients += assignee_emails
                    if recipients:
                        notifications.append({'issue': issue, 'recipients': recipients})
                    break
    return notifications


def process_notification_data(notification_data):
    if 'severity' not in notification_data:
        notification_data[notification_data] = {'default': ['AUTHOR']}
    if 'default_severity' not in notification_data:
        only_one_to_choose_from = 'severity' in notification_data and len(notification_data['severity']) == 1
        if only_one_to_choose_from:
            notification_data['default_severity'] = notification_data['severity'].keys()[0]
    if 'criteria' in notification_data:
        for label, timeframes in notification_data['criteria'].items():
            for timeframe in timeframes:
                if 'severity' in timeframe:
                    severity = timeframe['severity']
                else:
                    severity = notification_data['default_severity']
                timeframe['recipients'] = notification_data['severity'][severity]
                if 'catch-up' in notification_data and notification_data['catch-up']:
                    timeframe['catch-up'] = True
    else:
        raise(Exception('This system cannot function without notification "criteria" being specified'))
    return notification_data['criteria']


def get_notification_criteria():
    # todo: make config file dynamic
    with open('config.yaml', 'r') as yaml_file:
        notification_data = yaml.load(yaml_file)
    criteria = process_notification_data(notification_data)
    return criteria


def sort_issue_notifications_into_emails(issue_notifications):
    notification_groups = {}
    for notification in issue_notifications:
        recipients = ''.join(sorted(notification['recipients']))
        notification_groups[recipients] = notification_groups.get(recipients, []) + [notification]
    emails = []
    for note_group in notification_groups.values():
        issues = [notification['issue'] for notification in note_group]
        emails.append({'to': note_group[0]['recipients'], 'body': make_email_body(issues)})
    return emails


def send_email(subject, body, to=[], cc=[], bcc=[]):
    """
    This routine takes basic components, compiles and sends an email
    :param body: string containing HTML text to be sent
    :param to: LIST of subjects to mail to
    :param cc: LIST of subjects to cc
    :param bcc: LIST of subjects to bcc
    :return: None
    """
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    email_from = 'github_msg_bot@bot_machine.com'  # todo: figure this out
    msg['From'] = email_from
    if cc:
        msg['Cc'] = ', '.join(cc)

    server = smtplib.SMTP('localhost')
    server.sendmail(msg['From'], to + cc + bcc, msg.as_string())


def main(args=None):
    if args is None:
        args = arguments.Args()
        if len(args) < 3:
            print('Sends email reminders for Github Issues that need updates.')
            print('Usage: python report.py <GITHUB_TOKEN> <GITHUB_REPO> <GITHUB_ORG>')
            exit(1)
    token = args.get(0)
    repository = args.get(1)
    organization = args.get(2)
    if token is not None and repository is not None and organization is not None:
        g = Github(token)
        repos = g.get_organization(organization).get_repos(repository)
    criteria = get_notification_criteria()
    issue_notifications = get_notification_from_repos(criteria, repos)
    emails = sort_issue_notifications_into_emails(issue_notifications)
    for email in emails:
        send_email('Please update the following github issues', **email)


if __name__ == '__main__':
    main()
