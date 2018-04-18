#!/usr/bin/env python

import tensorflow as tf
import glob

filenames=glob.glob('subimg_lepton_n00000049*data')
filename_queue = tf.train.string_input_producer(filenames)

reader = tf.WholeFileReader()
filename, content = reader.read(filename_queue)
image = tf.decode_raw(content, tf.float32)
image = tf.reshape(image,[20,10,2])

sess = tf.Session(config=tf.ConfigProto(
        log_device_placement=False))
init_op = tf.initialize_all_variables()
tf.train.start_queue_runners(sess=sess)
f,im = sess.run([filename,image])
print len(im)
print "f.i=",f,im

