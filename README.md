# 🎙️ Voice Dictation Tool

A local Python application that captures voice input via global hotkeys, transcribes speech using Replicate's incredibly-fast-whisper model, and automatically pastes the result wherever your cursor is positioned.

## Features

- **Global Hotkey Support**: Press and hold Ctrl+Alt to start recording, release to stop (works even when the app isn't focused)
- **Device Selection**: Interactive audio device selection at startup
- **Fast Transcription**: Uses Replicate's incredibly-fast-whisper model (transcribes 150 minutes in ~100 seconds)
- **Automatic Pasting**: Transcribed text is automatically copied to clipboard and pasted at cursor position
- **Recording History**: All transcriptions are saved to `recordings.json` with timestamps
- **Custom Vocabulary**: Supports custom vocabulary corrections for better recognition of technical terms
- **Environment Configuration**: Configure settings via `.env` file

## Requirements

### System Requirements

- Python 3.8 or higher
- Linux, macOS, or Windows
- Microphone access
- Internet connection (for Replicate API)

### System Dependencies

#### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev
sudo apt-get install xclip  # Required for clipboard functionality
```

#### macOS

No additional system dependencies required (uses built-in audio system).

#### Windows

No additional system dependencies required.

### Python Dependencies

All Python dependencies are listed in `requirements.txt` and will be installed automatically (see Installation below).

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Create `.env` file**:

```bash
cp .env.example .env
```

5. **Configure your `.env` file**:

Edit `.env` and add your Replicate API token:

```env
REPLICATE_API_TOKEN=r8_your_api_token_here
```

Get your API token from: https://replicate.com/account/api-tokens

### Optional Environment Variables

You can customize the application behavior by setting these variables in `.env`:

```env
# Maximum recording duration in minutes (default: 5.0, range: 0.1-60.0)
MAX_RECORDING_MINUTES=5

# Audio sample rate in Hz (default: 44100, range: 8000-48000)
SAMPLE_RATE=44100

# Replicate model name (default: vaibhavs10/incredibly-fast-whisper)
REPLICATE_MODEL=vaibhavs10/incredibly-fast-whisper

# Minimum recording duration in seconds (default: 1.0, min: 0.1)
MIN_RECORDING_SECONDS=1.0
```

## Usage

1. **Activate the virtual environment** (if not already activated):

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Run the application**:

**On Linux** (requires `sudo` for global keyboard hotkey access):

Option 1 - Use the helper script (recommended):
```bash
./run.sh
```

Option 2 - Use sudo with venv Python directly:
```bash
sudo venv/bin/python start.py
```

Option 3 - Activate venv first, then use sudo:
```bash
source venv/bin/activate
sudo $(which python) start.py
```

**On macOS/Windows**:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python start.py
```

**Note**: On Linux, the `keyboard` library requires root permissions for global hotkey detection. Use `sudo` with the full path to your virtual environment's Python interpreter (`venv/bin/python`) to ensure it uses the correct Python and installed packages.

3. **Select your audio input device** when prompted (or press Enter for default)

4. **Start dictating**:
   - Position your cursor in the desired text field (any application)
   - Press and **hold** Ctrl+Alt to start recording
   - Speak your text
   - **Release** Ctrl+Alt to stop recording and process
   - The transcribed text will automatically appear at your cursor position

5. **Exit the application**: Press Ctrl+C in the terminal

## Configuration

### Custom Vocabulary

Edit `config.py` to add custom vocabulary corrections:

```python
CUSTOM_VOCABULARY = {
    'n8n': ['n8n', 'n 8 n', 'n eight n', 'nateon', 'AN10', 'N810', 'N8N', 'A10'],
    'Retell': ['Retell', 'retell', 're-tell', 'retail', 'retale', 're tell'],
    # Add your own terms here
}
```

The application will automatically correct common mispronunciations to your specified canonical terms.

### Recording Settings

You can adjust recording settings in `config.py`:

```python
RECORDING_SETTINGS = {
    'sample_rate': 44100,  # Audio sample rate
    'channels': 1,          # Mono audio
    'dtype': 'float32'      # Data type (float32 is more widely supported)
}
```

Or override via environment variables (see Optional Environment Variables above).

## Project Structure

```
voice2text/
├── start.py              # Main application script
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables file
├── .env                  # Your environment variables (create from .env.example)
├── recordings.json       # Transcription history (created automatically)
├── temp/                 # Temporary audio files directory
└── README.md             # This file
```

## Troubleshooting

### "PortAudio library not found" Error

**Linux**: Install PortAudio:
```bash
sudo apt-get install portaudio19-dev
```

**macOS**: Usually works out of the box. If not, try:
```bash
brew install portaudio
```

### "Permission denied" for Keyboard Access (Linux)

The `keyboard` library requires root permissions on Linux for global hotkey detection. Run with `sudo`:

```bash
sudo python start.py
```

### "No audio input devices found"

- Check that your microphone is connected and enabled
- Verify microphone permissions in your system settings
- On Linux, you may need to install audio drivers

### "REPLICATE_API_TOKEN not found"

- Make sure you've created a `.env` file from `.env.example`
- Verify your API token is set correctly in `.env`
- Check that the token starts with `r8_`

### Clipboard/Paste Not Working (Linux)

Install `xclip` or `xsel`:

```bash
sudo apt-get install xclip
# or
sudo apt-get install xsel
```

### Recording Too Short Error

Recordings must be at least 1 second long (configurable via `MIN_RECORDING_SECONDS` in `.env`). Make sure you're holding the hotkeys long enough while speaking.

### Maximum Recording Duration Reached

The default maximum is 5 minutes. Adjust `MAX_RECORDING_MINUTES` in your `.env` file if you need longer recordings.

## How It Works

1. **Hotkey Detection**: Global keyboard hook listens for Ctrl+Alt key combination
2. **Audio Recording**: While hotkeys are held, audio is captured from the selected input device
3. **Temporary Storage**: Audio is saved as a WAV file in the `temp/` directory
4. **Transcription**: Audio is sent to Replicate's incredibly-fast-whisper model via API
5. **Vocabulary Correction**: Transcribed text is processed through custom vocabulary mappings
6. **Text Insertion**: Text is copied to clipboard and automatically pasted using Ctrl+V
7. **Persistence**: Transcription is saved to `recordings.json` with timestamp
8. **Cleanup**: Temporary audio file is deleted after successful processing

## Limitations

- Requires active internet connection for transcription
- On Linux, may require `sudo` for global hotkey detection
- Maximum recording duration is configurable but recommended to keep under 5 minutes for optimal performance
- Transcription accuracy depends on audio quality and clarity of speech

## License

This project is provided as-is for personal and commercial use.

## Support

For issues, questions, or contributions, please refer to the project repository.
