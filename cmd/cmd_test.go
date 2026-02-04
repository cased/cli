package cmd

import (
	"context"
	"strings"
	"testing"
)

func TestVersion(t *testing.T) {
	if Version == "" {
		t.Error("Version should not be empty")
	}
	if !strings.HasPrefix(Version, "0.") {
		t.Errorf("Version = %q, expected to start with 0.", Version)
	}
}

func TestRunHelp(t *testing.T) {
	// Should not error when showing help
	err := Run(context.Background(), []string{"cased", "--help"})
	if err != nil {
		t.Errorf("Run(--help) error = %v", err)
	}
}

func TestRunVersion(t *testing.T) {
	// Should not error when showing version
	err := Run(context.Background(), []string{"cased", "--version"})
	if err != nil {
		t.Errorf("Run(--version) error = %v", err)
	}
}

func TestRunSubcommandHelp(t *testing.T) {
	// Should not error when showing subcommand help
	err := Run(context.Background(), []string{"cased", "errors", "--help"})
	if err != nil {
		t.Errorf("Run(errors --help) error = %v", err)
	}
}

func TestExitError(t *testing.T) {
	err := exitError("test %s %d", "message", 42)
	if err == nil {
		t.Fatal("exitError should return an error")
	}
	if !strings.Contains(err.Error(), "test message 42") {
		t.Errorf("exitError message = %q, should contain 'test message 42'", err.Error())
	}
}
