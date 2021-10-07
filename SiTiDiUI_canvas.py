#!./python
#-----------------------------------------------------------
#  SiTiDiUI_canvas.py
#    Python-based simple Timing Diagrammer with UI
#  Canvas-specific functions
#
#  Using PySimpleGUI (LGPL license), including use of their
#  demo code. This project is released with the MIT license.
#
#   RJN (GitNeff)  9/2021
#-----------------------------------------------------------

import PySimpleGUI as sg
import math

# this part executes at import time... I think
SIZE_X = 840
SIZE_Y = 400

# canvas size is in pixels, but for drawing purposes, a minimal
# unit size is 5 pixels. That's also minimum rise time, maybe
# make that configurable too.
# The horizontal lines making up the timing diagram are divided
# into (SIZE_X - <margins>) / MIN_UNIT_SIZE modifiable pieces
MIN_UNIT_SIZE = 5  # in pixels
UNITS_PER_LINE = int((SIZE_X - 40)/MIN_UNIT_SIZE)

# possible values for each unit of the lines
LOW_LINE = 0
HIGH_LINE = 1
RISING = 2
FALLING = 3
TRISTATE = 4  # figure this one out later
NUM_LOGIC_LEVELS = 4

# each timing takes up 55 pixels, top to bottom, 15 pixel margin between lines
LOW_LINE_OFFSET = 40
CENTER_OFFSET   = 20
HIGH_LINE_OFFSET = 0

CTE = 20        # CHART_TOP_EDGE 
CLE = 40        # CHART_LEFT_EDGE
CRE = SIZE_X    # CHART_RIGHT_EDGE
CBE = SIZE_Y    # CHART_BOTTOM_EDGE

XMARGINS = 40   # CHART_LEFT_EDGE + RIGHT_EDGE margin

activeLines = 4

lineName = [str(x) for x in range(6)]
lineNameId = [0] * 6  # keep the id so we can delete later if needed

# don't set up a 2-D array this way (inner array is duplicated, not unique):
#   timingLevel = [[0]*6] * UNITS_PER_LINE
# this method works:
timingLevel = [0] * 6
timingId = [0] * 6
for z in range(6):
    timingLevel[z] = [0] * UNITS_PER_LINE
    timingId[z]    = [0] * UNITS_PER_LINE
    
# -------------------------------------------
#  draw & label the axes
# (does not include timing lines)
# -------------------------------------------
def draw_axes(canvas, minTime, maxTime, numTicks, unitLabel, numLines):
    global activeLines
    global timingLine

    print ("Units per line: " + str(UNITS_PER_LINE))
    
    activeLines = numLines
    try:
        canvas.draw_line((0, CTE),   (SIZE_X, CTE))  # x axis line
        canvas.draw_line((CLE, CTE), (CLE, SIZE_Y))  # y axis line

        # put ticks and labels on x axis
        tickVal = minTime
        stepSize = int((SIZE_X - XMARGINS) / numTicks)
        stepResolution = int((maxTime - tickVal) / numTicks)

        for x in range(CLE, SIZE_X - XMARGINS, stepSize):
            canvas.draw_line((x, 15), (x, 20))                    # tick marks
            canvas.draw_text(str(tickVal), (x, 10), color='green')  # numeric labels
            tickVal += stepResolution
        canvas.draw_text(str(maxTime) + " " + unitLabel, (SIZE_X-30, 10), color='green')
        
    except:
        print ('Check inputs')


# -------------------------------------------
#  draw one unit
# -------------------------------------------
def draw_timing_unit(canvas, line, unit):
    # first, remove whatever was there
    canvas.delete_figure (timingId[line][unit])

    id = 0
    # draw new line
    if timingLevel[line][unit] == LOW_LINE:
       id = canvas.draw_line( [unit*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET],
                         [(unit+1)*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET] )
    elif timingLevel[line][unit] == HIGH_LINE:
       id = canvas.draw_line( [unit*5 + CLE, (line+1)*55 + HIGH_LINE_OFFSET],
                         [(unit+1)*5 + CLE, (line+1)*55 + HIGH_LINE_OFFSET] )
    elif timingLevel[line][unit] == RISING:
       id = canvas.draw_line( [unit*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET],
                         [(unit+1)*5 + CLE, (line+1)*55 + HIGH_LINE_OFFSET] )
    elif timingLevel[line][unit] == FALLING:
       id = canvas.draw_line( [unit*5 + CLE, (line+1)*55 + HIGH_LINE_OFFSET],
                         [(unit+1)*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET] )
##    elif timingLevel[line][unit] == TRISTATE:
##       # need to keep two Ids?  And first/last are special shapes too
         # or use predefined figures?     
##       id = canvas.draw_line( [unit*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET],
##                         [(unit+1)*5 + CLE, (line+1)*55 + HIGH_LINE_OFFSET] )
##       canvas.draw_line( [unit*5 + CLE,     (line+1)*55 + HIGH_LINE_OFFSET],
##                         [(unit+1)*5 + CLE, (line+1)*55 + LOW_LINE_OFFSET] )
    timingId[line][unit] = id
    
# -------------------------------------------
#  draw a full line
# -------------------------------------------
def draw_timing_line(canvas, line):
    canvas.delete_figure (lineNameId[line])
    lineNameId[line] = canvas.draw_text(lineName[line],
                            (int(CLE/2), CENTER_OFFSET + (line+1)*55), color='green')

    for unit in range (UNITS_PER_LINE):
        draw_timing_unit (canvas, line, unit)

# -------------------------------------------
#  check if y is in scope of timing line
# -------------------------------------------
def y_in_line(line, y):
    if y > (line+1)*55 + HIGH_LINE_OFFSET and y < (line+1)*55 + LOW_LINE_OFFSET:
        return True
    else:
        return False

# ------------------------------------------------
# if changing to high or low, and surrounded by
# rising/falling lines, change the whole section
# otherwise it's a whole lot of clicking
# ------------------------------------------------
def flip_stretch (canvas, n, unit):
    if timingLevel[n][unit] == LOW_LINE:
        for i in range (unit-1, 0, -1):
            if timingLevel[n][i] == FALLING:
                # found appropriate leading edge, look for end point
                for j in range (unit, UNITS_PER_LINE):
                    if timingLevel[n][j] == RISING:
                        # found end point, change this stretch
                        for k in range (i+1,j):
                            timingLevel[n][k] = LOW_LINE
                            draw_timing_unit(canvas, n, k)
                        break  # don't go forward past closest rising edge
                break  # don't go backward past closest falling edge
                
    elif timingLevel[n][unit] == HIGH_LINE:
        for i in range (unit-1, 0, -1):
            if timingLevel[n][i] == RISING:
                # found appropriate leading edge, look for end point
                for j in range (unit, UNITS_PER_LINE):
                    if timingLevel[n][j] == FALLING:
                        # found end point, change this stretch
                        for k in range (i+1,j):
                            timingLevel[n][k] = HIGH_LINE
                            draw_timing_unit(canvas, n, k)
                        break  # don't go forward past closest rising edge
                break  # don't go backward past closest falling edge
                            
# -------------------------------------------
#  handle a mouse click,
#  if on a timing line change the logic level
#  if at the start of a timing line, maybe bring up a
#  pop-up menu with options for the line: 
#    color, set low, high, sine wave or square wave?
# -------------------------------------------
def handle_mouse_click(canvas, x, y):
    
    activeBottom = (activeLines+1) * 55 + LOW_LINE_OFFSET
    if y < CTE or y > activeBottom:
        print ("outside y range")
        return
    if x > CRE:
        print ("outside x range")
        return
    
    # can take action - first find the line that applies
    for n in range(activeLines):
        if y_in_line(n,y) == True:
            if x < CLE:
                # bring up menu of options for this line
                # for now just get name of the line
                userStr = sg.popup_get_text('Enter name of line','Line Description', lineName[n])
                if userStr != None:
                    lineName[n] = userStr
                draw_timing_line (canvas, n)
            else:
                # act on the x unit in this line
                unit = int((x-CLE)/MIN_UNIT_SIZE)
                timingLevel[n][unit] = (timingLevel[n][unit] + 1) % NUM_LOGIC_LEVELS
                draw_timing_unit (canvas, n, unit)
                flip_stretch (canvas, n, unit)

# -------------------------------------------
#  draw a square wave
#  won't be exact, due to rounding errors and
#  size of units => periodically add a value?
# -------------------------------------------
def draw_clock(canvas, line, duration, minTime, maxTime):
    # convert duration time to number of units
    #    dur_time/line_time = dur_units/line_units
    #    => dur_units = line_units * dur_time/line_time
    durUnits = (UNITS_PER_LINE * duration) / (maxTime - minTime)
    # print ("Duration: " + str(duration) + ", units: " + str(durUnits))
    pos = 0
    holdTime = int(durUnits/2)-1  # 1/2 of full clock cycle
    halfcycle = False
    if durUnits/2 - int(durUnits/2) > 0.50:
        halfcycle = True
        
    # set values for a square wave clock cycle
    while pos + holdTime < UNITS_PER_LINE:
        timingLevel[line][pos] = RISING 
        for y in range(holdTime):
            timingLevel[line][pos+y+1] = HIGH_LINE
            
        pos = pos + holdTime + 1
        if pos + holdTime + 1 >= UNITS_PER_LINE:
            break
        
        timingLevel[line][pos] = FALLING 
        for y in range(holdTime):
            timingLevel[line][pos+y+1] = LOW_LINE
        if halfcycle == True:
            pos = pos + 1
            timingLevel[line][pos+holdTime] = LOW_LINE
        pos = pos + holdTime + 1

    # do a partial cycle at the end
    if pos < UNITS_PER_LINE:
        if timingLevel[line][pos-1] == HIGH_LINE:
            timingLevel[line][pos-1] = FALLING
            for y in range(pos, UNITS_PER_LINE):
                timingLevel[line][y] = LOW_LINE
        else:
            timingLevel[line][pos-1] = RISING
            for y in range(pos, UNITS_PER_LINE):
                timingLevel[line][y] = HIGH_LINE
        
    draw_timing_line(canvas, line)


# -------------------------------------------
#  draw a sine wave
# -------------------------------------------
def draw_sine_wave(canvas):
   prev_x = prev_y = None
   SIN_PERIOD = 10  # bigger number = longer period
   SIN_MAGNITUDE = 30
   SIN_PHASE_OFFSET = 2
   SIN_VERT_OFFSET = 60
   for x in range(10, SIZE_X):
      y = SIN_MAGNITUDE * math.sin(x/SIN_PERIOD + SIN_PHASE_OFFSET) + SIN_VERT_OFFSET
      if prev_x is not None:
          canvas.draw_line((prev_x, prev_y), (x, y), color='red')
      prev_x, prev_y = x, y
