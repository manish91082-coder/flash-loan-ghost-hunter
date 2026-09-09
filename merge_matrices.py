import os
import math

base_dir = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
input_dir = os.path.join(base_dir, 'blockchain_strategy_matrices')
output_dir = os.path.join(base_dir, 'merged_strategy_matrices')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def merge_files():
    # Get all markdown files
    files = [f for f in os.listdir(input_dir) if f.endswith('.md')]
    # Sort them by chain ID to keep it organized
    # Filename format: chain_ID_Name_strategy.md
    files.sort(key=lambda x: int(x.split('_')[1]))
    
    total_files = len(files)
    num_parts = 10
    
    # Calculate chunk size (ceiling division to ensure all files are included)
    chunk_size = math.ceil(total_files / num_parts)
    
    print(f"Total files: {total_files}")
    print(f"Chunk size: {chunk_size} files per part")
    
    for i in range(num_parts):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_files)
        
        chunk_files = files[start_idx:end_idx]
        if not chunk_files:
            break
            
        part_num = i + 1
        output_filename = f"PhantomX_Master_Strategy_Matrix_Part_{part_num}.md"
        output_filepath = os.path.join(output_dir, output_filename)
        
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            output_content = f"# PHANTOMX MASTER STRATEGY MATRIX - PART {part_num}\n"
            output_content += f"Contains Chain Data from file index {start_idx + 1} to {end_idx}\n\n"
            output_content += "---\n\n"
            outfile.write(output_content)
            
            for file in chunk_files:
                filepath = os.path.join(input_dir, file)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n\n---\n\n")
                    
        print(f"Created {output_filename} containing {len(chunk_files)} chains.")

    print(f"Merge Complete. Check the output directory: {output_dir}")

if __name__ == '__main__':
    merge_files()
