package main

import (
	"embed"
	"net/http"
	"os"
	"strings"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
)

// FileServerHandler serves local files for the frontend to access
type FileServerHandler struct{}

func (h *FileServerHandler) ServeHTTP(res http.ResponseWriter, req *http.Request) {
	requestedFilename := strings.TrimPrefix(req.URL.Path, "/local-file")
	// On Mac, the remaining path is /Users/... which is an absolute path.
	fileData, err := os.ReadFile(requestedFilename)
	if err != nil {
		res.WriteHeader(http.StatusBadRequest)
		res.Write([]byte(err.Error()))
		return
	}
	res.Write(fileData)
}

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	// Create an instance of the app structure
	app := NewApp()

	// Create application with options
	err := wails.Run(&options.App{
		Title:  "DKST Name Tag Maker",
		Width:  1280,
		Height: 768,
		AssetServer: &assetserver.Options{
			Assets:  assets,
			Handler: &FileServerHandler{},
		},
		BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 1},
		OnStartup:        app.startup,
		Bind: []interface{}{
			app,
		},
	})

	if err != nil {
		println("Error:", err.Error())
	}
}
