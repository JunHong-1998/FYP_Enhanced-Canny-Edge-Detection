import cv2
import numpy as np
import math
from PIL import Image
import random

class DIP:
    def __init__(self):
        pass

    def read(self, file):
        return np.array(Image.open(file))

    def save(self, file, image):
        return cv2.imwrite(file, image )

    def resize(self, image, size):
        return cv2.resize(image, (size[0], size[1]))

    def cvtGreyscale(self, image):
        grey = np.dot(image[...,:3], [0.2989, 0.5870, 0.114])
        grey /= np.max(grey)
        return grey

    def gaussianKernel(self, kernelSize, sigma, flag=True, BilSpatial=None):
        normal = 1 / (2.0 * np.pi * sigma * sigma)
        if flag:
            center = kernelSize // 2
            x, y = np.mgrid[-center:center + 1, -center:center + 1]
            kernel = np.exp(-((x * x + y * y) / (2.0 * sigma * sigma))) * normal
        else:
            kernel = np.exp(-(kernelSize*kernelSize / (2.0 * sigma * sigma)))
            kernel = np.multiply(kernel, BilSpatial)
        return kernel

    def gaussianFilter(self, image, kernelSize, sigma):
        gKernel = self.gaussianKernel(kernelSize, sigma)
        output = np.zeros(image.shape, np.float)
        padded_image = np.pad(image, int((kernelSize - 1) / 2), 'edge')
        for row in range(image.shape[1]):
            for col in range(image.shape[0]):
                output[col, row] = np.sum(gKernel * padded_image[col:col + kernelSize, row:row + kernelSize])

        output /= np.max(output)
        return output

    def gabf(self, image, kernelSize, sigmaS, sigmaR):
        spatialKernel = self.gaussianKernel(kernelSize, sigmaS)
        LP_guide = np.zeros(image.shape, np.float)
        output = np.zeros(image.shape, np.float)
        padded_image = np.pad(image, int((kernelSize - 1) / 2), 'edge')

        for row in range(image.shape[1]):
            for col in range(image.shape[0]):
                LP_guide[col, row] = np.sum(spatialKernel * padded_image[col:col + kernelSize, row:row + kernelSize])

        LP_guide /= np.max(LP_guide)
        padded_image = np.pad(LP_guide, int((kernelSize - 1) / 2), 'edge')
        for row in range(image.shape[1]):
            for col in range(image.shape[0]):
                neighb_win = padded_image[col:col + kernelSize, row:row + kernelSize]
                intensity_diff = np.absolute(image[col, row] - neighb_win)
                weights = self.gaussianKernel(intensity_diff, sigmaR, flag=False, BilSpatial=spatialKernel)
                vals = np.sum(np.multiply(weights, neighb_win))
                norm = np.sum(weights)
                output[col, row] = np.divide(vals, norm, out=np.zeros_like(vals), where=norm != 0)
        output /= np.max(output)
        return output

    def median(self, image, kernelSize):
        output = np.zeros(image.shape, np.float)
        padded_image = np.pad(image, int((kernelSize - 1) / 2), 'edge')
        for row in range(image.shape[1]):
            for col in range(image.shape[0]):
                neighb_win = padded_image[col:col + kernelSize, row:row + kernelSize]
                output[col, row] = np.median(neighb_win)
        output /= np.max(output)
        return output

    def gradient2x2(self, image):
        kernelSize = 2
        gX = np.array([
            [-1, 1],
            [-1, 1]
        ])
        gY = np.array([
            [1, 1],
            [-1, -1]
        ])
        G_x = np.zeros(image.shape, np.float)
        G_y = np.zeros(image.shape, np.float)

        padded_image = np.pad(image, int((kernelSize - 1) / 2), 'edge')
        for row in range(image.shape[1]):  # loop through row
            for col in range(image.shape[0]):  # loop through col
                pix = padded_image[col:col + kernelSize, row:row + kernelSize]  # get pixel value

                G_x[col, row] = np.sum(np.multiply(gX, pix))
                G_y[col, row] = np.sum(np.multiply(gY, pix))


        filtered_image = np.hypot(G_x, G_y)
        angle_image = np.arctan2(G_y, G_x)
        filtered_image /= np.max(filtered_image)
        return filtered_image, angle_image

    def nonMax_Supp(self, image, angle):
        output = np.zeros(image.shape, np.float64)
        angle = np.rad2deg(angle)
        angle[angle < 0] += 180
        for row in range(1, image.shape[1] - 1):  # loop through row
            for col in range(1, image.shape[0] - 1):  # loop through col
                if image[col, row] == 0:
                    continue
                if (0 <= angle[col, row] < 22.5) or (157.5 <= angle[col, row] <= 180):
                    adj_pix = max(image[col, row + 1], image[col, row - 1])
                # angle 45
                elif (22.5 <= angle[col, row] < 67.5):
                    adj_pix = max(image[col + 1, row - 1], image[col - 1, row + 1])
                # angle 90
                elif (67.5 <= angle[col, row] < 112.5):
                    adj_pix = max(image[col + 1, row], image[col - 1, row])
                # angle 135
                elif (112.5 <= angle[col, row] < 157.5):
                    adj_pix = max(image[col - 1, row - 1], image[col + 1, row + 1])

                if image[col, row] >= adj_pix:
                    output[col, row] = image[col, row]
                # else:
                #     output[col, row] = 0
        output /= np.max(output)
        output *= 255
        return output.astype(np.uint8)

    def thresholding(self, image, thresH, thresL):
        output = np.zeros(image.shape, np.uint8)
        output[image >= thresH] = 255
        output[(image < thresH) & (image >= thresL)] = 100

        return output

    def hysteresis(self, image, nms=None):
        connect = True
        marker = np.full(image.shape, False)
        while connect:
            connect = False
            for row in range(image.shape[1]):
                for col in range(image.shape[0]):
                    if (image[col, row]==255) and not marker[col,row]:
                        marker[col, row] = True
                        try:
                            if image[col+1, row-1] == 100:
                                image[col + 1, row - 1] = 255
                                connect = True
                            if image[col+1, row] == 100:
                                image[col + 1, row] = 255
                                connect = True
                            if image[col+1, row+1] == 100:
                                image[col+1, row+1] = 255
                                connect =  True
                            if image[col, row-1] == 100:
                                image[col, row - 1] = 255
                                connect = True
                            if image[col, row+1] == 100:
                                image[col, row + 1] = 255
                                connect = True
                            if image[col-1, row-1] == 100:
                                image[col - 1, row - 1] = 255
                                connect = True
                            if image[col-1, row] == 100:
                                image[col - 1, row] = 255
                                connect = True
                            if image[col-1, row+1] == 100:
                                image[col - 1, row + 1] = 255
                                connect = True
                        except IndexError as e:
                            pass
        image[image < 255] = 0
        if type(nms)==np.ndarray:
            nms[image==0] = 0
        return image, nms

    def chainFormation(self, image, nms):
        h, w = image.shape
        for col in range(h):  # loop through col
            for row in range(w):  # loop through row
                if image[col, row] == 0:  # centre aldy zero
                    continue
                elif 1 <= col < h - 2 and 1 <= row < w - 2 and np.count_nonzero(image[col - 1:col + 2, row - 1:row + 2] == 255) == 1:  # isolated point nt need compare
                    image[col, row] = 0

        image = image.astype('int32')
        image[image == 255] = np.count_nonzero(image == 255)
        key = 1  # initial key
        NewKey = 1  #
        again = True
        direction = 1
        found = 0
        temp_grad = 0
        info = []
        while (again):
            again = False
            if direction == 1:
                startR, stopR, stepR = 0, w, 1
            else:
                startR, stopR, stepR = w - 1, -1, -1

            currentCol = h - 2
            for col in range(h):  # loop through col
                if again:
                    break
                for row in range(startR, stopR, stepR):  # loop through row
                    if image[col, row] <= key:  # skip zero and traced edge
                        continue
                    if key < NewKey:
                        if image[col - 1, row - 1] == key or image[col, row - 1] == key or image[col + 1, row - 1] == key or \
                                image[col - 1, row] == key or image[col + 1, row] == key or \
                                image[col - 1, row + 1] == key or image[col, row + 1] == key or image[col + 1, row + 1] == key:
                            image[col, row] = key
                            temp_grad += nms[col, row]  # accumulate gradient of edge chain
                            currentCol = col
                    elif key == NewKey:  # intialize and assign new key
                        image[col, row] = key
                        NewKey += 1
                        temp_grad += nms[col, row]  # accumulate gradient of edge chain
                        currentCol = col
                if col > currentCol:
                    again = True
                    currentFound = np.count_nonzero(image == key) - found
                    found += currentFound
                    direction *= -1
                    if currentFound == 0:
                        if np.count_nonzero(image == key) == 0:
                            # print('no more key found')
                            again = False
                            break
                        temp_grad /= found
                        info.append((key, found, temp_grad))  ### key, edge_length, mean local max
                        key += 1  # end search of current key
                        found = 0  # restart count of edgel per chain
                        direction = 1  # always start forward

                        temp_grad = 0  # reset local max accumulator
                        print('reassign key ...', key)

        output = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
        for k in range(1, key):
            output[image == k] = (random.randrange(75, 256), random.randrange(75, 256), random.randrange(75, 256))

        ### key, edge_length, mean local max
        infoArr = np.array(info)
        meanEdgeLength = np.mean(infoArr[:, 1])
        meanLocalMax = np.mean(infoArr[:, 2])

        return output, image, (infoArr, meanEdgeLength, meanLocalMax)

    def chainFiltering(self, image, chainInfo, factorK1, factorK2):
        ori = image.copy()
        info, meanEdgeLength, meanLocalMax = chainInfo
        powerLocalMax = meanLocalMax * factorK1
        powerEdgeLength = meanEdgeLength * factorK2
        output = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)

        for infoo in info:
            if infoo[1] < meanEdgeLength and infoo[2] < powerLocalMax or infoo[1] < powerEdgeLength and infoo[2] < meanLocalMax:           # still need factor?
                image[image == infoo[0]] = 0
                print('remove edge-chain ... key ', infoo[0])

        image[image > 0] = 255
        output[(ori>0) & (image==0)]= (255,0,0)
        output2 = cv2.cvtColor(output.copy(), cv2.COLOR_BGR2GRAY)
        output2[output2>0] = 255
        kernel = np.ones((3, 3), np.uint8)
        output2 = cv2.dilate(output2, kernel, iterations=2)
        contours, hierarchy = cv2.findContours(output2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print('contours found...')
        output[image == 255] = (255, 255, 255)
        for cont in contours:
            (x, y), radius = cv2.minEnclosingCircle(cont)
            center = (int(x), int(y))
            cv2.circle(output, center, int(radius)+2, (0, 255, 0), 2)
        return image.astype(np.uint8), output

    def getConfusionMat(self, ground, edgeMap):
        TP_count = np.count_nonzero((ground == 255) & (edgeMap == 255))
        FP_count = np.count_nonzero((ground == 0) & (edgeMap == 255))
        FN_count = np.count_nonzero((ground == 255) & (edgeMap == 0))
        output = np.zeros((edgeMap.shape[0], edgeMap.shape[1], 3), np.uint8)

        output[(ground == 0) & (edgeMap == 255)] = (200, 0,0)
        output[(ground == 255) & (edgeMap == 0)] = (0, 0, 200)
        output[(ground == 255) & (edgeMap == 255)] = (255, 255, 255)
        Prec =  TP_count / (TP_count + FP_count)
        Rec = TP_count / (TP_count + FN_count)
        F_a = Prec*Rec/(0.5*Prec+0.5*Rec)
        print('Precision: '+str(Prec)+" Recall: "+str(Rec)+" F-measure: "+str(F_a))
        # return TP_count, FP_count, FN_count, output
        return Prec, Rec, F_a, output