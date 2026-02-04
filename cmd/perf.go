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

var perfCmd = &cli.Command{
	Name:  "perf",
	Usage: "Performance analysis",
	Commands: []*cli.Command{
		perfSlowCmd,
		perfLatencyCmd,
		perfN1Cmd,
		perfBreakdownCmd,
		perfRegressionCmd,
		perfSummaryCmd,
	},
}

var perfSlowCmd = &cli.Command{
	Name:  "slow",
	Usage: "Find slow spans",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Value: "24h",
		},
		&cli.IntFlag{
			Name:  "threshold",
			Usage: "Minimum duration in ms",
			Value: 1000,
		},
		&cli.StringFlag{
			Name:  "service",
			Usage: "Filter by service",
		},
		&cli.IntFlag{
			Name:  "limit",
			Value: 20,
		},
	},
	Action: perfAction("slow"),
}

var perfLatencyCmd = &cli.Command{
	Name:  "latency",
	Usage: "Show latency percentiles",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Value: "24h",
		},
		&cli.StringFlag{
			Name:  "service",
			Usage: "Filter by service",
		},
		&cli.StringFlag{
			Name:  "group-by",
			Usage: "Group by field",
		},
	},
	Action: perfAction("latency"),
}

var perfN1Cmd = &cli.Command{
	Name:  "n1",
	Usage: "Detect N+1 query patterns",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Value: "24h",
		},
		&cli.IntFlag{
			Name:  "min-count",
			Usage: "Minimum repetitions",
			Value: 5,
		},
		&cli.IntFlag{
			Name:  "limit",
			Value: 20,
		},
	},
	Action: perfAction("n1"),
}

var perfBreakdownCmd = &cli.Command{
	Name:      "breakdown",
	Usage:     "Show service time breakdown for a trace",
	ArgsUsage: "<trace_id>",
	Action: func(ctx context.Context, c *cli.Command) error {
		if c.NArg() < 1 {
			return exitError("Trace ID required")
		}
		traceID := c.Args().Get(0)

		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		params := url.Values{}
		params.Set("trace_id", traceID)

		data, err := client.Query("perf/breakdown", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var result map[string]any
		if err := json.Unmarshal(data, &result); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(result)
		}

		fmt.Printf("Trace Breakdown: %s\n\n", traceID)

		if services, ok := result["services"].([]any); ok {
			table := output.Table([]string{"Service", "Duration", "Percent"})
			for _, s := range services {
				if svc, ok := s.(map[string]any); ok {
					name := ""
					if v, ok := svc["service"].(string); ok {
						name = v
					}
					dur := ""
					if v, ok := svc["duration_ms"].(float64); ok {
						dur = fmt.Sprintf("%.0fms", v)
					}
					pct := ""
					if v, ok := svc["percent"].(float64); ok {
						pct = fmt.Sprintf("%.1f%%", v)
					}
					table.Append([]string{name, dur, pct})
				}
			}
			table.Render()
		}

		return nil
	},
}

var perfRegressionCmd = &cli.Command{
	Name:  "regression",
	Usage: "Detect performance regressions",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "service",
			Usage: "Filter by service",
		},
		&cli.StringFlag{
			Name:  "endpoint",
			Usage: "Filter by endpoint",
		},
		&cli.StringFlag{
			Name:  "baseline",
			Usage: "Baseline period (e.g., 7d)",
			Value: "7d",
		},
		&cli.StringFlag{
			Name:  "compare",
			Usage: "Compare period (e.g., 1d)",
			Value: "1d",
		},
	},
	Action: perfAction("regression"),
}

var perfSummaryCmd = &cli.Command{
	Name:  "summary",
	Usage: "Show overall performance summary",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Value: "24h",
		},
	},
	Action: perfAction("summary"),
}

func perfAction(endpoint string) func(context.Context, *cli.Command) error {
	return func(ctx context.Context, c *cli.Command) error {
		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		params := url.Values{}

		if v := c.String("since"); v != "" {
			hours, err := output.ParseSince(v)
			if err != nil {
				return exitError("Invalid --since: %v", err)
			}
			params.Set("hours", fmt.Sprintf("%d", hours))
		}
		if v := c.Int("threshold"); v > 0 {
			params.Set("threshold", fmt.Sprintf("%d", v))
		}
		if v := c.String("service"); v != "" {
			params.Set("service", v)
		}
		if v := c.String("group-by"); v != "" {
			params.Set("group_by", v)
		}
		if v := c.Int("min-count"); v > 0 {
			params.Set("min_count", fmt.Sprintf("%d", v))
		}
		if v := c.Int("limit"); v > 0 {
			params.Set("limit", fmt.Sprintf("%d", v))
		}
		if v := c.String("endpoint"); v != "" {
			params.Set("endpoint", v)
		}
		if v := c.String("baseline"); v != "" {
			hours, _ := output.ParseSince(v)
			params.Set("baseline_hours", fmt.Sprintf("%d", hours))
		}
		if v := c.String("compare"); v != "" {
			hours, _ := output.ParseSince(v)
			params.Set("compare_hours", fmt.Sprintf("%d", hours))
		}

		data, err := client.Query("perf/"+endpoint, params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		var result any
		if err := json.Unmarshal(data, &result); err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(result)
		}

		// Format based on endpoint
		switch endpoint {
		case "slow":
			return formatSlowSpans(result)
		case "latency":
			return formatLatency(result)
		case "n1":
			return formatN1(result)
		case "regression":
			return formatRegression(result)
		case "summary":
			return formatPerfSummary(result)
		}

		// Default: dump as JSON
		return output.JSON(result)
	}
}

func formatSlowSpans(result any) error {
	spans, ok := result.([]any)
	if !ok {
		return output.JSON(result)
	}

	if len(spans) == 0 {
		fmt.Println("No slow spans found")
		return nil
	}

	table := output.Table([]string{"Service", "Operation", "Duration", "Time"})
	for _, s := range spans {
		if span, ok := s.(map[string]any); ok {
			svc := getStr(span, "service_name")
			op := output.Truncate(getStr(span, "operation"), 30)
			dur := fmt.Sprintf("%.0fms", getFloat(span, "duration_ms"))
			ts := output.RelativeTime(getStr(span, "timestamp"))
			table.Append([]string{svc, op, dur, ts})
		}
	}
	table.Render()
	return nil
}

func formatLatency(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	fmt.Println("Latency Percentiles")
	fmt.Printf("  p50: %.0fms\n", getFloat(data, "p50"))
	fmt.Printf("  p95: %.0fms\n", getFloat(data, "p95"))
	fmt.Printf("  p99: %.0fms\n", getFloat(data, "p99"))
	return nil
}

func formatN1(result any) error {
	patterns, ok := result.([]any)
	if !ok {
		return output.JSON(result)
	}

	if len(patterns) == 0 {
		fmt.Println("No N+1 patterns detected")
		return nil
	}

	table := output.Table([]string{"Query", "Count", "Trace"})
	for _, p := range patterns {
		if pattern, ok := p.(map[string]any); ok {
			query := output.Truncate(getStr(pattern, "query"), 50)
			count := fmt.Sprintf("%.0f", getFloat(pattern, "count"))
			trace := getStr(pattern, "trace_id")
			if len(trace) > 16 {
				trace = trace[:16]
			}
			table.Append([]string{query, count, trace})
		}
	}
	table.Render()
	return nil
}

func formatRegression(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	regressions, ok := data["regressions"].([]any)
	if !ok || len(regressions) == 0 {
		fmt.Println("No regressions detected")
		return nil
	}

	table := output.Table([]string{"Endpoint", "Baseline", "Current", "Change"})
	for _, r := range regressions {
		if reg, ok := r.(map[string]any); ok {
			endpoint := output.Truncate(getStr(reg, "endpoint"), 30)
			baseline := fmt.Sprintf("%.0fms", getFloat(reg, "baseline_p95"))
			current := fmt.Sprintf("%.0fms", getFloat(reg, "current_p95"))
			change := fmt.Sprintf("+%.0f%%", getFloat(reg, "percent_change"))
			table.Append([]string{endpoint, baseline, current, output.Red(change)})
		}
	}
	table.Render()
	return nil
}

func formatPerfSummary(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	fmt.Println("Performance Summary")
	fmt.Printf("  Total traces: %.0f\n", getFloat(data, "total_traces"))
	fmt.Printf("  Avg latency:  %.0fms\n", getFloat(data, "avg_latency_ms"))
	fmt.Printf("  p95 latency:  %.0fms\n", getFloat(data, "p95_latency_ms"))
	fmt.Printf("  Error rate:   %.2f%%\n", getFloat(data, "error_rate")*100)
	return nil
}

func getStr(m map[string]any, key string) string {
	if v, ok := m[key].(string); ok {
		return v
	}
	return ""
}

func getFloat(m map[string]any, key string) float64 {
	if v, ok := m[key].(float64); ok {
		return v
	}
	return 0
}
