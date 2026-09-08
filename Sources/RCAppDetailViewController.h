#import <UIKit/UIKit.h>
@class RCAppRecord;
@class RCAnalysisSnapshot;
NS_ASSUME_NONNULL_BEGIN
@interface RCAppDetailViewController : UITableViewController
- (instancetype)initWithAppRecord:(RCAppRecord *)record snapshot:(RCAnalysisSnapshot *)snapshot;
@end
NS_ASSUME_NONNULL_END
