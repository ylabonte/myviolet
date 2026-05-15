# Contributing

## Development setup

```bash
git clone https://github.com/ylabonte/myviolet.git
cd myviolet

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e . --group dev --group test
pre-commit install
```

The repository ships with a devcontainer (`.devcontainer/devcontainer.json`)
that takes care of all of the above and auto-starts the local mock service on
port 8080. Open the repo in VS Code or GitHub Codespaces to use it.

## Running tests

```bash
pytest                             # unit tests with coverage
pytest -x                          # stop on first failure
pytest tests/test_readings.py -v   # run a single file
pytest -m integration              # integration tests (need the mock running)
```

## Code quality

```bash
ruff check .                       # lint
ruff format .                      # auto-format
mypy src                           # type check
```

Pre-commit hooks run these automatically on `git commit`.

## Mock service

The mock service replays a captured `demo.myviolet.de` snapshot and applies
writes to its in-memory state, so integration tests can verify true
round-trips against a faithful (if simplified) controller.

```bash
python -m tools.myviolet_mock      # listens on :8080, basic auth admin/admin
```

The devcontainer starts this automatically.

## Submitting changes

1. Fork the repository and create a feature branch from `main`.
2. Make your changes with tests.
3. Ensure `pytest`, `ruff check .`, and `mypy src` all pass locally.
4. **Add a changeset** if your change is user-visible (dep change, API change, bugfix,
   release-relevant docs):

   ```bash
   npx --yes @changesets/cli@^2 add
   ```

   Pick the bump type (major / minor / patch) and write a short narrative description. Commit
   the resulting `.changeset/<random-slug>.md` along with your code. See
   [`.changeset/README.md`](.changeset/README.md) for the full release flow.
5. Open a pull request against `main`. Use the PR template.

## Ideas and questions

Use [GitHub Issues](https://github.com/ylabonte/myviolet/issues) for
feature requests, bug reports, and questions so the community can benefit.

## Contact

Yannic Labonte <yannic.labonte@gmail.com>
