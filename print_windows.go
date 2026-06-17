// Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

//go:build windows
package main

import (
	"fmt"
	"syscall"
	"unsafe"
)

var (
	shell32          = syscall.NewLazyDLL("shell32.dll")
	procShellExecute = shell32.NewProc("ShellExecuteW")
)

func PrintPDF(filePath string) {
	verbPtr, _ := syscall.UTF16PtrFromString("print")
	filePtr, _ := syscall.UTF16PtrFromString(filePath)

	// ShellExecuteW(hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd)
	// SW_HIDE = 0
	ret, _, err := procShellExecute.Call(
		0,
		uintptr(unsafe.Pointer(verbPtr)),
		uintptr(unsafe.Pointer(filePtr)),
		0,
		0,
		0, // SW_HIDE
	)

	fmt.Printf("[PrintPDF] ShellExecuteW 'print' result code: %d, err: %v\n", ret, err)

	// A return value less than or equal to 32 specifies an error.
	if ret <= 32 {
		fmt.Printf("[PrintPDF] 'print' verb failed. Falling back to 'open' verb...\n")
		// If "print" verb fails (due to lack of association etc.), open the PDF using default viewer so the user can print it manually.
		openVerbPtr, _ := syscall.UTF16PtrFromString("open")
		// SW_SHOWNORMAL = 1
		retOpen, _, errOpen := procShellExecute.Call(
			0,
			uintptr(unsafe.Pointer(openVerbPtr)),
			uintptr(unsafe.Pointer(filePtr)),
			0,
			0,
			1, // SW_SHOWNORMAL
		)
		fmt.Printf("[PrintPDF] ShellExecuteW 'open' result code: %d, err: %v\n", retOpen, errOpen)
	}
}
