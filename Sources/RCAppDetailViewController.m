#import "RCAppDetailViewController.h"
#import "RCModels.h"
#import "RCDiagnostics.h"
#import "RCBuildInfo.h"

@interface RCAppDetailViewController ()
@property (nonatomic, strong) RCAppRecord *record;
@property (nonatomic, strong) RCAnalysisSnapshot *snapshot;
@end

@implementation RCAppDetailViewController
- (instancetype)initWithAppRecord:(RCAppRecord *)record snapshot:(RCAnalysisSnapshot *)snapshot {
    self = [super initWithStyle:UITableViewStyleInsetGrouped];
    if (self) { _record = record; _snapshot = snapshot; }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = self.record.name.length ? self.record.name : self.record.bundleIdentifier;
    self.navigationItem.rightBarButtonItem = [[UIBarButtonItem alloc] initWithTitle:@"报告" style:UIBarButtonItemStylePlain target:self action:@selector(shareReport)];
}

- (void)shareReport {
    NSString *report = [RCDiagnostics readOnlyReportForApp:self.record snapshot:self.snapshot];
    UIActivityViewController *vc = [[UIActivityViewController alloc] initWithActivityItems:@[report] applicationActivities:nil];
    vc.popoverPresentationController.barButtonItem = self.navigationItem.rightBarButtonItem;
    [self presentViewController:vc animated:YES completion:nil];
}

- (NSUInteger)activeEmbeddedCount {
    NSUInteger count = 0;
    for (RCEmbeddedInjectionRecord *r in self.record.embeddedInjections) if (r.activeDifferenceConfirmed) count++;
    return count;
}

- (BOOL)rootHideConfigurationPermitsInjection {
    return self.record.matchedTweaks.count > 0 && self.record.blacklistSupported && self.record.blacklistStateKnown && !self.record.blacklisted;
}

- (NSString *)rootHideSummary {
    if (!self.snapshot.tweakScanAvailable) return @"RootHide tweak 数据源不可用；不能判断 Filter 匹配";
    if (!self.record.matchedTweaks.count) return @"未发现按 Bundle ID 匹配的 RootHide tweak Filter";
    if (!self.record.blacklistSupported) return [NSString stringWithFormat:@"匹配 %lu 个 RootHide Filter；当前环境不支持普通 blacklist 状态判定", (unsigned long)self.record.matchedTweaks.count];
    if (!self.record.blacklistStateKnown) return [NSString stringWithFormat:@"匹配 %lu 个 RootHide Filter；blacklist 状态未知，不能判断配置是否允许注入", (unsigned long)self.record.matchedTweaks.count];
    if (self.record.blacklisted) return [NSString stringWithFormat:@"匹配 %lu 个 RootHide Filter，但 App 已 blacklist；Filter 匹配不等于当前实际注入", (unsigned long)self.record.matchedTweaks.count];
    return [NSString stringWithFormat:@"匹配 %lu 个 RootHide Filter，且 RC7 blacklist 配置允许；这是配置层推断，不是运行时 dylib 已加载证明", (unsigned long)self.record.matchedTweaks.count];
}

- (NSString *)embeddedSummary {
    if (!self.snapshot.embeddedEvidenceAvailable) return @"App bundle / TrollFools 证据扫描不可用；不能作未发现结论";
    if (!self.record.embeddedScanAttempted) return [NSString stringWithFormat:@"未执行 TrollFools 深度扫描：%@；不作‘未发现’结论", self.record.embeddedScanStatus.length ? self.record.embeddedScanStatus : @"原因未知"];
    if (self.record.embeddedScanTruncated) return [NSString stringWithFormat:@"TrollFools 证据为部分扫描：%@（已遍历 %lu 项，耗时 %.3fs）；结果可能不完整", self.record.embeddedScanStopReason.length ? self.record.embeddedScanStopReason : @"budget", (unsigned long)self.record.embeddedScanEntriesVisited, self.record.embeddedScanDuration];
    NSUInteger active = [self activeEmbeddedCount];
    if (active) return [NSString stringWithFormat:@"确认 %lu 条 TrollFools Load Command 活动差分", (unsigned long)active];
    if (self.record.embeddedInjections.count) return [NSString stringWithFormat:@"发现 %lu 条 TrollFools 来源证据，但当前活动 Load Command 差分未确认", (unsigned long)self.record.embeddedInjections.count];
    return @"未发现 TrollFools 高置信度证据；这不等于证明不存在其它 App 内嵌注入";
}

- (NSString *)combinedInterpretation {
    BOOL rootPermitted = [self rootHideConfigurationPermitsInjection];
    NSUInteger activeEmbedded = [self activeEmbeddedCount];
    if (rootPermitted && activeEmbedded) return @"⚠ 检测到 RootHide 配置允许 + TrollFools 活动 Load Command 差分。属于双来源注入证据，但仍不等同于运行时冲突证明。";
    if (self.record.matchedTweaks.count >= 2) return [NSString stringWithFormat:@"⚠ %lu 个 RootHide tweak Filter 同时匹配此 App。属于多插件匹配，不代表一定冲突。", (unsigned long)self.record.matchedTweaks.count];
    if (activeEmbedded) return @"检测到 TrollFools 活动注入差分。没有同时满足 RootHide 双来源判定条件。";
    if (self.record.highConfidenceOrphanRegistration) return @"⚠ LaunchServices 仍注册此 App，但对应 .app 路径不存在，符合高置信度孤立注册条件。";
    return @"当前没有触发高置信度组合提示；请结合下面各数据源状态和证据逐项判断。";
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView { return 6; }
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) return 5;
    if (section == 1) return 5;
    if (section == 2) return 3;
    if (section == 3) return MAX((NSUInteger)1, self.record.matchedTweaks.count);
    if (section == 4) return MAX((NSUInteger)1, self.record.embeddedInjections.count);
    return 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    if (section == 0) return @"应用 / RC7 状态";
    if (section == 1) return @"证据层级";
    if (section == 2) return @"注入摘要";
    if (section == 3) return @"RootHide Bundles Filter 匹配";
    if (section == 4) return @"App 内嵌 / TrollFools 证据";
    return @"解释";
}

- (UITableViewCell *)cellWithTitle:(NSString *)title detail:(NSString *)detail {
    UITableViewCell *cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:nil];
    cell.textLabel.text = title;
    cell.textLabel.numberOfLines = 0;
    cell.detailTextLabel.text = detail;
    cell.detailTextLabel.numberOfLines = 0;
    cell.selectionStyle = UITableViewCellSelectionStyleNone;
    return cell;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 0) {
        if (indexPath.row == 0) return [self cellWithTitle:self.record.bundleIdentifier detail:self.record.bundlePath ?: @"无 Bundle Path"];
        if (indexPath.row == 1) return [self cellWithTitle:[NSString stringWithFormat:@"安装来源：%@", RCAppInstallSourceText(self.record.installSource)] detail:[NSString stringWithFormat:@"置信度：%@\n%@", RCConfidenceText(self.record.installSourceConfidence), self.record.installSourceEvidence ?: @""]];
        if (indexPath.row == 2) {
            NSString *title = self.record.launchServicesRegistered ? @"LaunchServices：已注册" : @"LaunchServices：未确认注册";
            NSString *detail = self.record.bundlePath.length ? [NSString stringWithFormat:@"Bundle Path：%@\n实际路径：%@", self.record.bundlePath, self.record.bundlePathExists ? @"存在" : @"不存在"] : @"Bundle Path 不可用";
            return [self cellWithTitle:title detail:detail];
        }
        if (indexPath.row == 3) {
            NSString *title = self.record.highConfidenceOrphanRegistration ? @"⚠ 高置信度孤立应用注册" : (self.record.bundlePathExists ? @"孤立注册：未发现" : @"孤立注册：证据不足，未判定");
            NSString *detail = self.record.highConfidenceOrphanRegistration ? @"LaunchServices 有 Bundle ID / 标准 .app Path，但实际 .app 不存在" : (self.record.bundlePathExists ? @"Bundle Path 存在" : @"Bundle Path 不可用或不满足保守 .app 路径条件");
            return [self cellWithTitle:title detail:detail];
        }
        NSString *title = !self.record.blacklistStateKnown ? (self.record.blacklistSupported ? @"RC7 Blacklist：状态未知" : @"RC7 Blacklist：当前环境不支持") : (self.record.blacklisted ? @"RC7 Blacklist：已加入" : @"RC7 Blacklist：未加入");
        return [self cellWithTitle:title detail:self.record.blacklistEvidence ?: @""];
    }

    if (indexPath.section == 1) {
        if (indexPath.row == 0) {
            NSString *embeddedState = !self.snapshot.embeddedEvidenceAvailable ? @"不可用" : (!self.record.embeddedScanAttempted ? @"未扫描/不适用" : (self.record.embeddedScanTruncated ? @"部分" : @"完整"));
            NSString *detail = [NSString stringWithFormat:@"LaunchServices=%@ · TweakInject=%@ · DPKG=%@ · Blacklist=%@ · Embedded=%@",
                                self.snapshot.launchServicesAvailable ? @"可用" : @"不可用",
                                self.snapshot.tweakScanAvailable ? @"可用" : @"不可用",
                                (self.snapshot.dpkgStatusAvailable && self.snapshot.dpkgInfoAvailable) ? @"完整" : @"不完整",
                                self.snapshot.blacklistStateAvailable ? @"可用" : @"不完整", embeddedState];
            return [self cellWithTitle:@"Layer 0 · 数据源完整性" detail:detail];
        }
        if (indexPath.row == 1) {
            NSString *black = !self.record.blacklistSupported ? @"blacklist 不适用/不支持" : (!self.record.blacklistStateKnown ? @"blacklist 未知" : (self.record.blacklisted ? @"blacklist 阻止" : @"blacklist 配置允许"));
            return [self cellWithTitle:@"Layer 1 · 配置证据" detail:[NSString stringWithFormat:@"Filter.Bundles 匹配 %lu 个；%@。这仍不是运行时加载证明。", (unsigned long)self.record.matchedTweaks.count, black]];
        }
        if (indexPath.row == 2) {
            NSUInteger high = 0, medium = 0, unknown = 0;
            for (RCTweakRecord *t in self.record.matchedTweaks) {
                if (t.installSource == RCTweakInstallSourceDPKG && t.sourceConfidence == RCDetectionConfidenceHigh) high++;
                else if (t.installSource == RCTweakInstallSourceDPKG) medium++;
                else unknown++;
            }
            return [self cellWithTitle:@"Layer 2 · 来源 / 归属证据" detail:[NSString stringWithFormat:@"App 来源：%@（%@）；匹配 tweak DPKG 高=%lu 中/降级=%lu 未识别=%lu", RCAppInstallSourceText(self.record.installSource), RCConfidenceText(self.record.installSourceConfidence), (unsigned long)high, (unsigned long)medium, (unsigned long)unknown]];
        }
        if (indexPath.row == 3) {
            return [self cellWithTitle:@"Layer 3 · 二进制差分证据" detail:[NSString stringWithFormat:@"TrollFools 活动 Load Command 差分=%lu；scan=%@；stop=%@；duration=%.3fs", (unsigned long)[self activeEmbeddedCount], self.record.embeddedScanAttempted ? (self.record.embeddedScanTruncated ? @"部分" : @"完成") : @"未执行", self.record.embeddedScanStopReason.length ? self.record.embeddedScanStopReason : @"none", self.record.embeddedScanDuration]];
        }
        return [self cellWithTitle:@"Layer 4 · 运行时进程证明" detail:[NSString stringWithFormat:@"Analysis %@ 不读取目标 App 进程的 dyld image 列表，也不把配置/文件差分升级成‘运行时已加载’或‘确认冲突’。", RCAnalysisVersion()]];
    }

    if (indexPath.section == 2) {
        if (indexPath.row == 0) return [self cellWithTitle:@"RootHide" detail:[self rootHideSummary]];
        if (indexPath.row == 1) return [self cellWithTitle:@"TrollFools / App 内嵌" detail:[self embeddedSummary]];
        return [self cellWithTitle:@"组合判定" detail:[self combinedInterpretation]];
    }

    if (indexPath.section == 3) {
        if (!self.snapshot.tweakScanAvailable) return [self cellWithTitle:@"RootHide tweak 扫描不可用" detail:@"TweakInject 数据源未通过 preflight；这里不把空结果显示为未发现"];
        if (!self.record.matchedTweaks.count) return [self cellWithTitle:@"未发现 Bundle ID Filter 匹配" detail:@"扫描已执行；当前没有 tweak 的 Filter.Bundles 包含此 Bundle ID"];
        RCTweakRecord *t = self.record.matchedTweaks[indexPath.row];
        NSString *filterList = t.bundleIdentifiers.count ? [t.bundleIdentifiers componentsJoinedByString:@", "] : @"(无 Bundles filter)";
        NSString *detail = [NSString stringWithFormat:@"匹配原因：Filter.Bundles 包含 %@\nFilter plist：%@\nFilter.Bundles：%@\nPackage：%@\nVersion：%@\n来源：%@（%@）", self.record.bundleIdentifier ?: @"", t.plistPath ?: @"?", filterList, t.package.packageIdentifier ?: @"未识别", t.package.version ?: @"", RCTweakInstallSourceText(t.installSource), RCConfidenceText(t.sourceConfidence)];
        if (t.installSourceEvidence.length) detail = [detail stringByAppendingFormat:@"\n来源证据：%@", t.installSourceEvidence];
        if (!self.snapshot.dpkgStatusAvailable || !self.snapshot.dpkgInfoAvailable) detail = [detail stringByAppendingString:@"\nDPKG capability 不完整：来源字段可能为未知/降级置信度"];
        if (self.record.blacklistStateKnown && self.record.blacklisted) detail = [detail stringByAppendingString:@"\nRC7 状态：App 已 blacklist；Filter 匹配不等于实际注入"];
        return [self cellWithTitle:t.displayName detail:detail];
    }

    if (indexPath.section == 4) {
        if (!self.snapshot.embeddedEvidenceAvailable) return [self cellWithTitle:@"TrollFools 证据扫描不可用" detail:@"LaunchServices/App bundle 数据源不可用；空结果不能解释为未发现"];
        if (!self.record.embeddedScanAttempted) return [self cellWithTitle:@"TrollFools 深度扫描未执行" detail:self.record.embeddedScanStatus.length ? self.record.embeddedScanStatus : @"原因未知；不作未发现结论"];
        if (!self.record.embeddedInjections.count) {
            NSString *title = self.record.embeddedScanTruncated ? @"⚠ TrollFools 证据扫描不完整" : @"未发现 TrollFools 高置信度证据";
            NSString *detail = self.record.embeddedScanTruncated ? [NSString stringWithFormat:@"部分扫描：stop=%@，遍历 %lu 项，耗时 %.3fs。可能存在未扫描到的 .troll-fools.bak；DPKG/Filter/blacklist/孤立注册不受此项影响。", self.record.embeddedScanStopReason.length ? self.record.embeddedScanStopReason : @"budget", (unsigned long)self.record.embeddedScanEntriesVisited, self.record.embeddedScanDuration] : @"扫描已执行并在预算内完成；没有 backup-diff 证据时不会把普通 Framework/Dylib 当成巨魔注入。";
            return [self cellWithTitle:title detail:detail];
        }
        RCEmbeddedInjectionRecord *r = self.record.embeddedInjections[indexPath.row];
        NSString *title = r.loadPath.length ? r.loadPath.lastPathComponent : RCEmbeddedSourceText(r.source);
        NSString *detail = [NSString stringWithFormat:@"来源：%@\n活动差分：%@\n置信度：%@\nTarget Mach-O：%@\nBackup：%@\nLoad：%@\n证据：%@", RCEmbeddedSourceText(r.source), r.activeDifferenceConfirmed ? @"已确认" : @"未确认", RCConfidenceText(r.confidence), r.targetMachOPath ?: @"?", r.backupPath ?: @"?", r.loadPath ?: @"?", r.evidence ?: @""];
        return [self cellWithTitle:title detail:detail];
    }

    return [self cellWithTitle:@"判读原则" detail:@"Filter 匹配表示插件声明支持该 Bundle ID；blacklist 允许表示 RC7 配置层未阻止；TrollFools backup-diff 表示 App Mach-O 出现相对备份新增 Load Command。任何一项都不单独等于‘插件冲突’，也不替代运行时进程级证明。"];
}
@end
