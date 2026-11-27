# Cleaning log

Produced by `cleaning.py` from the actual run — every number below was measured, not typed in.

| Step | Rows |
|---|---|
| Rows in raw file | 12,120 |
| Exact duplicate rows removed | 120 |
| Distinct raw city spellings seen | 31 |
| Distinct cities after standardising | 20 |
| Rows dropped — missing city | 124 |
| Rows dropped — missing or non-positive quantity | 92 |
| Rows dropped — missing or non-positive unit price | 55 |
| Rows in cleaned file | 11,729 |

Rules applied: exact duplicates dropped; city spellings standardised (Bangalore→Bengaluru, Bombay→Mumbai, Calcutta→Kolkata, New Delhi→Delhi, plus case/space variants); category and status trimmed and title-cased; region re-derived from the cleaned city; rows with missing city, or missing / non-positive quantity or unit price, dropped.
