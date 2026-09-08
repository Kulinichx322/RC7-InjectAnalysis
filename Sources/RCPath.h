#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN
FOUNDATION_EXPORT NSString *RCRootPath(NSString *logicalPath);
FOUNDATION_EXPORT NSString *RCLogicalPackagePath(NSString *path);
FOUNDATION_EXPORT BOOL RCJBRootAvailable(void);
FOUNDATION_EXPORT NSString *RCJBRootImagePath(void);
NS_ASSUME_NONNULL_END
