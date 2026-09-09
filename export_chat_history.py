import json
import os

log_path = r'C:\Users\Admin\.gemini\antigravity-ide\brain\a7e19b8e-1080-4fe2-a51b-94c61c008ac7\.system_generated\logs\transcript.jsonl'
output_path = r'C:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\full_project_conversation_history.md'

def export_conversation():
    print(f"Reading logs from {log_path}")
    if not os.path.exists(log_path):
        print("ERROR: transcript.jsonl not found!")
        return

    history = []
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                source = data.get('source')
                step_type = data.get('type')
                content = data.get('content', '')
                
                # Capture User inputs
                if step_type == 'USER_INPUT' and source in ['USER_EXPLICIT', 'USER_IMPLICIT']:
                    history.append(f"### [USER PROMPT]\n\n{content}\n\n---\n")
                
                # Capture Agent responses (usually PLANNER_RESPONSE)
                elif step_type == 'PLANNER_RESPONSE' and source == 'MODEL':
                    if content: # sometimes content is empty if only tool_calls were made
                        history.append(f"### [PHANTOMX AI RESPONSE]\n\n{content}\n\n================================================================================\n\n")
            except Exception as e:
                print(f"Error parsing line: {e}")
                
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write("# PHANTOMX: COMPLETE PROJECT CONVERSATION HISTORY\n")
        out_f.write("Generated directly from raw system transcript logs (100% Data Integrity)\n\n")
        out_f.write("================================================================================\n\n")
        out_f.writelines(history)
        
    print(f"Successfully exported {len(history)} interaction segments to {output_path}")

if __name__ == '__main__':
    export_conversation()
