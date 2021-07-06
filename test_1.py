import cv2
import numpy as np

im = cv2.imread("./lena.png")
def clb_click(event,x,y,flags,param): 
  if event == cv2.EVENT_LBUTTONDBLCLK:
    print(im[y][x])

def main():
  print(type(im))
  print(im.shape)
  print(im[0][0]) # [y][x][BGR]

  area = (im[:,:,2] > 200) & (im[:,:,0] > 100) & (im[:,:,1] > 100)
  im[np.where(area)] = 0

  # im[:,:,0] = 0
  # im[:,:,1] = 255
  # im[:,:,2] = 0

  cv2.imshow("lena",im)
  cv2.setMouseCallback("lena",clb_click)
  while 1:
    if cv2.waitKey(0) & 0xFF == ord("q"):
      break
  
if __name__ == "__main__":
  main()