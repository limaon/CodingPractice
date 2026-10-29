# CodingPractice Judge 0.2.0

An Anki **Desktop** add-on for the `CodingPractice` note type. It sends complete programs to a Judge0-compatible HTTPS endpoint, runs the note's standard-input test cases, and reports each verdict. It does not execute code on the Anki host.

## Install from AnkiWeb

After this add-on is approved/published on AnkiWeb, copy its numeric code from the add-on page. In Anki Desktop, open **Tools → Add-ons → Get Add-ons**, enter that code, install, and restart Anki. AnkiWeb assigns the numeric code; it cannot be selected in advance. AnkiWeb's review/approval and publication process is separate from building the package.

## Requirements and setup

- Anki Desktop with modern `gui_hooks` support. Mobile Anki clients do not run this Python add-on; cards remain readable there.
- The `CodingPractice` note type and its front template. The current front must contain the **Test Solution** button and `Test Cases` field integration.
- A reachable Judge0-compatible HTTPS endpoint. The default is `https://ce.judge0.com`, which was reachable during development; it is a public service and its availability, authorization rules, quotas, terms, and supported languages may change. For reliable/public use, configure an endpoint you are authorized to use.

Open **Tools → Add-ons → CodingPractice Judge → Config** to set the endpoint, optional `X-Auth-Token` API key, and resource limits. This release does not support provider-specific headers such as RapidAPI's additional headers. Restart Anki after changing add-on configuration.

## Privacy and execution

Only after the user clicks **Test Solution** and confirms the native Anki dialog, the add-on sends the source code, test inputs, and expected outputs to the configured endpoint. The provider processes the submission under its own policies; do not send private code, credentials, or personal data. The endpoint may retain submissions. The native confirmation displays the destination.

Test cases are a JSON array of 1–10 objects with string `input` and `expected` properties:

```json
[
  { "input": "2 3\n", "expected": "5\n" },
  { "input": "-4 4\n", "expected": "0\n" }
]
```

Limits: source 32 KiB; each input/output 16 KiB; per test 2 CPU seconds, 5 wall seconds, 128000 KB memory by default; 45 seconds maximum wait per suite. Runtime IDs are discovered from the selected endpoint, choosing the newest matching version. Compilation/runtime errors stop remaining tests. `Accepted` means the submitted cases passed, not that a solution is correct for every possible input.

## Troubleshooting

- **No response/add-on unavailable:** restart Anki Desktop and verify the add-on is enabled; use review mode, not the card-template preview.
- **HTTP 401/403:** the endpoint requires credentials or does not authorize this client. Configure a supported `X-Auth-Token` or choose another endpoint.
- **No active runtime:** check the endpoint's active language list and use a language name such as `python`, `javascript`, `cpp`, or `java` in the note.
- **Wrong Answer:** expand the case result to compare expected and actual output.
- **Timeout/service error:** this can be an endpoint or queue failure rather than an incorrect solution.

## Package for AnkiWeb

Create a `.ankiaddon` ZIP whose root contains `__init__.py`, `bridge.py`, `judge0.py`, `config.json`, `config.md`, `manifest.json`, and this README. Do not include an enclosing add-on folder, `__pycache__`, `.pyc`, local profiles, credentials, or test data. Include the project's `LICENSE`. Upload the package through AnkiWeb's add-on sharing page; after review, AnkiWeb provides the installable numeric code.

References:
- [One](https://addon-docs.ankiweb.net/sharing.html,)
- [Two](https://addon-docs.ankiweb.net/addon-folders.html,)
- [Three](https://addon-docs.ankiweb.net/hooks-and-filters.html,)
- [Four](https://addon-docs.ankiweb.net/background-ops.html,)
- [Five][https://github.com/judge0/judge0/tree/master/docs/api/submissions.]
