#coding=utf-8

import find_mxnet
import mxnet as mx
import logging
import argparse
import train_model
from img_preprocess import call_im2rec
import os
import os.path
import re_train

# train_prefix_path = "./img_preprocess/train"
# train_img_root_path = "./img/train/"
#
# val_prefix_path = "./img_preprocess/val"
# val_img_root_path = "./img/val/"

train_prefix_path = "./img_preprocess/erotic_train"
train_img_root_path = "./img_erotic/train/"

val_prefix_path = "./img_preprocess/erotic_val"
val_img_root_path = "./img_erotic/val/"

# don't use -n and -s, which are resevered for the distributed training
parser = argparse.ArgumentParser(description='train an image classifer on imagenet')
parser.add_argument('--network', type=str, default='resnet152',
                    choices = ['alexnet', 'vgg', 'googlenet', 'inception-bn',
                               'inception-bn-full', 'inception-v3', 'inception-v4', 'resnet', 'inception-resnet-v2', 'resnet152'],
                    help = 'the cnn to use')
parser.add_argument('--data-dir', type=str, required=False, default='./img_preprocess/',
                    help='the input data directory')
parser.add_argument('--model-prefix', type=str,
                    help='the prefix of the model to load')
parser.add_argument('--save-model-prefix', type=str,
                    help='the prefix of the model to save')
parser.add_argument('--lr', type=float, default=.001,
                    help='the initial learning rate')
parser.add_argument('--lr-factor', type=float, default=1,
                    help='times the lr with a factor for every lr-factor-epoch epoch')
parser.add_argument('--lr-factor-epoch', type=float, default=1,
                    help='the number of epoch to factor the lr, could be .5')
parser.add_argument('--clip-gradient', type=float, default=5.,
                    help='clip min/max gradient to prevent extreme value')
parser.add_argument('--num-epochs', type=int, default=10,
                    help='the number of training epochs')
parser.add_argument('--load-epoch', type=int,
                    help="load the model on an epoch using the model-prefix")
parser.add_argument('--batch-size', type=int, default=1,
                    help='the batch size')
parser.add_argument('--gpus', type=str, default=None,
                    help='the gpus will be used, e.g "0,1,2,3"')
parser.add_argument('--kv-store', type=str, default='local',
                    help='the kvstore type')
parser.add_argument('--num-examples', type=int, default=24371,
                    help='the number of training examples')
parser.add_argument('--num-classes', type=int, default=5,
                    help='the number of classes')
parser.add_argument('--log-file', type=str, 
		            help='the name of log file')
parser.add_argument('--log-dir', type=str, default="/tmp/",
                    help='directory of the log file')
parser.add_argument('--train-dataset', type=str, default="train.rec",
                    help='train dataset name')
parser.add_argument('--val-dataset', type=str, default="val.rec",
                    help="validation dataset name")
parser.add_argument('--data-shape', type=int, default=299,
                    help='set image\'s shape')
args = parser.parse_args()

# network
import importlib
net = importlib.import_module('symbol_' + args.network).get_symbol(args.num_classes)

# data
if not os.path.exists(train_prefix_path + '.rec'):
	call_im2rec.convert(train_prefix_path, train_img_root_path)
if not os.path.exists(val_prefix_path + '.rec'):
	call_im2rec.convert(val_prefix_path, val_img_root_path)


def get_iterator(args, kv):

    data_shape = (3, args.data_shape, args.data_shape)
    train = mx.io.ImageRecordIter(
        path_imgrec = train_prefix_path + '.rec',
        # data_shape = (3,299,299),
        # path_imgrec = os.path.join(args.data_dir, args.train_dataset),
        # mean_r      = 123.68,
        # mean_g      = 116.779,
        # mean_b      = 103.939,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        rand_crop   = True,
        rand_mirror = True,
        # num_parts   = kv.num_workers,
        # part_index  = kv.rank
    )

    val = mx.io.ImageRecordIter(
        path_imgrec= val_prefix_path + '.rec',
        # data_shape = (3,299,299),
        # path_imgrec = os.path.join(args.data_dir, args.val_dataset),
        # mean_r      = 123.68,
        # mean_g      = 116.779,
        # mean_b      = 103.939,
        rand_crop   = False,
        rand_mirror = False,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        # num_parts   = kv.num_workers,
        # part_index  = kv.rank
    )

    return (train, val)

# train
train_model.fit(args, net, get_iterator)

# re_train.fit(args, net, get_iterator)