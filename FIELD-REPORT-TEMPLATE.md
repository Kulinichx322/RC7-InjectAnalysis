# RCInjectAnalysis 1.0.14 — first-device field report template

Paste the **完整报告** from `环境检查 → 报告` first. Do not manually rewrite its values.

Then add only the observations below:

```text
Installed deb filename:
Installed deb SHA-256 (if known):
Device / iOS:
RC7 Manager launches normally: YES / NO
Original blacklist UI still works: YES / NO
Analysis menu appears exactly once: YES / NO
Runtime Self-Check: PASS / WARN

Known multi-tweak App Bundle ID:
Expected tweak names/packages:
Observed Analysis result:

Known TrollStore App Bundle ID:
Observed installation source:

Known TrollFools-injected App Bundle ID:
Observed backup-diff result:

Known normal App incorrectly reported orphan: YES / NO
If YES, Bundle ID:

Real white-icon/orphan Bundle ID (if available):
Observed orphan result:

Any scan budget stop reasons:
entry-limit / per-app-time / global-time / none

Crash/hang/repro steps, if any:
```

If a single App is wrong, also open `单 App 深度分析`, share that App's report, and keep its `Scan-ID` together with the full report. A matching Scan-ID proves both reports came from the same snapshot.

Do **not** use a cleanup/unregister workaround during the first Analysis 1.0.14 validation. The purpose of this report is to measure false positives, false negatives, path/capability failures, and runtime identity before any destructive feature is considered.
