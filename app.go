// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"image/color"
	"os"
	"sort"
	"strconv"
	"strings"

	"NameTagMaker/models"
	"NameTagMaker/utils"

	"github.com/signintech/gopdf"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx     context.Context
	fontMap map[string]string // Family Name -> File Path
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	// Cache system fonts on startup
	a.fontMap = make(map[string]string)
	fonts := utils.FindSystemFonts()
	for _, f := range fonts {
		a.fontMap[f.Family] = f.Path
	}
}

// --- Default Model Providers ---

func (a *App) GetDefaultPaperSize() models.PaperSize {
	return models.DefaultPaperSize()
}

func (a *App) GetDefaultTagLayout() models.TagLayout {
	return models.DefaultTagLayout()
}

func (a *App) GetDefaultTagTemplate() models.TagTemplate {
	template := models.TagTemplate{}
	template.AddTextBox("이름")
	template.AddTextBox("직책")
	return template
}

// --- App Info ---

func (a *App) GetAppInfo() map[string]string {
	return map[string]string{
		"version":   "1.0",
		"buildDate": "2026-02-27",
	}
}

// --- Project Persistence ---

func (a *App) SaveProject(data models.ProjectData) (string, error) {
	filePath, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{
		Title: "프로젝트 저장",
		Filters: []runtime.FileFilter{
			{DisplayName: "명찰 프로젝트 파일 (*.ntag)", Pattern: "*.ntag"},
		},
		DefaultFilename: "project.ntag",
	})
	if err != nil || filePath == "" {
		return "", err
	}

	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return "", err
	}

	err = os.WriteFile(filePath, jsonData, 0644)
	return filePath, err
}

func (a *App) LoadProject() (*models.ProjectData, error) {
	filePath, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "프로젝트 열기",
		Filters: []runtime.FileFilter{
			{DisplayName: "명찰 프로젝트 파일 (*.ntag)", Pattern: "*.ntag"},
		},
	})
	if err != nil || filePath == "" {
		return nil, err
	}

	fileData, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var data models.ProjectData
	err = json.Unmarshal(fileData, &data)
	return &data, err
}

// --- Data Import/Export ---

func (a *App) ImportCSV() (*models.CSVResult, error) {
	filePath, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "CSV 파일 가져오기",
		Filters: []runtime.FileFilter{
			{DisplayName: "CSV / TSV 파일 (*.csv *.tsv *.txt)", Pattern: "*.csv;*.tsv;*.txt"},
		},
	})
	if err != nil || filePath == "" {
		return nil, err
	}

	content, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	headers, data, err := utils.ImportCSVText(string(content))
	if err != nil {
		return nil, err
	}

	return &models.CSVResult{Headers: headers, Data: data}, nil
}

func (a *App) ExportCSV(headers []string, data [][]string) (string, error) {
	filePath, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{
		Title: "CSV 파일 내보내기",
		Filters: []runtime.FileFilter{
			{DisplayName: "CSV 파일 (*.csv)", Pattern: "*.csv"},
			{DisplayName: "TSV 파일 (*.tsv)", Pattern: "*.tsv"},
		},
		DefaultFilename: "export.csv",
	})
	if err != nil || filePath == "" {
		return "", err
	}

	delimiter := ','
	if strings.HasSuffix(strings.ToLower(filePath), ".tsv") {
		delimiter = '\t'
	}

	csvText, err := utils.ExportCSVText(headers, data, rune(delimiter))
	if err != nil {
		return "", err
	}

	err = os.WriteFile(filePath, []byte(csvText), 0644)
	return filePath, err
}

// --- Asset Selection ---

func (a *App) SelectBackgroundImage() (string, error) {
	filePath, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "배경 이미지 선택",
		Filters: []runtime.FileFilter{
			{DisplayName: "이미지 파일 (*.png *.jpg *.jpeg *.bmp *.gif)", Pattern: "*.png;*.jpg;*.jpeg;*.bmp;*.gif"},
		},
	})
	if err != nil || filePath == "" {
		return "", err
	}
	return filePath, nil
}

func (a *App) GetSystemFonts() []utils.FontInfo {
	if a.fontMap == nil {
		return []utils.FontInfo{{Family: "Arial", Path: ""}}
	}
	fonts := make([]utils.FontInfo, 0, len(a.fontMap))
	for family, path := range a.fontMap {
		fonts = append(fonts, utils.FontInfo{Family: family, Path: path})
	}
	sort.Slice(fonts, func(i, j int) bool {
		return fonts[i].Family < fonts[j].Family
	})
	return fonts
}

// --- PDF Generation ---

func hexToRGBA(hex string) color.RGBA {
	hex = strings.TrimPrefix(hex, "#")
	if len(hex) == 6 {
		r, _ := strconv.ParseUint(hex[0:2], 16, 8)
		g, _ := strconv.ParseUint(hex[2:4], 16, 8)
		b, _ := strconv.ParseUint(hex[4:6], 16, 8)
		return color.RGBA{uint8(r), uint8(g), uint8(b), 255}
	}
	return color.RGBA{0, 0, 0, 255}
}

func (a *App) SavePDF(data models.ProjectData) (string, error) {
	filePath, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{
		Title:           "PDF로 저장",
		Filters:         []runtime.FileFilter{{DisplayName: "PDF 파일 (*.pdf)", Pattern: "*.pdf"}},
		DefaultFilename: "output.pdf",
	})
	if err != nil || filePath == "" {
		return "", err
	}

	pdf := gopdf.GoPdf{}
	mmToPt := 2.83464
	pdf.Start(gopdf.Config{
		PageSize: gopdf.Rect{
			W: data.Paper.WidthMM * mmToPt,
			H: data.Paper.HeightMM * mmToPt,
		},
	})

	totalTagsPerPage := data.Layout.Columns * data.Layout.Rows
	if totalTagsPerPage <= 0 {
		return "", fmt.Errorf("invalid layout")
	}

	for i, entry := range data.Entries {
		if !entry.Checked {
			continue
		}

		tagIndexOnPage := i % totalTagsPerPage
		if tagIndexOnPage == 0 {
			pdf.AddPage()
		}

		col := tagIndexOnPage % data.Layout.Columns
		row := tagIndexOnPage / data.Layout.Columns

		tagX := data.Layout.OffsetXMM + float64(col)*(data.Layout.TagWidthMM+data.Layout.GapXMM)
		tagY := data.Layout.OffsetYMM + float64(row)*(data.Layout.TagHeightMM+data.Layout.GapYMM)

		if data.Template.BackgroundImage != "" {
			_ = pdf.Image(data.Template.BackgroundImage, tagX*mmToPt, tagY*mmToPt, &gopdf.Rect{
				W: data.Layout.TagWidthMM * mmToPt,
				H: data.Layout.TagHeightMM * mmToPt,
			})
		}

		for _, tb := range data.Template.TextBoxes {
			text := tb.Label
			for valIdx, val := range entry.Values {
				placeholder := fmt.Sprintf("{%d}", valIdx+1)
				text = strings.ReplaceAll(text, placeholder, val)
			}
			// Apply common values if placeholders remain
			for valIdx, val := range data.CommonValues {
				placeholder := fmt.Sprintf("{%d}", valIdx+1)
				if strings.Contains(text, placeholder) && val != "" {
					text = strings.ReplaceAll(text, placeholder, val)
				}
			}

			rgba := hexToRGBA(tb.Color)
			pdf.SetFillColor(rgba.R, rgba.G, rgba.B)

			fontSize := tb.FontSize
			if fontSize <= 0 {
				fontSize = 12
			}

			// Add font to PDF if it's not a standard font
			fontFamily := tb.FontFamily
			if fontFamily == "" {
				fontFamily = "Arial"
			}

			// Simple font embedding logic
			fontName := fontFamily

			fontPath, ok := a.fontMap[fontFamily]
			if !ok {
				// Try case-insensitive lookup
				for f, p := range a.fontMap {
					if strings.EqualFold(f, fontFamily) {
						fontPath = p
						fontName = f
						break
					}
				}
			}

			if fontPath != "" {
				err = pdf.AddTTFFont(fontName, fontPath)
				if err != nil {
					fontName = "Arial" // fallback
				}
			} else {
				fontName = "Arial" // fallback
			}

			_ = pdf.SetFont(fontName, "", fontSize)

			tw, _ := pdf.MeasureTextWidth(text)

			posX := (tagX + tb.XMM) * mmToPt
			posY := (tagY + tb.YMM) * mmToPt
			boxWPx := tb.WidthMM * mmToPt
			boxHPx := tb.HeightMM * mmToPt

			// Alignment
			switch tb.Alignment {
			case "center":
				posX += (boxWPx - tw) / 2
			case "right":
				posX += (boxWPx - tw)
			}

			// Center vertically within the box height (approximate)
			posY += (boxHPx + fontSize*0.8) / 2

			pdf.SetXY(posX, posY)
			_ = pdf.Text(text)
		}
	}

	err = pdf.WritePdf(filePath)
	return filePath, err
}
