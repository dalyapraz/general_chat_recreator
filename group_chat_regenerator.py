import json
import os
import dateutil.parser
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

def parse_group_chat(file_path: str) -> List[Dict]:
    """
    Parse a file containing clean group chat messages in JSON format.
    
    Args:
        file_path: Path to the group chat JSON file
        
    Returns:
        List of message dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    # Ensure timestamps are parsed to datetime objects
    for msg in messages:
        if 'timestamp' in msg and isinstance(msg['timestamp'], str):
            msg['timestamp'] = dateutil.parser.parse(msg['timestamp'])
    
    return messages


def find_most_active_user(messages: List[Dict], chat_id: str) -> str:
    """
    Find the user who sent the most messages in the specified chat.
    
    Args:
        messages: List of message dictionaries
        chat_id: The chat ID to filter for
        
    Returns:
        Username of the most active sender in the chat
    """
    # Filter messages for the specified chat
    chat_messages = [msg for msg in messages if msg.get('chat_id') == chat_id]
    
    if not chat_messages:
        return ""
    
    # Count messages per user
    user_message_counts = {}
    for msg in chat_messages:
        if 'sender_alias' in msg:
            sender = msg['sender_alias']
            if sender in user_message_counts:
                user_message_counts[sender] += 1
            else:
                user_message_counts[sender] = 1
    
    # Find user with most messages
    if user_message_counts:
        return max(user_message_counts.items(), key=lambda x: x[1])[0]
    
    return ""


def group_chat_to_html(messages: List[Dict], chat_id: str, main_user: str, html_file: str, dropdown_configs: List[Dict[str, Any]]):
    """
    Creates an HTML file from group chat messages with the specified chat_id.
    Messages from the main_user will be shown on the right side, and all other users on the left.
    
    Args:
        messages: List of message dictionaries
        chat_id: The chat ID to filter for
        main_user: The username for the main user (messages will be shown on the right)
        html_file: Output HTML file path
        dropdown_configs: List of dictionaries defining dropdown configurations
    """
    # Process configuration to add defaults for optional fields
    for config in dropdown_configs:
        if 'button_text' not in config:
            config['button_text'] = f"Add {config['label']}"
        if 'csv_column' not in config:
            config['csv_column'] = config['label']
    
    # Filter messages for the specified chat_id
    chat_messages = [msg for msg in messages if msg.get('chat_id') == chat_id]
    
    if not chat_messages:
        print(f"No messages found for chat_id: {chat_id}")
        return
    
    # Sort messages by timestamp
    chat_messages.sort(key=lambda x: x.get('timestamp', datetime.min))
    
    # Get unique users in the chat
    users = set(msg.get('sender_alias', '') for msg in chat_messages if 'sender_alias' in msg)
    print(f"Users in chat: {', '.join(users)}")
    
    # Group messages by sender and turn
    turns = []
    current_sender = None
    current_turn = []
    
    for msg in chat_messages:
        sender = msg.get('sender_alias', '')
        timestamp = msg.get('timestamp', datetime.min)
        
        # If sender changes or time gap is more than 30 minutes, start a new turn
        if (sender != current_sender or 
            (current_turn and (timestamp - current_turn[-1].get('timestamp', datetime.min)).total_seconds() > 1800)):
            if current_turn:
                turns.append(current_turn)
            current_turn = [msg]
            current_sender = sender
        else:
            current_turn.append(msg)
    
    # Add the last turn
    if current_turn:
        turns.append(current_turn)
    
    # Generate HTML
    def generate_options(options):
        opts = '<option value="">--None--</option>\n'
        for opt in options:
            opts += f'<option value="{opt}">{opt}</option>\n'
        return opts

    # Prepare CSV header
    csv_header = ["Turn", "Sender"]
    for config in dropdown_configs:
        csv_header.append(config['csv_column'])
        if isinstance(config['options'], dict):
            csv_header.append(f"{config['csv_column']}_Detailed")
    
    # Begin HTML content
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Group Chat: {chat_id}</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #f9f9f9;
        margin: 20px;
    }}
    h2 {{
        color: #333;
    }}
    .turn {{
        margin: 10px 0;
        padding: 10px;
        border-radius: 8px;
        clear: both;
        overflow: auto;
    }}
    .turn.left {{
        background-color: #f0f0f0;
        text-align: left;
        float: left;
        max-width: 60%;
    }}
    .turn.right {{
        background-color: #dcf8c6;
        text-align: right;
        float: right;
        max-width: 60%;
    }}
    .message {{
        margin: 5px 0;
    }}
    .timestamp {{
        font-size: 0.8em;
        color: #555;
    }}
    .translation {{
        font-size: 1em;
        color: #666;
        font-style: italic;
    }}
    .dropdown-container {{
        margin-top: 10px;
        clear: both;
        font-size: 0.85em;
        font-style: italic;
        color: #444;
    }}
    .category-group, .dropdown-group-container {{
        padding: 5px;
        margin-bottom: 5px;
    }}
    .dropdown-group {{
        margin-bottom: 5px;
        display: inline-block;
        vertical-align: middle;
    }}
    .dropdown-group label {{
        font-weight: bold;
        margin-right: 5px;
    }}
    .add-button {{
        font-size: 0.75em;
        margin-left: 5px;
        vertical-align: middle;
    }}
    .download-button {{
        display: block;
        margin: 40px auto;
        padding: 10px 20px;
        font-size: 1em;
    }}
    .clear {{
        clear: both;
    }}
</style>
</head>
<body>
<h2>Group Chat: {chat_id}</h2>
<p>Main user (messages on right): <strong>{main_user}</strong></p>
<div class="clearfix" id="content">
"""

    # JavaScript for dependent dropdowns
    html += f"""
<script>
// Chat variables
var chat_id = "{chat_id}";
var main_user = "{main_user}";

// Mappings for dependent dropdowns
var dependentMappings = {{
"""

    # Add JavaScript mappings for dependent dropdowns
    for i, config in enumerate(dropdown_configs):
        if isinstance(config['options'], dict):
            html += f"    '{i+1}': {json.dumps(config['options'])},\n"
    
    html += """
};

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // --- Primary Dropdown Change Event for Dependent Dropdowns ---
    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('turn-dropdown')) {
            var catId = e.target.getAttribute('data-dd');
            var selected = e.target.value;
            var catGroup = e.target.closest('[data-cat="' + catId + '"]');
            
            if (!catGroup) return;
            
            // Check if this is a dependent dropdown
            if (dependentMappings[catId]) {
                var depGroup = catGroup.querySelector('.dropdown-group[data-dd="dep"]');
                var otherGroup = catGroup.querySelector('.dropdown-group[data-dd="other"]');
                var depSelect = depGroup ? depGroup.querySelector('select') : null;
                
                if (selected) {
                    if (selected === "Other") {
                        if (depGroup) depGroup.style.display = "none";
                        if (otherGroup) otherGroup.style.display = "inline-block";
                    } else if (dependentMappings[catId][selected]) {
                        if (otherGroup) otherGroup.style.display = "none";
                        if (depSelect) {
                            depSelect.innerHTML = '<option value="">--Select--</option>';
                            dependentMappings[catId][selected].forEach(function(opt) {
                                var option = document.createElement("option");
                                option.value = opt;
                                option.text = opt;
                                depSelect.appendChild(option);
                            });
                            depGroup.style.display = "inline-block";
                        }
                    } else {
                        if (depGroup) depGroup.style.display = "none";
                        if (otherGroup) otherGroup.style.display = "none";
                        if (depSelect) depSelect.innerHTML = '<option value="">--Select--</option>';
                    }
                } else {
                    if (depGroup) depGroup.style.display = "none";
                    if (otherGroup) otherGroup.style.display = "none";
                    if (depSelect) depSelect.innerHTML = '<option value="">--Select--</option>';
                }
            }
        }
    });

    // --- Dynamic Add Button Functionality ---
    document.querySelectorAll('.add-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var cat = this.getAttribute("data-cat");
            var container = this.parentElement;
            var isDependent = dependentMappings[cat] !== undefined;
            
            if (isDependent) {
                // For dependent dropdowns, clone the entire container
                var clone = container.cloneNode(true);
                clone.querySelectorAll('select, input').forEach(function(elem) {
                    elem.value = "";
                    elem.removeAttribute('id');
                });
                container.parentElement.appendChild(clone);
            } else {
                // For simple dropdowns, clone only the dropdown-group
                var originalGroup = container.querySelector('.dropdown-group');
                var clone = originalGroup.cloneNode(true);
                clone.querySelectorAll('select, input').forEach(function(elem) {
                    elem.value = "";
                    elem.removeAttribute('id');
                });
                container.insertBefore(clone, this);
            }
        });
    });

    // --- CSV Download Functionality ---
    document.getElementById("downloadCSVButton").addEventListener("click", function() {
        var csvRows = [];
        var headers = ["""

    # Add CSV headers
    header_str = ", ".join([f'"{h}"' for h in csv_header])
    html += header_str
    
    html += """];
        csvRows.push(headers.join(","));
        
        var turnDivs = document.querySelectorAll(".turn");
        turnDivs.forEach(function(turnDiv) {
            var turn = turnDiv.getAttribute("data-turn") || "";
            var sender = turnDiv.getAttribute("data-sender") || "";
            var row = [turn, sender];
"""

    # Generate JavaScript for processing each dropdown category
    for i, config in enumerate(dropdown_configs):
        cat_id = i + 1
        is_dependent = isinstance(config['options'], dict)
        html += f"""
            // Process category {cat_id}: {config['name']}
            (function() {{
                var cat = {cat_id};
                var isDependent = {str(is_dependent).lower()};
                var catGroups = turnDiv.querySelectorAll('[data-cat="' + cat + '"]');
                var primaryVals = [];
                var detailedVals = [];
                
                catGroups.forEach(function(group) {{
                    var primary = group.querySelector('select[data-dd="' + cat + '"]');
                    if (primary && primary.value.trim() !== "") {{
                        primaryVals.push(primary.value.trim());
                        
                        if (isDependent) {{
                            var detail = "";
                            var depSel = group.querySelector('.dropdown-group[data-dd="dep"] select');
                            var otherInp = group.querySelector('.dropdown-group[data-dd="other"] input');
                            
                            if (otherInp && getComputedStyle(otherInp.parentElement).display !== "none" && otherInp.value.trim() !== "") {{
                                detail = otherInp.value.trim();
                            }} else if (depSel && getComputedStyle(depSel.parentElement).display !== "none" && depSel.value.trim() !== "") {{
                                detail = depSel.value.trim();
                            }}
                            
                            if (detail !== "") {{
                                detailedVals.push(detail);
                            }}
                        }}
                    }}
                }});
                
                row.push(primaryVals.join(";"));
                if (isDependent) {{
                    row.push(detailedVals.join(";"));
                }}
            }})();
"""
    
    html += """
            csvRows.push(row.join(","));
        });
        
        var csvContent = "data:text/csv;charset=utf-8," + csvRows.join("\\n");
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "group_chat_"""

    # Create a safe filename
    safe_chat_id = ''.join(c for c in chat_id if c.isalnum() or c in '_-')
    html += f"{safe_chat_id}_coded.csv"
    
    html += """");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});
</script>
"""

    # Build conversation turns with the dropdowns
    for turn_idx, turn in enumerate(turns):
        sender = turn[0].get('sender_alias', '')
        
        alignment = "right" if sender == main_user else "left"
        html += f'<div class="turn {alignment}" data-turn="{turn_idx}" data-sender="{sender}">\n'
        html += f'<strong>Turn {turn_idx + 1} ({sender}):</strong><br>\n'
        for msg in turn:
            timestamp = msg.get('timestamp', '')
            message_text = msg.get('message', '')
            message_translated = msg.get('message_translated', '')
            
            html += f'<div class="message"><span class="timestamp">{timestamp}</span> - <span class="text">{message_text}</span>'
            
            # Add translation if available and different from original
            if message_translated and message_translated != message_text:
                html += f'<br><span class="translation">[Translation: {message_translated}]</span>'
            
            html += '</div>\n'
        html += '<div class="dropdown-container">\n'
        
        # Generate dropdowns based on configurations
        for i, config in enumerate(dropdown_configs):
            cat_id = i + 1
            is_dependent = isinstance(config['options'], dict)
            container_class = "category-group" if is_dependent else "dropdown-group-container"
            
            html += f'<div class="{container_class}" data-cat="{cat_id}" data-turn="{turn_idx}">\n'
            
            # Primary dropdown
            html += f'<div class="dropdown-group" data-dd="{cat_id}">\n'
            html += f'<label>{config["label"]}: </label>\n'
            html += f'<select class="turn-dropdown" data-dd="{cat_id}">\n'
            
            if is_dependent:
                # For dependent dropdown, options are the keys of the dictionary
                options_list = list(config['options'].keys())
                options_list.append("Other")  # Add "Other" option
                html += generate_options(options_list)
            else:
                # For simple dropdown, options are directly from the list
                html += generate_options(config['options'])
            
            html += '</select>\n'
            html += '</div>\n'
            
            # If dependent dropdown, add the dependent controls
            if is_dependent:
                # Dependent dropdown
                html += f'<div class="dropdown-group" data-dd="dep" style="display:none;">\n'
                html += f'<label>Detailed: </label>\n'
                html += f'<select class="dependent-dropdown" data-dd="dep">\n'
                html += '<option value="">--Select--</option>\n'
                html += '</select>\n'
                html += '</div>\n'
                
                # Input field for "Other"
                html += f'<div class="dropdown-group" data-dd="other" style="display:none;">\n'
                html += f'<label>Please specify: </label>\n'
                html += f'<input type="text" class="other-input" data-dd="other" />\n'
                html += '</div>\n'
            
            html += f'<button type="button" class="add-button" data-cat="{cat_id}">{config["button_text"]}</button>\n'
            html += '</div>\n'
        
        html += '</div>\n'  # End of dropdown-container
        html += '</div>\n'  # End of turn div

    html += '<div class="clear"></div>\n'
    # Download CSV button
    html += '<button class="download-button" id="downloadCSVButton">Download</button>\n'
    
    # Close tags
    html += """
</div>
</body>
</html>
"""
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML file '{html_file}' created successfully.")


def process_group_chat(
    file_path: str, 
    chat_id: str,
    main_user: str = None,
    dropdown_configs: List[Dict[str, Any]] = None,
    output_dir: str = "./"
):
    """
    Process a group chat file and generate an HTML view for the specified chat_id.
    
    Args:
        file_path: Path to the group chat file
        chat_id: The chat ID to filter for
        main_user: The username for the main user (messages will be shown on the right)
                  If None, the most active user will be used
        dropdown_configs: Configuration for HTML dropdowns
                         If None, sample configurations will be used
        output_dir: Directory to output HTML files (optional)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse the group chat file
    messages = parse_group_chat(file_path)
    print(f"Parsed {len(messages)} messages from {file_path}")
    
    if not messages:
        print("No messages found in file.")
        return
    
    # Use default configurations if none provided
    if dropdown_configs is None:
        dropdown_configs = get_sample_configs()
    
    # If main_user is not specified, use the most active user in the chat
    if not main_user:
        main_user = find_most_active_user(messages, chat_id)
        if main_user:
            print(f"Using '{main_user}' as the main user (messages shown on right)")
        else:
            print("Could not determine a main user.")
            # If no main user found, use the first sender in the filtered messages
            chat_messages = [msg for msg in messages if msg.get('chat_id') == chat_id]
            if chat_messages:
                main_user = chat_messages[0].get('sender_alias', '')
                print(f"Using first sender '{main_user}' as the main user")
        chat_messages = [msg for msg in messages if msg.get('chat_id') == chat_id]
        print(f"Filtered {len(chat_messages)} messages for chat_id: {chat_id}")
    # Generate HTML file
    safe_chat_id = ''.join(c for c in chat_id if c.isalnum() or c in '_-')
    html_file = os.path.join(output_dir, f'group_chat_{safe_chat_id}.html')
    group_chat_to_html(messages, chat_id, main_user, html_file, dropdown_configs)


def get_sample_configs():
    """
    Returns sample dropdown configurations
    """
    # Example 1: A nested dependent dropdown (dictionary of lists)
    intention_config = {
        'name': 'intention',
        'options': {
            "Personal": [
                "Sharing info",
                "Asking question", 
                "Social invitation"
            ],
            "Work": [
                "Task assignment",
                "Status update",
                "Meeting coordination"
            ]
        },
        'label': 'Intention'
    }
    
    # Example 2: A simple flat dropdown (just a list)
    tone_config = {
        'name': 'tone',
        'options': [
            "Happy", "Sad", "Urgent", "Casual", "Formal"
        ],
        'label': 'Tone'
    }
    
    # Combine all configurations
    return [intention_config, tone_config]


# Main execution
if __name__ == "__main__":
    import argparse
    import sys
    
    # Terminal execution
    parser = argparse.ArgumentParser(description='Process group chat log files and generate HTML conversation views')
    parser.add_argument('--file', required=True, help='Path to group chat log file')
    parser.add_argument('--chat_id', required=True, help='Chat ID to filter for')
    parser.add_argument('--main_user', default=None, help='Main user (messages shown on the right). If not specified, most active user will be used')
    parser.add_argument('--output', default='./output_html', help='Directory to output HTML file')
    parser.add_argument('--config', default='sample', help='Path to dropdown configuration file (JSON) or "sample" for default configs')
    
    args = parser.parse_args()
    
    # Get dropdown configurations
    if args.config == 'sample':
        dropdown_configs = get_sample_configs()
    else:
        with open(args.config, 'r') as f:
            dropdown_configs = json.load(f)
    
    # Process group chat
    process_group_chat(
        args.file,
        args.chat_id,
        args.main_user,
        dropdown_configs,
        args.output
    )
    
    print(f"Generated HTML file in {args.output}")