//go:build darwin
package main

/*
#cgo CFLAGS: -x objective-c
#cgo LDFLAGS: -framework Cocoa -framework Quartz
#import <Cocoa/Cocoa.h>
#import <Quartz/Quartz.h>

void PrintPDFNatively(const char* filePath) {
    @autoreleasepool {
        NSString* path = [NSString stringWithUTF8String:filePath];
        NSURL* url = [NSURL fileURLWithPath:path];
        PDFDocument* doc = [[PDFDocument alloc] initWithURL:url];
        if (doc) {
            NSPrintInfo* printInfo = [NSPrintInfo sharedPrintInfo];
            // scalingMode: 1 is kPDFPrintPageScaleToFit
            NSPrintOperation* printOp = [doc printOperationForPrintInfo:printInfo scalingMode:1 autoRotate:YES];
            [printOp setShowsPrintPanel:YES];
            [printOp setShowsProgressPanel:YES];
            
            // Run Cocoa operations on main thread
            dispatch_async(dispatch_get_main_queue(), ^{
                [printOp runOperation];
            });
        }
    }
}
*/
import "C"
import "unsafe"

func PrintPDF(filePath string) {
	cFilePath := C.CString(filePath)
	defer C.free(unsafe.Pointer(cFilePath))
	C.PrintPDFNatively(cFilePath)
}
