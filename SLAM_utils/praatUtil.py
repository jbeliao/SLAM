
"""

@package praatUtil This module contains some utility functions to seamlessly
	incorporate Praat analysis functionality into Python

@copyright GNU Public License
@author written 2009-2014 by Christian Herbst (www.christian-herbst.org)
@author Partially supported by the SOMACCA advanced ERC grant, University of Vienna,
	Dept. of Cognitive Biology

@note
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.
@par
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
@par
You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>.

"""

import numpy

def readBinPitchTier(fileName):

      metadata=None
      dataX=None
      dataY=None
      with open(fileName, "rb") as bin :
          try:
              # header
              header = numpy.fromfile(bin, dtype='S22', count=1).astype(str)[0].split('\t')
              xMin   = numpy.fromfile(bin, dtype='>d', count=1)[0]
              xMax   = numpy.fromfile(bin, dtype='>d', count=1)[0]
              nb     = numpy.fromfile(bin, dtype='>i4', count=1).astype(int)[0]
              # check file header
              if not (header[0]== 'ooBinaryFile' and header[1] == 'PitchTier'):
                  raise IOError('file header not recongized !')
              # read data as 2D-array
              dataType = numpy.dtype([('x','>d'),('y','>d')])
              data = numpy.fromfile(bin, dtype=dataType, count=nb)
              # check file end
              if len(bin.read()) > 0:
                  raise EOFError
          except:
              raise

          dataX = data['x']
          dataY = data['y']
          return(dataX, dataY)

def readPitchTier(fileName):
	"""
	reads Praat PitchTier data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and the
		corresponding F0 (inaccurately called "pitch" in Praat) data
	"""
	dataX, dataY, metaData = readPraatShortTextFile(fileName, 'PitchTier')
	return dataX, dataY

def readIntensityTier(fileName):
	"""
	reads Praat IntensityTier data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and data
	"""
	dataX, dataY, metaData = readPraatShortTextFile(fileName, 'Intensity')
	return dataX, dataY

def readPraatShortTextFile(fileName, obj):
	"""
	this function reads a Praat pitch tier file (saved as a 'short text file')
	@param fileName
	@param obj the file type. Currently we support these file types (as defined
		internally by Praat):
			- Harmonicity 2
			- PitchTier
			- Intensity
			- SpectrumTier
			- Spectrum 2
			- Cepstrum 1
	@return a two-dimensional array of floats, the first row
		(index = 0) representing the time offsets of data values, and the
		second row representing the detected fundamental frequency values
	"""
	file = open(fileName, "r")
	cnt = 0
	numDataPoints = 0
	offset = 0
	dataX = []
	dataY = []
	dataIdx = 0
	timeStep = 0
	timeOffset = 0

	arrFileTypes = [
		'Harmonicity 2', 'PitchTier', 'Intensity', 'SpectrumTier', \
			'Spectrum 2', 'Cepstrum 1'
	]

	if not obj in arrFileTypes:
		raise Exception('readPraatShortTextFile - file type must be: '
			+ ', '.join(arrFileTypes))
	metaData = []
	for line in file:
		line = line.strip()
		cnt += 1
		#print cnt, line # debug information
		if cnt > 6:
			if obj == 'Harmonicity 2' or obj == 'Intensity 2':
				if cnt > 13:
					val = float(line)
					if val > -100:
						dataY.append(val)
					else:
						dataY.append(None)
					dataX.append(timeOffset + float(dataIdx) * timeStep)
					dataIdx += 1
				else:
					if cnt == 7:
						timeStep = float(line)
					if cnt == 8:
						timeOffset = float(line)
			else:
			# read data here
				if cnt % 2 == 0:
					dataY.append(float(line))
					dataIdx += 1
				else:
					dataX.append(float(line))
		else:
			if cnt > 3:
				metaData.append(line)
			# error checking and loop initialization
			if cnt == 1:
				if line != "File type = \"ooTextFile\"":
					raise Exception ("file " + fileName \
						+ " is not a Praat pitch" + " tier file")
			if cnt == 2:
				err = False
				#print line
				if obj == 'Harmonicity':
					if line != "Object class = \"Harmonicity\"" \
							and line != "Object class = \"Harmonicity 2\"":
						err = True
				elif obj == 'Intensity':
					if line != "Object class = \"IntensityTier\"" \
							and line != "Object class = \"Intensity 2\"":
						err = True
				else:
					if line != "Object class = \"" + obj + "\"":
						err = True
				if err == True:
					raise Exception ("file " + fileName + " is not a Praat "
						+ obj + " file")
			if cnt == 6:
				if line[0:15] == 'points: size = ':
					numDataPoints = int(line.split('=')[1].strip())
					raise Exception (\
						"only the 'short text file' type is supported. " \
						+ " Save your Praat " + obj \
						+ " with 'Write to short text file.")
				else:
					numDataPoints = int(line)
	return (numpy.array(dataX), numpy.array(dataY), metaData)
