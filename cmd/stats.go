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

var statsCmd = &cli.Command{
	Name:  "stats",
	Usage: "Get telemetry statistics",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
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

		data, err := client.Query("stats", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var stats map[string]any
		if err := json.Unmarshal(data, &stats); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(stats)
		}

		fmt.Printf("Telemetry Stats (last %s)\n\n", c.String("since"))

		// Events section
		if events, ok := stats["events"].(map[string]any); ok {
			fmt.Println("Events:")
			if v, ok := events["total_events"].(float64); ok {
				fmt.Printf("  Total:     %.0f\n", v)
			}
			if v, ok := events["events_last_24h"].(float64); ok {
				fmt.Printf("  Last 24h:  %.0f\n", v)
			}
			if v, ok := events["error_count"].(float64); ok && v > 0 {
				fmt.Printf("  Errors:    %s\n", output.Red(fmt.Sprintf("%.0f", v)))
			}
		}

		// Metrics section
		if metrics, ok := stats["metrics"].(map[string]any); ok {
			fmt.Println("\nMetrics:")
			if v, ok := metrics["total_metrics"].(float64); ok {
				fmt.Printf("  Total:     %.0f\n", v)
			}
			if v, ok := metrics["unique_clusters"].(float64); ok {
				fmt.Printf("  Clusters:  %.0f\n", v)
			}
			if v, ok := metrics["unique_pods"].(float64); ok {
				fmt.Printf("  Pods:      %.0f\n", v)
			}
		}

		// Traces section
		if traces, ok := stats["traces"].(map[string]any); ok {
			if v, ok := traces["total_spans"].(float64); ok && v > 0 {
				fmt.Println("\nTraces:")
				fmt.Printf("  Total spans: %.0f\n", v)
				if s, ok := traces["unique_services"].(float64); ok {
					fmt.Printf("  Services:    %.0f\n", s)
				}
			}
		}

		return nil
	},
}
