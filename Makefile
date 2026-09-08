TARGET := iphone:clang:latest:15.0
ARCHS = arm64 arm64e

include $(THEOS)/makefiles/common.mk

before-all::
	@python3 Integration/generate_version_header.py

LIBRARY_NAME = RCInjectAnalysis
RCInjectAnalysis_FILES = \
    Sources/RCEntry.mm \
    Sources/RCPath.mm \
    Sources/RCModels.m \
    Sources/RCBuildInfo.m \
    Sources/RCDpkgResolver.m \
    Sources/RCTweakScanner.m \
    Sources/RCAppScanner.m \
    Sources/RCBlacklistStateScanner.m \
    Sources/RCDiagnostics.m \
    Sources/RCMachOScanner.m \
    Sources/RCAnalysisManager.m \
    Sources/RCAnalysisViewController.m \
    Sources/RCAppBrowserViewController.m \
    Sources/RCEnvironmentViewController.m \
    Sources/RCAppDetailViewController.m
RCInjectAnalysis_FRAMEWORKS = Foundation UIKit
RCInjectAnalysis_CFLAGS = -fobjc-arc -Wall -Wextra
RCInjectAnalysis_LDFLAGS = -Wl,-install_name,@executable_path/Frameworks/RCInjectAnalysis.dylib

include $(THEOS_MAKE_PATH)/library.mk
