//go:build !darwin
package main

func PrintPDF(filePath string) {
	// Fallback/No-op for other systems (we can implement Windows PDF printing if needed)
}
