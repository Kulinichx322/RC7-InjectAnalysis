#import <Foundation/Foundation.h>
#import "RCModels.h"
NS_ASSUME_NONNULL_BEGIN
@interface RCAppScanner : NSObject
- (NSArray<RCAppRecord *> *)scanRegisteredApplications;
@end
NS_ASSUME_NONNULL_END
