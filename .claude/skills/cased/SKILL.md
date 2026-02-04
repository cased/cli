---
name: cased
description: Query telemetry data (errors, traces, metrics) and AI agent sessions using the Cased CLI. Use when investigating production errors, debugging issues, analyzing traces, checking pod metrics, reviewing agent sessions, or examining observability data.
allowed-tools: Bash(cased:*)
---

# Cased CLI - Telemetry & Agent Queries

Query errors, traces, metrics, and AI agent sessions from Cased.

## Setup

Requires `CASED_API_KEY` environment variable. Get your key from https://app.cased.com/settings/api

## Commands

### Query Errors

```bash
# Recent errors (last 24h by default)
cased errors --since 24h

# Search for specific errors
cased errors --search "KeyError" --level error

# Output as JSON for processing
cased errors --since 1h --json
```

Options:
- `--since`: Time range (1h, 24h, 7d)
- `--level`: Filter by level (error, warning, fatal)
- `--search`: Search in exception type/value
- `--project`: Filter by project ID
- `--limit`: Max results (default 50)
- `--json`: JSON output

### Query Traces

```bash
# Recent traces
cased traces --since 1h

# Filter by service and status
cased traces --service demo-web --status error

# Get all spans for a specific trace
cased traces --trace-id abc123
```

Options:
- `--since`: Time range
- `--cluster`: Filter by cluster ID
- `--service`: Filter by service name
- `--trace-id`: Get spans for specific trace
- `--status`: Filter by status (ok, error)
- `--limit`: Max results
- `--json`: JSON output

### Query Metrics

```bash
# Recent metrics
cased metrics --since 1h

# Filter by pod
cased metrics --pod my-pod-abc123

# Filter by metric type
cased metrics --metric cpu_percent --namespace default
```

Options:
- `--since`: Time range
- `--cluster`: Filter by cluster ID
- `--namespace`: Filter by namespace
- `--pod`: Filter by pod name
- `--metric`: Filter by name (cpu_percent, memory_bytes)
- `--limit`: Max results
- `--json`: JSON output

### Overview Commands

```bash
# Statistics summary
cased stats

# List clusters
cased clusters
```

### Agent Sessions

```bash
# List recent sessions
cased sessions --since 24h

# Filter by status
cased sessions --status completed
cased sessions --status failed

# Filter by type
cased sessions --type root_cause_analysis

# Get session details
cased session <session_id>

# View session logs
cased session <session_id> --logs

# View conversation history
cased session <session_id> --conversation
```

Options for `sessions`:
- `--since`: Time range (1h, 24h, 7d)
- `--status`: Filter by status (created, agent_running, completed, failed, cancelled)
- `--type`: Filter by type (deploy_monitor, root_cause_analysis, general)
- `--limit`: Max results (default 20)
- `--json`: JSON output

Options for `session`:
- `--logs`: Show execution logs
- `--conversation`: Show conversation history
- `--json`: Full JSON output

### Source Maps

Upload source maps to de-minify JavaScript stack traces:

```bash
# Upload source maps for a release
cased sourcemaps upload -p my-project -r v1.2.3 dist/*.map

# List uploaded source maps
cased sourcemaps list -p my-project

# Delete source maps for a release
cased sourcemaps delete -p my-project -r v1.2.3
```

Options for `sourcemaps upload`:
- `--project, -p`: Project ID or slug (required)
- `--release, -r`: Release version (required)
- `--url-prefix`: URL prefix to strip when matching files

### Performance Analysis

Analyze distributed trace performance:

```bash
# Find slow spans (>500ms by default)
cased perf slow --since 1h --threshold 500
cased perf slow --service api --since 24h

# View latency percentiles (p50, p95, p99)
cased perf latency --since 1h
cased perf latency --service api --group-by endpoint

# Detect N+1 query patterns
cased perf n1 --since 1h
cased perf n1 --min-count 10

# Service breakdown for a trace
cased perf breakdown <trace_id>

# Detect performance regressions
cased perf regression --service api
cased perf regression --service api --baseline 7d --compare 1d

# Overall performance summary
cased perf summary --since 1h
```

Options for `perf slow`:
- `--since`: Time range (1h, 24h, 7d)
- `--threshold`: Minimum duration in ms (default: 500)
- `--service`: Filter by service name
- `--limit`: Max results (default 50)

Options for `perf latency`:
- `--since`: Time range
- `--service`: Filter by service
- `--group-by`: service, endpoint, or both

Options for `perf n1`:
- `--since`: Time range
- `--min-count`: Minimum repetitions to flag (default: 5)

Options for `perf regression`:
- `--service`: Service to analyze (required)
- `--endpoint`: Optional endpoint filter
- `--baseline`: Baseline period (default: 7d)
- `--compare`: Comparison period (default: 1d)

### LLM Monitoring

Analyze LLM/AI usage across agent sessions:

```bash
# Token usage by model/provider
cased llm usage --since 24h
cased llm usage --group-by provider --json

# Cost estimation
cased llm cost --since 24h
cased llm cost --model claude-3-5-sonnet-20241022

# Latency percentiles (p50, p95, p99)
cased llm latency --since 1h
cased llm latency --model gpt-4o

# Error statistics
cased llm errors --since 24h

# Overall summary (calls, tokens, cost, top models)
cased llm summary --since 24h

# Per-session rollups (multi-turn conversation analysis)
cased llm sessions --since 24h --limit 20
cased llm sessions --sort-by cost
```

Options for `llm usage`:
- `--since`: Time range (1h, 24h, 7d)
- `--model`: Filter by model name
- `--provider`: Filter by provider (anthropic, openai)
- `--group-by`: model, provider, or both (default: model)
- `--json`: JSON output

Options for `llm cost`:
- `--since`: Time range
- `--model`: Filter by model
- `--provider`: Filter by provider
- `--group-by`: model, provider, or both

Options for `llm latency`:
- `--since`: Time range
- `--model`: Filter by model
- `--provider`: Filter by provider

Options for `llm errors`:
- `--since`: Time range
- `--model`: Filter by model
- `--limit`: Max recent errors to show

Options for `llm sessions`:
- `--since`: Time range
- `--limit`: Max sessions (default 20)
- `--sort-by`: cost, tokens, calls, or latency (default: cost)

## Investigation Workflow

1. Start with `cased stats` to get an overview
2. Check `cased errors --since 1h` for recent issues
3. Use `--search` to find specific error types
4. Look at `cased traces --status error` for failed requests
5. Check `cased metrics` for resource issues
6. Review `cased sessions --status failed` for failed agent runs
7. Use `cased perf slow` to find performance bottlenecks
8. Run `cased perf n1` to detect N+1 query patterns
9. Use `cased perf regression --service api` to detect latency regressions
10. Use `cased llm summary` to see LLM usage overview
11. Run `cased llm sessions` to analyze cost per conversation

Use `--json` flag when you need to process output programmatically.
