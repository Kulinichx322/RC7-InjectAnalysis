#import "RCModels.h"

@implementation RCEnvironmentProfile
@end

@implementation RCScanTimelineEvent
@end

@implementation RCPackageRecord
@end

@implementation RCTweakRecord
- (NSString *)displayName {
    if (self.package.name.length) return self.package.name;
    if (self.plistName.length) return self.plistName;
    return @"Unknown Tweak";
}
@end

@implementation RCEmbeddedInjectionRecord
@end

@implementation RCEmbeddedScanResult
@end

@implementation RCScanMetrics
@end

@implementation RCAppRecord
@end

@implementation RCBlacklistResidueRecord
@end

@implementation RCAnalysisSnapshot
@end

NSString *RCConfidenceText(RCDetectionConfidence confidence) {
    switch (confidence) {
        case RCDetectionConfidenceHigh: return @"高";
        case RCDetectionConfidenceMedium: return @"中";
        default: return @"低";
    }
}

NSString *RCTweakIssueSeverityText(RCTweakIssueSeverity severity) {
    switch (severity) {
        case RCTweakIssueSeverityHighConfidence: return @"高置信度异常";
        case RCTweakIssueSeveritySuspicious: return @"可疑";
        case RCTweakIssueSeverityInformational: return @"信息";
        default: return @"正常";
    }
}

NSString *RCAppInstallSourceText(RCAppInstallSource source) {
    switch (source) {
        case RCAppInstallSourceTrollStore: return @"TrollStore";
        case RCAppInstallSourceTrollStoreLite: return @"TrollStore Lite";
        default: return @"未判定";
    }
}

NSString *RCTweakInstallSourceText(RCTweakInstallSource source) {
    switch (source) {
        case RCTweakInstallSourceDPKG: return @"软件包安装（DPKG）";
        default: return @"未识别";
    }
}

NSString *RCEmbeddedSourceText(RCEmbeddedInjectionSource source) {
    switch (source) {
        case RCEmbeddedInjectionSourceTrollFools: return @"TrollFools / 巨魔注入";
        default: return @"App 内嵌来源未识别";
    }
}
