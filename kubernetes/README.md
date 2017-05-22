# Create Secrets
Create four files named github-token, github-repository, github-organization, github-tag.
Make the content of each of the files the information needed.
Create a generic secret in Kubernetes:
`kubectl create secret generic github-creds --from-file=github-token --from-file=github-repository --from-file=github-organization --from-file=github-tag`
