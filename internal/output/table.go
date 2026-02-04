package output

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/fatih/color"
	"github.com/olekukonko/tablewriter"
	"github.com/olekukonko/tablewriter/tw"
)

// JSON outputs data as JSON.
func JSON(data any) error {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	return enc.Encode(data)
}

// TableWriter wraps tablewriter.Table with a simpler API.
type TableWriter struct {
	table   *tablewriter.Table
	headers []string
	rows    [][]string
}

// Table creates a new table writer with headers.
func Table(headers []string) *TableWriter {
	return &TableWriter{
		headers: headers,
		rows:    [][]string{},
	}
}

// Append adds a row to the table.
func (t *TableWriter) Append(row []string) {
	t.rows = append(t.rows, row)
}

// Render outputs the table.
func (t *TableWriter) Render() {
	table := tablewriter.NewTable(os.Stdout,
		tablewriter.WithRowAlignment(tw.AlignLeft),
		tablewriter.WithHeaderAlignment(tw.AlignLeft),
	)
	table.Header(t.headers)
	for _, row := range t.rows {
		table.Append(row)
	}
	table.Render()
}

// Truncate shortens a string to max length.
func Truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max-3] + "..."
}

// FormatTime formats a timestamp for display.
func FormatTime(t string) string {
	parsed, err := time.Parse(time.RFC3339, t)
	if err != nil {
		return t
	}
	return parsed.Local().Format("2006-01-02 15:04:05")
}

// RelativeTime returns a human-readable relative time.
func RelativeTime(t string) string {
	parsed, err := time.Parse(time.RFC3339, t)
	if err != nil {
		return t
	}
	diff := time.Since(parsed)
	if diff < time.Minute {
		return "just now"
	}
	if diff < time.Hour {
		return fmt.Sprintf("%dm ago", int(diff.Minutes()))
	}
	if diff < 24*time.Hour {
		return fmt.Sprintf("%dh ago", int(diff.Hours()))
	}
	return fmt.Sprintf("%dd ago", int(diff.Hours()/24))
}

// Color helpers
var (
	Red    = color.New(color.FgRed).SprintFunc()
	Yellow = color.New(color.FgYellow).SprintFunc()
	Green  = color.New(color.FgGreen).SprintFunc()
	Blue   = color.New(color.FgBlue).SprintFunc()
	Dim    = color.New(color.Faint).SprintFunc()
	Bold   = color.New(color.Bold).SprintFunc()
)

// LevelColor returns colored level string.
func LevelColor(level string) string {
	switch strings.ToLower(level) {
	case "error", "fatal", "critical":
		return Red(level)
	case "warning", "warn":
		return Yellow(level)
	case "info":
		return Blue(level)
	case "debug":
		return Dim(level)
	default:
		return level
	}
}

// StatusColor returns colored status string.
func StatusColor(status string) string {
	switch strings.ToLower(status) {
	case "completed", "success", "ok":
		return Green(status)
	case "failed", "error":
		return Red(status)
	case "running", "in_progress", "agent_running":
		return Yellow(status)
	default:
		return status
	}
}

// ParseSince converts "24h", "7d", "2w" to hours.
func ParseSince(s string) (int, error) {
	if s == "" {
		return 24, nil // default 24 hours
	}

	n := 0
	unit := ""
	_, err := fmt.Sscanf(s, "%d%s", &n, &unit)
	if err != nil {
		// Try just a number (assume hours)
		if _, err := fmt.Sscanf(s, "%d", &n); err == nil {
			return n, nil
		}
		return 0, fmt.Errorf("invalid time format: %s", s)
	}

	switch unit {
	case "h":
		return n, nil
	case "d":
		return n * 24, nil
	case "w":
		return n * 24 * 7, nil
	default:
		return 0, fmt.Errorf("unknown unit: %s", unit)
	}
}
