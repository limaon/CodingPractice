# CodingPractice Judge settings

Edit through **Tools → Add-ons → CodingPractice Judge → Config** in Anki.

- `enabled`: enables the reviewer bridge.
- `model_name`: exact Anki note-type name allowed to request tests.
- `judge0_endpoint`: Judge0-compatible HTTPS endpoint. The default public endpoint
  is for convenience only; availability and use policies can change.
- `judge0_api_key`: optional secret sent in `X-Auth-Token`. Keep credentials out
  of cards and shared screenshots. Anki stores add-on configuration locally.
- `cpu_time_limit`: CPU seconds per test (default 2).
- `wall_time_limit`: wall-clock seconds per test (default 5).
- `memory_limit`: memory in kilobytes per test (default 128000).

The add-on shows a native confirmation before sending source and tests to the
configured remote endpoint. Credentials for providers requiring other header
schemes are not supported in this version.
