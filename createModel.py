import tensorflow as tf
import os
from random import randint
import numpy as np


folders = ["O", "X"]
datasetFolder = "train"
testFolder = "letters"

def getNumber(letter):
	if(letter == "O"):
		#returns the first row of a 2-d array with ones in the diagonal and zeros elsewhere
		return np.array([0], dtype=np.int)#np.eye(2, dtype=np.float32)[0]
	if(letter == "X"):
		return np.array([1], dtype=np.int)#np.eye(2, dtype=np.float32)[1]

def getListOfImages():
	global folders
	global datasetFolder
	allImagesArray = np.array([], dtype=np.str)
	allImagesLabelsArray = np.array([], dtype=np.str)

	for folder in folders:
		print("Loading Image Name of ", folder)
		currentLetterFolder = datasetFolder+"/"+folder+"/"
		#listdir returns the list containing the names of the entries in the directory given by path
		imagesName = os.listdir(currentLetterFolder)
		allImagesArray = np.append(allImagesArray, imagesName)
		for i in range(0, len(imagesName)):
			print(i)
			#100 images in each folder
			if(i % 100 == 0):
				print("progress -> ", i)
			allImagesLabelsArray = np.append(allImagesLabelsArray, currentLetterFolder)
		#print(allImagesArray)
	return allImagesArray, allImagesLabelsArray

def getListofTestImages():
	global testFolder
	global folders
	allImagesArray = np.array([], dtype=np.str)
	allImagesLabelsArray = np.array([], dtype=np.str)

	for folder in folders:
		print("Loading Test Images of ", folder)
		currentLetterFolder = testFolder + "/" + folder + "/"
		imagesName = os.listdir(currentLetterFolder)
		allImagesArray = np.append(allImagesArray, imagesName)
		for i in range(0, len(imagesName)):
			print(i)
			if(i%20 == 0):
				print("progress -> ", i)
			allImagesLabelsArray = np.append(allImagesLabelsArray, currentLetterFolder)
	return allImagesArray, allImagesLabelsArray

def shuffleImagesPath(imagesPathArray, imagesLabelsArray):
	print("Size of imagesPathArray is ", len(imagesPathArray))
	for i in range(0, 100000):
		if(i % 1000 == 0):
			print("Shuffling in progress -> ", i)
		randomIndex1 = randint(0, len(imagesPathArray)-1)
		randomIndex2 = randint(0, len(imagesPathArray)-1)
		imagesPathArray[randomIndex1], imagesPathArray[randomIndex2] = imagesPathArray[randomIndex2], imagesPathArray[randomIndex1]
		imagesLabelsArray[randomIndex1], imagesLabelsArray[randomIndex2] = imagesLabelsArray[randomIndex2], imagesLabelsArray[randomIndex1]
	return imagesPathArray, imagesLabelsArray

def getBatchOfLetterImages(batchSize, imagesArray, labelsArray):
	global startIndexOfBatch
	dataset = np.ndarray(shape=(0,784), dtype=np.float32)
	labels = np.ndarray(shape=(0,2), dtype=np.float32)
	print("initialized dataset -> ", dataset)
	print("initialized labels -> ", labels)
	print("this is the imagesArray", imagesArray)
	with tf.Session() as sess:
		for i in range(startIndexOfBatch, len(imagesArray)):
			pathToImage = labelsArray[i] + imagesArray[i]
			print("this is the path to image -> " ,pathToImage)
			#rfind returns the last index where substring str is found
			lastIndexOfSlash = pathToImage.rfind("/")
			folder = pathToImage[lastIndexOfSlash - 1]
			print("it is in the folder -> " ,folder)
			print("last index is -> " ,lastIndexOfSlash)
			if(not pathToImage.endswith(".DS_Store")):
				try:
					imageContents = tf.read_file(str(pathToImage))
					print("this is the image contents -> ", imageContents)
					image = tf.image.decode_png(imageContents, dtype=tf.uint8)
					image = tf.image.rgb_to_grayscale(image)
					print("did converting the image to grayscale work? -> ", image)
					resized_image = tf.image.resize_images(image, [28,28])
					imarray = resized_image.eval()
					print("this is imarray -> ", imarray)
					imarray = imarray.reshape(-1) #need to reshape. currently multiplying 3 (channels), 28 (height) and 28 (width)
					#print("this is the size of imarray -> ",len(imarray))
					appendingImageArray = np.array([imarray], dtype=np.float32)
					appendingNumberLabel = np.array([getNumber(folder)], dtype=np.float32)
					#print("appending this image -> ",appendingImageArray)
					#print("appending this label -> ",appendingNumberLabel)

					labels = np.append(labels, appendingNumberLabel, axis=0)
					dataset = np.append(dataset, appendingImageArray, axis=0)
					if(len(labels) < batchSize):
						print(len(labels))
						print("should not be here. length of labels must be greater or equal to the batch size")
						print("this is the batch size -> ", batchSize)
						print("this is the length of the labels -> ", len(labels))
					if(len(labels) >= batchSize):
						print("the label size is more than batch size")
						startIndexOfBatch = i+1
						print("this is the dataset and labels -> ", dataset, labels)
						return dataset, labels
				except:
					print("unexpected image, it's okay, skipping")




startIndexOfBatch = 0
imagesPathArray, imagesLabelsArray = getListOfImages()
imagesPathArray, imagesLabelsArray = shuffleImagesPath(imagesPathArray, imagesLabelsArray)
#print("this is the test image path array -> ", imagesPathArray)
#print("this is the test label path array -> ", imagesLabelsArray)
tf.reset_default_graph()

x = tf.placeholder(tf.float32, shape=[None, 784])
W = tf.Variable(tf.truncated_normal([784, 2]), dtype=tf.float32, name="weights_0")
b = tf.Variable(tf.truncated_normal([2]), dtype=tf.float32, name="bias_0")
y = tf.nn.softmax(tf.matmul(x,W) + b)

trainingRate = 0.001
trainingLoops = 10
batchSize = 64

y_ = tf.placeholder(tf.float32, [None, 2])

crossEntropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))

#crossEntropy = -tf.reduce_sum(y_ * tf.log(y))

trainStep = tf.train.GradientDescentOptimizer(trainingRate).minimize(crossEntropy)

sess = tf.InteractiveSession()

saver = tf.train.Saver()

sess.run(tf.global_variables_initializer())
for i in range(0, trainingLoops):
	print("Training loop number: ", i)
	batchX, batchY = getBatchOfLetterImages(batchSize, imagesPathArray, imagesLabelsArray)
	print(batchX.shape, batchY.shape)
	sess.run(trainStep, feed_dict={x: batchX, y_: batchY})

savedPath = saver.save(sess, "models/model.ckpt")
print("Model saved at: ", savedPath)

#test trained model
testImagesPathArray, testImagesLabelsArray = getListofTestImages()
testImagesPathArray, testImagesLabelsArray = shuffleImagesPath(testImagesPathArray, testImagesLabelsArray)
testbatchX, testbatchY = getBatchOfLetterImages(batchSize, testImagesPathArray, testImagesLabelsArray)

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(sess.run(accuracy, feed_dict={x: testbatchX, y_: testbatchY}))




# #add accuracy and correct_predictions
# #testing
# # batchSize = 10
# startIndexOfBatch = 0
# batchSize = 64
# # print("this is the test image path array -> ", testImagesPathArray)
# # print("this is the test label path array -> ", testImagesLabelsArray)
# # print("this is the shuffled test image path array -> ", testImagesPathArray)
# # print("this is the shuffled test label path array -> ", testImagesLabelsArray)
# # print("this is the correct predictions -> ", correct_prediction)
# total_valid = int(1829/batch_size)

# for i in range(total_valid):
# 	print("Training loop number: ", i)
# 	print("this is the test images array - >", testImagesPathArray)
# 	print("this is the test labels array - >", testImagesLabelsArray)
# 	print(batchSize)
# 	testbatchX, testbatchY = getBatchOfLetterImages(batchSize, testImagesPathArray, testImagesLabelsArray)
# 	print("these are the shapes -> ", testbatchX.shape, testbatchY.shape)
# 	print(sess.run(accuracy, feed_dict={x: testbatchX, y_: testbatchY}))

