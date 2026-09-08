#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

#ifdef __cplusplus
extern "C" {
#endif

FOUNDATION_EXPORT NSString *RCAnalysisVersion(void);
FOUNDATION_EXPORT NSString *RCAnalysisExpectedInstallName(void);
FOUNDATION_EXPORT NSString *RCAnalysisLoadedImagePath(void);
FOUNDATION_EXPORT NSString *RCAnalysisLoadedImageUUID(void);
FOUNDATION_EXPORT NSString *RCAnalysisRuntimeArchitecture(void);
FOUNDATION_EXPORT BOOL RCAnalysisLoadedImagePathLooksExpected(void);
FOUNDATION_EXPORT BOOL RCAnalysisHostHasExpectedWeakLoad(void);
FOUNDATION_EXPORT NSString *RCAnalysisHostWeakLoadDetail(void);
FOUNDATION_EXPORT NSDictionary<NSString *, id> *RCAnalysisBuildManifest(void);
FOUNDATION_EXPORT NSString *RCAnalysisBuildManifestPath(void);
FOUNDATION_EXPORT NSDictionary<NSString *, id> *RCAnalysisHostExecutableFileState(void);
FOUNDATION_EXPORT NSDictionary<NSString *, id> *RCAnalysisLoadedDylibFileState(void);

#ifdef __cplusplus
}
#endif

NS_ASSUME_NONNULL_END
