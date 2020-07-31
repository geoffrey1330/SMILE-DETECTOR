import numpy as np
import imutils
import time
import cv2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
net = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")
#loading the already trained deep learning model from disk
model = load_model('model/trained_model.h5')

vs = cv2.VideoCapture(0)
time.sleep(2.0)
# looping over the frames from the video stream
while True:
	ret,frame= vs.read()
	if ret is None:
		break
	frame = imutils.resize(frame, height=500)
	frame_copy=frame.copy()
	# grab the frame dimensions and convert it to a blob
	(h, w) = frame.shape[:2]
	print(h,w)
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
		(300, 300), (104.0, 177.0, 123.0))
 
	net.setInput(blob)
	detections = net.forward()
	frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# looping over the detections
	for i in range(0, detections.shape[2]):
		
		confidence = detections[0, 0, i, 2]

		
		if confidence < 0.6:
			continue

		
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")
		(startX, startY) = (max(0, startX), max(0, startY))
		(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

		face = frame[startY:endY, startX:endX]
		face = cv2.resize(face, (28,28))
		face = img_to_array(face)
		face = preprocess_input(face)
		face = np.expand_dims(face, axis=0)

            
		(NotSmiling, Smiling) = model.predict(face)[0]

            
		label = "Smiling" if Smiling > NotSmiling else "Not Smiling"
		color = (0, 255, 0) if label == "Smiling" else (0, 0, 255)

           
		label = "{}".format(label)


		cv2.rectangle(frame_copy, (startX, startY), (endX, endY), color, 2)
		
		cv2.rectangle(frame_copy, (startX, startY-30), (endX, startY),
			color, -1)

		cv2.putText(frame_copy, label, (startX, startY - 10),
          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
		
	cv2.imshow("Frame", frame_copy)
	key = cv2.waitKey(1)
	
	if key  & 0xFF == ord("q"):
		break


vs.release()
cv2.destroyAllWindows()