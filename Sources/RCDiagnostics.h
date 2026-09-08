#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@class RCAnalysisSnapshot;
@class RCEnvironmentProfile;
@class RCAppRecord;

@interface RCDiagnosticItem : NSObject
@property (nonatomic, copy) NSString *name;
@property (nonatomic) BOOL passed;
@property (nonatomic, copy) NSString *detail;
@end

@interface RCDiagnostics : NSObject
- (RCEnvironmentProfile *)environmentProfile;
- (NSArray<RCDiagnosticItem *> *)runPreflight;
+ (NSString *)plainTextReportForItems:(NSArray<RCDiagnosticItem *> *)items;
+ (NSString *)fullReadOnlyReportForSnapshot:(RCAnalysisSnapshot *)snapshot;
+ (NSString *)readOnlyReportForApp:(RCAppRecord *)app snapshot:(RCAnalysisSnapshot *)snapshot;
@end

FOUNDATION_EXPORT void RCLog(NSString *format, ...) NS_FORMAT_FUNCTION(1,2);

NS_ASSUME_NONNULL_END
