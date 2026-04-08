// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package utils

const (
	// ScreenDPI 화면 표시용 기본 DPI
	ScreenDPI = 96.0
	// PrintDPI 인쇄용 DPI
	PrintDPI = 300.0
	// MMPerInch 1인치당 밀리미터 비율
	MMPerInch = 25.4
)

// MMToInch converts mm to inches
func MMToInch(mm float64) float64 {
	return mm / MMPerInch
}

// InchToMM converts inches to mm
func InchToMM(inch float64) float64 {
	return inch * MMPerInch
}

// MMToPx converts mm to pixels
func MMToPx(mm float64, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	return mm / MMPerInch * dpi
}

// InchToPx converts inches to pixels
func InchToPx(inch float64, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	return inch * dpi
}

// PxToMM converts pixels to mm
func PxToMM(px float64, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	return px / dpi * MMPerInch
}

// PxToInch converts pixels to inches
func PxToInch(px float64, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	return px / dpi
}

// ToPx converts a value of given unit to pixels
func ToPx(value float64, unit string, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	switch unit {
	case "mm":
		return float64(MMToPx(value, dpi))
	case "inch":
		return float64(InchToPx(value, dpi))
	default:
		return value
	}
}

// FromPx converts a pixel value to the given unit
func FromPx(px float64, unit string, dpi float64) float64 {
	if dpi == 0 {
		dpi = ScreenDPI
	}
	switch unit {
	case "mm":
		return PxToMM(px, dpi)
	case "inch":
		return PxToInch(px, dpi)
	default:
		return px
	}
}

// MMToPt converts mm to points (1pt = 1/72 inch)
func MMToPt(mm float64) float64 {
	return mm / MMPerInch * 72
}

// PtToMM converts points to mm
func PtToMM(pt float64) float64 {
	return pt / 72 * MMPerInch
}
