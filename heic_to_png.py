import os
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

def convert_heic_to_png(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    converted_files = 0
    exif_removed_files = 0

    for filename in os.listdir(input_folder):
        if filename.endswith('.heic'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.png')

            with Image.open(input_path) as img:
                # Remove exif metadata
                data = list(img.getdata())
                img_without_exif = Image.new(img.mode, img.size)
                img_without_exif.putdata(data)

                img_without_exif.save(output_path, 'PNG')
                converted_files += 1
                exif_removed_files += 1

            # Delete the original heic file
            os.remove(input_path)

    # Print the total number of files converted
    print(f"Converted {converted_files} files to png")

    # Print the total number of files with EXIF metadata removed
    print(f"Removed exif metadata from {exif_removed_files} files")

# Example usage
input_folder = "C:/Users/your/file/path/here/1"
output_folder = "C:/Users/your/file/path/here/2"
convert_heic_to_png(input_folder, output_folder)
