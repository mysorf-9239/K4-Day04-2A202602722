# IT Helpdesk Agent - Streamlit UI

## Overview

This is a Streamlit-based UI for the IT Helpdesk Agent. It reuses the `run_model_tool_loop` from `chat.py` to ensure consistency between CLI, eval evidence, and UI.

## Features

- **Chat Interface**: Modern chat UI with Streamlit
- **Tool Visualization**: Visual display of tool calls and results
- **Configuration**: Easy setup of provider, model, and parameters
- **Transcript Management**: Save and load transcripts for eval evidence
- **Artifact Info**: Display version and hash information

## Quick Start

1. **Install dependencies** (if not already installed):
   ```powershell
   python -m pip install -r requirements.txt
   ```

2. **Run the UI**:
   ```powershell
   cd starter_v0
   streamlit run app.py --server.headless true --server.port 8501
   ```

3. **Open browser**: Navigate to `http://localhost:8501`

## Usage

### Configuration

In the sidebar:
- **Model Provider**: Select OpenAI, OpenRouter, Anthropic, or Gemini
- **Model Name**: Optional custom model name
- **History Window**: Number of recent message pairs to keep (1-20)
- **Max Tool Rounds**: Maximum tool calling rounds per turn (1-10)

### Chat

1. Click **Load/Reload Artifacts** to initialize the agent
2. Type your IT support question in the chat input
3. View tool calls and results in real-time
4. Download transcript for eval evidence

### Features

- **Tool Calls**: Displayed with blue left border and JSON formatting
- **Tool Results**: Displayed with green left border and JSON formatting
- **Session Metrics**: Shows total turns, tool events, and last status
- **Clear Chat**: Reset conversation history
- **Download Transcript**: Export transcript as JSON

## Architecture

The UI follows the same architecture as CLI and eval:

```
UI (app.py) → run_model_tool_loop (chat.py) → Provider → Tools
```

This ensures consistency across all interfaces.

## Files

- `app.py`: Main Streamlit application
- `chat.py`: Core agent loop (reused from CLI)
- `artifacts/system_prompt.md`: System prompt for the agent
- `artifacts/tools.yaml`: Tool declarations

## Troubleshooting

### UI not loading
- Ensure Streamlit is installed: `python -m pip install "streamlit>=1.30.0"`
- Check if port 8501 is available
- Verify `.env` file has correct API keys

### Tool calls not working
- Ensure provider is loaded (click Load/Reload Artifacts)
- Check API key validity
- Verify tool declarations in `tools.yaml`

### Transcript not saving
- Check write permissions in `starter_v0/` directory
- Ensure sufficient disk space

## Development

To modify the UI:

1. Edit `app.py`
2. Streamlit auto-reloads on file changes
3. Check terminal for errors

## Integration with Eval

The UI generates transcripts in the same format as CLI and eval:

```json
{
  "transcript_id": "ui_20260914T185306630037",
  "artifact_version": "v0+p233ec2cecfdf+teb3e2243f237",
  "provider": "openai",
  "turns": [...]
}
```

These transcripts can be used as eval evidence in the report.