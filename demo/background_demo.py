import cv2

img_path = "./background.jpg"
window_name = "image_demo" 
img = cv2.imread(img_path,0)
cv2.imshow(window_name, img)
cv2.waitKey(0) 
cv2.destroyAllWindows()
