# Mock data (local directory storage)

`applications/` holds synthetic candidate/member profiles selectable from the React UI.
`documents/<candidate_id>/` holds supporting documents surfaced through the MCP file server.

These files are read exclusively through the `candidate-files` MCP server defined in
`mcp.config.json`. All data is synthetic.
