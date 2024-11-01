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
    if rcc -g python resources.qrc | sed '0,/PySide2/s//PyQt6/' > ../resources.py; then
        echo "Compiled resources.qrc successfully."
    else
        echo "Failed to compile resources.qrc" >&2
        # exit 1
    fi
else
    echo "No resources file (resources.qrc) found in directory $current_dir"  # Message for missing resource file
fi