import json
import pandas as pd

def conversation_to_html(conversation_turns, user_i, user_j, html_file):
    """
    Creates an HTML file from a conversation history between two users (user_i and user_j)
    based on a conversation_turns dictionary. For each turn, three control categories are added:
      - Category 1 (Intention + Detailed):
            * A primary dropdown for Intention.
            * A dependent control (dropdown or text input when "Other" is selected).
            * An "Add Intention" button to clone the entire group.
      - Category 2 (Expressing Tone/Emotion):
            * A primary dropdown for Tone.
            * An "Add Tone" button to clone the dropdown inline.
      - Category 3: Role Indicators (dropdown with an inline Add button)

    When the user clicks the "Download" button, selections for each turn (with unit and turn indices)
    are gathered and stored in a CSV. For Category 1, if a manual entry is provided (in the Other field)
    it replaces the dependent answer in the CSV. Category 2 now only uses the primary dropdown.
    """
    # Retrieve conversation from conversation_turns.
    if (user_i, user_j) in conversation_turns:
        units = conversation_turns[(user_i, user_j)]
    elif (user_j, user_i) in conversation_turns:
        units = conversation_turns[(user_j, user_i)]
    else:
        print(f"No conversation found between {user_i} and {user_j}.")
        return

    # Dropdown options.
    options_dd1 = ["PERSONAL", "WORK Coordination", "WORK Help & Advice", "WORK Information Flow",
                   "Small Talk", "Ping", "Humor", "SHOW ENGAGEMENT (REACTION)", "Other"]
    options_dd2 = ["Excitement", "Gratitude", "Apology", "Frustration", "Politeness", "Hedging", "Support", "Command"]
    options_dd3 = ["Formal Addressing", "Informal Addressing", "Relative Role (Above)",
                   "Relative Role (Below)", "Real Name"]

    # Mapping for Category 1 (Intention) – single dependency level.
    dependent_mapping_dd1 = {
        "PERSONAL": [
            "Inquire for Personal Info/Opinion",
            "Sharing Personal Info",
            "Personal Favor & Reguest for Advice",
            "Sharing Opinion (Non-Work)/Suggestions & Well-Wishes",
            "Gossiping",
            "Social Invitation",
            "ELABORATION (Request for ELABORATION)"
        ],
        "WORK Coordination": [
            "Work Request/Order",
            "Work Request/Order Acceptance",
            "Request for Approval",
            "Request Status Update (TEAM)",
            "Status Report (TEAM)",
            "Request Status Update (INDIVIDUAL)",
            "Status Report (INDIVIDUAL)"
        ],
        "WORK Help & Advice": [
            "Request for Help/Advice",
            "Provision of Help/Advice",
            "Acceptance of Request for Help/Advice",
            "ELABORATION (Request for ELABORATION)"
        ],
        "WORK Information Flow": [
            "Inquire for Information",
            "Information Passing",
            "File sharing",
            "Provision of Knowledge",
            "Sharing Opinion (Work)",
            "ELABORATION (Request for ELABORATION)"
        ]
    }

    def generate_options(options):
        opts = '<option value="">--None--</option>\n'
        for opt in options:
            opts += f'<option value="{opt}">{opt}</option>\n'
        return opts

    csv_filename = f"conversation_{user_i}_{user_j}_coded.csv"

    # Begin HTML content.
    # NOTE: The CSS below highlights only the Intention (Category 1) area.
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
    /* Category-group styling for all categories */
    .category-group, .dropdown-group-container {{
        padding: 5px;
        margin-bottom: 5px;
    }}
    /* Highlight Category 1 (Intention) only */
    .category-group[data-cat="1"] {{
        border: 2px solid #f39c12;
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
<script>
var user_i = "{user_i}";
var user_j = "{user_j}";

// Mapping variables for Category 1 (Intention).
var intentionMapping = {json.dumps(dependent_mapping_dd1)};
// Category 2 now has no dependent mapping.
</script>
"""

    cumulative_turn = 1
    # Build conversation turns with the dropdowns.
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
            # --- Category 1: Intention + Detailed (Only 1 dependency level now) ---
            html += f'<div class="category-group" data-cat="1" data-unit="{unit_idx}" data-turn="{turn_idx}">\n'
            # Primary dropdown.
            html += '<div class="dropdown-group" data-dd="1">\n'
            html += '<label>Intention: </label>\n'
            html += '<select class="turn-dropdown" data-dd="1">\n'
            html += generate_options(options_dd1)
            html += '</select>\n'
            html += '</div>\n'
            # Dependent dropdown for Detailed.
            html += '<div class="dropdown-group" data-dd="dep" style="display:none;">\n'
            html += '<label>Detailed: </label>\n'
            html += '<select class="dependent-dropdown" data-dd="dep">\n'
            html += '<option value="">--Select--</option>\n'
            html += '</select>\n'
            html += '</div>\n'
            # Input field for Other.
            html += '<div class="dropdown-group" data-dd="other" style="display:none;">\n'
            html += '<label>Please specify: </label>\n'
            html += '<input type="text" class="other-input" data-dd="other" />\n'
            html += '</div>\n'
            html += '<button type="button" class="add-button" data-cat="1">Add Intention</button>\n'
            html += '</div>\n'
            # --- Category 2: Expressing Tone/Emotion (Only Primary Dropdown) ---
            html += f'<div class="dropdown-group-container" data-cat="2" data-unit="{unit_idx}" data-turn="{turn_idx}">\n'
            html += '<div class="dropdown-group" data-dd="2">\n'
            html += '<label>Tone/Emotion: </label>\n'
            html += '<select class="turn-dropdown" data-dd="2">\n'
            html += generate_options(options_dd2)
            html += '</select>\n'
            html += '</div>\n'
            html += '<button type="button" class="add-button" data-cat="2">Add Tone</button>\n'
            html += '</div>\n'
            # --- Category 3: Role Indicators ---
            html += f'<div class="dropdown-group-container" data-cat="3" data-unit="{unit_idx}" data-turn="{turn_idx}">\n'
            html += '<div class="dropdown-group" data-dd="3">\n'
            html += '<label>Role Indicators: </label>\n'
            html += '<select class="turn-dropdown" data-dd="3">\n'
            html += generate_options(options_dd3)
            html += '</select>\n'
            html += '</div>\n'
            html += '<button type="button" class="add-button" data-cat="3">Add Role</button>\n'
            html += '</div>\n'
            html += '</div>\n'  # End of dropdown-container.
            html += '</div>\n'  # End of turn div.
            cumulative_turn += 1

    html += '<div class="clear"></div>\n'
    # Download CSV button.
    html += f"""
<button class="download-button" id="downloadCSVButton">Download</button>

<script>
// --- Primary Dropdown Change for Category 1 (Intention) ---
document.addEventListener('change', function(e) {{
    if (e.target && e.target.matches('select[data-dd="1"]')) {{
        var selected = e.target.value;
        var catGroup = e.target.closest('.category-group');
        if (!catGroup) return;
        var depGroup = catGroup.querySelector('.dropdown-group[data-dd="dep"]');
        var otherGroup = catGroup.querySelector('.dropdown-group[data-dd="other"]');
        var depSelect = depGroup.querySelector('select');
        if (selected) {{
            if (selected === "Other") {{
                depGroup.style.display = "none";
                otherGroup.style.display = "inline-block";
            }} else if (intentionMapping[selected]) {{
                otherGroup.style.display = "none";
                depSelect.innerHTML = '<option value="">--Select--</option>';
                intentionMapping[selected].forEach(function(opt) {{
                    var option = document.createElement("option");
                    option.value = opt;
                    option.text = opt;
                    depSelect.appendChild(option);
                }});
                depGroup.style.display = "inline-block";
            }} else {{
                depGroup.style.display = "none";
                otherGroup.style.display = "none";
                depSelect.innerHTML = '<option value="">--Select--</option>';
            }}
        }} else {{
            depGroup.style.display = "none";
            otherGroup.style.display = "none";
            depSelect.innerHTML = '<option value="">--Select--</option>';
        }}
    }}
}});

// --- Dynamic Add Button Functionality ---
// For Category 1, clone the entire container; for Category 2 and 3, clone only the dropdown-group and insert inline.
document.querySelectorAll('.add-button').forEach(function(button) {{
    button.addEventListener('click', function() {{
        var cat = this.getAttribute("data-cat");
        if (cat === "1") {{
            var container = this.parentElement;
            var clone = container.cloneNode(true);
            clone.querySelectorAll('select, input').forEach(function(elem) {{
                elem.value = "";
                elem.removeAttribute('id');
            }});
            container.parentElement.appendChild(clone);
        }} else if (cat === "2" || cat === "3") {{
            var container = this.parentElement;
            var originalGroup = container.querySelector('.dropdown-group');
            var clone = originalGroup.cloneNode(true);
            clone.querySelectorAll('select, input').forEach(function(elem) {{
                elem.value = "";
                elem.removeAttribute('id');
            }});
            container.insertBefore(clone, this);
        }}
    }});
}});

// --- CSV Download Functionality ---
document.getElementById("downloadCSVButton").addEventListener("click", function() {{
    var csvRows = [];
    csvRows.push("Unit,Turn,Intention,Detailed,Tone,Role Indicators");
    var turnDivs = document.querySelectorAll(".turn");
    turnDivs.forEach(function(turnDiv) {{
        var unit = turnDiv.getAttribute("data-unit") || "";
        var turn = turnDiv.getAttribute("data-turn") || "";
        // Category 1: Intention and Detailed.
        var cat1Groups = turnDiv.querySelectorAll('.category-group[data-cat="1"]');
        var intentionVals = [];
        var detailedVals = [];
        cat1Groups.forEach(function(group) {{
            var primary = group.querySelector('select[data-dd="1"]');
            if (primary && primary.value.trim() !== "") {{
                intentionVals.push(primary.value.trim());
            }}
            var detail = "";
            var depSel = group.querySelector('.dropdown-group[data-dd="dep"] select');
            var otherInp = group.querySelector('.dropdown-group[data-dd="other"] input');
            if (otherInp && otherInp.style.display !== "none" && otherInp.value.trim() !== "") {{
                detail = otherInp.value.trim();
            }} else if (depSel && depSel.style.display !== "none" && depSel.value.trim() !== "") {{
                detail = depSel.value.trim();
            }}
            if (detail !== "") {{
                detailedVals.push(detail);
            }}
        }});
        // Category 2: Tone (only primary dropdown).
        var cat2Container = turnDiv.querySelector('[data-cat="2"]');
        var toneVal = "";
        if (cat2Container) {{
            var primaryTone = cat2Container.querySelector('select[data-dd="2"]');
            if (primaryTone && primaryTone.value.trim() !== "") {{
                toneVal = primaryTone.value.trim();
            }}
        }}
        // Category 3: Role Indicators.
        function getGroupValues(category) {{
            var groups = turnDiv.querySelectorAll('.dropdown-group[data-dd="' + category + '"]');
            var vals = [];
            groups.forEach(function(g) {{
                var elems = g.querySelectorAll('select, input');
                elems.forEach(function(elem) {{
                    if (elem.value && elem.value.trim() !== "") {{
                        vals.push(elem.value.trim());
                    }}
                }});
            }});
            return vals.join(";");
        }}
        var roleVal = getGroupValues("3");
        csvRows.push(unit + "," + turn + "," + intentionVals.join(";") + "," + detailedVals.join(";") + "," + toneVal + "," + roleVal);
    }});
    var csvContent = "data:text/csv;charset=utf-8," + csvRows.join("\\n");
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "conversation_" + user_i + "_" + user_j + "_coded.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}});
</script>

</body>
</html>
"""
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML file '{html_file}' created successfully.")

# Example usage:
# Users Test: baget and hof, baget and bentley, etc.
user1 = 'bentley'
user2 = 'mavemat'
filename = 'conversation_history_' + user1 + '_' + user2 + '.html'
conversation_to_html(conversation_turns, user1, user2, filename)
# conversation_to_html(conversation_turns, 'baget', 'bentley', "conversation_history_baget_bentley.html")

# read pickle file
def read_pickle(file_path):
    return pd.read_pickle(file_path)

conversation_turns_file = 'Qualitative_Coding/conversation_turns.pkl'
conversation_turns = read_pickle(conversation_turns_file)