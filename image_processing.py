from PIL import Image
from tqdm import tqdm
import os, shutil, sys, getpass
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
"""
IMPORTANT:
After image capture, your directory set up should look like this.

Your_parent_directory/
│
├── GeoGuessrAI/
│   ├── image_capture.py
│   ├── image_processing.py
│   └── ...
│
├── YourCountryFolder1/
│   ├── Image1.jpg
│   ├── Image2.jpg
│   └── ...
│
└── YourCountryFolder1_pngs/
    ├── Image1.jpg
    ├── Image2.jpg
    └── ...
"""
def convert_png_to_jpg(path):
    image_names = os.listdir(path)
    image_names = [name for name in image_names if name.endswith(".png")]
    def convert_image(name):
        image = Image.open(os.path.join(path, name))
        rgb_image = image.convert('RGB')
        new_name = name.split(".png")[0] + ".jpg"
        rgb_image.save(os.path.join(path, new_name))
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(tqdm(executor.map(convert_image, image_names), total=len(image_names), desc="PNG to JPG conversion progress", unit="pics"))

def resize(folder_path, output_path, width, height):
    folder_path # ./GGAI/country
    parent_folder = os.path.dirname(folder_path) # ./GGAI
    separator = "/" if "/" in folder_path else "\\"
    country = folder_path.split(separator)[-1] # /country
    folder_path = os.path.join(parent_folder, country)
    if not os.path.exists(output_path): 
        os.makedirs(output_path)
    
    def resize_image(filename):
        if filename.endswith(".jpg"):
            input_path = os.path.join(folder_path, filename)
            image = Image.open(input_path)
            
            # Get current dimensions
            img_width, img_height = image.size
            
            # Calculate cropping coordinates
            left = (img_width - width) / 2
            top = (img_height - height) / 2
            right = left + width
            bottom = top + height
            
            # Cropping image
            cropped_image = image.crop((left, top, right, bottom))
            output_file_path = os.path.join(output_path, filename)
            cropped_image.save(output_file_path)
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(tqdm(executor.map(resize_image, os.listdir(folder_path)), total=len(os.listdir(folder_path)), desc="Resizing images", unit="pics"))

def is_black(image_path, threshold=10):
    with Image.open(image_path) as img:
        grayscale = img.convert('L')  # Convert to grayscale
        black_pixels = sum(1 for pixel in grayscale.getdata() if pixel <= threshold)
        total_pixels = grayscale.size[0] * grayscale.size[1]  # Width * Height
        ratio_black = black_pixels / total_pixels

    return ratio_black > 0.95  # If 95% or more of the image is black, consider it as a black image

def remove_black_images(folder_path):
    i = 0
    directory = [i for i in os.listdir(folder_path) if ".jpg" in i]
    def remove_image(filename):
        nonlocal i
        image_path = os.path.join(folder_path, filename)
        if is_black(image_path):
            os.remove(image_path)
            print(f"Removed black image: {filename}")
            i += 1
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(tqdm(executor.map(remove_image, directory), total=len(directory), desc="Removing bad images", unit="pics"))
    print(f"Removed {i} bad images.")

def get_folder_size(folder_path):
    png_size = 0
    jpg_size = 0
    num_pngs = 0
    num_jpgs = 0
    total_size = 0
    for filename in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)
        
        # Check if the file is a PNG file
        if filename.endswith('.png'):
            # Get the size of the PNG file
            size = os.path.getsize(file_path)
            total_size += size
            png_size += size
            num_pngs += 1
        
        # Check if the file is a JPG file
        elif filename.endswith('.jpg'):
            # Get the size of the JPG file
            size = os.path.getsize(file_path)
            total_size += size
            jpg_size += size
            num_jpgs += 1

    # Convert the total size to gigabytes
    gb_converter = 1024**3
    total_size_gb = total_size / gb_converter
    png_size_gb = png_size / gb_converter
    jpg_size_gb = jpg_size / gb_converter
    
    return total_size_gb, png_size_gb, jpg_size_gb, num_pngs, num_jpgs

def move_pngs(source_folder):
    # Move pngs to a separate directory.
    source_folder # ./GGAI/country
    parent_folder = os.path.dirname(source_folder) # ./GGAI
    separator = "/" if "/" in source_folder else "\\"
    country = source_folder.split(separator)[-1] # /country
    
    # Assign source -> destination folders
    print("From:", source_folder)
    destination_folder = os.path.join(parent_folder, f"{country}_pngs")
    print("To:", destination_folder)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    i = 0
    for root, _, files in os.walk(source_folder):
        files = [f for f in files if f.endswith(".png")]
        for file in tqdm(files, desc="Moving PNGs out", unit="pngs"):
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_folder, file)
            os.makedirs(destination_folder, exist_ok=True)
            shutil.move(source_file_path, destination_file_path)
            i += 1
    print(f"Moved {i} PNGs from {parent_folder} to {destination_folder}.")

if __name__ == "__main__":
    """Only need to change the country name. Then hit run."""
    countries = ["testing"]


    username = getpass.getuser()
    width = int(input("Enter width: "))
    height = int(input("Enter height: "))
    assert width == height, "Image dimensions are not square."
    for country in countries:
        path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), country)
        path_to_resized_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"{country}{width}x{height}")

        convert_png_to_jpg(path_to_images)
        
        t, p, j, np, nj = get_folder_size(path_to_images)
        
        print(f"Folder size: {t} GB")
        print(f"Total size of PNGs: {p} GB")
        print(f"Total size of JPGs: {j} GB")
        print(f"Total number of PNGs: {np}")
        print(f"Total number of JPGs: {nj}")
        
        move_pngs(path_to_images)
        remove_black_images(path_to_images)
        
        resize(path_to_images,path_to_resized_images, height, width)     