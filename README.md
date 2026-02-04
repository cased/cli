# Cased CLI

CLI for Cased - designed for agents, not humans.

## Install

```bash
go install github.com/cased/cli@latest
```

Or download from [releases](https://github.com/cased/cli/releases).

## Quick Start

```bash
# Authenticate
cased configure

# Query errors
cased errors --since 24h

# Follow logs in real-time
cased logs -f

# Query traces
cased traces --service api
```

## Commands

### Telemetry

```bash
cased errors [--since 24h] [--level error] [--search term]
cased logs [--since 24h] [-f/--follow] [--level info] [--service name]
cased traces [--since 24h] [--service name] [--status ok|error]
cased metrics [--since 24h] [--pod name] [--cluster name]
cased stats [--since 24h]
cased clusters
```

### Performance Analysis

```bash
cased perf slow [--threshold 1000]     # Find slow spans
cased perf latency                      # p50/p95/p99 latencies
cased perf n1                           # Detect N+1 queries
cased perf breakdown <trace_id>         # Service breakdown
cased perf regression                   # Detect regressions
cased perf summary
```

### LLM Monitoring

```bash
cased llm usage [--model name]          # Token usage
cased llm cost                          # Cost estimates
cased llm latency                       # Latency percentiles
cased llm errors                        # Error stats
cased llm sessions                      # Per-session usage
cased llm summary
```

### Agent Sessions

```bash
cased sessions [--status completed|failed|running]
cased session <id> [--logs] [--conversation]
```

### Investigation

```bash
# Open error in Claude Code
cased investigate <event_id>
```

### Source Maps

```bash
cased sourcemaps upload --project foo --release v1.0 *.map
cased sourcemaps list --project foo
cased sourcemaps delete --project foo --release v1.0
```

### Documentation

```bash
cased docs upload <file>
cased docs upload --title "My Doc" --cleanup doc.md
```

## JSON Output

Add `--json` or `-j` to any command:

```bash
cased errors --json | jq '.[] | .exception_type'
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CASED_API_KEY` | API token (overrides config) |
| `CASED_API_URL` | API URL (default: https://app.cased.com) |

Config stored in `~/.config/cased/config.json`
