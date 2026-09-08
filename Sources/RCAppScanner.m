#import "RCAppScanner.h"
#import <objc/message.h>
#import <objc/runtime.h>

static id RCMsg0(id obj, const char *selName) {
    if (!obj) return nil;
    SEL sel = sel_registerName(selName);
    if (![obj respondsToSelector:sel]) return nil;
    return ((id (*)(id, SEL))objc_msgSend)(obj, sel);
}

@implementation RCAppScanner
- (NSArray<RCAppRecord *> *)scanRegisteredApplications {
    Class workspaceClass = NSClassFromString(@"LSApplicationWorkspace");
    id workspace = RCMsg0((id)workspaceClass, "defaultWorkspace");
    NSArray *proxies = RCMsg0(workspace, "allInstalledApplications");
    if (![proxies isKindOfClass:NSArray.class]) return @[];

    NSFileManager *fm = NSFileManager.defaultManager;
    NSMutableArray<RCAppRecord *> *results = [NSMutableArray array];
    for (id proxy in proxies) {
        NSString *bundleID = RCMsg0(proxy, "bundleIdentifier");
        NSURL *bundleURL = RCMsg0(proxy, "bundleURL");
        NSString *name = RCMsg0(proxy, "localizedName");
        if (!name.length) name = RCMsg0(proxy, "itemName");
        NSString *executable = RCMsg0(proxy, "bundleExecutable");
        NSString *applicationType = RCMsg0(proxy, "applicationType");

        BOOL fileURL = [bundleURL isKindOfClass:NSURL.class] && bundleURL.isFileURL;
        NSString *bundlePath = fileURL ? bundleURL.path.stringByStandardizingPath : nil;
        BOOL looksLikeAppBundle = [bundlePath.pathExtension.lowercaseString isEqualToString:@"app"];
        BOOL bundlePathExists = bundlePath.length ? [fm fileExistsAtPath:bundlePath] : NO;

        RCAppRecord *r = [RCAppRecord new];
        r.bundleIdentifier = bundleID ?: @"";
        r.name = name.length ? name : (bundleID.length ? bundleID : @"Unknown App");
        r.bundlePath = bundlePath;
        r.bundleExecutable = executable;
        r.applicationType = applicationType;
        r.launchServicesRegistered = YES;
        r.bundlePathExists = bundlePathExists;

        // Analysis 1.0.x deliberately requires a file URL ending in .app.
        // A missing/non-file URL is "insufficient evidence", not an orphan.
        r.highConfidenceOrphanRegistration = (bundleID.length > 0 && fileURL && looksLikeAppBundle && bundlePath.length > 0 && !bundlePathExists);

        r.installSource = RCAppInstallSourceUnknown;
        r.installSourceConfidence = RCDetectionConfidenceLow;
        r.installSourceEvidence = @"未发现 TrollStore container marker；不据此推断 App Store/系统安装来源";
        r.matchedTweaks = @[];
        r.embeddedInjections = @[];

        if (bundlePath.length && looksLikeAppBundle) {
            NSString *container = bundlePath.stringByDeletingLastPathComponent;
            NSString *tsMarker = [container stringByAppendingPathComponent:@"_TrollStore"];
            NSString *tsLiteMarker = [container stringByAppendingPathComponent:@"_TrollStoreLite"];
            if ([fm fileExistsAtPath:tsMarker]) {
                r.installSource = RCAppInstallSourceTrollStore;
                r.installSourceConfidence = RCDetectionConfidenceHigh;
                r.installSourceEvidence = [NSString stringWithFormat:@"Container marker: %@", tsMarker];
            } else if ([fm fileExistsAtPath:tsLiteMarker]) {
                r.installSource = RCAppInstallSourceTrollStoreLite;
                r.installSourceConfidence = RCDetectionConfidenceHigh;
                r.installSourceEvidence = [NSString stringWithFormat:@"Container marker: %@", tsLiteMarker];
            }
        }
        [results addObject:r];
    }
    [results sortUsingComparator:^NSComparisonResult(RCAppRecord *a, RCAppRecord *b) {
        return [a.name localizedCaseInsensitiveCompare:b.name];
    }];
    return results;
}
@end
