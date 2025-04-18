import json
from typing import Dict, List, Union, Any, Tuple

def conversation_to_html_generalized(
    conversation_turns: Dict, 
    user_i: str, 
    user_j: str, 
    html_file: str,
    dropdown_configs: List[Dict[str, Any]]
):
    """
    Creates an HTML file from a conversation history with flexible dropdown configurations.
    
    Args:
        conversation_turns: Dictionary of conversation turns
        user_i: First user ID
        user_j: Second user ID
        html_file: Output HTML file path
        dropdown_configs: List of dictionaries defining dropdown configurations
            Each config must have:
            - 'name': Name of the dropdown category
            - 'options': Either a list for simple dropdown or a dict for dependent dropdown
            - 'label': Label to display
            Optional keys:
            - 'button_text': Text for the add button (defaults to "Add {label}")
            - 'csv_column': Name of the column in CSV output (defaults to label)
    """
    # Process configuration to add defaults for optional fields
    for config in dropdown_configs:
        if 'button_text' not in config:
            config['button_text'] = f"Add {config['label']}"
        if 'csv_column' not in config:
            config['csv_column'] = config['label']
            
    # Retrieve conversation from conversation_turns.
    if (user_i, user_j) in conversation_turns:
        units = conversation_turns[(user_i, user_j)]
    elif (user_j, user_i) in conversation_turns:
        units = conversation_turns[(user_j, user_i)]
    else:
        print(f"No conversation found between {user_i} and {user_j}.")
        return

    def generate_options(options):
        opts = '<option value="">--None--</option>\n'
        for opt in options:
            opts += f'<option value="{opt}">{opt}</option>\n'
        return opts

    csv_filename = f"conversation_{user_i}_{user_j}_coded.csv"
    
    # Prepare CSV header
    csv_header = ["Unit", "Turn"]
    for config in dropdown_configs:
        csv_header.append(config['csv_column'])
        if isinstance(config['options'], dict):
            csv_header.append(f"{config['csv_column']}_Detailed")
    
    # Begin HTML content
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Conversation: {user_i} and {user_j}</title>
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
<h2>Conversation: {user_i} & {user_j}</h2>
<div class="clearfix" id="content">
"""

    # JavaScript for dependent dropdowns
    html += f"""
<script>
// User variables
var user_i = "{user_i}";
var user_j = "{user_j}";

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
            var unit = turnDiv.getAttribute("data-unit") || "";
            var turn = turnDiv.getAttribute("data-turn") || "";
            var row = [unit, turn];
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
        link.setAttribute("download", "conversation_"""

    html += f"{user_i}_{user_j}_coded.csv"
    
    html += """");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});
</script>
"""

    # Build conversation turns with the dropdowns
    cumulative_turn = 1
    for unit_idx, unit in enumerate(units):
        for turn_idx, turn in enumerate(unit):
            if not turn:
                continue
            turn_sender = turn[0][1]
            alignment = "right" if turn_sender == user_i else "left"
            html += f'<div class="turn {alignment}" data-unit="{unit_idx}" data-turn="{turn_idx}">\n'
            html += f'<strong>Turn {cumulative_turn} ({turn_sender}):</strong><br>\n'
            for msg in turn:
                timestamp = msg[0]
                message_text = msg[3]
                html += f'<div class="message"><span class="timestamp">{timestamp}</span> - <span class="text">{message_text}</span></div>\n'
            html += '<div class="dropdown-container">\n'
            
            # Generate dropdowns based on configurations
            for i, config in enumerate(dropdown_configs):
                cat_id = i + 1
                is_dependent = isinstance(config['options'], dict)
                container_class = "category-group" if is_dependent else "dropdown-group-container"
                
                html += f'<div class="{container_class}" data-cat="{cat_id}" data-unit="{unit_idx}" data-turn="{turn_idx}">\n'
                
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
            cumulative_turn += 1

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


def all_conversations_sorted_with_turns_and_html(
    conti_chats: List[str], 
    user_match_list: str,
    dropdown_configs: List[Dict[str, Any]] = None,
    output_users: List[Tuple[str, str]] = None,
    output_dir: str = "./"
) -> Dict:
    """
    Process chat log files, sort conversations, segment them by date and speaking turns,
    and optionally generate HTML files for specified user pairs.
    
    Args:
        conti_chats: List of file paths to chat log JSON files
        user_match_list: Path to the JSON file containing user alias mappings
        dropdown_configs: Configuration for HTML dropdowns (optional)
        output_users: List of user pairs to generate HTML for (optional)
        output_dir: Directory to output HTML files (optional)
        
    Returns:
        Dictionary of conversation segments split by date and then into speaking turns
    """
    # First, process all conversations and get turns
    import json
    import dateutil.parser
    import os
    import argparse
    from typing import List, Dict, Any, Tuple
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Step 0: Load alias mapping from the provided JSON file
    try:
        with open(user_match_list, "r") as f:
            alias_list = json.load(f)
    except Exception as e:
        print(f"Failed to load alias mapping from {user_match_list}: {e}")
        alias_list = []
    
    # Build a dictionary mapping each alias (and primary) to its canonical primary name
    alias_mapping = {}
    for entry in alias_list:
        primary = entry.get('primary')
        if primary:
            alias_mapping[primary] = primary  # Map the primary to itself
            for alias in entry.get('aliases', []):
                alias_mapping[alias] = primary

    # Step 1: Count messages in JSON log files
    structured_messages = {}  # dict to store conversations
    initial_count = 0
    
    # Process each chat log file directly
    for file_path in conti_chats:
        if os.path.exists(file_path):
            with open(file_path) as f:
                json_data = json.load(f)
            
            for item in json_data:
                if 'ts' in item:
                    item['ts'] = dateutil.parser.isoparse(item['ts'])  # ISO 8601 extended format
            
            logs = json_data
            initial_count += len(logs)
            
            for i in logs:
                # Get raw sender/receiver values from the log
                sender = i['from']
                receiver = i['to']

                # Normalize using alias mapping if the name is an alias
                sender_canonical = alias_mapping.get(sender, sender)
                receiver_canonical = alias_mapping.get(receiver, receiver)

                # Use sorted keys for uniqueness (order-independent conversation key)
                key1, key2 = sorted([sender_canonical, receiver_canonical])
                if key1 not in structured_messages:
                    structured_messages[key1] = {}
                if key2 not in structured_messages[key1]:
                    structured_messages[key1][key2] = []
                structured_messages[key1][key2].append((i['ts'], sender_canonical, receiver_canonical, i['body']))
        else:
            print(f"Warning: File not found: {file_path}")
    
    # Step 2: Count messages in structured_messages
    processed_count = sum(len(convo) for user in structured_messages.values() for convo in user.values())
    print(f"Total processed message count: {processed_count}")

    # Sorting each conversation by time (assuming timestamp is the first tuple element)
    for user in structured_messages.keys():
        for convo in structured_messages[user].keys():
            structured_messages[user][convo].sort(key=lambda x: x[0])

    if initial_count != processed_count:
        print(f"Mismatch detected! Initial count: {initial_count}, Processed count: {processed_count}")
    
    # Step 3: Segment conversations by date
    conversation_segments = {}

    for user_i, threads in structured_messages.items():
        for user_j, messages in threads.items():
            # Group messages by date
            conversation_units = defaultdict(list)
            for msg in messages:
                msg_date = msg[0].date()  # Extract the date from the timestamp
                conversation_units[msg_date].append(msg)

            # Store the segmented conversation
            conversation_segments[(user_i, user_j)] = list(conversation_units.values())
    
    print(f'Total number of conversation histories {len(conversation_segments)}')
    
    # Step 4: Split into speaking turns
    conversation_turns = {}

    # Iterate over each conversation identified by a pair (user_i, user_j)
    for (user_i, user_j), units in conversation_segments.items():
        new_units = []  # For storing all turn-split units within this conversation

        for unit in units:
            if not unit:
                continue  # Skip empty units if any

            current_turn = [unit[0]]  # Start with the first message in the unit
            turns = []

            # Go through each subsequent message in the unit
            for i in range(1, len(unit)):
                curr_msg = unit[i]
                prev_msg = unit[i - 1]
                
                # Check if the sender has changed OR if the time difference is more than 30 minutes.
                if curr_msg[1] != prev_msg[1] or ((curr_msg[0] - prev_msg[0]).total_seconds() > 1800):
                    # Save the finished turn and start a new one.
                    turns.append(current_turn)
                    current_turn = [curr_msg]
                else:
                    # Same sender and less than 30 minutes apart: continue the same turn.
                    current_turn.append(curr_msg)

            # Append the final current turn for this unit.
            if current_turn:
                turns.append(current_turn)

            new_units.append(turns)

        conversation_turns[(user_i, user_j)] = new_units
    
    # Step 5: Generate HTML files if requested
    if output_users and dropdown_configs:
        os.makedirs(output_dir, exist_ok=True)
        for user_i, user_j in output_users:
            html_file = os.path.join(output_dir, f'conversation_history_{user_i}_{user_j}.html')
            conversation_to_html_generalized(
                conversation_turns, 
                user_i, 
                user_j, 
                html_file,
                dropdown_configs
            )
    
    return conversation_turns


# Example usage with predefined dropdown configurations
if __name__ == "__main__":
    import argparse
    import sys
    import os
    
    # Define a function to create sample dropdown configurations
    def get_sample_configs():
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
            # button_text and csv_column will be auto-generated
        }
        
        # Example 2: A simple flat dropdown (just a list)
        tone_config = {
            'name': 'tone',
            'options': [
                "Happy", "Sad", "Urgent", "Casual", "Formal"
            ],
            'label': 'Tone'
            # button_text and csv_column will be auto-generated
        }
        
        # Combine all configurations
        return [intention_config, tone_config]
    
    # Check if script is run from terminal
    if len(sys.argv) > 1:
        # Terminal execution
        parser = argparse.ArgumentParser(description='Process chat log files and generate HTML conversation views')
        parser.add_argument('--files', nargs='+', required=True, help='Paths to chat log JSON files')
        parser.add_argument('--aliases', required=True, help='Path to user alias mapping JSON file')
        parser.add_argument('--users', nargs='+', help='User pairs to generate HTML for (format: user1,user2)')
        parser.add_argument('--output', default='./output_html', help='Directory to output HTML files')
        parser.add_argument('--config', default='sample', help='Path to dropdown configuration file (JSON) or "sample" for default configs')
        
        args = parser.parse_args()
        
        # Process user pairs
        user_pairs = []
        if args.users:
            for pair in args.users:
                user1, user2 = pair.split(',')
                user_pairs.append((user1.strip(), user2.strip()))
        
        # Get dropdown configurations
        if args.config == 'sample':
            dropdown_configs = get_sample_configs()
        else:
            with open(args.config, 'r') as f:
                dropdown_configs = json.load(f)
        
        # Process conversations
        conversation_turns = all_conversations_sorted_with_turns_and_html(
            args.files,
            args.aliases,
            dropdown_configs=dropdown_configs,
            output_users=user_pairs,
            output_dir=args.output
        )
        
        print(f"Generated HTML files in {args.output}")
    
    else:
        # This section runs when imported in a notebook
        # It's just a placeholder - in a notebook, users will call functions directly
        print("Import complete. You can now use the following functions:")
        print("- all_conversations_sorted_with_turns_and_html(): Process logs and generate HTML")
        print("- conversation_to_html_generalized(): Create HTML for specific conversations")
        print("\nExample usage:")
        print("dropdown_configs = get_sample_configs()")
        print("conversation_turns = all_conversations_sorted_with_turns_and_html(")
        print("    ['path/to/chat_logs1.json'],")
        print("    'user_match_list.json',")
        print("    dropdown_configs=dropdown_configs,")
        print("    output_users=[('user1', 'user2')],")
        print("    output_dir='output_html'")
        print(")")
        
    # This makes the get_sample_configs function accessible when imported
    get_sample_configs = get_sample_configs