#import <UIKit/UIKit.h>
@class RCAnalysisSnapshot;
NS_ASSUME_NONNULL_BEGIN
@interface RCAppBrowserViewController : UITableViewController <UISearchResultsUpdating>
- (instancetype)initWithSnapshot:(RCAnalysisSnapshot *)snapshot;
@end
NS_ASSUME_NONNULL_END
