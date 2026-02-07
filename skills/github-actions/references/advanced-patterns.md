# GitHub Actions Advanced Patterns

## Conditional Execution

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: npm run deploy

- name: Comment on PR
  if: failure()
  uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: 'Build failed!'
      })
```

## Reusable Workflows

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy Template
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      deploy_key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ inputs.environment }}"
```

Use in another workflow:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: ...
  
  deploy:
    needs: build
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
    secrets:
      deploy_key: ${{ secrets.DEPLOY_KEY }}
```

## Notifications

### Slack Notification
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}",
        "status": "${{ job.status }}"
      }
```

### Email on Failure
```yaml
- name: Send email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USER }}
    password: ${{ secrets.EMAIL_PASS }}
    to: team@example.com
    subject: Build failed!
```

## Rate Limiting & Retries

```yaml
- name: Deploy with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 5
    max_attempts: 3
    retry_wait_seconds: 10
    command: npm run deploy
```

## Self-Hosted Runners

Use your own server for long builds or private dependencies:

```yaml
runs-on: [self-hosted, linux, x64]
```

Register runner via repo Settings → Actions → Runners
