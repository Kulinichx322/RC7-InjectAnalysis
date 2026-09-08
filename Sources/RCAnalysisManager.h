#import <Foundation/Foundation.h>
#import "RCModels.h"
NS_ASSUME_NONNULL_BEGIN
@interface RCAnalysisManager : NSObject
+ (instancetype)sharedManager;
@property (atomic, strong, readonly, nullable) RCAnalysisSnapshot *snapshot;
- (void)refreshWithCompletion:(void (^)(RCAnalysisSnapshot *snapshot))completion;
@end
NS_ASSUME_NONNULL_END
