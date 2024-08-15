# Just extract and save the preview image.
# Note: This program has been tested on only one ezd file
# and just a few ez3 files. So it's mostly a proof of concept.
# No real error checking: just throws exception and bombs on
# missing or bad input files.
# Uses pillow (Python image library)

import sys
# import struct
from PIL import Image

InFile1='ez3_in.ez3'
OutFile = '/tmp/ez3_img.png'

if len(sys.argv) > 1:
	InFile1 = sys.argv[1]
if len(sys.argv) > 2:
	OutFile = sys.argv[2]

with open(InFile1,'rb') as f: InBytes1 = f.read()
print('File {0} len {1} 0x{1:x}\n'.format(InFile1,len(InBytes1) ) )

# First 16 bytes are just a filetype string.
str1a=InBytes1[0:16].decode('utf-16')

# Get the pointer to the image.
myptr = 0x160
if str1a == 'EZCADX64':
	# ez3 file
	myptr = 0x160
elif str1a ==  'EZCADUNI':
	# ezd file
	myptr = 0x158
else:
	print('File header does not look right')
	sys.exit(0)

ImgPtr = int.from_bytes(InBytes1[myptr:myptr+8],'little',signed=False)
print('Image pointer 0x{0:x}'.format(ImgPtr) )
if ImgPtr == 0:
	print('No preview image found')
	sys.exit(0)

# header values. in one sample file they are:
#  0=0 c8=200 c8=200 320=800 200001=2097153 0=0 0=0 0=0
# The 0xc8 values are the height and width in pixels.
# Files I have seen are all 200x200, so don't know which is height and which is width.
# Don't know what any of the other numbers are either.
myptr = ImgPtr
Vec=[]
for k in range(8):
	Val=int.from_bytes(InBytes1[myptr:myptr+4],'little',signed=False)
	myptr += 4
	print(' {0:x}={0}'.format(Val),end='')
	Vec.append(Val)
print()

Hgt=Vec[1] # FIXME: these might be swapped.
Wid=Vec[2] # FIXME: these might be swapped.

Colors=[]
# myptr is now the pointer to the first byte of the bitmap.
RowLenBytes = Wid*4
for h in range(Hgt):
	rowptr =  myptr + RowLenBytes * (Hgt-1-h)
	for w in range(Wid):
		# FIXME: order may be wrong.
		b = InBytes1[rowptr] ; rowptr += 1
		g = InBytes1[rowptr] ; rowptr += 1
		r = InBytes1[rowptr] ; rowptr += 1
		x = InBytes1[rowptr] ; rowptr += 1
		rgb=[r,g,b]
		Colors.extend(rgb)
Colors = bytes(Colors)
img = Image.frombytes('RGB', (Wid, Hgt), Colors) # FIXME: are Wid and Hgt reversed?
# img.show() # This exec's something to display it, like 'display'
img.save(OutFile)

