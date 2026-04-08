// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package utils

import (
	"encoding/csv"
	"strings"
	"unicode/utf8"
)

// DetectDelimiter detects if the CSV is comma or tab separated
func DetectDelimiter(text string) rune {
	lines := strings.SplitN(text, "\n", 2)
	if len(lines) == 0 {
		return ','
	}
	firstLine := lines[0]
	tabCount := strings.Count(firstLine, "\t")
	commaCount := strings.Count(firstLine, ",")
	if tabCount > commaCount {
		return '\t'
	}
	return ','
}

// ImportCSVText parses CSV/TSV text and returns headers and data rows
func ImportCSVText(text string) ([]string, [][]string, error) {
	delimiter := DetectDelimiter(text)
	r := csv.NewReader(strings.NewReader(text))
	r.Comma = delimiter
	r.LazyQuotes = true

	rows, err := r.ReadAll()
	if err != nil {
		return nil, nil, err
	}

	if len(rows) == 0 {
		return []string{}, [][]string{}, nil
	}

	headers := rows[0]
	data := rows[1:]
	return headers, data, nil
}

// ExportCSVText converts headers and data to CSV/TSV string
func ExportCSVText(headers []string, data [][]string, delimiter rune) (string, error) {
	var sb strings.Builder
	// Add UTF-8 BOM for Excel compatibility (matching Python's utf-8-sig)
	sb.Write([]byte{0xEF, 0xBB, 0xBF})

	w := csv.NewWriter(&sb)
	w.Comma = delimiter

	if err := w.Write(headers); err != nil {
		return "", err
	}
	for _, row := range data {
		if err := w.Write(row); err != nil {
			return "", err
		}
	}
	w.Flush()
	return sb.String(), nil
}

// EnsureValidUTF8 ensures the string is valid UTF-8
func EnsureValidUTF8(s string) string {
	if utf8.ValidString(s) {
		return s
	}
	v := make([]rune, 0, len(s))
	for i, r := range s {
		if r == utf8.RuneError {
			_, size := utf8.DecodeRuneInString(s[i:])
			if size == 1 {
				continue
			}
		}
		v = append(v, r)
	}
	return string(v)
}
