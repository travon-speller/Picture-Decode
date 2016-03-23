import binascii
import zlib

PNG_SIGNATURE = 0x89504e470d0a1a0a
PNG_COLOR_TYPE_RGB = 2


def createImage(refImage, fileName):
  encodePGN(refImage, fileName+'.png')


def encodePGN(refImage, fileName):
  print "Encoding PNG"
  image = open(fileName, 'wb')

  width = len(refImage)
  height = len(refImage[0])

  # Write the PNG Signature
  image.write(binascii.unhexlify("%X" % PNG_SIGNATURE))

  #Writes the IHDR Chunk
  chunkData = ''
  chunkData += "%08X" % width #width
  chunkData += "%08X" % height #height
  chunkData += "%02X" % 8 #bitDepth
  chunkData += "%02X" % PNG_COLOR_TYPE_RGB #colorType
  chunkData += "%02X" % 0 #compressionMethod
  chunkData += "%02X" % 0 #filterMethod
  chunkData += "%02X" % 0 #interlaceMethod
  chunkData = binascii.unhexlify(chunkData)
  writePNGChunk(image, "IHDR", chunkData)

  # Write the IDAT Chunk
  chunkSize = 0
  chunkData = ''
  pixData = ''
  lastPix = width * height
  # Build pixel buffer
  for i in xrange(lastPix):
    pix = refImage[i%width][i/width]
    pixData += '%02X%02X%02X' % pix

  # Filter and compress Pixel data
  chunkData = filterPixelData(pixData, width)
  chunkData = binascii.unhexlify(chunkData)
  chunkData = zlib.compress(chunkData)
  writePNGChunk(image, "IDAT", chunkData)

  # End the PNG
  writePNGChunk(image, "IEND", '')

  image.close()
  print 'Done'

def writePNGChunk(f, chunkType, data):
  size = len(data)
  f.write(binascii.unhexlify("%08X" % size)) # Chunk Size
  chunk = ''
  chunk += chunkType
  if size > 0 :
    chunk += data # Chunk Data
  f.write(chunk)
  crc = binascii.crc32(chunk) & 0xFFFFFFFF
  f.write(binascii.unhexlify("%08X" % crc))


def filterPixelData(data, width):
  filterMode = 1
  scanlineSize = width*3 # assumes bitDepth of 8
  scanIndex = 0
  prevStream = '00' * 3 # assumes bitDepth of 8
  dataLen = len(data)
  fileredData = '01'
  for i in xrange(0, dataLen, 2):
    byte = int(data[i:i+2], 16)
    if scanIndex == scanlineSize:
      scanIndex = 0
      filterMode = 2
      prevScan = data[i-scanlineSize*2:i]
      fileredData += '02'

    if filterMode == 1:
      prevByte = int(prevStream[0:2], 16)
      byte -= prevByte
    elif filterMode == 2:
      byteStart = scanIndex*2
      byte -= int(prevScan[byteStart:byteStart+2], 16)

    byte %= 256
    fileredData += "%02X" % byte

    prevStream = prevStream[2:] + data[i:i+2]
    scanIndex += 1

  return fileredData



 # Decoding PNG CODE
 # Decoding PNG CODE
 # Decoding PNG CODE

def openImage(fileName):
  return decodePNG(fileName)

def decodePNG(fileName):
  print 'Decoding PNG'
  image = open(fileName, 'rb')

  sigHex =  binascii.hexlify(image.read(8))
  if int(sigHex, 16) != PNG_SIGNATURE:
    print('ERROR: Only PNG Format is supported. Try a PNG formated image.')
    return

  chunkType  = "Game On"
  refImage = []
  idata = ''
  while chunkType != 'IEND':
    chunkSize = int(binascii.hexlify(image.read(4)), 16)
    chunkType = image.read(4)
    chunk = image.read(chunkSize)
    chunkCRC = image.read(4)

    if chunkType == "IHDR":
      refImage, colorType, bitDepth = createRefImage(chunk)
      if colorType != PNG_COLOR_TYPE_RGB:
        print('ERROR: Unsuported PNG Color Type: ' + str(colorType) + ' Try another PNG image.')
        return
    elif chunkType == "IDAT":
      idata += chunk

  fillRefImage(refImage, idata, bitDepth)
  image.close()
  print 'Done'
  return refImage

def createRefImage(chunk):
  # Processes the IHDR chunk and creates a ref image for the PNG
  hexData = binascii.hexlify(chunk)
  width = int(hexData[0:8], 16)
  height = int(hexData[8:16], 16)

  bitDepth =          int(hexData[16:18], 16)
  colorType =         int(hexData[18:20], 16)
  compressionMethod = int(hexData[20:22], 16)
  filterMethod =      int(hexData[22:24], 16)
  interlaceMethod =   int(hexData[24:], 16)

  refImage = [x[:] for x in [[(0,0,0)] * height] * width]
  print 'Demensions: ' + str((width, height)) + '\tColor Type: ' + str(colorType) + '\tBit Depth: ' + str(bitDepth)
  print 'CompressionMethod: ' + str(compressionMethod) + '\tFilterMethod: ' + str(filterMethod) + '\tInterlaceMethod: ' + str(interlaceMethod)
  return (refImage, colorType, bitDepth)

def fillRefImage(refImage, chunk, bitDepth):
  # Processes the IDAT chunk and creates a ref image for the PNG

  scanline = -1
  chunk = zlib.decompress(chunk)
  hexData = binascii.hexlify(chunk)
  width = len(refImage)

  hexUnfiltered = ''
  filterMode = 0
  scanlineSize = width*3 # assumes bitDepth of 8
  scanIndex = scanlineSize
  prevStream = '00' * 3 # assumes bitDepth of 8
  nextScan = [0] * scanlineSize
  for i in xrange(0, len(hexData), 2):
    byte = int(hexData[i:i+2], 16)
    if scanIndex == scanlineSize:
      scanIndex = 0
      filterMode = byte
      prevStream = '00' * 3
      prevScan = nextScan
      nextScan = []
    else:
      if filterMode == 1:
        prevByte = int(prevStream[0:2], 16)
        byte += prevByte
      elif filterMode == 2:
        byte += prevScan[scanIndex]
      elif filterMode == 3:
        prevByte = int(prevStream[0:2], 16)
        byte += (prevScan[scanIndex] + prevByte)/2
      elif filterMode == 4:
        a = int(prevStream[0:2], 16)
        b = prevScan[scanIndex]
        c = 0 if (scanIndex <= 2) else prevScan[scanIndex-3]
        byte += paethFilter(a, b, c)


      byte %= 256
      nextScan.append(byte)
      hexUnfiltered += "%0.2X" % byte
      prevStream = prevStream[2:] + ("%0.2X" % byte)
      scanIndex += 1

  colorLen = (bitDepth/8) * 2
  for i in xrange(0, len(hexUnfiltered), colorLen * 3):
    pixIndex = i/(colorLen * 3)
    if pixIndex % width == 0:
      scanline += 1

    ri = i
    gi = ri+colorLen
    bi = gi+colorLen
    r = int(hexUnfiltered[ri:ri+colorLen], 16)
    g = int(hexUnfiltered[gi:gi+colorLen], 16)
    b = int(hexUnfiltered[bi:bi+colorLen], 16)
    refImage[pixIndex%width][scanline] = (r,g,b)


def paethFilter(a,b,c):
  p = a + b - c
  pa = abs(p - a)
  pb = abs(p - b)
  pc = abs(p - c)
  if pb >= pa <= pc:
    return a
  elif pb <= pc:
    return b

  return c



