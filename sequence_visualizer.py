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
legend = "\n-  +\n     Adenine\n     Thymine\n     Guanine\n     Cytosine"
display_size = 18

# Functions to be used by the switcher depending on the display mode.
def display_zero():
    sequence.tag_configure(key, background = value)
def display_one():
    sequence.tag_configure(key, foreground = value)
def display_two():
    sequence.tag_configure(key, background = value, foreground = "white")
def display_three():
    sequence.tag_configure(key, background = value, foreground = value)

def display_configure(number):
    switcher = {0: display_zero, 1: display_one, 2: display_two, 3: display_three}
    func = switcher.get(number, lambda: "Invalid display")
    func()

# Functions to calculate the color assigned to each of the letters. 
def calculate_percentage(base, column):
    return (column.count(base) * 100) / (len(column) - column.count("-") - column.count(None))

def saturation(base, column):
    percentage = calculate_percentage(base, column)
    i = 0
    while (percentage > percentages[i]):
        i += 1
    return bases[base] + str(percentages[i])
    
# Get the name of the file for the window title.
file_name = sys.argv[1]
title = file_name[file_name.rfind('/') + 1:].split(".",1)[0]

# Window generation, pretty standard stuff. 
window = tkinter.Tk()
window.title(title)
if(len(sys.argv) >= 4):
    display_size = sys.argv[3]
font_style = tkinter.font.Font(family="Courier New", size=display_size)
sequence = tkinter.scrolledtext.ScrolledText(window, font = font_style, wrap = tkinter.NONE)
title_and_legend = tkinter.scrolledtext.ScrolledText(window, font = font_style, width = 35, wrap = tkinter.NONE)

# Experimenting with some scrolling. 
sequence_frame = tkinter.Frame(window, borderwidth = 1, relief = "sunken")
vscroll = tkinter.Scrollbar(sequence_frame, orient = tkinter.HORIZONTAL, command = sequence.xview)
sequence['xscroll'] = vscroll.set

# To build the data frame, first we create a list of base arrays based on the file that has been provided.
sequences = []
string = "" # Used to display the sequences in the window.
titles = "" # Used to display the titles of each of the sequences. 
line_counter = 0
with open(sys.argv[1], 'r') as fragment_file:
    for line in fragment_file:
        line_counter += 1
        if line_counter % 2 == 0:
            string += line
            clean_line = line.strip() # Done so the sequences don't include the \n part, which might become an issue.
            sequences.append(list(clean_line))
        else:
            titles += line
sequences_dataframe = pandas.DataFrame(sequences)
string = string.strip() # Since some fasta files might have an empty line at the end, we get rid of it.
sequence.insert(tkinter.INSERT, string)
title_and_legend.insert(tkinter.INSERT, titles)
title_and_legend.insert(tkinter.INSERT, legend)

# Prepare each of the tags to be added to the string. If the third arg is 0, then the background will be colored, else, the letters.
if (len(sys.argv) < 3 or len(sys.argv) > 4):
    print("Usage of the sequence visor:\npython sequence_visualizer.py <fasta_file> <display_mode> <font_size>\n\nDisplay modes:\n0: Colored background, black letters.\n1: Colored letters, no background.\n2: Colored background, white letters.\n3: Colored background, no letters.\n\nFont size is by default 18pt.")
    exit()

for key, value in bases_and_saturation.items():
    if (int(sys.argv[2]) >= 0 and int(sys.argv[2]) <= 3):
        display_configure(int(sys.argv[2]))
    else:
        print("Invalid display configuration. The sequence will show up as regular text.")
    title_and_legend.tag_configure(key, background = value)

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

# Add the tags to the legend
line_counter = len(sequences_dataframe.index) + 3
for value in bases.values():
    for i in range(len(bases)):
        title_and_legend.tag_add(value + str(percentages[i]), str(line_counter) + '.' + str(i))
    line_counter += 1

# Testing the window display.
title_and_legend.configure(state = 'disabled')
sequence.configure(state = 'disabled')
vscroll.pack(side = "bottom", fill = 'x')
title_and_legend.pack(expand = True, fill = tkinter.BOTH, side = tkinter.LEFT)
sequence.pack(expand = True, fill = tkinter.BOTH, side = tkinter.LEFT)
sequence_frame.place()
window.mainloop()