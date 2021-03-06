# import the necessary packages
import imutils
from imutils.video import VideoStream
import numpy as np
import time
import cv2
import caffe
import sys

caffe_root = '/home/yinyuecheng/caffe/'
sys.path.insert(0, caffe_root + 'python')  


# loading the model.
caffemodel = "MobileNetSSD_deploy.caffemodel"
net_file = "MobileNetSSD_deploy.prototxt"
print("[INFO] loading model...")
#net = cv2.dnn.readNetFromCaffe(caffemodel, net_file)
net = caffe.Net(net_file,caffemodel,caffe.TEST)  

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# initialize the video stream, allow the cammera sensor to warmup.
print("[INFO] starting video stream...")
vs = cv2.VideoCapture(0)
time.sleep(2.0) # pause, and wait for 2 seconds.
detected_objects = []

# initialize the time.
fps_time = 0

# loop over the frames from the video stream
while True:
    # Capture frame-by-frame
    ret, frame = vs.read()
    frame = imutils.resize(frame, width=800)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (500, 500)), 0.007843, (300, 300), 127.5)
    # pass the blob through the network and obtain the detections and predictions
    #net.setInput(blob)
    net.blobs['data'].data[...] = blob
    
    out = net.forward()
    
    detections = out['detection_out']
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the prediction
        confidence = detections[0, 0, i, 2]
        # set minimum confidence:
        minConfidence = 0.3 
	# filter out weak detections by ensuring the `confidence` is greater than the minimum confidence.
        if confidence > minConfidence:
            # extract the index of the class label from the `detections`, then compute the (x, y)-coordinates of the bounding box for the object.
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
	    # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            detected_objects.append(label)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
            cv2.putText(frame, "FPS: %f" % (1.0 / (time.time() - fps_time)), (20, 20),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            # show the output frame
            cv2.imshow("Frame", frame)
            fps_time = time.time()
            # if the `q` key was pressed, break from the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):  
        break

# do a bit of cleanup
cv2.destroyAllWindows()
