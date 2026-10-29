# CodingPractice for Anki

Standalone Git repository containing only the CodingPractice Anki template and
its Anki Desktop Judge0 add-on.

## Contents

- `template/` — note type fields, card templates, styling, and template usage documentation.
- `addon/` — Anki Desktop bridge and Judge0 client.
- `LICENSE` — GPL-3.0, inherited from the source repository.

The add-on sends source and test cases to the configured Judge0-compatible HTTPS endpoint only after native confirmation in Anki. The default endpoint is public; its availability, access rules, and quotas can change. Configure an endpoint you are authorized to use, and do not submit private code or personal data.

## Build an AnkiWeb package

From the repository root, run `python3 scripts/build_addon.py`. It creates a `.ankiaddon` ZIP in `dist/` with files at archive root (no enclosing folder), includes `LICENSE`, and refuses a non-empty API key. The package omits `__pycache__`, `.pyc`, profile data, and credentials. Upload it through AnkiWeb's add-on sharing page; AnkiWeb assigns the install code after publication.

GitHub Actions checks Python syntax and builds the package on pushes, pull requests, and manual runs. Download the `.ankiaddon` from the successful run's **Artifacts** section.

See `addon/README.md` for Judge0 setup, limits, privacy, test-case format, and troubleshooting.
