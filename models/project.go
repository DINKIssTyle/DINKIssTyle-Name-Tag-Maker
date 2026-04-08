// Created by DINKIssTyle on 2026.
// Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

package models

// ProjectData represents the full state of a name tag project for saving to .ntag
type ProjectData struct {
	Version      int         `json:"version"`
	Paper        PaperSize   `json:"paper"`
	Layout       TagLayout   `json:"layout"`
	Template     TagTemplate `json:"template"`
	Entries      []TagEntry  `json:"entries"`
	CommonValues []string    `json:"common_values"`
}

// CSVResult used for ImportCSV
type CSVResult struct {
	Headers []string   `json:"headers"`
	Data    [][]string `json:"data"`
}
