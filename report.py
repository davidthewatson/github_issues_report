import markdown
import dominate
import bunch
from github import Github
from clint import arguments
from dominate.tags import table, thead, tbody, tr, td, th, h1, a
from dominate.util import raw


def make_table_header():
    h = thead()
    with h:
        r = tr()
        r.add(th('NUMBER'))
        r.add(th('TITLE'))
        r.add(th('ASSIGNEES'))
        r.add(th('PRIORITY'))
        r.add(th('LAST COMMENT'))


def make_table_row(decorated_issue):
    r = tr()
    with r:
        td(a(decorated_issue.issue.number, href=decorated_issue.issue.html_url))
        td(decorated_issue.issue.title, width='200')
        td(raw(decorated_issue.assignees), width='200')
        td(raw(decorated_issue.priority), width='100')
        td(raw(decorated_issue.last_comment))


def github_name(github_user):
    if github_user.name is not None:
        return github_user.name
    else:
        return github_user.login


def assemble_attribue_dict(issue):
    if issue.assignees is not None:
        assignees = ', '.join((github_name(assignee) for assignee in issue.assignees))
    elif issue.assignee is not None:
        assignees = github_name(issue.assignee)
    else:
        assignees = markdown.markdown('**Please assign!**')
    if str(issue.labels).find('priority') > -1:
        priority = [l.name.split(':')[1] for l in issue.labels if 'priority' in l.name][0]
    else:
        priority = markdown.markdown('**Please set priority!**')
    if issue.comments != 0:
        last_comment = [markdown.markdown(comment.body) for comment in issue.get_comments()][-1]
    else:
        last_comment = markdown.markdown('**Please add last_comment comment!**')
    return {'issue': issue, 'assignees': assignees, 'priority': priority, 'last_comment': last_comment}


def build_bunch(**kwargs):
    decorated_issue = bunch.Bunch()
    for k, v in kwargs.items():
        decorated_issue[k] = v
    return decorated_issue


def filter_issue(issue, label):
    if label is not None:
        if label in str(issue.labels):
            return True
    return False


def build_decorated_issues(issues):
    decorated_issues = []
    for issue in issues:
        d = assemble_attribue_dict(issue)
        decorated_issue = build_bunch(**d)
        decorated_issues.append(decorated_issue)
    return decorated_issues


def make_table(repos, label):
    make_table_header()
    for repo in repos:
        issues = repo.get_issues()
        issues = filter(lambda x: filter_issue(x, label), issues)
        decorated_issues = build_decorated_issues(issues)
        decorated_issues.sort(key=lambda issue: issue.priority)
        for decorated_issue in decorated_issues:
            make_table_row(decorated_issue)


def main(args=None):
    if args == None:
        args = arguments.Args()
        if len(args) < 4:
            print('Returns Github Issues from the Github API based on the arguments and generates an HTML table.')
            print('Usage: python report.py <GITHUB_TOKEN> <GITHUB_REPO> <GITHUB_ORG> <GITHUB_ISSUE_LABEL> >report.html')
            exit(1)
    token = args.get(0)
    repository = args.get(1)
    organization = args.get(2)
    label = args.get(3)
    if token is not None and repository is not None and organization is not None and label is not None:
        g = Github(token)
        repos = g.get_organization(organization).get_repos(repository)
    title = 'Github Issue Status'
    d = dominate.document(title=title)
    with d.body:
        h1(title)
        with table(border='1', width='1024', cellpadding='10').add(tbody()):
            make_table(repos, label)
    print(d)


if __name__ == '__main__':
    main()
