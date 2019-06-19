import cv2

def find_contours(mask, preview=False):

    # Convert to gray
    gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    # Filter the gray
    ret, filtered = cv2.threshold(gray, 127, 255, 0)

    # Find contours on filtered
    contours, hirarhy = cv2.findContours(filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if preview:
        # Draw contours on mask
        color = (0, 255, 0)
        c_mask = mask.copy()
        mask = cv2.drawContours(c_mask, contours, contourIdx=0, color=color, thickness=3)

        cv2.imshow('Find Contours', mask)
        cv2.waitKey(0)

    return contours, hirarhy

def draw_contours(mask, contours, color=(0, 255, 0), thickness=3, preview=False):
    # Draw contours on mask
    cv2.drawContours(mask, contours, contourIdx=-1, color=color, thickness=thickness)
    if preview:
        cv2.imshow('Draw Contours', mask)
        cv2.waitKey(0)
    return mask

def draw_centroids(mask, contours, color=(255,255,255), preview=False):
    for i in contours:
        M = cv2.moments(i)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(mask, (cX, cY), 5, color, -1)
        cv2.putText(mask, "centroid", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if preview:
        cv2.imshow('Draw Centroids', mask)
        cv2.waitKey(0)

    return mask

