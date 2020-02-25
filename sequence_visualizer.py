import tkinter
import tkinter.scrolledtext
import tkinter.font
import sys
import pandas

# Used to generate each of the colors that will be used in the visualizer.
bases = {"A":"adenine", "T": "thymine", "G":"guanine", "C":"cytosine"}
percentages = [25, 50, 75, 100]
bases_and_saturation = {"adenine25":"RoyalBlue1", "adenine50":"RoyalBlue2", "adenine75":"RoyalBlue3", "adenine100":"RoyalBlue4",
                        "thymine25":"firebrick1", "thymine50":"firebrick2", "thymine75":"firebrick3", "thymine100":"firebrick4",
                        "guanine25":"PaleGreen1", "guanine50":"PaleGreen2", "guanine75":"PaleGreen3", "guanine100":"PaleGreen4",
                        "cytosine25":"MediumPurple1", "cytosine50":"MediumPurple2", "cytosine75":"MediumPurple3", "cytosine100":"MediumPurple4"}

# Functions to calculate the color assigned to each of the letters. 
def calculate_percentage(base, column):
    return (column.count(base) * 100) / (len(column) - column.count("-") - column.count(None))

def saturation(base, column):
    percentage = calculate_percentage(base, column)
    i = 0
    while (percentage > percentages[i]):
        i += 1
    return bases[base] + str(percentages[i])
    
#Get the name of the file for the window title.
last_slash = 0
position = 0
for char in sys.argv[1]:
    if (char == '/'):
        last_slash = position
    position += 1
title = sys.argv[1].split(".",1)[0][last_slash + 1:]

# Window generation, pretty standard stuff. 
window = tkinter.Tk()
window.title(title)
font_style = tkinter.font.Font(family="Courier New", size=18, weight = "bold")
sequence = tkinter.scrolledtext.ScrolledText(window, font = font_style, wrap = tkinter.NONE)

# Experimenting with some scrolling. 
sequence_frame = tkinter.Frame(window, borderwidth = 1, relief = "sunken")
vscroll = tkinter.Scrollbar(sequence_frame, orient = tkinter.HORIZONTAL, command = sequence.xview)
sequence['xscroll'] = vscroll.set

# To build the data frame, first we create a list of base arrays based on the file that has been provided.
sequences = []
string = "" # Used to display the sequences in the window.
line_counter = 0
with open(sys.argv[1], 'r') as fragment_file:
    for line in fragment_file:
        line_counter += 1
        if line_counter % 2 == 0:
            string += line
            clean_line = line.strip() # Done so the sequences don't include the \n part, which might become an issue.
            sequences.append(list(clean_line))
sequences_dataframe = pandas.DataFrame(sequences)
string = string.strip() # Since some fasta files might have an empty line at the end, we get rid of it.
sequence.insert(tkinter.INSERT, string)

# Prepare each of the tags to be added to the string. If the third arg is 0, then the background will be colored, else, the letters.
for key, value in bases_and_saturation.items():
    if(sys.argv[2] == '0'):
        sequence.tag_configure(key, background = value)
    else:
        sequence.tag_configure(key, foreground = value)

consensus = "" # Concensus sequence that is gonna be added at the end of the string.
for i in range(len(sequences_dataframe.columns)):
    column_counts = sequences_dataframe[i].value_counts().to_dict()
    most_common_bases = list(column_counts.keys())
    most_common = most_common_bases[0]
    # The idea is to not add a '-' to the consensus unless it is absolutely necessary (situation only given in borders)
    if (most_common != '-'): 
        consensus += most_common
    elif (most_common == '-' and len(most_common_bases) > 1):
        consensus += most_common_bases[1]
    else:
        consensus += '-'
    # Note: this code shall be updated in the case there's a way to represent when there is 2 or more bases with the same amount of ocurrences
sequence.insert(tkinter.INSERT, "\n\n" + consensus)

# Calculate the percentage and add the corresponding tags to each of the elements in the display.
for i in sequences_dataframe:
    column = list(sequences_dataframe[i])
    saturations = {}
    for base in bases:
        saturations[base] = saturation(base, column)
    for j in range(len(column)):
        if(column[j] != '-' and column[j] != None):
            sequence.tag_add(saturations[column[j]], str(j + 1) + '.' + str(i))

# Add the final tags to the consensus
for i in range(len(sequences_dataframe.columns)):
    sequence.tag_add(bases[consensus[i]] + '100', str(len(sequences_dataframe.index) + 2) + '.' + str(i))

# Testing the window display.
sequence.configure(state = 'disabled')
vscroll.pack(side = "bottom", fill = 'x')
sequence.pack(expand = True, fill = tkinter.BOTH)
sequence_frame.place()
window.mainloop()