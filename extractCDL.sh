#!/bin/bash
#
# This script receives one ALE and outputs individual CDL files for each clip to the same directory.
# Tested with Resolve 12.  Export timeline as "ALE and CDL"
# Files will be named to match original clip names, and Tape_Scene_Take will be in the Description tag.
set -e	# rudimentary error handling
naming=0	# default to clip naming
if [ -z "$1" ]; then # make sure an argument is passed
	echo "  usage:    extractCDL.sh [-s] /path/to/ALE"
	echo "    -s	use Tape_Scene_Take naming instead"
else	# check for command-line options
	while getopts ":s" opt; do
		case $opt in
		s)
			naming=1	# use Tape_Scene_Take for output, and clip name in description
			;;
		\?)
			echo "Invalid option -$OPTARG"
			exit 1
			;;
		esac
	done
	shift $((OPTIND-1))		# remove opts, leaving only positional parameters

	if [ -f "$1" ]; then	# make sure an argument is passed
		output_path="${1%.*}_CDLs"
		mkdir "$output_path"
		input_data=$(tail -n +11 "$1" | tr \\11 \\7)	# replace tabs with alarm bell to handle blank columns
#	ALE column headers should be in row 8
		((ASC_SOP=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "ASC_SOP") {print x}}' "$1")-1))
		((ASC_SAT=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "ASC_SAT") {print x}}' "$1")-1))
		((Tape=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "Tape") {print x}}' "$1")-1))
		((Scene=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "Scene") {print x}}' "$1")-1))
		((Take=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "Take") {print x}}' "$1")-1))
		((DisplayName=$(gawk 'NR==8 {split($0,array,"\t"); for (x in array) if (array[x] == "Display Name") {print x}}' "$1")-1))

		while IFS=$'\a' read -r -a myArray;	do
			if [ "$naming" = 1 ]; then
				output_file="${output_path}/${myArray[$Tape]}_${myArray[$Scene]}_${myArray[$Take]}.cdl" # Tape_Scene_Take
				description="${myArray[$DisplayName]}" # Display_Name
			else
				output_file="${output_path}/${myArray[$DisplayName]}.cdl" # Display_Name
				description="${myArray[$Tape]}_${myArray[$Scene]}_${myArray[$Take]}" # Tape_Scene_Take
			fi
			slope=$(echo "${myArray[$ASC_SOP]}" | sed "s_(\(.*\))(.*)(.*_\1_")
			offset=$(echo "${myArray[$ASC_SOP]}" | sed "s_.*)(\(.*\))(.*_\1_")
			power=$(echo "${myArray[$ASC_SOP]}" | sed "s_.*)(.*)(\(.*\)).*_\1_")
			echo -e "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<ColorDecisionList xmlns=\"urn:ASC:CDL:v1.01\">\n\t<ColorDecision>\n\t\t<ColorCorrection>\n\t\t\t<SOPNode>\n\t\t\t\t<Description>$description</Description>\n\t\t\t\t<Slope>$slope</Slope>\n\t\t\t\t<Offset>$offset</Offset>\n\t\t\t\t<Power>$power</Power>\n\t\t\t</SOPNode>\n\t\t\t<SATNode>\n\t\t\t\t<Saturation>${myArray[$ASC_SAT]}</Saturation>\n\t\t\t</SATNode>\n\t\t</ColorCorrection>\n\t</ColorDecision>\n</ColorDecisionList>" > "$output_file"

		done <<< "$input_data"
		echo "   Successfully extracted to $output_path."
		echo
	elif [ ! -z "$1" ]; then echo "$1 is not a valid file"
	else echo "  usage:    extractCDL.sh [-s] /path/to/ALE"
	fi
fi
