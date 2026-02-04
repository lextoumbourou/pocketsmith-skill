# PocketSmith Skill for OpenClaw

> Manage PocketSmith transactions, categories, and financial data via the API.

**Repository:** https://github.com/lextoumbourou/pocketsmith-skill

## Features

- **Transactions** - List, view, create, update, and delete transactions
- **Categories** - Full CRUD for spending categories
- **User Info** - View authenticated user details
- **Write Protection** - Safe by default, write operations require explicit opt-in

## Installation

### Manual Installation

```bash
# Clone into your skills directory
cd ~/.claude/skills  # or your preferred skills location
git clone https://github.com/lextoumbourou/pocketsmith-skill.git pocketsmith

# Install dependencies
cd pocketsmith
uv sync
```

### Verify Installation

```bash
cd ~/.claude/skills/pocketsmith
uv run pocketsmith --help
```

## Setup

### 1. Get PocketSmith Developer Key

1. Log in to [PocketSmith](https://my.pocketsmith.com/)
2. Go to **Settings** > **Security** > **Manage Developer Keys**
3. Create a new developer key and copy it

### 2. Set Environment Variables

For OpenClaw, add to `~/.openclaw/.env`:

```bash
POCKETSMITH_DEVELOPER_KEY=your_developer_key
```

Or add to `~/.openclaw/openclaw.json`:

```json
{
  "env": {
    "POCKETSMITH_DEVELOPER_KEY": "your_developer_key"
  }
}
```

See [OpenClaw Environment Configuration](https://docs.openclaw.ai/environment) for more options.

For shell usage, add to `~/.bashrc` or `~/.zshrc`:

```bash
export POCKETSMITH_DEVELOPER_KEY="your_developer_key"
```

### 3. Enable Write Operations (Optional)

Write operations (create, update, delete) are disabled by default for safety. To enable, add to your environment:

For OpenClaw (`~/.openclaw/.env`):

```bash
POCKETSMITH_ALLOW_WRITES=true
```

For shell:

```bash
export POCKETSMITH_ALLOW_WRITES=true
```

### 4. Verify Authentication

```bash
uv run pocketsmith auth status
```

## Usage

### CLI Commands

```bash
# Get current user
uv run pocketsmith me

# List transactions for a user
uv run pocketsmith transactions list-by-user 123456

# Search transactions
uv run pocketsmith transactions list-by-user 123456 --search "coffee" --start-date 2024-01-01

# Get a specific transaction
uv run pocketsmith transactions get 987654

# Update a transaction (requires POCKETSMITH_ALLOW_WRITES=true)
uv run pocketsmith transactions update 987654 --category-id 28637787

# Create a transaction
uv run pocketsmith transactions create 456789 --payee "Coffee Shop" --amount -5.50 --date 2024-01-15

# List categories
uv run pocketsmith categories list 123456

# Create a category
uv run pocketsmith categories create 123456 --title "Subscriptions" --parent-id 28601039

# Get help
uv run pocketsmith --help
uv run pocketsmith transactions --help
uv run pocketsmith categories --help
```

### In OpenClaw/Claude

Just ask naturally:

- "Show me my PocketSmith transactions from last month"
- "Find all transactions containing 'Netflix'"
- "Categorize transaction 123456 as Subscriptions"
- "Create a new category called 'Side Projects' under Entertainment"
- "List all my spending categories"

## API Reference

See [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md) for implementation details and endpoint coverage.

## Output

All commands output JSON to stdout. Errors are written to stderr.

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Run directly
uv run pocketsmith me
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `POCKETSMITH_DEVELOPER_KEY environment variable is required` | Set `POCKETSMITH_DEVELOPER_KEY` |
| `Write operations are disabled` | Set `POCKETSMITH_ALLOW_WRITES=true` |
| `401 Unauthorized` | Check your developer key is valid |
| `404 Not Found` | Check the resource ID exists |

## License

MIT
