# Generate Github Issues Report

You can run this code locally or using docker. Pick your poison:

## Local Install

    pyenv local 3.5.2
    mkvirtualenv github_issues_report
    pip install -r requirements.txt

Usage:

    python report.py <GITHUB_TOKEN> <GITHUB_REPO> <GITHUB_ORG> <GITHUB_ISSUE_LABEL> >report.html

## Docker Container
    docker build .
    docker images
    docker tag <ID_OF_WHAT_YOU_JUST_BUILT> your_dockerhub_user/github_issues_report:latest
    docker run davidthewatson/github_issues_report python report.py <YOUR_API_TOKEN> <YOUR_REPO> <YOUR_ORG> <YOUR_LABEL> >report.html

The result is the same regardless of whether you run locally or via docker container.

The code in this repo generates a report based on the arguments by hitting the Github API and returning an HTML table of issues like this:

    <h1>Github Issue Status</h1>
    <table border="1" cellpadding="10" width="1024">
      <tbody>
        <thead>
          <tr>
            <th>NUMBER</th>
            <th>TITLE</th>
            <th>ASSIGNEES</th>
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
        <th>ASSIGNEES</th>
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

## issue_update_prompter.py

The issue update prompting tool builds off of the basic issue report. It checks the target github repository, identifies issues which should be updated and emails issue tables to those responsible. The indentification of issues require update is based on a yaml config fill that defines how often issues with certain tags should be updated. The emails are sent to the public email addresses associated with the github assignees of each issue. The emails are sent from 'localhost' and require that an smtp server to running on the host machine.

An example email is below:

<h3>Please update, close or change the priority of the following issues so your team knows what is going on.</h3>
<table border="1" cellpadding="10" width="1024">
  <tbody>
    <thead>
      <tr>
        <th>NUMBER</th>
        <th>TITLE</th>
        <th>ASSIGNEES</th>
        <th>PRIORITY</th>
        <th>STATUS</th>
      </tr>
    </thead>
    <tr>
      <td>
        <a href="https://github.com/davidthewatson/fizzbuzz/issues/1">1</a>
      </td>
      <td width="200">This repo is harmful to children!</td>
      <td width="200">David Watson</td>
      <td width="100">2</td>
      <td><p><strong>Updated that was a long time able for this issue</strong></p></td>
    </tr>
  </tbody>
</table>

