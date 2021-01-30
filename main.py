import os
import cv2 as cv
import sys
import json
import numpy as np
import math

# Arguments passed
dir_source =  sys.argv[1]
dir_dest =  sys.argv[2]

def load_json(file):
    json_name = file + '.info.json'
    with open(os.path.join(dir_source,json_name)) as f:
        data = json.load(f)
    return data

def calculateDistance(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def perspective (img, src, dst,h,w):
    # use cv.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv.getPerspectiveTransform(src, dst)
    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv.warpPerspective(img, M, (w, h), flags=cv.INTER_LINEAR)
    return warped

# r=root, d=directories, f = files
for r, d, f in os.walk(dir_source):
    for file in f:
        name = file.split('.')
        if 'jpg' in name[-1]:
            print('------------')
            print('Opening ', file)
            img = cv.imread(os.path.join(dir_source,file),1)
            json_data = load_json(file)

            src_corner = np.array(json_data['canonical_board']['tl_tr_br_bl'], np.float32)
            x1 = src_corner[0][0]
            y1 = src_corner[0][1]
            x2 = src_corner[1][0]
            y2 = src_corner[1][1]
            w_d = calculateDistance(x1,y1,x2,y2)
            x1 = src_corner[0][0]
            y1 = src_corner[0][1]
            x2 = src_corner[3][0]
            y2 = src_corner[3][1]
            h_d = calculateDistance(x1,y1,x2,y2)

            # print(h_d,w_d)
            if w_d > h_d:
                dest_corner = np.array([(0,0), (w_d,0), (w_d,h_d), (0,h_d)], np.float32)
            else:
                dest_corner = np.array([(0,h_d), (0,0), (w_d,0), (w_d,h_d) ], np.float32)

            perspective_img = perspective(img, src_corner, dest_corner, int(h_d), int(w_d))
            if w_d <= h_d:
                perspective_img = cv.rotate(perspective_img, cv.cv2.ROTATE_90_CLOCKWISE)
            cimg = cv.cvtColor(perspective_img,cv.COLOR_BGR2GRAY)
            # cimg = cv.Canny(cimg,250,300)

            minDist = int(w_d*0.06)
            minRadius = int(w_d*0.035)
            maxRadius = int(w_d*0.043)
            # print(minDist, minRadius, maxRadius)
            circles = cv.HoughCircles(cimg,cv.HOUGH_GRADIENT, dp = 1, param1=250, param2 = 13,
                        minDist = minDist, minRadius = minRadius, maxRadius = maxRadius)

            h_final = (perspective_img.shape[0])
            w_final = (perspective_img.shape[1])
            delta_w = int((w_final/12)*1.022)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                # print(circles)
                for i in circles[0,:]:
                    cv.circle(perspective_img,(i[0],i[1]),i[2],(0,255,0),3)
                    cv.circle(perspective_img,(i[0],i[1]),2,(0,0,255),5)

            pltbh = json_data['canonical_board']['pip_length_to_board_height']*0.87
            top = np.zeros(12)
            bottom = np.zeros(12)
            for i in circles[0,:]:
                if (float(i[1])-float(i[2])) < h_final*pltbh:
                    index = int(i[0]/delta_w)
                    if index <13:
                        top[index] += 1
                    else:
                        print('ALARMA')
                elif (i[1]+i[2]) > (h_final*(1-pltbh)):
                    index = int(i[0]/delta_w)
                    if index <13:
                        bottom[index] += 1
                    else:
                        print('ALARMA')
            # cv.line(perspective_img, (0, int(h_final*pltbh)), (w_final, int(h_final*pltbh)), (0, 0, 255), thickness=2)
            # cv.line(perspective_img, (0, int(h_final*(1-pltbh))), (w_final, int(h_final*(1-pltbh))), (0, 0, 255), thickness=2)

            # for index, x in enumerate(top):
            #     x_1 = index*delta_w
            #     x_2 = x_1
            #     y_1 = 0
            #     y_2 = h_final
            #     cv.line(perspective_img, (x_1, y_1), (x_2, y_2), (0, 255, 0), thickness=2)

            print(top)
            print(bottom)

            save_name = os.path.join(dir_dest,file)
            # save_name2 = os.path.join(dir_dest,name[0]+'bgr.jpg')
            cv.imwrite(save_name, perspective_img)
            # cv.imwrite(save_name2, cimg)

            json_out = {}
            json_out['top'] = top.tolist()
            json_out['bottom'] = bottom.tolist()
            print(json_out)
            json_name = os.path.join(dir_dest,file + '.checkers.json')
            with open(json_name, 'w') as json_file:
                json.dump(json_out, json_file, indent = 4)


