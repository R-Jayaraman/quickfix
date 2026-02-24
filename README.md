### Quickfix

quickfix work

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

## A2 — Multi-Site & Configuration

### Config Files Explanation

site_config.json is used for site-specific settings such as database name,
admin password, and developer_mode. Each site has its own site_config.json,
so values here apply only to that site.

common_site_config.json contains settings shared across all sites in the bench,
such as Redis configuration and database host.

If a secret is accidentally placed in common_site_config.json, it becomes
accessible to every site on the bench, which is a security risk and may allow
unauthorized access.

Sensitive credentials should always be stored in the individual site's
site_config.json to prevent cross-site exposure.

### Bench Start Processes

bench start launches four main processes:

1. Web — handles incoming HTTP requests
2. Worker — processes background jobs from the queue
3. Scheduler — triggers scheduled tasks (cron jobs)
4. SocketIO — manages real-time events and notifications

If the worker process crashes, background jobs such as emails, report
generation, and long-running tasks will stop processing and remain stuck in
the queue until the worker restarts.