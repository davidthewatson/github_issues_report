# Generate Github Issues Report

## Install

    pyenv local 3.5.2
    mkvirtualenv github_issues_report
    pip install -r requirements.txt

Usage:

    python report.py <GITHUB_TOKEN> <GITHUB_REPO> <GITHUB_ORG> <GITHUB_ISSUE_LABEL> >report.html

The code in this repo generates a report based on the arguments by hitting the Github API and returning an HTML table of issues like this:

    <h1>Github Issue Status</h1>
    <table border="1" cellpadding="10" width="1024">
      <tbody>
        <thead>
          <tr>
            <th>NUMBER</th>
            <th>TITLE</th>
            <th>ASSIGNEE</th>
            <th>PRIORITY</th>
            <th>STATUS</th>
          </tr>
        </thead>
        <tr>
          <td>
            <a href="https://github.com/davidthewatson/fizzbuzz/issues/1">1</a>
          </td>
          <td width="200">This repo is harmful to children!</td>
          <td width="200">david watson</td>
          <td width="100">2</td>
          <td><p><strong>Please add status comment!</strong></p></td>
        </tr>
      </tbody>
    </table>

When it's formatted:

<h1>Github Issue Status</h1>
<table border="1" cellpadding="10" width="1024">
  <tbody>
    <thead>
      <tr>
        <th>NUMBER</th>
        <th>TITLE</th>
        <th>ASSIGNEE</th>
        <th>PRIORITY</th>
        <th>STATUS</th>
      </tr>
    </thead>
    <tr>
      <td>
        <a href="https://github.com/davidthewatson/fizzbuzz/issues/1">1</a>
      </td>
      <td width="200">This repo is harmful to children!</td>
      <td width="200">david watson</td>
      <td width="100">2</td>
      <td><p><strong>Please add status comment!</strong></p></td>
    </tr>
  </tbody>
</table>
