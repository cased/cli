package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"os/exec"
	"strings"

	"github.com/cased/cli/internal/api"
	"github.com/cased/cli/internal/config"
	"github.com/cased/cli/internal/output"
	"github.com/urfave/cli/v3"
)

var investigateCmd = &cli.Command{
	Name:      "investigate",
	Usage:     "Open error in Claude Code for investigation",
	ArgsUsage: "<event_id>",
	Flags: []cli.Flag{
		&cli.BoolFlag{
			Name:  "no-launch",
			Usage: "Print prompt instead of launching Claude Code",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		if c.NArg() < 1 {
			return exitError("Event ID required")
		}
		eventID := c.Args().Get(0)

		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		params := url.Values{}
		params.Set("event_id", eventID)

		data, err := client.Query("errors", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var errors []map[string]any
		if err := json.Unmarshal(data, &errors); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if len(errors) == 0 {
			return exitError("Error not found: %s", eventID)
		}

		event := errors[0]

		if jsonOutput {
			return output.JSON(event)
		}

		// Build investigation prompt
		prompt := buildInvestigationPrompt(event)

		if c.Bool("no-launch") {
			fmt.Println(prompt)
			return nil
		}

		// Try to launch Claude Code
		claudePath, err := exec.LookPath("claude")
		if err != nil {
			fmt.Println("Claude Code not found. Install from: https://claude.ai/code")
			fmt.Println("\nInvestigation prompt:")
			fmt.Println(prompt)
			return nil
		}

		cmd := exec.Command(claudePath, "-p", prompt)
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		return cmd.Run()
	},
}

func buildInvestigationPrompt(event map[string]any) string {
	var sb strings.Builder

	sb.WriteString("Investigate this error:\n\n")

	// Exception info
	if typ, ok := event["exception_type"].(string); ok {
		sb.WriteString(fmt.Sprintf("Exception: %s\n", typ))
	}
	if val, ok := event["exception_value"].(string); ok {
		sb.WriteString(fmt.Sprintf("Message: %s\n", val))
	}

	// Timestamp and environment
	if ts, ok := event["timestamp"].(string); ok {
		sb.WriteString(fmt.Sprintf("Time: %s\n", ts))
	}
	if env, ok := event["environment"].(string); ok {
		sb.WriteString(fmt.Sprintf("Environment: %s\n", env))
	}

	// Stacktrace
	if frames, ok := event["stacktrace"].([]any); ok && len(frames) > 0 {
		sb.WriteString("\nStacktrace (most recent first):\n")
		// Show last 10 frames
		start := 0
		if len(frames) > 10 {
			start = len(frames) - 10
		}
		for i := len(frames) - 1; i >= start; i-- {
			if frame, ok := frames[i].(map[string]any); ok {
				file := ""
				if f, ok := frame["filename"].(string); ok {
					file = f
				}
				line := 0
				if l, ok := frame["lineno"].(float64); ok {
					line = int(l)
				}
				fn := ""
				if f, ok := frame["function"].(string); ok {
					fn = f
				}
				sb.WriteString(fmt.Sprintf("  %s:%d in %s\n", file, line, fn))

				if code, ok := frame["context_line"].(string); ok && code != "" {
					sb.WriteString(fmt.Sprintf("    > %s\n", strings.TrimSpace(code)))
				}
			}
		}
	}

	// Breadcrumbs
	if crumbs, ok := event["breadcrumbs"].([]any); ok && len(crumbs) > 0 {
		sb.WriteString("\nRecent breadcrumbs:\n")
		// Show last 5
		start := 0
		if len(crumbs) > 5 {
			start = len(crumbs) - 5
		}
		for i := start; i < len(crumbs); i++ {
			if crumb, ok := crumbs[i].(map[string]any); ok {
				cat := ""
				if c, ok := crumb["category"].(string); ok {
					cat = c
				}
				msg := ""
				if m, ok := crumb["message"].(string); ok {
					msg = m
				}
				sb.WriteString(fmt.Sprintf("  [%s] %s\n", cat, msg))
			}
		}
	}

	sb.WriteString("\nPlease investigate this error and suggest fixes.")

	return sb.String()
}
