#!/bin/bash

# Check if an input file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <input_image_path> [output_image_path]"
    echo "Example: $0 myimage.jpg myimage_square.jpg"
    exit 1
fi

INPUT_IMAGE="$1"
# Generate a default output filename: myimage.jpg -> myimage_square.jpg
# Or use the second argument if provided
OUTPUT_IMAGE="${2:-$(basename -- "$INPUT_IMAGE" .${INPUT_IMAGE##*.})_square.${INPUT_IMAGE##*.}}"

# Check if the input file exists
if [ ! -f "$INPUT_IMAGE" ]; then
    echo "Error: Input file '$INPUT_IMAGE' not found."
    exit 1
fi

echo "Processing '$INPUT_IMAGE'..."

# Get original image dimensions using ImageMagick's identify command
# -format "%w %h" outputs width and height separated by a space
read WIDTH HEIGHT <<< $(identify -format "%w %h" "$INPUT_IMAGE")

echo "Original dimensions: ${WIDTH}x${HEIGHT}"

# Determine the side length for the square crop
# This will be the smaller of the width or height
SQUARE_SIDE=""
if (( WIDTH < HEIGHT )); then
    SQUARE_SIDE="$WIDTH"
else
    SQUARE_SIDE="$HEIGHT"
fi

echo "Cropping to a square of size: ${SQUARE_SIDE}x${SQUARE_SIDE}"
echo "Output file will be: ${OUTPUT_IMAGE}"

# Perform the crop using ImageMagick
# -gravity Center ensures the crop is taken from the exact middle
# -crop ${SQUARE_SIDE}x${SQUARE_SIDE}+0+0 specifies the size of the crop.
convert "$INPUT_IMAGE" -gravity Center -crop "${SQUARE_SIDE}x${SQUARE_SIDE}+0+0" "$OUTPUT_IMAGE"

# Check if the convert command was successful
if [ $? -eq 0 ]; then
    echo "Successfully cropped '$INPUT_IMAGE' to square '$OUTPUT_IMAGE'."
else
    echo "Error: ImageMagick command failed."
    exit 1
fi
