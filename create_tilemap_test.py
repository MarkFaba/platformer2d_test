from PIL import Image
import os

def get_image_files_from_folder(folder_path):
    file_extensions = ['.jpg', '.png', '.jpeg']
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.splitext(f)[-1].lower() in file_extensions]

# specify your image directory here
image_directory = "D:\Python_projects\platformer2d_test\image"

# get all image files from the directory
image_list = get_image_files_from_folder(image_directory)
# create an empty image with the given size
final_image = Image.new('RGB', (1184, 800))

# the size to which we want to resize our images
resize_size = (8, 8)

x_offset = 0
y_offset = 0

for image_file in image_list:
    try:
        img = Image.open(image_file)

        # resize the image
        img = img.resize(resize_size)

        # paste the resized image onto the final image
        final_image.paste(img, (x_offset, y_offset))

        # move the x offset to the right by 32 pixels (the width of our images)
        x_offset += 8
        if x_offset >= final_image.width:
            # if we have reached the right edge of the final image, reset the x offset
            # and move the y offset down by 32 pixels (the height of our images)
            x_offset = 0
            y_offset += 8

        # if we have reached the bottom edge of the final image, stop processing images
        if y_offset >= final_image.height:
            break
    except Exception as e:
        print(f"Failed to process image {image_file}. Error: {e}")

# save the final image to a file
final_image.save('final_image.png', 'PNG')
