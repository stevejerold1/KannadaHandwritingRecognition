#!/usr/bin/env python
import sys	# This module provides access to some variables used or maintained by the interpreter.
import os	# This module provides a portable way of using operating system dependent functionality.
import shutil	# The module offers a number of high-level operations on files and collections of files.	
import time 	# This module provides various time-related functions.
import glob 	# The glob module finds all the pathnames matching a specified pattern according to the rules used by the Unix shell.
from PIL import Image, ImageChops, ImageOps 	# The Python Imaging Library (PIL) adds image processing capabilities to your Python interpreter.
from skimage import color 	# scikit-image is a collection of algorithms for image processing.
from skimage.morphology import skeletonize_3d 	
from skimage.util import invert
from joblib import Parallel, delayed 	# Lightweight pipelining: using Python functions as pipeline jobs.
import cv2 	# Open CV is uesd image processing
from scipy.misc import toimage # It provides routines for numerical integration and optimization.

start_time = time.time()	# Used to start time record
count=0 					# Count for no.of files
rootdir = sys.argv[1]		# Take aregument from command line 
ori=os.getcwd()				# Save current directory for looping stage
folder = "Preprocessed_" + sys.argv[1]	# Creating new folder to save the preprocessed images 
newfolder = os.path.join(os.getcwd(),folder)	# Creating the path to the new folder
if not os.path.exists(newfolder):	# Check if directory already exists
	os.makedirs(newfolder)	# Making new directory
# This function is used to crop and thin the image file
# We pass th 'im' file as a parameter
def ct(im):
	img = Image.open(im)
	bg = Image.new(img.mode, img.size, img.getpixel((0,0))) # This is used to save a background and save the corner pixel 
	diff = ImageChops.difference(img, bg)				 # Which is specified by getpixel(0,0)
	diff = ImageChops.add(diff, diff, 2.0, -100)		 # Diff holds the difference with main 'im' and 'bg'
	bbox = diff.getbbox()		# The difference box is generated
	if bbox:					# If the box existes it is saved 
		img = img.crop(bbox)
		img.save(im)
	image = cv2.imread(im,0)
	# The given image should be in Grayscale or Binary format
	# skeletonize_3d assumes White as foreground and black as background.
	# Hence we invert the image (This can be removed based on what form of input images we decide to provide at later stage)
	image = color.rgb2gray(invert(image))
	# skeletonize_3d is mainly used for 3D images but can be used for 2D also. 
	# Advantage - Removes spurs and provides better output
	skeleton = skeletonize_3d(image)
	# Saving output image
	image = toimage(skeleton) 	# Takes a numpy array and returns a PIL image
	image.save(im)
# The loop below is used to iterate through each folder and subfolder
# It generats a tupel root,dirs,files
# Root is the current directory
# Dirs is a List of all subfolders in the root
# Files is a List of all files inside each folder
for root,dirs,files in os.walk(rootdir,topdown=False):	
	for name in dirs: 	# Looping through each folder inside rootdir
		#print("started with ",name) For Debbuging
		dir3 = os.path.join(root,name) 	# Create new path to the current subfolder in the loop specified by 'name'
		os.chdir(os.path.abspath(dir3))	# We are moving into the folder specified by dir3 using the absolute path
		# Now since we are inside the requied directory we check for images
		# The loop below is used to iterate through each file that ends with '.png' later we can add '.PNG'
		subfolder = os.path.join(newfolder,name)	# We	make a path with'name' to the new folder		
		if not os.path.exists(subfolder): # Check if subfolder already exists
			os.makedirs(subfolder) # We make the folder
		# The cropped images have been saved in the same folder as original images
		# We will now move them to the new folder in there specified subfolder
		src = os.getcwd() 	# source directory is the path of the  subfolder we are currently in
		dst = subfolder 	# The destination is the new subfolder created 
		files1 = os.listdir(src)	# creates a list of all files in the source directory
		# We make a loop which iterates through each files in the directory
		for f1 in files1: 
			src_file = os.path.join(src, f1)	# Path to source file
			dst_file = os.path.join(dst, f1)	# # Path to destination file
			if (f1.startswith("img")):				# IMPORTENT! make sure the image file starts with 'img' 
				if os.path.exists(dst_file):		# prior to processing with this program
					os.remove(dst_file)			# Basic overwiter function
					shutil.copy(src_file, dst_file)
				else:
					shutil.copy(src_file, dst_file)	# This makes usre we only move those files and overwrite if it existes 
		os.chdir(subfolder)		# Now we move into the subfolder 
		flist=glob.glob('*.png')	# Creats a list of files that end with '.png' later we can add '.PNG'
		count=count+len(flist)	# Count number of files being processed
		# The function below is used to parallelize the image processing
		# n_jobs is the number of cores to use (-1 is all cores)
		# Delayed is used to run the function 'ct' with aregument 'n' from list 'flist' 
		Parallel(n_jobs=-1)(delayed(ct)(n) for n in flist)
		print("done with ",name)	# Once done with 
		os.chdir(ori)	# At the end of the loop we move back to original directory so that looping can start again
end_time = time.time()	# Used to stop time record
seconds=end_time - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print ("Total time: %dH:%02dM:%02dS" % (h, m, s))
print ("Total number of images processed:",count) 