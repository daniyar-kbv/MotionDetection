import datetime as dt
import cv2
import mahotas
import time


class ThiefDetector:
    recording_fps = 30

    __video_capture = None
    __scale = 1
    __video_writer = None

    def __thresh_otsu(self, image):
        T_otsu = mahotas.thresholding.otsu(image)
        thresh_otsu = image.copy()
        thresh_otsu[thresh_otsu > T_otsu] = 255
        thresh_otsu[thresh_otsu < 255] = 0
        return cv2.bitwise_not(thresh_otsu)

    def __get_contours(self, frame, backround):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(backround, gray)
        blurred = cv2.GaussianBlur(difference, (5, 5), 0)
        thresh = self.__thresh_otsu(blurred)
        edged = cv2.Canny(thresh, 30, 150)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2 .CHAIN_APPROX_SIMPLE)
        return contours

    def __get_contour_coordinates(self, contour):
        x1 = 10000000
        y1 = 10000000
        x2 = 0
        y2 = 0

        for coord in contour:
            x = coord[0][0]
            y = coord[0][1]
            if x < x1:
                x1 = x
            if x > x2:
                x2 = x
            if y < y1:
                y1 = y
            if y > y2:
                y2 = y

        return x1, y1, x2, y2

    def __put_text(self, frame, is_safe):
        cv2.putText(img=frame,
                    text='SAFE' if is_safe else 'UNSAFE',
                    org=(frame.shape[1] - 300, 100),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=2,
                    color=(0, 0, 255),
                    thickness=3,
                    lineType=2)

    def __record(self, background):
        while self.__video_capture.isOpened():
            _, frame = self.__video_capture.read()
            contours = self.__get_contours(frame, background)
            large_contours = [contour for contour in contours if cv2.contourArea(contour) > 1000]

            for contour in large_contours:
                x1, y1, x2, y2 = self.__get_contour_coordinates(contour)
                cv2.rectangle(frame, (x1, y1), (x2, y2),(255, 255, 0), 2)

            self.__put_text(frame, len(large_contours) == 0)

            self.__video_writer.write(frame)

            cv2.imshow("Motion detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.__video_capture.release()
                self.__video_writer.release()

        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def start(self):
        self.__video_capture = cv2.VideoCapture(0)

        width = self.__video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.__video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.__video_writer = cv2.VideoWriter(f'{dt.datetime.now()}.mp4', fourcc, 30, (int(width), int(height)))

        time.sleep(2)

        _, background = self.__video_capture.read()
        background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

        self.__record(background_gray)


thief_detector = ThiefDetector()
thief_detector.start()