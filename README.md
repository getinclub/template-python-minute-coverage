# The Coverage Report That Hid the Quiet Minutes

The release review expects a minute-by-minute coverage report for **alpha** and **beta**. The preview shows just two healthy rows. There should be six rows; a minute with 60 raw records also fails the distinct-second requirement.

Repair only **report.sql**. Keep harness.py, fixtures.py, monitor.py and the existing tests unchanged. Use Python 3.11+ with its standard-library SQLite. No pip packages, accounts, network or production database are needed.

```sh
python monitor.py
python -m unittest discover -v
```
Starter tests intentionally fail. After all pass, open a PR against main with your regression evidence. Do not hard-code asset names, windows or visible fixture outputs.

## Exact metric contract
For EACH asset in expected_assets and EACH minute in the report window, return exactly one row, even when no matching observation exists. An asset with no observations still belongs in the report. Empty roster or zero-length window means no rows.

- Table `expected_assets(asset TEXT PRIMARY KEY COLLATE BINARY)`: finite, authoritative roster. Asset labels are exact and case-sensitive; don't trim or normalize them.
- Table `report_window(start_second INTEGER, end_second INTEGER)`: exactly one row. Nonnegative UTC epoch-second bounds, both divisible by 60; half-open interval `[start_second,end_second)`. Each reporting minute starts at start_second + 60*k strictly below end_second. Windows span at most 1440 minutes.
- Table `observations(asset TEXT, observed_second INTEGER, valid INTEGER)`: authored records. A row contributes only when its asset exactly matches the roster, `valid=1`, and its non-null timestamp is in the relevant half-open minute. `valid=0` or NULL, null asset or timestamp, out-of-roster assets and out-of-window timestamps contribute nothing. Duplicate observations of the same second contribute only one covered second for that asset. A valid observation counts even if an invalid duplicate exists. Different assets never share coverage credit.
- Timestamp units are whole seconds, not milliseconds. No time-zone or daylight-saving conversion. All windows contain whole 60-second minutes; there is no partial-minute denominator.

Return these columns, in this exact order:
`asset`, `minute_start`, `covered_seconds`, `expected_seconds`, `status`.
`covered_seconds` is an integer from 0 to 60; `expected_seconds` is always integer 60. `status` is exactly `HEALTHY` when covered_seconds=60, otherwise `GAP` (including 0). No percentage/rounding column. Sort by asset using SQLite BINARY collation, then minute_start ascending. Do not return aggregate summaries or extra rows/columns.

The harness validates input shapes and types before executing the SQL. It provides at most 100 unique nonempty asset labels, 1440 minutes and 100,000 observation rows, an asset/time index, and a query-work guard. Preserve this interface; solving means changing the query, not pre-cleaning fixtures or hiding failed results. The guard is a runaway-query safety limit, not a performance benchmark or security sandbox. The SQL must be a single read-only statement.

## Incident fixture
Window [0,180), roster alpha,beta. alpha covers every second 0–59. Its next minute has seconds 60–118 plus a repeated record at second60. Neither asset has records for minute120, and beta has none anywhere. Expected rows:

| asset | minute_start | covered_seconds | expected_seconds | status |
|---|---:|---:|---:|---|
| alpha | 0 | 60 | 60 | HEALTHY |
| alpha | 60 | 59 | 60 | GAP |
| alpha | 120 | 0 | 60 | GAP |
| beta | 0 | 0 | 60 | GAP |
| beta | 60 | 0 | 60 | GAP |
| beta | 120 | 0 | 60 | GAP |

This reports observed second coverage under an authored requirement. It is not a claim that every real asset must emit once per second or that silence always indicates a production outage. Freshness, late-arrival policy, changing rosters and business SLOs would need separate real-world contracts. Actual GetIn import, provisioning, CI/webhooks and grading are unverified.

`HEALTHY` means only complete coverage under this authored once-per-second requirement. It does not assess value accuracy, freshness, correctness, or broader service health.

The monitor prints an informational preview and does not set a pass/fail exit status. Use the unit-test command as the local acceptance gate.
