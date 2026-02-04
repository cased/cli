package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"

	"github.com/cased/cli/internal/api"
	"github.com/cased/cli/internal/config"
	"github.com/cased/cli/internal/output"
	"github.com/urfave/cli/v3"
)

var sessionsCmd = &cli.Command{
	Name:  "sessions",
	Usage: "List AI agent sessions",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
		},
		&cli.StringFlag{
			Name:  "status",
			Usage: "Filter by status (completed, failed, running)",
		},
		&cli.StringFlag{
			Name:  "type",
			Usage: "Filter by type (deploy_monitor, root_cause_analysis, general)",
		},
		&cli.IntFlag{
			Name:  "limit",
			Usage: "Max results",
			Value: 20,
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		hours, err := output.ParseSince(c.String("since"))
		if err != nil {
			return exitError("Invalid --since: %v", err)
		}

		params := url.Values{}
		params.Set("hours", fmt.Sprintf("%d", hours))
		params.Set("limit", fmt.Sprintf("%d", c.Int("limit")))
		if v := c.String("status"); v != "" {
			params.Set("status", v)
		}
		if v := c.String("type"); v != "" {
			params.Set("type", v)
		}

		data, err := client.Agent("sessions", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var resp struct {
			Results []map[string]any `json:"results"`
			Count   int              `json:"count"`
		}
		if err := json.Unmarshal(data, &resp); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(resp)
		}

		if len(resp.Results) == 0 {
			fmt.Println("No sessions found")
			return nil
		}

		table := output.Table([]string{"Time", "Type", "Status", "Title", "ID"})
		for _, s := range resp.Results {
			ts := ""
			if v, ok := s["created_at"].(string); ok {
				ts = output.RelativeTime(v)
			}
			typ := ""
			if v, ok := s["session_type"].(string); ok {
				typ = v
			}
			status := ""
			if v, ok := s["status"].(string); ok {
				status = output.StatusColor(v)
			}
			title := ""
			if v, ok := s["title"].(string); ok {
				title = output.Truncate(v, 40)
			}
			id := ""
			if v, ok := s["id"].(string); ok {
				if len(v) > 8 {
					id = v[:8]
				} else {
					id = v
				}
			}
			table.Append([]string{ts, typ, status, title, id})
		}
		table.Render()

		fmt.Printf("\nTotal: %d sessions\n", resp.Count)
		return nil
	},
}

var sessionCmd = &cli.Command{
	Name:      "session",
	Usage:     "Get session details",
	ArgsUsage: "<session_id>",
	Flags: []cli.Flag{
		&cli.BoolFlag{
			Name:  "logs",
			Usage: "Show execution logs",
		},
		&cli.BoolFlag{
			Name:  "conversation",
			Usage: "Show conversation history",
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		if c.NArg() < 1 {
			return exitError("Session ID required")
		}
		sessionID := c.Args().Get(0)

		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		params := url.Values{}
		if c.Bool("logs") {
			params.Set("logs", "true")
		}
		if c.Bool("conversation") {
			params.Set("conversation", "true")
		}

		data, err := client.Agent("sessions/"+sessionID, params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var session map[string]any
		if err := json.Unmarshal(data, &session); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(session)
		}

		// Print session summary
		fmt.Printf("%s Session Details\n\n", output.Bold("Agent"))

		if v, ok := session["title"].(string); ok && v != "" {
			fmt.Printf("Title:   %s\n", v)
		}
		if v, ok := session["session_type"].(string); ok {
			fmt.Printf("Type:    %s\n", v)
		}
		if v, ok := session["status"].(string); ok {
			fmt.Printf("Status:  %s\n", output.StatusColor(v))
		}
		if v, ok := session["created_at"].(string); ok {
			fmt.Printf("Created: %s\n", output.FormatTime(v))
		}

		// Summary section
		if summary, ok := session["summary"].(map[string]any); ok {
			fmt.Println()
			if desc, ok := summary["description"].(string); ok && desc != "" {
				fmt.Printf("Description:\n  %s\n", desc)
			}
			if outcome, ok := summary["outcome"].(string); ok && outcome != "" {
				fmt.Printf("Outcome:\n  %s\n", outcome)
			}
			if actions, ok := summary["key_actions"].([]any); ok && len(actions) > 0 {
				fmt.Println("Key Actions:")
				for _, a := range actions {
					fmt.Printf("  - %v\n", a)
				}
			}
		}

		// Logs section
		if logs, ok := session["logs"].([]any); ok && len(logs) > 0 {
			fmt.Printf("\n%s\n", output.Bold("Execution Logs:"))
			for _, l := range logs {
				if log, ok := l.(map[string]any); ok {
					ts := ""
					if t, ok := log["timestamp"].(string); ok {
						ts = output.FormatTime(t)
					}
					msg := ""
					if m, ok := log["message"].(string); ok {
						msg = m
					}
					fmt.Printf("  %s %s\n", output.Dim(ts), msg)
				}
			}
		}

		// Conversation section
		if conv, ok := session["conversation"].([]any); ok && len(conv) > 0 {
			fmt.Printf("\n%s\n", output.Bold("Conversation:"))
			for _, m := range conv {
				if msg, ok := m.(map[string]any); ok {
					role := ""
					if r, ok := msg["role"].(string); ok {
						role = r
					}
					content := ""
					if c, ok := msg["content"].(string); ok {
						content = output.Truncate(c, 100)
					}
					fmt.Printf("  %s: %s\n", output.Blue(role), content)
				}
			}
		}

		return nil
	},
}
