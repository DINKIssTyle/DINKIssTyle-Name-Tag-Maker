// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"image/color"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"NameTagMaker/models"
	"NameTagMaker/utils"

	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"

	"github.com/signintech/gopdf"
	"github.com/wailsapp/wails/v2/pkg/runtime"
	_ "embed"
	stdruntime "runtime"
)

//go:embed res/NanumGothic-Regular.ttf
var nanumGothicFont []byte

// App struct
type App struct {
	ctx                context.Context
	fontMap            map[string]string // Family Name -> File Path
	currentProjectPath string            // Path of the loaded/saved project
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
	if err == nil {
		a.currentProjectPath = filePath
	}
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
	if err == nil {
		a.currentProjectPath = filePath
	}
	return &data, err
}

func (a *App) AutoSaveProject(data models.ProjectData) error {
	if a.currentProjectPath == "" {
		return nil // No active project path, skip auto-save silently
	}

	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(a.currentProjectPath, jsonData, 0644)
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

func getImageDimensions(filePath string) (float64, float64, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return 0, 0, err
	}
	defer file.Close()

	imgConfig, _, err := image.DecodeConfig(file)
	if err != nil {
		return 0, 0, err
	}
	return float64(imgConfig.Width), float64(imgConfig.Height), nil
}

func hasKorean(s string) bool {
	for _, r := range s {
		if (r >= 0xAC00 && r <= 0xD7A3) || (r >= 0x1100 && r <= 0x11FF) || (r >= 0x3130 && r <= 0x318F) {
			return true
		}
	}
	return false
}

func cleanFontName(name string) string {
	s := strings.ToLower(name)
	s = strings.ReplaceAll(s, " ", "")
	s = strings.ReplaceAll(s, "-", "")
	s = strings.ReplaceAll(s, "_", "")
	return s
}

func (a *App) getKoreanFallbackFont() (string, string) {
	// Preferred Korean font families by OS
	var preferred []string
	switch stdruntime.GOOS {
	case "darwin":
		preferred = []string{"Apple SD Gothic Neo", "AppleGothic"}
	case "windows":
		preferred = []string{"Malgun Gothic", "Gulim", "Dotum", "Batang"}
	case "linux":
		preferred = []string{"Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "NanumBarunGothic", "UnDotum"}
	default:
		preferred = []string{"Apple SD Gothic Neo", "Malgun Gothic", "NanumGothic"}
	}

	for _, name := range preferred {
		cleanedPreferred := cleanFontName(name)
		if path, ok := a.fontMap[name]; ok {
			return name, path
		}
		// Try lookup with cleaned names
		for f, p := range a.fontMap {
			if cleanFontName(f) == cleanedPreferred || strings.Contains(cleanFontName(f), cleanedPreferred) || strings.Contains(cleanedPreferred, cleanFontName(f)) {
				return f, p
			}
		}
	}

	// Fallback to any font that might have "gothic", "nanum", "noto", "malgun", or "apple" in it
	for f, p := range a.fontMap {
		lf := strings.ToLower(f)
		if strings.Contains(lf, "gothic") || strings.Contains(lf, "nanum") || strings.Contains(lf, "noto") || strings.Contains(lf, "malgun") || strings.Contains(lf, "apple") {
			return f, p
		}
	}

	// If absolutely nothing is found, return the first font in the map if it exists
	for f, p := range a.fontMap {
		return f, p
	}

	return "Arial", ""
}

func drawPageGridLines(pdf *gopdf.GoPdf, data models.ProjectData) {
	mmToPt := 2.83464
	pdf.SetLineWidth(0.5)
	pdf.SetStrokeColor(180, 180, 180)

	// Draw horizontal lines across the entire page width
	for r := 0; r < data.Layout.Rows; r++ {
		y1 := data.Layout.OffsetYMM + float64(r)*(data.Layout.TagHeightMM+data.Layout.GapYMM)
		y2 := y1 + data.Layout.TagHeightMM
		pdf.Line(0, y1*mmToPt, data.Paper.WidthMM*mmToPt, y1*mmToPt)
		pdf.Line(0, y2*mmToPt, data.Paper.WidthMM*mmToPt, y2*mmToPt)
	}

	// Draw vertical lines across the entire page height
	for c := 0; c < data.Layout.Columns; c++ {
		x1 := data.Layout.OffsetXMM + float64(c)*(data.Layout.TagWidthMM+data.Layout.GapXMM)
		x2 := x1 + data.Layout.TagWidthMM
		pdf.Line(x1*mmToPt, 0, x1*mmToPt, data.Paper.HeightMM*mmToPt)
		pdf.Line(x2*mmToPt, 0, x2*mmToPt, data.Paper.HeightMM*mmToPt)
	}
}

func (a *App) buildPDF(filePath string, data models.ProjectData) error {
	pdf := gopdf.GoPdf{}
	nanumGothicAdded := false
	mmToPt := 2.83464
	pdf.Start(gopdf.Config{
		PageSize: gopdf.Rect{
			W: data.Paper.WidthMM * mmToPt,
			H: data.Paper.HeightMM * mmToPt,
		},
	})

	totalTagsPerPage := data.Layout.Columns * data.Layout.Rows
	if totalTagsPerPage <= 0 {
		return fmt.Errorf("invalid layout")
	}

	for i, entry := range data.Entries {
		if !entry.Checked {
			continue
		}

		tagIndexOnPage := i % totalTagsPerPage
		if tagIndexOnPage == 0 {
			pdf.AddPage()
			if data.Layout.ShowCuttingLines {
				drawPageGridLines(&pdf, data)
			}
		}

		col := tagIndexOnPage % data.Layout.Columns
		row := tagIndexOnPage / data.Layout.Columns

		tagX := data.Layout.OffsetXMM + float64(col)*(data.Layout.TagWidthMM+data.Layout.GapXMM)
		tagY := data.Layout.OffsetYMM + float64(row)*(data.Layout.TagHeightMM+data.Layout.GapYMM)

		if data.Template.BackgroundImage != "" {
			bgMode := data.Template.BackgroundImageMode
			if bgMode == "" {
				bgMode = "stretch"
			}

			tagW := data.Layout.TagWidthMM
			tagH := data.Layout.TagHeightMM

			imgX := tagX
			imgY := tagY
			imgW := tagW
			imgH := tagH

			if bgMode == "fit" || bgMode == "cover" {
				imgPixelW, imgPixelH, err := getImageDimensions(data.Template.BackgroundImage)
				if err == nil && imgPixelW > 0 && imgPixelH > 0 {
					imgAspect := imgPixelW / imgPixelH
					tagAspect := tagW / tagH

					if bgMode == "fit" {
						if imgAspect > tagAspect {
							// fit width
							imgW = tagW
							imgH = tagW / imgAspect
							imgX = tagX
							imgY = tagY + (tagH-imgH)/2
						} else {
							// fit height
							imgH = tagH
							imgW = tagH * imgAspect
							imgX = tagX + (tagW-imgW)/2
							imgY = tagY
						}
					} else if bgMode == "cover" {
						if imgAspect > tagAspect {
							// cover height, overflow width
							imgH = tagH
							imgW = tagH * imgAspect
							imgX = tagX + (tagW-imgW)/2
							imgY = tagY
						} else {
							// cover width, overflow height
							imgW = tagW
							imgH = tagW / imgAspect
							imgX = tagX
							imgY = tagY + (tagH-imgH)/2
						}
					}
				}
			}

			if bgMode == "cover" {
				// Clip to tag boundary
				points := []gopdf.Point{
					{X: tagX * mmToPt, Y: tagY * mmToPt},
					{X: (tagX + tagW) * mmToPt, Y: tagY * mmToPt},
					{X: (tagX + tagW) * mmToPt, Y: (tagY + tagH) * mmToPt},
					{X: tagX * mmToPt, Y: (tagY + tagH) * mmToPt},
				}
				pdf.SaveGraphicsState()
				pdf.ClipPolygon(points)
				_ = pdf.Image(data.Template.BackgroundImage, imgX*mmToPt, imgY*mmToPt, &gopdf.Rect{
					W: imgW * mmToPt,
					H: imgH * mmToPt,
				})
				pdf.RestoreGraphicsState()
			} else {
				_ = pdf.Image(data.Template.BackgroundImage, imgX*mmToPt, imgY*mmToPt, &gopdf.Rect{
					W: imgW * mmToPt,
					H: imgH * mmToPt,
				})
			}
		}

		// Draw cutting lines (칼선) - 0.5pt light gray border on top of the image
		if data.Layout.ShowCuttingLines {
			pdf.SetLineWidth(0.5)
			pdf.SetStrokeColor(180, 180, 180)
			pdf.Rectangle(tagX*mmToPt, tagY*mmToPt, (tagX+data.Layout.TagWidthMM)*mmToPt, (tagY+data.Layout.TagHeightMM)*mmToPt, "D", 0, 0)
		}

		for tbIdx, tb := range data.Template.TextBoxes {
			text := tb.Label
			if strings.Contains(text, "{") {
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
			} else {
				// Direct mapping by index (matching frontend preview behavior)
				if tbIdx < len(entry.Values) && entry.Values[tbIdx] != "" {
					text = entry.Values[tbIdx]
				} else if tbIdx < len(data.CommonValues) && data.CommonValues[tbIdx] != "" {
					text = data.CommonValues[tbIdx]
				} else {
					text = ""
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
						ok = true
						break
					}
				}
			}

			// CJK/Standard Font Fallback Logic:
			// If text contains Korean characters and the requested font is a standard non-CJK font (like "Arial"),
			// or if the font file cannot be found in the system, or if it's a TrueType Collection (.ttc) file
			// (which gopdf doesn't support), we fallback to our embedded NanumGothic-Regular.ttf.
			isStandardNonCJK := fontFamily == "Arial" || fontFamily == "Helvetica" || fontFamily == "Courier" || fontFamily == "Times"
			isTTC := strings.HasSuffix(strings.ToLower(fontPath), ".ttc") || strings.HasSuffix(strings.ToLower(fontPath), ".otc")
			useEmbeddedFallback := (isStandardNonCJK && hasKorean(text)) || fontPath == "" || isTTC

			var fontErr error
			if useEmbeddedFallback {
				fontName = "NanumGothic"
				if !nanumGothicAdded {
					fontErr = pdf.AddTTFFontData("NanumGothic", nanumGothicFont)
					if fontErr == nil {
						nanumGothicAdded = true
					}
				}
			} else {
				fontErr = pdf.AddTTFFont(fontName, fontPath)
				if fontErr != nil {
					// If loading fails, use embedded NanumGothic as safety fallback
					fontName = "NanumGothic"
					if !nanumGothicAdded {
						fontErr = pdf.AddTTFFontData("NanumGothic", nanumGothicFont)
						if fontErr == nil {
							nanumGothicAdded = true
						}
					} else {
						fontErr = nil // already added successfully in a previous loop iteration
					}
				}
			}

			// Only render if a font was successfully loaded. If everything failed (which shouldn't
			// happen with embedded fallback), skip measuring/drawing to prevent panics.
			if fontErr == nil {
				boxWPx := tb.WidthMM * mmToPt
				boxHPx := tb.HeightMM * mmToPt

				// Split text into lines to support auto-scaling and multiline drawing
				lines := strings.Split(text, "\n")
				lineSpacing := tb.LineSpacing
				if lineSpacing <= 0 {
					lineSpacing = 1.2
				}

				// Font size auto-scaling loop (matches frontend Canvas logic)
				for fontSize > 4.0 {
					_ = pdf.SetFont(fontName, "", fontSize)

					maxW := 0.0
					for _, line := range lines {
						w, _ := pdf.MeasureTextWidth(line)
						if w > maxW {
							maxW = w
						}
					}

					totalH := float64(len(lines)) * fontSize * lineSpacing

					if maxW <= boxWPx && totalH <= boxHPx {
						break
					}
					fontSize -= 0.5
				}

				// Final set of corrected font size
				_ = pdf.SetFont(fontName, "", fontSize)
				lineH := fontSize * lineSpacing

				// Render each line individually
				for lineIdx, line := range lines {
					lineOffsetY := (float64(lineIdx) - float64(len(lines)-1)/2.0) * lineH
					lineY := (tagY+tb.YMM)*mmToPt + boxHPx/2.0 + lineOffsetY + (fontSize * 0.35)

					tw, _ := pdf.MeasureTextWidth(line)
					posX := (tagX + tb.XMM) * mmToPt
					switch tb.Alignment {
					case "center":
						posX += (boxWPx - tw) / 2.0
					case "right":
						posX += (boxWPx - tw)
					}

					pdf.SetXY(posX, lineY)
					_ = pdf.Text(line)
				}
			}
		}
	}

	return pdf.WritePdf(filePath)
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

	err = a.buildPDF(filePath, data)
	return filePath, err
}

// Print triggers the native system print dialog for the webview window
func (a *App) Print() {
	runtime.WindowPrint(a.ctx)
}

// PrintProject generates a temporary PDF and triggers native system printing
func (a *App) PrintProject(data models.ProjectData) error {
	tempFile := filepath.Join(os.TempDir(), "dkst_print_temp.pdf")
	err := a.buildPDF(tempFile, data)
	if err != nil {
		return err
	}
	PrintPDF(tempFile)
	return nil
}

// ShowConfirm displays a native question dialog with custom yes/no button labels
func (a *App) ShowConfirm(title, message, yesLabel, noLabel string) (bool, error) {
	selection, err := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
		Type:          runtime.QuestionDialog,
		Title:         title,
		Message:       message,
		Buttons:       []string{yesLabel, noLabel},
		DefaultButton: yesLabel,
		CancelButton:  noLabel,
	})
	if err != nil {
		return false, err
	}
	return selection == yesLabel, nil
}

// ResetCurrentProjectPath clears the active project path when a new project is created
func (a *App) ResetCurrentProjectPath() {
	a.currentProjectPath = ""
}

// ShowNewProjectConfirm displays a native dialog for New Project confirmation (Save/Don't Save/Cancel)
func (a *App) ShowNewProjectConfirm(title, message, saveLabel, discardLabel, cancelLabel string) (string, error) {
	selection, err := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
		Type:          runtime.QuestionDialog,
		Title:         title,
		Message:       message,
		Buttons:       []string{saveLabel, discardLabel, cancelLabel},
		DefaultButton: saveLabel,
		CancelButton:  cancelLabel,
	})
	if err != nil {
		return "", err
	}
	return selection, nil
}

