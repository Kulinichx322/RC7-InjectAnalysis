#import <Foundation/Foundation.h>
#import "RCModels.h"
NS_ASSUME_NONNULL_BEGIN
@interface RCBlacklistStateScanner : NSObject
- (void)applyBlacklistStateToApps:(NSArray<RCAppRecord *> *)apps;
- (NSArray<RCBlacklistResidueRecord *> *)scanResidualEntriesAgainstApps:(NSArray<RCAppRecord *> *)apps;
@end
NS_ASSUME_NONNULL_END
