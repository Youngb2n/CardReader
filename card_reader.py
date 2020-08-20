import numpy as np
import cv2
import openpyxl
import pytesseract
import re



class card_reader:
    def lookexcel(self,txt):
        try:
            load_wb = openpyxl.load_workbook("C:/WorkSpace/python/card_reader/bintable.xlsx", data_only=True)
            # 시트 이름으로 불러오기
            load_ws = load_wb['sheet1']
            text = txt[0:6]

            for i in load_ws['C'] :
                if str(text) == str(i.value) :
                        info = f'Pin :{text}\n발급사 : {load_ws[i.row][1].value}\n전표인자명 : {load_ws[i.row][3].value}\n개인/법인 : {load_ws[i.row][4].value}\n브랜드 : {load_ws[i.row][5].value}\n신용/체크 : {load_ws[i.row][6].value}\n'
            return info
        except UnboundLocalError:
            return -1

    def ocr_tesseract(self,im):
        kernel = np.ones((3, 3), np.uint8)
        kernel2 = np.ones((1, 1), np.uint8)

        #이미지를 다시 한번 노이즈제거
        img_result = cv2.GaussianBlur(im, ksize=(5, 5), sigmaX=0)
        _, img_result = cv2.threshold(img_result, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        img_result = cv2.copyMakeBorder(img_result, top=20, bottom=20, left=20, right=20, borderType=cv2.BORDER_CONSTANT,
                                        value=(0, 0, 0))

        img_result = cv2.erode(img_result, kernel2, iterations=1)
        img_result = cv2.morphologyEx(img_result, cv2.MORPH_OPEN, kernel)
        img_result = cv2.erode(img_result, kernel2, iterations=1)


        #cv2.imshow('result',img_result)
        cv2.waitKey(0)

        text = pytesseract.image_to_string(img_result, 'eng')
        result_text = re.sub('[^0-9]', '', text)
        #print(result_text[:6])
        return result_text


    def tesseracts(self, imgfile):

        try:
            #imagefile = 'C:/WorkSpace/python/card_reader/image/4.jpg'
            img = cv2.imread(imgfile)
            #r = 600.0 / img.shape[0]
            #dim = (int(img.shape[1] * r), 600)
            #img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    #회색조로 바꿈
            height, width, channel = img.shape  #정보받음
        except:
            return -2


        #탑햇 블랙햇으로 이미지 보정
        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement)
        imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)

        imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
        gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)


        #블러처리
        img_blurred = cv2.GaussianBlur(gray, ksize=(3, 3), sigmaX=0)

        #adaptiveTreshold
        img_thresh = cv2.adaptiveThreshold(
            img_blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, blockSize=11, C=3 )

        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        #opening closing
        imgOpen = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, structuringElement)
        imgOClose = cv2.morphologyEx(imgOpen, cv2.MORPH_CLOSE, structuringElement)
        #cv2.imshow('hi',imgOClose)


        #컨투어 따기
        contours, _ = cv2.findContours(imgOClose, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours_dict = [] #컨투어딕셔너리
        temp_result = np.zeros((height, width, channel), dtype=np.uint8)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour) #컨투어의 틀좌표 받기
            cv2.rectangle(temp_result, pt1=(x, y), pt2=(x + w, y + h), color=(255, 255, 255), thickness=1)#사각형그리기
            # dict에 좌표 넣기
            contours_dict.append({
                'contour': contour,
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'cx': x + (w / 2),
                'cy': y + (h / 2)
            })
        #cv2.imshow('1',temp_result)



        MIN_AREA = 100  #최소 넓이
        MIN_WIDTH, MIN_HEIGHT = 20, 30   #최소 너비와 높이
        MIN_RATIO, MAX_RATIO = 0.5 , 1.00   #최소 최대 비율

        possible_contours = []

        cnt = 0
        for i in contours_dict:
            area = i['w'] * i['h']  #사각형의넓이
            ratio = i['w'] / i['h'] #사각형의비율

            #card number라 추측되는 컨투어들을 찾기
            if area > MIN_AREA \
                    and i['w'] > MIN_WIDTH and i['h'] > MIN_HEIGHT \
                    and MIN_RATIO < ratio < MAX_RATIO: #조건
                i['idx'] = cnt #인덱스 번호넣기
                cnt += 1
                possible_contours.append(i)




        #찾은 cardnumber contour들을 그리기
        for d in possible_contours:
            cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x'] + d['w'], d['y'] + d['h']), color=(255, 255, 255),
                          thickness=2)
        #찾은 컨투어 인덱스를 결과에 넣기
        result_idx = self.find_chars(possible_contours) #2차 조건 함수

        matched_result = []
        for idx_list in result_idx:
            matched_result.append(np.take(possible_contours, idx_list))




        for r in matched_result:
            for d in r:
                #         cv
                cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x'] + d['w'], d['y'] + d['h']),
                              color=(255, 255, 255),
                              thickness=2)

        for i, matched_chars in enumerate(matched_result):
            sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])

        try :
            topLeft = [sorted_chars[0]['x']-20, sorted_chars[0]['y']]
            topRight = [sorted_chars[-1]['x']+sorted_chars[-1]['w']+20, sorted_chars[-1]['y']]
            bottomRight = [sorted_chars[-1]['x']+sorted_chars[-1]['w']+20, sorted_chars[-1]['y']+sorted_chars[0]['h']]
            bottomLeft = [sorted_chars[0]['x']-20, sorted_chars[0]['y']+sorted_chars[0]['h']]
        except UnboundLocalError:
            return -1



        pts1 = np.float32([topLeft, topRight, bottomRight, bottomLeft])

        w1 = abs(bottomRight[0] - bottomLeft[0])
        w2 = abs(topRight[0] - topLeft[0])
        h1 = abs(topRight[1] - bottomRight[1])
        h2 = abs(topLeft[1] - bottomLeft[1])
        minWidth = min([w1 , w2]) #최소 너비
        minHeight = min([h1 , h2]) #최소높이
        pts2 = np.float32([[0, 0], [minWidth - 1, 0],
                           [minWidth - 1, minHeight - 1], [0, minHeight - 1]])
        # 이미지 펴기
        M = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(imgOClose, M, (int(minWidth), int(minHeight)))

        #cv2.imshow('elf',img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        return result


    def find_chars(self,contour_list):
        MAX_DIAG_MULTIPLYER = 10  #컨투어 사이의 최대 거리
        MAX_ANGLE_DIFF = 10.0 #각도차
        MAX_AREA_DIFF = 0.2 #넓이차
        MAX_WIDTH_DIFF = 0.2 #너비차
        MAX_HEIGHT_DIFF = 0.8 #높이차
        MIN_N_MATCHED = 11  #최소 숫자수
        matched_result_idx = []

        for d1 in contour_list:
            matched_contours_idx = []
            for d2 in contour_list:
                if d1['idx'] == d2['idx']:
                    continue

                dx = abs(d1['cx'] - d2['cx'])
                dy = abs(d1['cy'] - d2['cy'])

                diagonal_length1 = np.sqrt(d1['w'] ** 2 + d1['h'] ** 2)

                distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
                if dx == 0: #각도가 0도일떄
                    angle_diff = 90
                else:
                    angle_diff = np.degrees(np.arctan(dy / dx))
                area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h']) / (d1['w'] * d1['h'])    #면적비율
                width_diff = abs(d1['w'] - d2['w']) / d1['w']   #너비비율
                height_diff = abs(d1['h'] - d2['h']) / d1['h']  #높이비율

                if distance < diagonal_length1 * MAX_DIAG_MULTIPLYER \
                        and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF \
                        and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                    matched_contours_idx.append(d2['idx'])

            matched_contours_idx.append(d1['idx'])

            if len(matched_contours_idx) < MIN_N_MATCHED:
                continue

            matched_result_idx.append(matched_contours_idx)

        return matched_result_idx





