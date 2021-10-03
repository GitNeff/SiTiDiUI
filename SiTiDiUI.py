#!./python
#-------------------------------------------------------------------
#  SiTiDiUI.py
#    Python-based simple Timing Diagrammer with UI
#
#  Using PySimpleGUI module (LGPL license), including use of their
#  demo code. This project is released with the MIT license.
#
#   RJN (GitNeff)  9/2021
#-------------------------------------------------------------------
# see example at:
# https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Graph_Element_Sine_Wave.py
#-------------------------------------------------------------------

import PySimpleGUI as sg
from PIL import ImageGrab  # install with pip as 'pillow'

# could do all this in one file, but good to learn scope rules, etc
import SiTiDiUI_canvas as td_can


#-----------------------------------------------------------
#  Save image
# see PySimpleGui example: Demo_Save_Window_As_Image.py
#-----------------------------------------------------------
def save_canvas():
    widget = canvas.Widget

    # box coordinates are (x0, y0, x1, y1) (upper left and lower right)
    # but something is awry, at least on my Mac need to double the
    # numbers then add a little margin 
    # full-screen save (no bbox argument for grab() is okay
    box = (widget.winfo_rootx() * 2 - 10,
           widget.winfo_rooty() * 2 - 10,
           (widget.winfo_rootx() * 2 - 10) + int(2 * widget.winfo_width() + 20),
           (widget.winfo_rooty() * 2 - 10) + int(2 * widget.winfo_height() + 20))
##    print ("x0:" + str(widget.winfo_rootx()) +
##           ", y0:" + str(widget.winfo_rooty()) +
##           ", width" + str(widget.winfo_width()) +
##           ", height" + str(widget.winfo_height()))
    
    filename = sg.popup_get_file('Choose file (GIF) to save to',
                                 default_extension = "gif")
    if filename != None:
        # default_extension doesn't seem to work in popup_get_file
        if filename[-3:] != "gif":
           filename = filename + ".gif"
        grab = ImageGrab.grab(bbox=box)
        grab.save(filename)


#-----------------------------------------------------------
#  Main program
#-----------------------------------------------------------
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside the window.
canvas = sg.Graph( (td_can.SIZE_X, td_can.SIZE_Y),
                   (0,td_can.SIZE_Y), (td_can.SIZE_X,0), 'LightYellow',
                   enable_events = True, key="-canvas-")
layout = [  [sg.Text('Horizontal Axis: Start Time'), sg.InputText('0',key='-MinTime-',size=6),
             sg.Text('End Time'), sg.InputText('100',key='-MaxTime-',size=6),
             sg.Text('Number of Ticks'), sg.InputText('10',key='-NumTicks-',size=6),
             sg.Text('Units'), sg.InputText('Sec',key='-Units-',size=6),],
            [sg.Text('Number of lines'), sg.InputText('4',key='-NumLines-',size=6),
             sg.Text('  '), sg.Button('Redraw X,Y Axis'),
             sg.Text('  '), sg.Button('Save Image'),
             sg.Text('  '), sg.Button('Exit'),],
            [canvas] ]

# -----------------
# Create the Window
# -----------------
window = sg.Window('Simple Timing Diagrammer (SiTiDi UI)', layout, finalize=True)

# should be a way to do this without repeating magic numbers
#  - can we get values before an event?
td_can.draw_axes(canvas, 0, 100, 10, "Sec", 4)
for n in range(4):
    td_can.draw_timing_line(canvas, n)

# -----------------
# Event Loop to process "events" and get the "values" of the inputs
# -----------------
while True:
    event, values = window.read()
    if event == 'Redraw X,Y Axis':
        canvas.erase()
        lines = int(values['-NumLines-'])
        if lines > 6:
            lines = 6
        td_can.draw_axes(canvas, int(values['-MinTime-']), int(values['-MaxTime-']),
                         int(values['-NumTicks-']), values['-Units-'], lines)
        for n in range(lines):
            td_can.draw_timing_line(canvas, n)
    elif event == 'Save Image':
        save_canvas()
    elif event == "-canvas-": # mouse event in the graph
        x, y = values['-canvas-']
        td_can.handle_mouse_click(canvas, x, y)
    elif event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
        break
    else:
        print (event)

window.close()
