// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package utils

import (
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

// FontInfo stores font name and its file path
type FontInfo struct {
	Family string
	Path   string
}

// FindSystemFonts scans OS-specific directories for font files
func FindSystemFonts() []FontInfo {
	var fontDirs []string

	switch runtime.GOOS {
	case "darwin":
		fontDirs = []string{
			"/System/Library/Fonts/Supplemental",
			"/System/Library/Fonts",
			"/Library/Fonts",
			filepath.Join(os.Getenv("HOME"), "Library/Fonts"),
		}
	case "windows":
		windir := os.Getenv("WINDIR")
		if windir == "" {
			windir = "C:\\Windows"
		}
		fontDirs = []string{filepath.Join(windir, "Fonts")}
	case "linux":
		fontDirs = []string{
			"/usr/share/fonts",
			"/usr/local/share/fonts",
			filepath.Join(os.Getenv("HOME"), ".fonts"),
		}
	}

	var fonts []FontInfo
	seenFamilies := make(map[string]bool)

	for _, dir := range fontDirs {
		_ = filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil
			}
			if info.IsDir() {
				return nil
			}

			ext := strings.ToLower(filepath.Ext(path))
			if ext == ".ttf" || ext == ".otf" || ext == ".ttc" {
				family := strings.TrimSuffix(filepath.Base(path), ext)

				// Basic cleaning for presentation
				family = strings.ReplaceAll(family, "-", " ")
				family = strings.ReplaceAll(family, "_", " ")

				// Detect if it's already seen (case insensitive)
				key := strings.ToLower(family)
				if !seenFamilies[key] {
					fonts = append(fonts, FontInfo{
						Family: family,
						Path:   path,
					})
					seenFamilies[key] = true
				}
			}
			return nil
		})
	}

	return fonts
}
