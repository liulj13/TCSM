#import tesseract
from PIL import Image
import sys
import os

"""
api = tesseract.TessBaseAPI()
api.Init(".","eng",tesseract.OEM_DEFAULT)
api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
api.SetPageSegMode(tesseract.PSM_AUTO)
"""

os.system("didjvu separate -o 1.out -m sauvola 1.jpg > /dev/null 2>&1")

im = Image.open("1.out")
im = im.crop((1, 1, 199, 48))
image = im.convert('RGB')
#r, g, b = image.getpixel((0, 0))

# get points
s = (200, 0)
e = (0, 0)
for x1 in range(198):
	x = 197 - x1
	flag = False
	for y in range(47):
		if image.getpixel((x, y))[0] < 50:
			e = (x, y)
			flag = True
			break
	if flag:
		break

last = [[(-1, -1) for i in range(47)] for j in range(198)]

q = []
qn = 0
q.append(e)
while (len(q) > qn):
	x, y = q[qn]
	if x < s[0]:
		s = (x, y)
	if x - 1 >= 0 and last[x - 1][y][0] == -1 and image.getpixel((x - 1, y))[0] < 50:
		q.append((x - 1, y))
		last[x - 1][y] = (x, y)
	if y + 1 < 47 and last[x][y + 1][0] == -1 and image.getpixel((x, y + 1))[0] < 50:
		q.append((x, y + 1))
		last[x][y + 1] = (x, y)
	if y - 1 >= 0 and last[x][y - 1][0] == -1 and image.getpixel((x, y - 1))[0] < 50:
		q.append((x, y - 1))
		last[x][y - 1] = (x, y)
	qn = qn + 1

line = []
while s != e:
	line.append(s)
	s = last[s[0]][s[1]]
line.append(e)

for (x, y) in line:
	upper, lower = 0, 0
	for i in range(48):
		if y + i >= 47 or image.getpixel((x, y + i))[0] > 50:
			upper = y + i
			break
	for i in range(48):
		if y - i <= 0 or image.getpixel((x, y - i))[0] > 50:
			lower = y - i
			break
	if upper - lower < 6:
		for j in range(lower + 1, upper):
			image.putpixel((x, j), (255, 255, 255))

image = image.crop((53, 0, 170, 47))
img = image.copy()

for x in range(117):
	for y in range(47):
		cnt = 0
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				if x + dx < 0 or x + dx >= 117 or y + dy < 0 or y + dy >= 47 or image.getpixel((x+dx, y+dy))[0] < 50:
					cnt += 1
		if cnt > 5:
			img.putpixel((x, y), (0, 0, 0))
		else:
			img.putpixel((x, y), (255, 255, 255))

img.save('1_.png', 'PNG')

os.system("tesseract 1_.png stdout")

"""
mImgFile = "1_.png"
mBuffer=open(mImgFile,"rb").read()
result = tesseract.ProcessPagesBuffer(mBuffer,len(mBuffer),api)
print result[0:4]
api.End()
"""

