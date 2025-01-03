import json
from datetime import datetime

# Paths for input and output
input_path = r"C:\Users\robmo\OneDrive\Documents\evidenceai_test\output\OFW_Messages_Report_Dec\enriched_threads.json"
output_path = r"C:\Users\robmo\OneDrive\Documents\evidenceai_test\ab_tools_ChatGPT\outputs\timelines.json"

try:
    # Load enriched data
    with open(input_path, "r") as f:
        threads_data = json.load(f)

    # Generate timelines
    timelines = []

    for thread in threads_data:
        thread_id = thread.get("thread_id")
        messages = thread.get("messages", [])
        
        # Sort messages by timestamp
        sorted_messages = sorted(
            messages,
            key=lambda msg: datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
        )
        
        # Generate dynamic summary
        if sorted_messages:
            first_message = sorted_messages[0]["content"]
            last_message = sorted_messages[-1]["content"]
            tags = [tag for msg in sorted_messages for tag in msg.get("tags", [])]
            summary = f"Discussion about {first_message.lower()} and {last_message.lower()}, with tags: {', '.join(set(tags))}."
        else:
            summary = "No messages available in this thread."

        # Build timeline structure
        timeline = {
            "thread_id": thread_id,
            "timeline": [
                {
                    "timestamp": msg["timestamp"],
                    "author": msg["author"],
                    "content": msg["content"],
                    "tags": msg.get("tags", []),
                    "topics": msg.get("topics", [])
                }
                for msg in sorted_messages
            ],
            "summary": summary
        }
        timelines.append(timeline)

    # Save timelines to output file
    with open(output_path, "w") as f:
        json.dump(timelines, f, indent=2)

    print(f"Timelines generated and saved to {output_path}")

except FileNotFoundError as e:
    print(f"File not found: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
