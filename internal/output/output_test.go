package output

import (
	"testing"
	"time"
)

func TestParseSince(t *testing.T) {
	tests := []struct {
		input   string
		want    int
		wantErr bool
	}{
		{"", 24, false},          // default
		{"24h", 24, false},       // hours
		{"1h", 1, false},
		{"48h", 48, false},
		{"7d", 168, false},       // days
		{"1d", 24, false},
		{"14d", 336, false},
		{"2w", 336, false},       // weeks
		{"1w", 168, false},
		{"24", 24, false},        // bare number = hours
		{"invalid", 0, true},
		{"5x", 0, true},          // unknown unit
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got, err := ParseSince(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("ParseSince(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("ParseSince(%q) = %d, want %d", tt.input, got, tt.want)
			}
		})
	}
}

func TestTruncate(t *testing.T) {
	tests := []struct {
		input string
		max   int
		want  string
	}{
		{"hello", 10, "hello"},
		{"hello world", 8, "hello..."},
		{"hi", 2, "hi"},
		{"hello", 5, "hello"},
		{"hello", 4, "h..."},
		{"", 5, ""},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := Truncate(tt.input, tt.max)
			if got != tt.want {
				t.Errorf("Truncate(%q, %d) = %q, want %q", tt.input, tt.max, got, tt.want)
			}
		})
	}
}

func TestFormatTime(t *testing.T) {
	// Test valid RFC3339
	input := "2024-01-15T10:30:00Z"
	got := FormatTime(input)
	// Should be formatted as local time
	if got == input {
		t.Error("FormatTime should convert from RFC3339")
	}
	if len(got) != 19 { // "2006-01-02 15:04:05"
		t.Errorf("FormatTime(%q) = %q, unexpected format", input, got)
	}

	// Test invalid input returns as-is
	invalid := "not-a-date"
	if FormatTime(invalid) != invalid {
		t.Errorf("FormatTime should return invalid input as-is")
	}
}

func TestRelativeTime(t *testing.T) {
	now := time.Now()

	tests := []struct {
		name  string
		input string
		want  string
	}{
		{"just now", now.Add(-30 * time.Second).Format(time.RFC3339), "just now"},
		{"minutes", now.Add(-5 * time.Minute).Format(time.RFC3339), "5m ago"},
		{"hours", now.Add(-3 * time.Hour).Format(time.RFC3339), "3h ago"},
		{"days", now.Add(-48 * time.Hour).Format(time.RFC3339), "2d ago"},
		{"invalid", "not-a-date", "not-a-date"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := RelativeTime(tt.input)
			if got != tt.want {
				t.Errorf("RelativeTime() = %q, want %q", got, tt.want)
			}
		})
	}
}

func TestLevelColor(t *testing.T) {
	// Just verify it doesn't panic and returns something
	levels := []string{"error", "ERROR", "warning", "warn", "info", "debug", "unknown"}
	for _, level := range levels {
		got := LevelColor(level)
		if got == "" {
			t.Errorf("LevelColor(%q) returned empty string", level)
		}
	}
}

func TestStatusColor(t *testing.T) {
	// Just verify it doesn't panic and returns something
	statuses := []string{"completed", "success", "ok", "failed", "error", "running", "in_progress", "unknown"}
	for _, status := range statuses {
		got := StatusColor(status)
		if got == "" {
			t.Errorf("StatusColor(%q) returned empty string", status)
		}
	}
}
