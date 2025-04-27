import os
import argparse
from PIL import Image
from reportlab.pdfgen import canvas
from effect import progress_bar

def convert_webp_to_jpg(webp_path):
    """Convert a WebP image to JPG and save it in the same folder."""
    try:
        # Open the WebP image
        img = Image.open(webp_path)
        
        # Create the output JPG filename (same name, different extension)
        jpg_path = os.path.splitext(webp_path)[0] + '.jpg'
        
        # If image has transparency (RGBA), convert to RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        # Save as JPG
        img.save(jpg_path, 'JPEG', quality=90)
        
        return jpg_path
    except Exception as e:
        print(f"  Error converting {webp_path} to JPG: {e}")
        return None

def convert_images_to_pdf(folder_path):
    """Convert all images in a folder to a single PDF file named after the folder."""
    # Get folder name for PDF filename
    folder_name = os.path.basename(os.path.normpath(folder_path))
    pdf_filename = f"{folder_name}.pdf"
    output_path = os.path.join(os.path.dirname(folder_path), pdf_filename)
    
    # Get all image files in the folder
    image_files = []
    webp_files = []
    standard_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    
    # First scan for all image files, separating WebP files
    for file in sorted(os.listdir(folder_path)):
        file_lower = file.lower()
        file_path = os.path.join(folder_path, file)
        
        if file_lower.endswith('.webp'):
            webp_files.append(file_path)
        elif any(file_lower.endswith(ext) for ext in standard_extensions):
            image_files.append(file_path)
    
    # Convert WebP files to JPG and add them to the image list
    converted_files = []
    for webp_file in webp_files:
        jpg_file = convert_webp_to_jpg(webp_file)
        if jpg_file:
            converted_files.append(jpg_file)
        progress_bar(len(converted_files), len(webp_files))
    
    print("\n")
    
    # Add converted files to the image list
    image_files.extend(converted_files)
    
    # Sort the combined list to ensure proper order
    image_files.sort()
    
    if not image_files:
        print(f"No image files found in {folder_path}")
        return None
    
    # Create PDF
    print(f"Creating PDF for {folder_name}...")
    
    # Get dimensions of first image for PDF setup
    first_img = Image.open(image_files[0])
    img_width, img_height = first_img.size
    
    # Create a PDF with reportlab
    c = canvas.Canvas(output_path, pagesize=(img_width, img_height))
    
    pgs = 0
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            # If image has transparency (RGBA), convert to RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Add image to PDF
            c.setPageSize((img.width, img.height))
            c.drawImage(img_path, 0, 0, width=img.width, height=img.height)
            c.showPage()
            pgs += 1
            progress_bar(pgs, len(image_files))
        except Exception as e:
            print(f"  Error processing {img_path}: {e}")
    
    # Save the PDF
    c.save()
    print(f"PDF saved as {output_path}")
    return output_path

def find_and_process_folders(parent_path, min_images=1):
    """Find all folders within parent_path and process them."""
    results = []
    
    print(f"Scanning {parent_path} for folders with images...")
    
    # Walk through all directories in the parent path
    for root, dirs, files in os.walk(parent_path):
        # Skip the parent directory itself
        if root == parent_path:
            continue
        
        # Count image files in this directory
        image_count = 0
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        
        for file in files:
            file_lower = file.lower()
            if any(file_lower.endswith(ext) for ext in valid_extensions):
                image_count += 1
        
        # Process this directory if it has enough images
        if image_count >= min_images:
            print(f"\nFound folder with {image_count} images: {root}")
            pdf_path = convert_images_to_pdf(root)
            if pdf_path:
                results.append(pdf_path)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Convert images in all subfolders to PDFs')
    parser.add_argument('parent_path', help='Parent directory containing folders with images')
    parser.add_argument('--min-images', type=int, default=1, 
                        help='Minimum number of images required in a folder to process it (default: 1)')
    args = parser.parse_args()
    
    if not os.path.isdir(args.parent_path):
        print(f"Error: {args.parent_path} is not a valid directory")
        return
    
    pdfs_created = find_and_process_folders(args.parent_path, args.min_images)
    
    if pdfs_created:
        print("\nSummary: PDFs created:")
        for pdf in pdfs_created:
            print(f"- {pdf}")
        print(f"\nTotal PDFs created: {len(pdfs_created)}")
    else:
        print("No PDFs were created. No suitable folders found.")

if __name__ == "__main__":
    main()