import os,time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy
import basefun as bf
 
 
def get_cell_nuclei_mask(img, img_org, value):
    ret_, thresh = cv2.threshold(img, value, 255, cv2.THRESH_BINARY_INV)
    image_, contours, hierarchy_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    [_h, _w] = img.shape
    xo = _w/2
    yo = _h/2
    long_ = 200
    contours_best = []
    area_max = 0
    _long = 0
    if len(contours) == 0:
        return 0, 0, 0, 0, 0, 0, 0, 0
    for cnt in range(0, len(contours)):
        x,y,w,h=cv2.boundingRect(contours[cnt])
        xo2 = x+w/2
        yo2 = y+h/2
        _long = ((xo-xo2)**2+(yo-yo2)**2)**(1/2)
        if _long < long_:
            contours_best = contours[cnt]
            long_ = _long
    area = cv2.contourArea(contours_best)
    perimeter = cv2.arcLength(contours_best,True)
    hull = cv2.convexHull(contours_best)
    area2 = cv2.contourArea(hull)
    
    if area == 0:
        return 0, 0, 0, 0, 0, 0, 0, 0
    rule = perimeter/area
    thresh_ = thresh*0
    thresh__ = cv2.fillPoly(thresh_, [contours_best], 255)
    thresh__ = cv2.polylines(thresh__, [hull], True, 255, 1)
    value_1,_ = bf.get_2value(img_org,chan=2, mask = thresh__)
    return 1, thresh__, cnt+1, area, area2, perimeter, rule, value_1
    
    
def get_cell_cytoplasm_mask(img, nuclei_mask, img_org, value):
    ret_, thresh = cv2.threshold(img, value, 255, cv2.THRESH_BINARY_INV)
    image_, contours, hierarchy_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    if len(contours) == 0:
        return 0,0,0,0,0,0,0
    area_ = 0
    contours_max = []
    for cnt in range(0, len(contours)):
        area = cv2.contourArea(contours[cnt])
        if area > area_:
            contours_max = contours[cnt]
            area_ = area
    hull = cv2.convexHull(contours_max)
    area2 = cv2.contourArea(hull)
    perimeter = cv2.arcLength(contours_max,True)
    if area_ == 0:
        return 0,0,0,0,0,0,0
    rule = perimeter/area_
    thresh_ = thresh*0
    thresh__ = cv2.fillPoly(thresh_, [contours_max], 255)
    thresh__ = cv2.polylines(thresh__, [hull], True, 255, 1)
    nuclei_mask_off = np.ones(nuclei_mask.shape)*255 - nuclei_mask
    thresh___ = thresh__*(nuclei_mask_off/255)
    value_1,_ = bf.get_2value(img_org,chan = 0,mask = thresh__)
    return 1, thresh___, area_, area2, perimeter, rule, value_1
 
if __name__ == "__main__":
    dstroot = 'crop'
    listcells = os.listdir(dstroot)
    cellsinfo = []
    for n in listcells:
        cellinfo = {}
        cellpath = os.path.join(dstroot, n)
        img = cv2.imread(cellpath)
        img_gray = cv2.imread(cellpath, 0)
        img_gray = bf.get_fit_img(img_gray)
     #   cv2.imwrite(cellpath+'abc0.png',img_gray)
        value_1,value_2 = bf.get_2value(img_gray)
        sign_nuclei, cell_nuclei_mask, nuclei_cnt, nuclei_area, nuclei_hull_area, nuclei_circ, nuclei_rule, cell_nuclei_value = get_cell_nuclei_mask(img_gray, img, value_1) #获取细胞核掩码、个数、面积、凸面积、周长、核形规则度、获取细胞核深染程度
     #   cv2.imwrite(cellpath+'abc1.png',cell_nuclei_mask)
        if sign_nuclei == 0:
            continue
        sign_cytoplasm, cell_cytoplasm_mask, cytoplasm_area, cytoplasm_hull_area, cytoplasm_circ, cytoplasm_rule, cell_cytoplasm_value = get_cell_cytoplasm_mask(img_gray, cell_nuclei_mask, img, value_2) #获取细胞质掩码、面积、凸面积、周长、细胞规则度、获取细胞质情况
     #   cv2.imwrite(cellpath+'abc2.png',cell_cytoplasm_mask)
        if sign_cytoplasm == 0:
            continue
        cell_N_C = nuclei_area/(cytoplasm_area-nuclei_area) #计算核质比
        cellinfo_keys = ['cellpath','nuclei_cnt','nuclei_area','nuclei_hull_area','nuclei_circ','nuclei_rule','cell_nuclei_value','cytoplasm_area','cytoplasm_hull_area','cytoplasm_circ','cytoplasm_rule','cell_cytoplasm_value','cell_N_C']
        cellinfo_values = [cellpath,nuclei_cnt,nuclei_area,nuclei_hull_area,nuclei_circ,nuclei_rule,cell_nuclei_value,cytoplasm_area,cytoplasm_hull_area,cytoplasm_circ,cytoplasm_rule,cell_cytoplasm_value,cell_N_C]
        cellinfo = dict(zip(cellinfo_keys, cellinfo_values))
        cellsinfo.append(cellinfo)
    np.save("./cells_info/cells_info.npy", cellsinfo)
