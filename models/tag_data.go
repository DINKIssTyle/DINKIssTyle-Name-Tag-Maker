// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package models

// TextBox 네임태그 내 텍스트 박스
type TextBox struct {
	Label         string  `json:"label"`
	XMM           float64 `json:"x_mm"`
	YMM           float64 `json:"y_mm"`
	WidthMM       float64 `json:"width_mm"`
	HeightMM      float64 `json:"height_mm"`
	FontFamily    string  `json:"font_family"`
	FontSize      float64 `json:"font_size"`
	LineSpacing   float64 `json:"line_spacing"`
	LetterSpacing float64 `json:"letter_spacing"`
	Alignment     string  `json:"alignment"` // left, center, right
	Color         string  `json:"color"`
	Bold          bool    `json:"bold"`
	Italic        bool    `json:"italic"`
}

func DefaultTextBox() TextBox {
	return TextBox{
		Label:         "텍스트",
		XMM:           5.0,
		YMM:           5.0,
		WidthMM:       80.0,
		HeightMM:      15.0,
		FontFamily:    "Arial", // 기본 글꼴 (나중에 환경에 맞게 대체)
		FontSize:      12.0,
		LineSpacing:   1.2,
		LetterSpacing: 0.0,
		Alignment:     "center",
		Color:         "#000000",
		Bold:          false,
		Italic:        false,
	}
}

// TagTemplate 네임태그 템플릿
type TagTemplate struct {
	BackgroundImage string    `json:"background_image,omitempty"`
	TextBoxes       []TextBox `json:"text_boxes"`
}

func (t *TagTemplate) AddTextBox(label string) TextBox {
	if label == "" {
		label = "텍스트"
	}
	tb := DefaultTextBox()
	tb.Label = label
	tb.YMM = 5.0 + float64(len(t.TextBoxes))*18.0
	t.TextBoxes = append(t.TextBoxes, tb)
	return tb
}

func (t *TagTemplate) RemoveTextBox(index int) {
	if index >= 0 && index < len(t.TextBoxes) {
		t.TextBoxes = append(t.TextBoxes[:index], t.TextBoxes[index+1:]...)
	}
}

func (t *TagTemplate) MoveTextBox(fromIdx, toIdx int) {
	if fromIdx >= 0 && fromIdx < len(t.TextBoxes) && toIdx >= 0 && toIdx < len(t.TextBoxes) {
		item := t.TextBoxes[fromIdx]
		t.TextBoxes = append(t.TextBoxes[:fromIdx], t.TextBoxes[fromIdx+1:]...)

		// Insert at toIdx
		t.TextBoxes = append(t.TextBoxes[:toIdx], append([]TextBox{item}, t.TextBoxes[toIdx:]...)...)
	}
}

func (t *TagTemplate) GetLabels() []string {
	labels := make([]string, len(t.TextBoxes))
	for i, tb := range t.TextBoxes {
		labels[i] = tb.Label
	}
	return labels
}

// TagEntry 스프레드시트의 한 행 (네임태그 하나의 데이터)
type TagEntry struct {
	Checked bool     `json:"checked"`
	Values  []string `json:"values"`
}

func (e *TagEntry) GetValue(index int) string {
	if index >= 0 && index < len(e.Values) {
		return e.Values[index]
	}
	return ""
}

func (e *TagEntry) SetValue(index int, value string) {
	for len(e.Values) <= index {
		e.Values = append(e.Values, "")
	}
	e.Values[index] = value
}
