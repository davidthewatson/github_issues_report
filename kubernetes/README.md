# Kubernetes README
Create four files named github-token, github-repository, github-organization, github-tag.
Make the content of each of the files the information needed.

INSTALL

0. `kubectl create secret generic github-creds --from-file=github-token --from-file=github-repository --from-file=github-organization --from-file=github-tag`
0. `kubectl create -f .\cronjob.yaml`
