# Local Web App

The project includes a lightweight local browser UI so users can try the agent without editing command-line arguments.

## Start

```powershell
py -3 scripts/app_server.py --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

## User Flow

1. Load the fictional sample.
2. Edit the product brief and synthetic competitor table.
3. Generate the report.
4. Review the evidence levels and manual review notes.
5. Copy or download the Markdown output.

## Safety Boundary

- The app is local-only.
- It does not fetch live market data.
- It does not persist user-entered brief text or competitor rows into tracked files.
- The sample data remains fictional and synthetic.
- The output keeps facts, inferences, recommendations, evidence levels, and review notes visible.

## Product Manager Value

The UI makes the agent easier to evaluate as a portfolio product:

- Inputs are visible and editable.
- Output is immediate and inspectable.
- Review gates are part of the generated report.
- The workflow feels like a small internal research tool while remaining safe for public demonstration.
