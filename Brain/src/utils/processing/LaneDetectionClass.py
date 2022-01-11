import numpy as np
import cv2

class Lane:
  def __init__(self,width,height):
      self.width = width
      self.height = height

      x_scl = 0.20
      y_scl = 0.45

      a = (0.00*self.width,      1.00*self.height)
      b = (x_scl*self.width,     y_scl*self.height)
      c = ((1-x_scl)*self.width, y_scl*self.height)
      d = (1.00*self.width,      1.00*self.height)
      self.mask_vertices = np.array([[a,b,c,d]], dtype=np.int32) 

  def get_roi(self, img):
     
      mask=np.zeros_like(img)

      if len(img.shape) > 2:
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
      else:
          ignore_mask_color = 255

      cv2.fillPoly(mask, self.mask_vertices, ignore_mask_color)
      return cv2.bitwise_and(img, mask)

  def eq_hist(self, img): # Histogram normalization
      img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
      img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
      img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])
      return img

  #Returns saturation channel of img
  def s_hls(self, img):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    return hls[:,:,2]

  # Sharpen image
  def sharpen_img(self, img):
      gb = cv2.GaussianBlur(img, (5,5), 20.0)
      return cv2.addWeighted(img, 2, gb, -1, 0)

  # Compute linear image transformation img*s+m
  def lin_img(self, img,s=1.0,m=0.0):
      img2=cv2.multiply(img, np.array([s]))
      return cv2.add(img2, np.array([m]))

  # Change image contrast; s>1 - increase
  def contr_img(self, img, s=1.0):
      m=127.0*(1.0-s)
      return self.lin_img(img, s, m)

  # Create perspective image transformation matrices
  def create_M(self, ):

      dst = np.int32([[569, 223], [711, 223], [0, 0], [1280, 0]])
      M = cv2.getPerspectiveTransform(self.mask_vertices, dst)
      Minv = cv2.getPerspectiveTransform(dst, self.mask_vertices)
      return M, Minv

  # Main image transformation routine to get a warped image
  def transform(self, img, M):
      img_size = (self.width, self.height)
      img = cv2.warpPerspective(img, M, img_size)
      img = self.sharpen_img(img)
      img = self.contr_img(img, 1.1)
      return img