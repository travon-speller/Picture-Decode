
from spyi import createImage
# def createImage(refImage, fileName):
from spyi import openImage
# def openImage(fileName):

# After you decode each image, please store the message(numeric) in its corresponding
# variable below.
messageSingleChannel = 1228
messageGreyAverage = 12280
messageUpSample = 0

# Algorithm Description:
# check each x value and y value and compare the r value to 245. if the r value is equal to 245, change the pixel to white.
def decryptSingleChannel(refImage): #refimage[x][y]
  for x in range(len(refImage)): 
    for y in range(len(refImage[x])):
      color = refImage[x][y]
      if color[0] == 245:
        refImage[x][y] = (255,255,255)

  return refImage

# Algorithm Description:
# check each x value and y value and add each color value together and divid them by 3 then assign that value to each color value
def decryptGreyAverage(refImage):
  for x in range(len(refImage)): 
    for y in range(len(refImage[x])):
      color = refImage[x][y]
      greyscale = (color[0] + color[1] + color[2])/ 3
      refImage[x][y] = (greyscale, greyscale, greyscale)
  return refImage

# Algorithm Description:
# unfinshed
def decryptUpSample(refImage):
  for x in range(len(refImage)): 
    for y in range(len(refImage[x])):
      if refImage[x][y] == (0,0,0):
        refImage[x][y] = (255,255,255)
  
  


#Use this function to test your coded
def decrypt():
  # Below is a sample test
  img = openImage('UpSample.png')
  decryptedImg = decryptUpSample(img) 
  createImage(decryptedImg, 'out3')

decrypt()


# Extra Credit Section
def makeColor(r_img, g_img, b_img):
 pass

def filter(r_img, g_img, b_img):
  pass
