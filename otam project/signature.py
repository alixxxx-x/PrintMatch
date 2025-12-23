import cv2
from skimage.metrics import structural_similarity as similarite


def match(path1, path2):
    # read the images
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    # turn images to gray
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # resize images so both are same size
    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))

    # display both images (replaced by the preview in the GUI)
    #cv2.imshow("One", img1)
    #cv2.imshow("Two", img2)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    # compare the images
    similarity = "{:.2f}".format(similarite(img1, img2)*100)

    return float(similarity)
