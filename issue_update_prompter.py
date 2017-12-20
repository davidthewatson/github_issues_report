import dominate
import itertools
import copy
import bunch
import yaml
from datetime import datetime
from github import Github
import argparse
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
    if 'catch-up' in timeframe and timeframe.catch-up:
        return day_delta >= timeframe.days
    else:
        return day_delta == timeframe.days


def generate_recipients(timeframe, issue):
    recipients = copy.deepcopy(timeframe.recipients)
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


def get_notification_from_issues(criteria, issues):
    notifications = []
    notification_labels = set(criteria.keys())
    for issue in issues:
        issue_labels = set(str(issue.name) for issue in issue.labels)
        target_labels = issue_labels & notification_labels
        for target_label in target_labels:
            # reversed sorted order so if there is a different notification level at 60 and one at 30, only the 60 is sent
            for timeframe in sorted(criteria[target_label], key=lambda x: x.days, reverse=True):
                if time_to_notify(timeframe, issue.updated_at):
                    recipients = generate_recipients(timeframe, issue)
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
            notification_data['criteria'][label] = list(map(bunch.Bunch, timeframes))
    else:
        raise(Exception('This system cannot function without notification "criteria" being specified'))
    return notification_data['criteria']


def get_notification_criteria(config_file_path=None):
    # todo: should use a schema file to make sure format is correct
    if config_file_path is None:
        config_file_path = 'config.yaml'
    with open(config_file_path, 'r') as yaml_file:
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
        emails.append(bunch.Bunch({'to': note_group[0]['recipients'], 'body': make_email_body(issues),
                                   'issues': issues}))
    return emails


def print_email_debug(emails):
    print('Email Summary\n(Add --send flag to send out emails)')
    for email in emails:
        issue_titles = '    \n'.join(issue.title for issue in email.issues)
        print('recipients {} are getting {} emails:\n    {}'.format(emails.to, len(email.issues), issue_titles))


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


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Sends email reminders for Github Issues that need updates.')
    parser.add_argument('-s', '--send', dest='send', action='store_true', help="print email details but don't send")
    parser.add_argument('github_token', type=str, help='Github authentication token')
    parser.add_argument('github_repo', type=str, help='Target Github Repository')
    parser.add_argument('github_org', type=str, help='Target Github Organization')
    parser.add_argument('config_file_path', type=str, nargs='?', help='Full-path to config file', default='config.yaml')
    args = parser.parse_args()
    return args


def main(args=None):
    if args is None:
        args = get_arg_parser()
    token = args.github_token
    repository = args.github_repo
    organization = args.github_org
    config_file_path = args.config_file_path
    g = Github(token)
    repos = g.get_organization(organization).get_repos(repository)

    criteria = get_notification_criteria(config_file_path)
    issue_notifications = get_notification_from_repos(criteria, repos)
    emails = sort_issue_notifications_into_emails(issue_notifications)
    if args.send:
        for email in emails:
            send_email('Please update the following github issues', email.body, email.to)
    else:
        print_email_debug(emails)

if __name__ == '__main__':
    main()
