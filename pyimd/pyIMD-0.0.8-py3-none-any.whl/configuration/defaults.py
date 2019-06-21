# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

FIGURE_FORMAT = 'png'
FIGURE_WIDTH = 56.44
FIGURE_HEIGHT = 45.16
FIGURE_UNITS = 'cm'
FIGURE_RESOLUTION_DPI = 72
FIGURE_NAME_PRE_START_NO_CELL = 'FitNoCellData'
FIGURE_NAME_PRE_START_WITH_CELL = 'FitWithCellData'
FIGURE_NAME_MEASURED_DATA = 'CalculatedCellMass'
FIGURE_PLOT_EVERY_NTH_POINT = 1
CONVERSION_FACTOR_HZ_TO_KHZ = 1000.0
CONVERSION_FACTOR_DEG_TO_RAD = -57.3
SPRING_CONSTANT = 4.0
INITIAL_PARAMETER_GUESS = [70.0, 2.0, 0.0, 0.0]
LOWER_PARAMETER_BOUNDS = [10.0, 1.0, -3, -3]
UPPER_PARAMETER_BOUNDS = [100.0, 5.0, 3, 3]
ROLLING_WINDOW_SIZE = 1000
CORRECT_FOR_FREQUENCY_OFFSET = False
FREQUENCY_OFFSET_MODE = 'Auto'
FREQUENCY_OFFSET_N_MEASUREMENTS_USED = 1
FREQUENCY_OFFSET = 0
READ_TEXT_DATA_FROM_LINE = 23
CANTILEVER_LENGTH = 100
CELL_POSITION = 5
TEXT_DATA_DELIMITER = '\t'
