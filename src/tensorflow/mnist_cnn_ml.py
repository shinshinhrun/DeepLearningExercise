from helper import *

IMAGE_WIDTH = 28
IMAGE_HEIGHT = 28
IMAGE_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT
CATEGORY_NUM = 10
LEARNING_RATE = 0.01
FILTER_SIZE = 5
FILTER_NUM = 32
FILTER_NUM2 = 64
FEATURE_DIM = 1024
KEEP_PROB = 0.5
TRAINING_LOOP = 20000
BATCH_SIZE = 50
SUMMARY_DIR = 'log_cnn_ml'
SUMMARY_INTERVAL = 100

mnist = input_data.read_data_sets('data', one_hot=True)

with tf.Graph().as_default():
    with tf.name_scope('input'):
        y_ = tf.placeholder(tf.float32, [None, CATEGORY_NUM], name='labels')
        x = tf.placeholder(tf.float32, [None, IMAGE_SIZE], name='input_images')

    with tf.name_scope('convolution'):
        W_conv = weight_variable([FILTER_SIZE, FILTER_SIZE, 1, FILTER_NUM], name='weight_conv')
        b_conv = bias_variable([FILTER_NUM], name='bias_conv')
        x_image = tf.reshape(x, [-1, IMAGE_WIDTH, IMAGE_HEIGHT, 1])
        h_conv = tf.nn.relu(conv2d(x_image, W_conv) + b_conv)

    with tf.name_scope('pooling'):
        scale = 1 / 4.0
        h_pool = max_pool_2x2(h_conv)

    with tf.name_scope('convolution2'):
        W_conv2 = weight_variable([FILTER_SIZE, FILTER_SIZE, FILTER_NUM, FILTER_NUM2], name='weight_conv2')
        b_conv2 = bias_variable([FILTER_NUM2], name='bias_conv2')
        h_conv2 = tf.nn.relu(conv2d(h_pool, W_conv2) + b_conv2)

    with tf.name_scope('pooling2'):
        scale /= 4.0
        h_pool2 = max_pool_2x2(h_conv2)

    with tf.name_scope('fully-connected'):
        W_fc = weight_variable([int(IMAGE_SIZE * scale * FILTER_NUM2), FEATURE_DIM], name='weight_fc')
        b_fc = bias_variable([FEATURE_DIM], name='bias_fc')
        h_pool2_flat = tf.reshape(h_pool2, [-1, int(IMAGE_SIZE * scale * FILTER_NUM2)])
        h_fc = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc) + b_fc)

    with tf.name_scope('dropout'):
        keep_prob = tf.placeholder(tf.float32)
        h_drop = tf.nn.dropout(h_fc, keep_prob)

    with tf.name_scope('readout'):
        W = weight_variable([FEATURE_DIM, CATEGORY_NUM], name='weight')
        b = bias_variable([CATEGORY_NUM], name='bias')
        y = tf.nn.softmax(tf.matmul(h_drop, W) + b)

    with tf.name_scope('optimize'):
        cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))
        train_step = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cross_entropy)

    with tf.Session() as sess:
        train_writer = tf.train.SummaryWriter(SUMMARY_DIR + '/train', sess.graph)
        test_writer = tf.train.SummaryWriter(SUMMARY_DIR + '/test', sess.graph)

        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        train_accuracy_summary = tf.scalar_summary('accuracy', accuracy)
        test_accuracy_summary = tf.scalar_summary('accuracy', accuracy)

        sess.run(tf.initialize_all_variables())
        for i in range(TRAINING_LOOP + 1):
            batch = mnist.train.next_batch(BATCH_SIZE)
            sess.run(train_step, {x: batch[0], y_: batch[1], keep_prob: KEEP_PROB})

            if i % SUMMARY_INTERVAL == 0:
                print('step %d' % i)
                summary = sess.run(tf.merge_summary([train_accuracy_summary]), {x: batch[0], y_: batch[1], keep_prob: 1.0})
                train_writer.add_summary(summary, i)
                summary = sess.run(tf.merge_summary([test_accuracy_summary]), {x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
                test_writer.add_summary(summary, i)
