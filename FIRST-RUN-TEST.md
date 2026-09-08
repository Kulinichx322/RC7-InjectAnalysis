# RCInjectAnalysis 1.0.14 — first device test protocol

This protocol is intentionally read-only. Do not add cleanup, unregister, uicache, respring or blacklist-write actions during this test pass.

## 0. Build receipt before installation

Before installing anything, keep the pipeline-generated `RCInjectAnalysis-1.0.14-RELEASE-RECEIPT.txt` next to the final deb. Confirm it records the intended package version/SHA, both arm64/arm64e UUIDs, `StaticReleaseGate=PASS`, and `RuntimeDeviceTest=NOT_PERFORMED`. Use `FIELD-REPORT-TEMPLATE.md` for the observations returned after the run.

Before install, also confirm `BuildID` and `SourceTreeSHA256` are present in the release receipt and deployment manifest. Keep the `provenance/` source snapshot intact; the first in-app report should show the same BuildID/source-tree digest. A mismatch is a packaging/build-identity warning, not a scanner result.

If there is no release receipt or the exact final deb was changed after the receipt was generated, rerun the release pipeline/static gate before installing. Prefer installing from `RCInjectAnalysis-1.0.14-DEPLOYMENT-KIT.zip`; verify the kit first and keep its `rollback/` deb untouched.

## A. Install / launch sanity

1. Keep the original `1.3.9+bindtrust1` deb available as rollback.
2. Install the generated `+analysis1.0.14` deb.
3. Launch RootHide Manager normally.
4. Confirm original blacklist/settings functions still open and render normally.
5. Confirm a new `Analysis 1.0.14` section appears with `注入分析` and `环境检查`.
6. Open both pages repeatedly and return to the native menu. There must be no duplicate Analysis section and no launch crash.

Record PASS/FAIL, crash time if any, and the shared full diagnostic report.

## B. Build / runtime identity

Before interpreting any scanner result, open `环境检查` and verify the first two rows plus the full report `[Build / Runtime Identity]`.

Expected for a deb produced by the 1.0.14 builder:

- `AnalysisVersion=1.0.14`;
- runtime architecture is `arm64` or `arm64e` as appropriate for the loaded slice;
- `LoadedImage` resolves to `RootHide.app/Frameworks/RCInjectAnalysis.dylib`;
- `LoadedImageUUID` is non-empty;
- `LoadedPathExpected=YES`;
- `HostWeakLoadPresent=YES`;
- `MenuHooksInstalled=YES`;
- hook install attempts is normally `1` (a later successful retry is acceptable if the host class was not ready on the first constructor attempt);
- `ManifestPresent=YES`;
- manifest version matches 1.0.14;
- manifest UUID for the current runtime architecture matches the in-memory loaded slice UUID;
- `ManifestLoadMode=weak`;
- install-name equals `@executable_path/Frameworks/RCInjectAnalysis.dylib`;
- manifest signed-dylib SHA-256 is non-empty;
- `RuntimeSelfCheck=PASS`;
- `HostExecutableState=YES`, with uid `0`, gid `0`, executable + setuid; actual mode is reported;
- `DylibFileState=YES`.

If the Analysis menu is visible but the manifest is missing, the current slice UUID mismatches the manifest, or the host weak load is absent, treat that as a loose/development load or packaging mismatch and return the full report before debugging scanner logic. If the menu is not visible, capture device crash/logging and verify the built deb with `Integration/verify_release.py` before changing detection code.

## B2. Static final-package gate

Before installing the generated deb, run:

```sh
python3 Integration/verify_release.py \
  '/path/to/original.deb' \
  --built-deb '/path/to/com.roothide.manager_1.3.9+bindtrust1+analysis1.0.14.deb'
```

Expected: `RELEASE GATE PASS`. The package-delta subcheck must report that only the RootHide executable and Version field changed and only the Analysis dylib/buildinfo files were added. Any other changed/removed/new original package entry is a stop condition.

## C. RootHide runtime profile

Open `环境检查` → `RootHide 运行环境` before interpreting scan results.

Expected on the target RC7 baseline:

- `RootHide: 检测到`;
- `jbroot: 可用`;
- `jbroot image` identifies the image that exports the symbol when resolvable;
- logical and mapped paths are displayed for TweakInject, DPKG status/info and RootHideConfig.

Do not require `Path mapping: ACTIVE` as a universal PASS condition. Compare the mapped paths with the capability checks instead.

## D. Capability / preflight gate

Inspect `启动自检`.

Expected on a normal packaged RC7 target:

- `Analysis loaded path` PASS;
- `RC7 host weak load` PASS;
- `Analysis build manifest` PASS;
- `RC7 menu hooks` PASS;
- `Runtime release self-check` PASS;
- `RootHide jbroot` PASS;
- `SettingViewController` PASS;
- `LSApplicationWorkspace` PASS;
- `TweakInject path` PASS;
- `DPKG status` PASS;
- `DPKG info` PASS;
- RootHide config is either present or explicitly using RC7 default semantics.

A WARN is not automatically an Analysis bug. Return the complete report before interpreting dependent empty results.

## E. Scan timeline / performance

Record:

- `Scan-ID` for each refresh;
- total duration;
- tweak + DPKG phase;
- LaunchServices phase;
- blacklist phase;
- match-graph phase;
- TrollFools / embedded phase;
- embedded entries visited;
- Apps actually deep-scanned;
- incomplete App count;
- `timeLimitedApps`;
- `globalSkippedApps`;
- slowest embedded App + duration.

1.0.14 budgets are deliberately soft: 50,000 entries/App, 1.5s/App and 12s total for the TrollFools phase. If any budget fires, verify that the report contains `[Budget / Anomaly Locator]` and the exact stop reason (`entry-limit`, `per-app-time` or `global-time`).

A budget hit must change only the TrollFools/embedded source to partial/not-scanned. DPKG, Filter, blacklist and orphan-registration results must remain available. An App skipped after the global budget expires must never be presented as a clean TrollFools result.

Refresh three times. The slow phase should remain identifiable. Concurrent refresh requests should coalesce rather than start duplicate full scans.

## F. Searchable App browser

Open `注入分析` → `单 App 深度分析`.

Expected:

- list count matches the current LaunchServices snapshot App count;
- searching by display name filters correctly;
- searching by exact/partial Bundle ID filters correctly;
- clearing the query restores the full list;
- opening an App pushes a detail page without starting a destructive action;
- opening/closing the browser repeatedly does not duplicate the Analysis menu.

If LaunchServices preflight failed, the browser must show `App 深度分析不可用`, not an empty App list.

## G. Normal App detail control

Choose a normal installed App that is not expected to have RootHide tweak matches or TrollFools evidence.

Verify:

- the detail page shows `证据层级` / Layer 0 through Layer 4;
- Layer 4 explicitly says runtime process proof is not collected;
- Bundle ID and Bundle Path are correct;
- existing path is not reported as an orphan;
- unknown install source remains `未知` rather than being guessed as App Store;
- if TrollFools traversal was actually attempted and completed, zero evidence may display as `未发现 TrollFools 高置信度证据`;
- if the App is not eligible for the current TrollFools-specific scan, detail must say `未执行` / `不适用`, not `未发现`.

## H. Known multi-tweak App

Choose one installed App already known to have at least two RootHide tweaks whose `Filter.Bundles` contain its Bundle ID.

Expected:

- App appears in `多插件 Filter 匹配`;
- count equals matching Filter records;
- the same App is reachable from the searchable browser;
- detail lists every matching tweak;
- each tweak explains `Filter.Bundles` contains the App Bundle ID;
- exact filter plist path is shown;
- complete scanned Bundles list is shown;
- package/version is correct when DPKG is available;
- blacklist state is shown separately from Filter matching.

The page must not call this a confirmed conflict or runtime-load proof.

## I. DPKG source test

Choose a tweak known to be installed as a Debian package.

Expected:

- exact path ownership in `/Library/dpkg/info/*.list` → `软件包安装（DPKG）`, high confidence;
- unique basename-only fallback → DPKG, medium confidence;
- no owner → unknown, not automatically `manual install`;
- UI does not claim the frontend was definitely Sileo.

## J. TrollStore App source

Test at least one known TrollStore-installed App.

Expected:

- `_TrollStore` marker → TrollStore, high confidence;
- `_TrollStoreLite` marker → TrollStore Lite, high confidence;
- normal App Store/system Apps are not labelled TrollStore merely because of container layout.

## K. TrollFools injection evidence

Use an App whose TrollFools state is already known.

Expected active case:

- per-App status says embedded scan was attempted;
- `.troll-fools.bak` evidence exists;
- current Mach-O has a dylib Load Command absent from the backup;
- detail/report shows active difference confirmed and the added load path.

Expected inactive/old-backup case:

- backup marker alone is not called active injection.

Expected skipped case:

- missing/nonexistent Bundle Path or a path outside the current user-App TrollFools scan scope is `NOT SCANNED` / `未执行`;
- it must not be converted to `未发现 TrollFools`.

## L. RootHide + TrollFools mixed-source case

If available, use an App with both:

- one or more RootHide Bundles-filter matches and a **known supported RC7 blacklist state that permits injection**;
- confirmed active TrollFools Load Command difference.

Expected: it appears in `RootHide 允许 + TrollFools 活动注入`.

If blacklist is unsupported/unknown, or either scan source is unavailable, expected result is an incomplete/unknown condition rather than `未发现`.

## M. Orphan / white-icon registration

Test controls first:

- normal App → must not be reported;
- TrollStore App → must not be reported merely because of install source;
- normal RootHide App → must not be reported.

Then test one genuine white-icon residual registration if available.

High-confidence orphan report requires all of:

- LaunchServices registration present;
- Bundle ID present;
- file URL/path obtainable;
- path is a `.app` path;
- actual `.app` path does not exist.

For such an orphan, TrollFools deep scan should be shown as not executed because the `.app` path is missing. No unregister or icon-cache action should be offered in 1.0.14.

## N. Stale blacklist record

Expected residue requires:

- `appconfig[bundleID]` stored truthy;
- Bundle ID absent from the current LaunchServices snapshot.

Stored false entries must not be reported as stale blacklist residue.

If `blacklistDisabled=YES`, treat ordinary per-App blacklist state as unsupported/unknown for injection-permission inference.

## O. Per-App report

On each test App, tap `报告`.

Verify the report contains:

- `APP READ ONLY REPORT`;
- Bundle ID / path / installation-source evidence;
- snapshot capabilities;
- `Scan-ID`;
- `EmbeddedScanAttempted`, `Truncated`, `Entries`, `Duration`, `StopReason`, time-budget/global-skip state and `Status`;
- `[Evidence Layers]` including Layer 4 runtime-proof-not-collected wording;
- RootHide Filter matches with plist/Bundles evidence;
- TrollFools backup/load evidence when present;
- interpretation wording that does not claim a runtime conflict.

The report is shared as an in-memory string; Analysis should not create a diagnostic file.

## P. Full report handling

Tap `报告` on `注入分析` or `环境检查` and return:

1. the complete full report;
2. the per-App report for each failed/interesting case;
3. the App used for the multi-tweak test;
4. the tweak used for DPKG ownership;
5. the Apps used for TrollStore/TrollFools tests;
6. whether a genuine white-icon residual registration was available.

Reports may include App names, Bundle IDs, package IDs/versions and filesystem paths. Review them before sharing outside a trusted debugging context.

## Stop conditions

Rollback immediately to the original RC7 deb if any of these occur:

- RootHide Manager no longer launches;
- original blacklist UI/functionality changes unexpectedly;
- repeated Analysis menu insertion;
- scan causes persistent UI hang;
- a normal control App is reported as high-confidence orphan registration;
- a skipped/unavailable source is presented as a definitive clean result;
- Analysis performs any state-changing action.
