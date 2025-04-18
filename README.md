# Chat Regenerator

A set of tools for processing, analyzing, and visualizing conversation data from various chat platforms.

## Overview

The Chat Regenerator allows you to parse, structure, and visualize conversations from different chat sources:

1. **Conti Chat Parser** - For processing dual-party (Conti chats) conversations from JSON logs
2. **Group Chat Parser** - For processing multi-party conversations in JSON-like format **NOT WORKING YET**

Both modules produce HTML files that allow for interactive annotation of conversations with customizable dropdown categories. The annotated data can be downloaded as CSV for further analysis.

## Features

- **Log Parsing**: Process chat logs from different formats
- **Conversation Structuring**: Organizes messages into turns and segments
- **User Alias Mapping**: Consolidates user identities across different aliases
- **Interactive HTML Interface**: Visual representation of conversations for annotation
- **Flexible Annotation System**: Configurable dropdowns for coding conversations
- **CSV Export**: Export annotated data for analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/general_chat_recreator.git
cd general_chat_recreator

# Install required dependencies
pip install -r requirements.txt
```

## Usage

### Example 1: Processing Conti Chat Logs

```python
from convo_regenerator import all_conversations_sorted_with_turns_and_html

# Configure dropdown categories
intention_config = {
    'name': 'intention',
    'options': {
        "Personal": ["Sharing info", "Asking question", "Social invitation"],
        "Work": ["Task assignment", "Status update", "Meeting coordination"]
    },
    'label': 'Intention'
}

tone_config = {
    'name': 'tone',
    'options': ["Happy", "Sad", "Urgent", "Casual", "Formal"],
    'label': 'Tone'
}

# Combine configurations
dropdown_configs = [intention_config, tone_config]

# Process conversations and generate HTML
files = ['logs/Conti_chat_logs.json', 'logs/Conti_jabber_logs.json']
user_aliases = 'logs/Conti_user match list.json'
output_pairs = [('user1', 'user2'), ('user3', 'user4')]

conversation_turns = all_conversations_sorted_with_turns_and_html(
    files, 
    user_aliases,
    dropdown_configs=dropdown_configs,
    output_users=output_pairs,
    output_dir="output_html"
)
```

### Example 2: Processing Group Chats

```python
from convo_regenerator import process_group_chat, get_sample_configs

# Example of processing a group chat log
file = "logs/cleaned_BlackBasta_translated.json" # Cleaned group chat logs from translated BlackBasta
chat_id = "!kJVcUcyUsQhwBCuIPD" # chat ID stripped from server

process_group_chat(
    file_path=file,
    dropdown_configs=dropdown_configs,
    chat_id = chat_id,
    output_dir="output_html" 
)
```

### Command Line Usage

You can also run the tools from the command line:

```bash
# For Conti chats (if implemented as CLI)
python convo_regenerator.py --files logs/Conti_chat_logs.json logs/Conti_jabber_logs.json --aliases logs/Conti_user_match_list.json --users "user1,user2" "user3,user4" --output "./output_html"
```


```bash
# For BlackBasta
python group_chat_regenerator.py --file logs/cleaned_BlackBasta_translated.json --chat_id '!kJVcUcyUsQhwBCuIPD' --output "./output_html"
```

## Dropdown Configuration

You can define any number of dropdown categories with either:

1. **Simple dropdowns**: A list of options
2. **Dependent dropdowns**: A dictionary where keys are primary options and values are lists of secondary options

Each dropdown config requires:
- `name`: Internal identifier
- `options`: Either a list or dictionary of options
- `label`: Display name

Optional fields with defaults:
- `button_text`: Text for the "Add" button (defaults to "Add {label}")
- `csv_column`: Name in CSV output (defaults to the label)

## Interactive HTML Interface

The generated HTML files allow for:

- Viewing conversations with proper attribution
- Adding annotations via dropdown selections
- Adding multiple annotations per turn
- Exporting annotations as CSV
NOTE!: Reloading the html page will reset all dropdown selections. Saving as you go with the html is not a feature.  

## Quick Start

For a quick demonstration of all features, refer to `ExamplesHowTo.ipynb` notebook which provides interactive examples of how to create and use the chat regenerators.

## Dependencies

- Python 3.6+
- python-dateutil
- Standard Python libraries (json, re, os, collections)