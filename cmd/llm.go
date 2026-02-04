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

var llmCmd = &cli.Command{
	Name:  "llm",
	Usage: "LLM monitoring",
	Commands: []*cli.Command{
		llmUsageCmd,
		llmCostCmd,
		llmLatencyCmd,
		llmErrorsCmd,
		llmSummaryCmd,
		llmSessionsCmd,
	},
}

var llmUsageCmd = &cli.Command{
	Name:  "usage",
	Usage: "Show LLM token usage",
	Flags: llmFlags(),
	Action: llmAction("usage"),
}

var llmCostCmd = &cli.Command{
	Name:  "cost",
	Usage: "Show estimated LLM costs",
	Flags: llmFlags(),
	Action: llmAction("cost"),
}

var llmLatencyCmd = &cli.Command{
	Name:  "latency",
	Usage: "Show LLM latency percentiles",
	Flags: llmFlags(),
	Action: llmAction("latency"),
}

var llmErrorsCmd = &cli.Command{
	Name:  "errors",
	Usage: "Show LLM error statistics",
	Flags: llmFlags(),
	Action: llmAction("errors"),
}

var llmSummaryCmd = &cli.Command{
	Name:  "summary",
	Usage: "Show overall LLM summary",
	Flags: []cli.Flag{
		&cli.StringFlag{Name: "since", Value: "24h"},
	},
	Action: llmAction("summary"),
}

var llmSessionsCmd = &cli.Command{
	Name:  "sessions",
	Usage: "Show per-session LLM usage",
	Flags: []cli.Flag{
		&cli.StringFlag{Name: "since", Value: "24h"},
		&cli.StringFlag{Name: "sort-by", Usage: "Sort by: cost, tokens, latency", Value: "cost"},
		&cli.IntFlag{Name: "limit", Value: 20},
	},
	Action: llmAction("sessions"),
}

func llmFlags() []cli.Flag {
	return []cli.Flag{
		&cli.StringFlag{Name: "since", Value: "24h"},
		&cli.StringFlag{Name: "model", Usage: "Filter by model"},
		&cli.StringFlag{Name: "provider", Usage: "Filter by provider"},
		&cli.StringFlag{Name: "group-by", Usage: "Group by field"},
		&cli.IntFlag{Name: "limit", Value: 20},
	}
}

func llmAction(endpoint string) func(context.Context, *cli.Command) error {
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
		if v := c.String("model"); v != "" {
			params.Set("model", v)
		}
		if v := c.String("provider"); v != "" {
			params.Set("provider", v)
		}
		if v := c.String("group-by"); v != "" {
			params.Set("group_by", v)
		}
		if v := c.String("sort-by"); v != "" {
			params.Set("sort_by", v)
		}
		if v := c.Int("limit"); v > 0 {
			params.Set("limit", fmt.Sprintf("%d", v))
		}

		data, err := client.Query("llm/"+endpoint, params)
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

		switch endpoint {
		case "usage":
			return formatLLMUsage(result)
		case "cost":
			return formatLLMCost(result)
		case "latency":
			return formatLLMLatency(result)
		case "errors":
			return formatLLMErrors(result)
		case "summary":
			return formatLLMSummary(result)
		case "sessions":
			return formatLLMSessions(result)
		}

		return output.JSON(result)
	}
}

func formatLLMUsage(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	// Get totals from nested object
	totals, _ := data["totals"].(map[string]any)
	if totals == nil {
		totals = data
	}

	fmt.Println("LLM Token Usage")
	fmt.Printf("  Input tokens:  %.0f\n", getFloat(totals, "input_tokens"))
	fmt.Printf("  Output tokens: %.0f\n", getFloat(totals, "output_tokens"))
	fmt.Printf("  Cached tokens: %.0f\n", getFloat(totals, "cached_tokens"))
	fmt.Printf("  Total tokens:  %.0f\n", getFloat(totals, "total_tokens"))
	fmt.Printf("  Total calls:   %.0f\n", getFloat(totals, "calls"))
	return nil
}

func formatLLMCost(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	fmt.Println("LLM Costs")
	fmt.Printf("  Total: $%.4f\n", getFloat(data, "total_cost_usd"))

	if byModel, ok := data["by_model"].([]any); ok && len(byModel) > 0 {
		fmt.Println("\n  By Model:")
		for _, m := range byModel {
			if model, ok := m.(map[string]any); ok {
				name := getStr(model, "model")
				cost := getFloat(model, "cost_usd")
				fmt.Printf("    %s: $%.4f\n", name, cost)
			}
		}
	}
	return nil
}

func formatLLMLatency(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	stats, ok := data["latency_stats"].([]any)
	if !ok || len(stats) == 0 {
		fmt.Println("No latency data")
		return nil
	}

	fmt.Println("LLM Latency by Model")
	table := output.Table([]string{"Model", "Calls", "Avg", "p50", "p95", "p99"})
	for _, s := range stats {
		if stat, ok := s.(map[string]any); ok {
			model := output.Truncate(getStr(stat, "model"), 20)
			calls := fmt.Sprintf("%.0f", getFloat(stat, "call_count"))
			avg := fmt.Sprintf("%.0fms", getFloat(stat, "avg_ms"))
			p50 := fmt.Sprintf("%.0fms", getFloat(stat, "p50_ms"))
			p95 := fmt.Sprintf("%.0fms", getFloat(stat, "p95_ms"))
			p99 := fmt.Sprintf("%.0fms", getFloat(stat, "p99_ms"))
			table.Append([]string{model, calls, avg, p50, p95, p99})
		}
	}
	table.Render()
	return nil
}

func formatLLMErrors(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	// Get totals
	totals, _ := data["totals"].(map[string]any)
	errCount := getFloat(totals, "error_count")
	totalCalls := getFloat(totals, "total_calls")

	fmt.Printf("LLM Errors: %.0f / %.0f calls (%.2f%% error rate)\n\n",
		errCount, totalCalls, getFloat(totals, "error_rate")*100)

	errors, ok := data["error_stats"].([]any)
	if !ok || len(errors) == 0 {
		fmt.Println("No error details")
		return nil
	}

	table := output.Table([]string{"Error", "Count", "Model", "Last Seen"})
	for _, e := range errors {
		if err, ok := e.(map[string]any); ok {
			errType := output.Truncate(getStr(err, "error_type"), 30)
			count := fmt.Sprintf("%.0f", getFloat(err, "count"))
			model := getStr(err, "model")
			lastSeen := output.RelativeTime(getStr(err, "last_seen"))
			table.Append([]string{errType, count, model, lastSeen})
		}
	}
	table.Render()
	return nil
}

func formatLLMSummary(result any) error {
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	fmt.Println("LLM Summary")
	fmt.Printf("  Requests:     %.0f\n", getFloat(data, "total_requests"))
	fmt.Printf("  Total tokens: %.0f\n", getFloat(data, "total_tokens"))
	fmt.Printf("  Total cost:   $%.4f\n", getFloat(data, "total_cost_usd"))
	fmt.Printf("  Error rate:   %.2f%%\n", getFloat(data, "error_rate")*100)
	fmt.Printf("  Avg latency:  %.0fms\n", getFloat(data, "avg_latency_ms"))
	return nil
}

func formatLLMSessions(result any) error {
	// API returns {"sessions": [...], "totals": {...}}
	data, ok := result.(map[string]any)
	if !ok {
		return output.JSON(result)
	}

	sessions, ok := data["sessions"].([]any)
	if !ok || len(sessions) == 0 {
		fmt.Println("No LLM sessions found")
		return nil
	}

	table := output.Table([]string{"Session", "Tokens", "Cost", "Calls", "Duration"})
	for _, s := range sessions {
		if sess, ok := s.(map[string]any); ok {
			id := getStr(sess, "session_id")
			if len(id) > 8 {
				id = id[:8]
			}
			// Calculate total tokens
			input := getFloat(sess, "total_input_tokens")
			out := getFloat(sess, "total_output_tokens")
			tokens := fmt.Sprintf("%.0f", input+out)
			cost := fmt.Sprintf("$%.2f", getFloat(sess, "total_cost_usd"))
			calls := fmt.Sprintf("%.0f", getFloat(sess, "call_count"))
			dur := fmt.Sprintf("%.0fs", getFloat(sess, "duration_seconds"))
			table.Append([]string{id, tokens, cost, calls, dur})
		}
	}
	table.Render()

	// Show totals
	if totals, ok := data["totals"].(map[string]any); ok {
		fmt.Printf("\nTotal: %.0f sessions, %.0f calls, $%.2f\n",
			getFloat(totals, "sessions"),
			getFloat(totals, "calls"),
			getFloat(totals, "cost_usd"))
	}
	return nil
}
