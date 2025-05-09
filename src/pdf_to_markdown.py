import os
import warnings
import time
import re
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from docling.document_converter import DocumentConverter

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")

def get_file_size(file_path):
    """Get file size in a human-readable format"""
    size_bytes = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def analyze_markdown_structure(file_path):
    """Analyze markdown file structure and suggest embedding parameters"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analyze content
    total_chars = len(content)
    total_words = len(content.split())
    total_paragraphs = len(re.split(r'\n\s*\n', content))
    total_sections = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
    
    # Calculate average paragraph length
    paragraphs = re.split(r'\n\s*\n', content)
    avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # Suggest chunk size based on content analysis
    if avg_paragraph_length < 50:
        chunk_size = 512
        overlap = 128
    elif avg_paragraph_length < 100:
        chunk_size = 1024
        overlap = 256
    else:
        chunk_size = 2048
        overlap = 512
    
    # Analyze content type
    has_code_blocks = bool(re.search(r'```[\s\S]*?```', content))
    has_tables = bool(re.search(r'\|[\s\S]*?\|', content))
    has_lists = bool(re.search(r'^[\s]*[-*+]\s+', content, re.MULTILINE))
    
    # Generate recommendations
    recommendations = {
        "content_stats": {
            "total_chars": total_chars,
            "total_words": total_words,
            "total_paragraphs": total_paragraphs,
            "total_sections": total_sections,
            "avg_paragraph_length": round(avg_paragraph_length, 2)
        },
        "embedding_params": {
            "suggested_chunk_size": chunk_size,
            "suggested_overlap": overlap,
            "content_type": {
                "has_code_blocks": has_code_blocks,
                "has_tables": has_tables,
                "has_lists": has_lists
            }
        },
        "recommendations": []
    }
    
    # Add specific recommendations
    if has_code_blocks:
        recommendations["recommendations"].append(
            "Consider using a smaller chunk size for code blocks to maintain context"
        )
    if has_tables:
        recommendations["recommendations"].append(
            "Ensure chunk size is large enough to capture complete tables"
        )
    if has_lists:
        recommendations["recommendations"].append(
            "Consider splitting at list boundaries to maintain list context"
        )
    
    return recommendations

def convert_pdfs_to_markdown():
    start_time = time.time()
    
    # Define paths
    docs_dir = Path("docs")
    knowledge_base_dir = Path("docs/knowledge_base")
    
    # Ensure knowledge_base directory exists
    knowledge_base_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Get all PDF files from docs directory
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    log_message(f"Found {len(pdf_files)} PDF files to process")
    log_message(f"Source directory: {docs_dir.absolute()}")
    log_message(f"Destination directory: {knowledge_base_dir.absolute()}")
    
    # Process each PDF file with progress bar
    for pdf_file in tqdm(pdf_files, desc="Converting PDFs", unit="file"):
        try:
            file_size = get_file_size(pdf_file)
            log_message(f"Processing {pdf_file.name} ({file_size})...")
            
            # Convert PDF to Docling document
            result = converter.convert(str(pdf_file))
            
            # Generate markdown content
            markdown_content = result.document.export_to_markdown()
            
            # Create output filename
            output_file = knowledge_base_dir / f"{pdf_file.stem}.md"
            
            # Save markdown content
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            log_message(f"Successfully converted {pdf_file.name} to {output_file.name}")
            
            # Analyze the generated markdown file
            log_message(f"\nAnalyzing {output_file.name} for embedding recommendations:")
            analysis = analyze_markdown_structure(output_file)
            
            # Log content statistics
            stats = analysis["content_stats"]
            log_message(f"\nContent Statistics:")
            log_message(f"- Total characters: {stats['total_chars']}")
            log_message(f"- Total words: {stats['total_words']}")
            log_message(f"- Total paragraphs: {stats['total_paragraphs']}")
            log_message(f"- Total sections: {stats['total_sections']}")
            log_message(f"- Average paragraph length: {stats['avg_paragraph_length']} words")
            
            # Log embedding parameters
            params = analysis["embedding_params"]
            log_message(f"\nSuggested Embedding Parameters:")
            log_message(f"- Chunk size: {params['suggested_chunk_size']}")
            log_message(f"- Overlap: {params['suggested_overlap']}")
            
            # Log content type analysis
            content_type = params["content_type"]
            log_message(f"\nContent Type Analysis:")
            log_message(f"- Contains code blocks: {content_type['has_code_blocks']}")
            log_message(f"- Contains tables: {content_type['has_tables']}")
            log_message(f"- Contains lists: {content_type['has_lists']}")
            
            # Log recommendations
            if analysis["recommendations"]:
                log_message(f"\nSpecific Recommendations:")
                for rec in analysis["recommendations"]:
                    log_message(f"- {rec}")
            
            log_message("\n" + "="*80 + "\n")
            
        except Exception as e:
            log_message(f"Error processing {pdf_file.name}: {str(e)}")
            log_message("Continuing with next file...")
    
    # Calculate and display total processing time
    end_time = time.time()
    total_time = end_time - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    log_message(f"Total processing time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    log_message(f"Processed {len(pdf_files)} files")

if __name__ == "__main__":
    try:
        convert_pdfs_to_markdown()
    except Exception as e:
        log_message(f"An error occurred: {str(e)}") 