# CardReader
opencv2 , PyQt5를 활용한 Pin번호 인식 프로그램

Requirements
-------------
### The test environment is
### Python 3.5.2
### OpenCV 4.1.0
### PyQT5
### Pytesseract

Image Convert
------------
> ### Test image  
<img src="/image/4.jpg" width="40%" height="80%" title="img2" alt="img2"></img>    
> ### TopHat, BlackHat, Grayscale, blur, opening, closing 등을 이용하여 이미지 보정을함.      

<img src="/image/1.JPG" width="80%" height="80%" title="img2" alt="img2"></img>       

> ### 영상내의 컨투어들을 읽어드림   

<img src="/image/3.JPG" width="80%" height="80%" title="img2" alt="img2"></img>   
> ### 컨투어간의 거리와 크기를 확인하여 카드번호로 추정되는 위치리를 얻어 원 영상에서 Crop하여 보정함    

<img src="/image/2.JPG" width="80%" height="80%" title="img2" alt="img2"></img>   




Result
------
<img src="/image/5.JPG" width="80%" height="80%" title="img2" alt="img2"></img>   

> ### Result   
<img src="/image/6.JPG" width="80%" height="80%" title="img2" alt="img2"></img>   
### 더 자세한 내용은 코드를 확인하세요.
