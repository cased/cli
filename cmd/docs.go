package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/cased/cli/internal/api"
	"github.com/cased/cli/internal/config"
	"github.com/urfave/cli/v3"
)

var docsCmd = &cli.Command{
	Name:  "docs",
	Usage: "Manage documentation",
	Commands: []*cli.Command{
		docsUploadCmd,
	},
}

var docsUploadCmd = &cli.Command{
	Name:      "upload",
	Usage:     "Upload document to knowledge base",
	ArgsUsage: "<file>",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "title",
			Usage: "Document title (default: filename)",
		},
		&cli.BoolFlag{
			Name:  "cleanup",
			Usage: "AI cleanup/formatting",
		},
		&cli.StringFlag{
			Name:  "format",
			Usage: "Format: markdown, text, conversation",
			Value: "markdown",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		if c.NArg() < 1 {
			return exitError("File path required (use - for stdin)")
		}
		filePath := c.Args().Get(0)

		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		var content []byte
		var err error
		var title string

		if filePath == "-" {
			content, err = io.ReadAll(os.Stdin)
			title = "stdin-upload"
		} else {
			content, err = os.ReadFile(filePath)
			// Convert filename to title (kebab-case to Title Case)
			base := filepath.Base(filePath)
			ext := filepath.Ext(base)
			name := strings.TrimSuffix(base, ext)
			name = strings.ReplaceAll(name, "-", " ")
			name = strings.ReplaceAll(name, "_", " ")
			title = strings.Title(name)
		}

		if err != nil {
			return exitError("Failed to read file: %v", err)
		}

		// Check file size (100KB limit)
		if len(content) > 100*1024 {
			return exitError("File too large (max 100KB)")
		}

		if t := c.String("title"); t != "" {
			title = t
		}

		payload := map[string]any{
			"title":   title,
			"content": string(content),
			"format":  c.String("format"),
			"cleanup": c.Bool("cleanup"),
		}

		url := fmt.Sprintf("%s/api/v1/docs/", cfg.APIURL)
		resp, err := client.Post(url, payload)
		if err != nil {
			return exitError("Upload failed: %v", err)
		}

		var result map[string]any
		if err := json.Unmarshal(resp, &result); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			enc := json.NewEncoder(os.Stdout)
			enc.SetIndent("", "  ")
			return enc.Encode(result)
		}

		fmt.Printf("Uploaded: %s\n", title)
		if id, ok := result["id"].(string); ok {
			fmt.Printf("ID: %s\n", id)
		}

		return nil
	},
}
