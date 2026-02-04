package cmd

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/cased/cli/internal/config"
	"github.com/cased/cli/internal/output"
	"github.com/urfave/cli/v3"
)

var sourcemapsCmd = &cli.Command{
	Name:  "sourcemaps",
	Usage: "Manage source maps",
	Commands: []*cli.Command{
		sourcemapsUploadCmd,
		sourcemapsListCmd,
		sourcemapsDeleteCmd,
	},
}

var sourcemapsUploadCmd = &cli.Command{
	Name:      "upload",
	Usage:     "Upload source map files",
	ArgsUsage: "<file.map>...",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:     "project",
			Usage:    "Project slug",
			Required: true,
		},
		&cli.StringFlag{
			Name:     "release",
			Usage:    "Release version",
			Required: true,
		},
		&cli.StringFlag{
			Name:  "url-prefix",
			Usage: "URL prefix to strip",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		if c.NArg() < 1 {
			return exitError("At least one .map file required")
		}

		cfg := config.MustLoad()
		project := c.String("project")
		release := c.String("release")
		urlPrefix := c.String("url-prefix")

		for _, filePath := range c.Args().Slice() {
			if !strings.HasSuffix(filePath, ".map") {
				fmt.Printf("Skipping non-.map file: %s\n", filePath)
				continue
			}

			file, err := os.Open(filePath)
			if err != nil {
				return exitError("Failed to open %s: %v", filePath, err)
			}

			// Create multipart form
			var buf bytes.Buffer
			writer := multipart.NewWriter(&buf)

			part, err := writer.CreateFormFile("file", filepath.Base(filePath))
			if err != nil {
				file.Close()
				return exitError("Failed to create form: %v", err)
			}

			if _, err := io.Copy(part, file); err != nil {
				file.Close()
				return exitError("Failed to copy file: %v", err)
			}
			file.Close()

			writer.WriteField("release", release)
			if urlPrefix != "" {
				writer.WriteField("url_prefix", urlPrefix)
			}
			writer.Close()

			// Upload
			uploadURL := fmt.Sprintf("%s/api/v1/telemetry/projects/%s/sourcemaps/", cfg.APIURL, project)
			req, err := http.NewRequest("POST", uploadURL, &buf)
			if err != nil {
				return exitError("Failed to create request: %v", err)
			}
			req.Header.Set("Authorization", "Bearer "+cfg.Token)
			req.Header.Set("Content-Type", writer.FormDataContentType())

			client := &http.Client{Timeout: 120 * time.Second}
			resp, err := client.Do(req)
			if err != nil {
				return exitError("Upload failed: %v", err)
			}

			body, _ := io.ReadAll(resp.Body)
			resp.Body.Close()

			if resp.StatusCode >= 400 {
				return exitError("Upload failed for %s: %s", filePath, string(body))
			}

			fmt.Printf("Uploaded: %s\n", filepath.Base(filePath))
		}

		return nil
	},
}

var sourcemapsListCmd = &cli.Command{
	Name:  "list",
	Usage: "List uploaded source maps",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:     "project",
			Usage:    "Project slug",
			Required: true,
		},
		&cli.StringFlag{
			Name:  "release",
			Usage: "Filter by release",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		cfg := config.MustLoad()
		project := c.String("project")

		params := url.Values{}
		if v := c.String("release"); v != "" {
			params.Set("release", v)
		}

		listURL := fmt.Sprintf("%s/api/v1/telemetry/projects/%s/sourcemaps/", cfg.APIURL, project)
		if len(params) > 0 {
			listURL += "?" + params.Encode()
		}

		req, _ := http.NewRequest("GET", listURL, nil)
		req.Header.Set("Authorization", "Bearer "+cfg.Token)

		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			return exitError("Request failed: %v", err)
		}
		defer resp.Body.Close()

		body, _ := io.ReadAll(resp.Body)
		if resp.StatusCode >= 400 {
			return exitError("Request failed: %s", string(body))
		}

		var maps []map[string]any
		if err := json.Unmarshal(body, &maps); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(maps)
		}

		if len(maps) == 0 {
			fmt.Println("No source maps found")
			return nil
		}

		table := output.Table([]string{"File", "Release", "Uploaded"})
		for _, m := range maps {
			file := ""
			if v, ok := m["filename"].(string); ok {
				file = v
			}
			release := ""
			if v, ok := m["release"].(string); ok {
				release = v
			}
			uploaded := ""
			if v, ok := m["uploaded_at"].(string); ok {
				uploaded = output.RelativeTime(v)
			}
			table.Append([]string{file, release, uploaded})
		}
		table.Render()

		return nil
	},
}

var sourcemapsDeleteCmd = &cli.Command{
	Name:  "delete",
	Usage: "Delete source maps for a release",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:     "project",
			Usage:    "Project slug",
			Required: true,
		},
		&cli.StringFlag{
			Name:     "release",
			Usage:    "Release version",
			Required: true,
		},
		&cli.BoolFlag{
			Name:    "yes",
			Aliases: []string{"y"},
			Usage:   "Skip confirmation",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		cfg := config.MustLoad()
		project := c.String("project")
		release := c.String("release")

		if !c.Bool("yes") {
			fmt.Printf("Delete all source maps for %s release %s? [y/N] ", project, release)
			var confirm string
			fmt.Scanln(&confirm)
			if strings.ToLower(confirm) != "y" {
				fmt.Println("Cancelled")
				return nil
			}
		}

		deleteURL := fmt.Sprintf("%s/api/v1/telemetry/projects/%s/sourcemaps/?release=%s",
			cfg.APIURL, project, url.QueryEscape(release))

		req, _ := http.NewRequest("DELETE", deleteURL, nil)
		req.Header.Set("Authorization", "Bearer "+cfg.Token)

		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			return exitError("Request failed: %v", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 400 {
			body, _ := io.ReadAll(resp.Body)
			return exitError("Delete failed: %s", string(body))
		}

		fmt.Printf("Deleted source maps for release %s\n", release)
		return nil
	},
}
