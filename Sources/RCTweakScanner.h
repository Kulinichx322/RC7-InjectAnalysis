#import <Foundation/Foundation.h>
#import "RCModels.h"
@class RCDpkgResolver;
NS_ASSUME_NONNULL_BEGIN
@interface RCTweakScanner : NSObject
- (NSArray<RCTweakRecord *> *)scanWithPackageResolver:(RCDpkgResolver *)resolver;
@end
NS_ASSUME_NONNULL_END
