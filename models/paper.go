// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package models

var PaperPresets = map[string][2]float64{
	"A3":     {297.0, 420.0},
	"A4":     {210.0, 297.0},
	"A5":     {148.0, 210.0},
	"B4":     {250.0, 353.0},
	"B5":     {176.0, 250.0},
	"Letter": {215.9, 279.4},
	"Legal":  {215.9, 355.6},
	"Custom": {210.0, 297.0},
}

// PaperSize 용지 크기
type PaperSize struct {
	Name     string  `json:"name"`
	WidthMM  float64 `json:"width_mm"`
	HeightMM float64 `json:"height_mm"`
}

func DefaultPaperSize() PaperSize {
	return PaperSize{
		Name:     "A4",
		WidthMM:  210.0,
		HeightMM: 297.0,
	}
}

func PaperSizeFromPreset(name string) PaperSize {
	if size, ok := PaperPresets[name]; ok {
		return PaperSize{
			Name:     name,
			WidthMM:  size[0],
			HeightMM: size[1],
		}
	}
	return DefaultPaperSize()
}

// TagLayout 네임태그 레이아웃 설정
type TagLayout struct {
	TagWidthMM  float64 `json:"tag_width_mm"`
	TagHeightMM float64 `json:"tag_height_mm"`
	Columns     int     `json:"columns"`
	Rows        int     `json:"rows"`
	OffsetXMM   float64 `json:"offset_x_mm"`
	OffsetYMM   float64 `json:"offset_y_mm"`
	GapXMM      float64 `json:"gap_x_mm"`
	GapYMM      float64 `json:"gap_y_mm"`
}

func DefaultTagLayout() TagLayout {
	return TagLayout{
		TagWidthMM:  90.0,
		TagHeightMM: 54.0,
		Columns:     2,
		Rows:        5,
		OffsetXMM:   15.0,
		OffsetYMM:   13.5,
		GapXMM:      0.0,
		GapYMM:      0.0,
	}
}
