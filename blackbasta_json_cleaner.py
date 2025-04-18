import json
import re
import os
import argparse
from typing import List, Dict, Any, Union

def clean_matrix_json(input_file: str, output_file: str = None) -> List[Dict[str, Any]]:
    """
    Clean a Matrix chat JSON file by:
    1. Stripping server parts from chat_id and sender_alias
    2. Removing @ prefix from usernames
    3. Handling quoted strings
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to save cleaned JSON (if None, doesn't save to file)
        
    Returns:
        List of cleaned message dictionaries
    """
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure the data is a list
        if not isinstance(data, list):
            print(f"Warning: Expected a list of messages, got {type(data)}. Attempting to process anyway.")
            if isinstance(data, dict):
                data = [data]
            else:
                raise ValueError("Input data is not a list or dictionary")
        
        # Clean each message
        cleaned_data = []
        for msg in data:
            cleaned_msg = msg.copy()  # Create a copy to avoid modifying the original
            
            # Clean chat_id
            if 'chat_id' in msg:
                chat_id = msg['chat_id']
                # Remove quotes
                chat_id = chat_id.replace('"', '')
                # Extract the room ID part (before the server)
                match = re.search(r'!([\w\d]+)', chat_id)
                if match:
                    cleaned_msg['chat_id'] = f"!{match.group(1)}"
                else:
                    # Keep original if no match
                    cleaned_msg['chat_id'] = chat_id
            
            # Clean sender_alias
            if 'sender_alias' in msg:
                sender = msg['sender_alias']
                # Remove quotes
                sender = sender.replace('"', '')
                # Extract the username part (after @ and before :)
                match = re.search(r'@?([\w\d_-]+)', sender)
                if match:
                    cleaned_msg['sender_alias'] = match.group(1)
                else:
                    # Keep original if no match
                    cleaned_msg['sender_alias'] = sender
            
            cleaned_data.append(cleaned_msg)
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
                print(f"Cleaned data saved to {output_file}")
        
        return cleaned_data
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Error processing file: {e}")
        return []


def batch_clean_matrix_json(input_dir: str, output_dir: str, file_pattern: str = "*.json"):
    """
    Process multiple JSON files in a directory
    
    Args:
        input_dir: Directory containing input JSON files
        output_dir: Directory to save cleaned JSON files
        file_pattern: Pattern to match JSON files
    """
    import glob
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all matching files
    file_paths = glob.glob(os.path.join(input_dir, file_pattern))
    
    if not file_paths:
        print(f"No files matching '{file_pattern}' found in {input_dir}")
        return
    
    print(f"Found {len(file_paths)} files to process")
    
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_dir, f"cleaned_{file_name}")
        
        print(f"Processing {file_name}...")
        messages = clean_matrix_json(file_path, output_path)
        print(f"Processed {len(messages)} messages")


def print_summary(messages: List[Dict[str, Any]]):
    """
    Print a summary of the cleaned messages
    
    Args:
        messages: List of message dictionaries
    """
    if not messages:
        print("No messages to summarize")
        return
    
    # Count unique chat rooms
    chat_rooms = set()
    users = set()
    
    for msg in messages:
        if 'chat_id' in msg:
            chat_rooms.add(msg['chat_id'])
        if 'sender_alias' in msg:
            users.add(msg['sender_alias'])
    
    print("\nSummary:")
    print(f"Total messages: {len(messages)}")
    print(f"Unique chat rooms: {len(chat_rooms)}")
    print(f"Unique users: {len(users)}")
    
    if chat_rooms:
        print("\nChat rooms:")
        for room in sorted(chat_rooms):
            room_messages = [msg for msg in messages if msg.get('chat_id') == room]
            print(f"  {room}: {len(room_messages)} messages")
    
    if users:
        print("\nUsers:")
        for user in sorted(users):
            user_messages = [msg for msg in messages if msg.get('sender_alias') == user]
            print(f"  {user}: {len(user_messages)} messages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean Matrix chat JSON files')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('--output', '-o', help='Output JSON file or directory (default: cleaned_[input])')
    parser.add_argument('--batch', '-b', action='store_true', help='Process all JSON files in the input directory')
    parser.add_argument('--pattern', '-p', default="*.json", help='File pattern for batch mode (default: *.json)')
    parser.add_argument('--summary', '-s', action='store_true', help='Print summary of cleaned messages')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch mode
        input_dir = args.input
        output_dir = args.output or "cleaned_" + os.path.basename(input_dir.rstrip('/\\'))
        batch_clean_matrix_json(input_dir, output_dir, args.pattern)
    else:
        # Single file mode
        input_file = args.input
        output_file = args.output or "cleaned_" + os.path.basename(input_file)
        
        messages = clean_matrix_json(input_file, output_file)
        
        if args.summary:
            print_summary(messages)