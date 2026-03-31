import cv2
import numpy as np
import drawsvg as svg

def get_svg_outline_from_bw(image_path, output_svg_path):
    # 1. Load the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.copyMakeBorder(
        img,
        top=5, bottom=5, left=5, right=5,
        borderType=cv2.BORDER_CONSTANT,
        value=255  # white for grayscale
    )

    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # Ensure the image is truly binary (black and white)
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 2. Find contours
    # RETR_LIST retrieves all contours without any hierarchical relationship.
    # CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments
    # and leaves only their end points.
    contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 3. Convert contours to SVG paths and 4. Generate the SVG file
    d = svg.Drawing(img.shape[1], img.shape[0], origin='top-left')

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 10:  # skip tiny noise
            continue
        if area > 0.9 * img.shape[0] * img.shape[1]:
            # skip the giant background contour
            continue

        if contour.shape[0] > 1:  # Ensure contour has more than one point
            # Start path at the first point
            path_data = f"M {contour[0][0][0]} {contour[0][0][1]}"
            # Add subsequent points as lines
            for point in contour[1:]:
                path_data += f" L {point[0][0]} {point[0][1]}"
            path_data += " Z"  # Close the path

            
            d.append(svg.Path(d=path_data, stroke='black', stroke_width=1, fill='none'))#fill='none'))

    d.save_svg(output_svg_path)
    print(f"SVG outline saved to {output_svg_path}")

# Example:
# Create a dummy black and white image for testing
# dummy_image = np.zeros((200, 200), dtype=np.uint8)
# cv2.rectangle(dummy_image, (50, 50), (150, 150), 255, -1) # White square
# cv2.circle(dummy_image, (100, 100), 20, 0, -1) # Black circle inside
# cv2.imwrite("dummy_bw_image.png", dummy_image)

# root = '../data/omniglot'
# root = './data/omniglot-master/python/images_background'
root = './data/omniglot-master/python/images_evaluation'
svgs_savedir = "./processed_data/svgs"
import os
os.makedirs(svgs_savedir, exist_ok=True)
os.makedirs('broken_glbs', exist_ok=True)
os.makedirs('fixed_glbs', exist_ok=True)
language_paths = [os.path.join(root,path) for path in sorted(os.listdir(root))]

for lang_path in language_paths:
    letters_paths = [os.path.join(lang_path,path) for path in sorted(os.listdir(lang_path))]
    for l_path in letters_paths:
        save_dir = os.path.join(svgs_savedir, '/'.join(l_path.split('/')[-2:]))
        os.makedirs(save_dir, exist_ok=True)
        file_names = os.listdir(l_path)
        for fn in file_names:
            src = os.path.join(l_path, fn)
            dst = os.path.join(save_dir, fn.replace('.png', '.svg'))
            print(src)
            print(dst)
            print()

            get_svg_outline_from_bw(src, dst)



