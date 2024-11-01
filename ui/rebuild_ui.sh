#!/bin/bash

current_dir=$(pwd)  # Get the current directory path

for ui_file in *.ui; do
  if [[ -f "$ui_file" ]]; then
    output_file="${ui_file%.ui}.py"
    echo "Input file = $ui_file"
    echo "Output file = $output_file"
    if pyuic6 -o "$output_file" "$ui_file"; then
      echo "Conversion successful."
    else
      echo "Conversion failed for $ui_file." >&2
    fi
  elif [[ -z "$(ls *.ui 2>/dev/null)" ]]; then # Check if no .ui files exist at all (and suppress ls error message)
    echo "No .ui files found in directory $current_dir"
    # exit 1
  fi
done

if [[ -f "resources.qrc" ]]; then
    TEMP_RCC_OUTPUT=$(mktemp)  # Create a temporary file

    if rcc -g python resources.qrc > "$TEMP_RCC_OUTPUT" 2>&1; then # Redirect both stdout and stderr to the temp file
        # rcc succeeded, now replace PySide2 with PyQt6
        sed '0,/PySide2/s//PyQt6/' "$TEMP_RCC_OUTPUT" > ../resources.py
        echo "Compiled resources.qrc successfully using Qt6 rcc."
        rm "$TEMP_RCC_OUTPUT"  # Remove the temporary file
    elif pyrcc5 resources.qrc -o "$TEMP_RCC_OUTPUT"; then
        sed 's/PyQt5/PyQt6/g' "$TEMP_RCC_OUTPUT" > ../resources.py
        rm "$TEMP_RCC_OUTPUT"  # Remove the temporary file
        echo "Compiled resources.qrc successfully using pyrcc5."
    else
        # rcc failed, print the error message
        cat "$TEMP_RCC_OUTPUT" >&2
        rm "$TEMP_RCC_OUTPUT"
        echo "Failed to compile resources.qrc (Qt6 rcc failed, pyrcc5 failed)." >&2
        exit 1
    fi
else
    echo "No resources file (resources.qrc) found in directory $(pwd)" >&2
fi