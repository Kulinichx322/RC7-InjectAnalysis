#import <Foundation/Foundation.h>
#import "RCModels.h"
NS_ASSUME_NONNULL_BEGIN
@interface RCMachOScanner : NSObject
- (NSSet<NSString *> *)loadDylibPathsAtMachOPath:(NSString *)path;
- (NSArray<RCEmbeddedInjectionRecord *> *)scanTrollFoolsEvidenceForApp:(RCAppRecord *)app;
- (RCEmbeddedScanResult *)scanTrollFoolsEvidenceForApp:(RCAppRecord *)app maxEntries:(NSUInteger)maxEntries;
- (RCEmbeddedScanResult *)scanTrollFoolsEvidenceForApp:(RCAppRecord *)app
                                            maxEntries:(NSUInteger)maxEntries
                                              deadline:(NSTimeInterval)deadline
                                         timeoutReason:(NSString *)timeoutReason;
@end
NS_ASSUME_NONNULL_END
