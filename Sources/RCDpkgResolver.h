#import <Foundation/Foundation.h>
#import "RCModels.h"

NS_ASSUME_NONNULL_BEGIN
@interface RCDpkgResolver : NSObject
@property (nonatomic, readonly) NSDictionary<NSString *, RCPackageRecord *> *packagesByIdentifier;
- (void)reload;
- (nullable RCPackageRecord *)packageOwningInstalledPath:(NSString *)path;
- (nullable RCPackageRecord *)packageOwningInstalledPath:(NSString *)path
                                               confidence:(RCDetectionConfidence * _Nullable)confidence
                                                 evidence:(NSString * _Nullable * _Nullable)evidence;
@end
NS_ASSUME_NONNULL_END
