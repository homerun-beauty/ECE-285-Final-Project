import os
import argparse

import torch
from easydict import EasyDict as edict

def parse_train_configs():
    parser = argparse.ArgumentParser(description='The Implementation of Complex YOLOv4')
    parser.add_argument('--seed', type=int, default=2020, help='re-produce the results with seed random')
    
    parser.add_argument('--gpu_idx', default=None, type=int, help='GPU index to use.')
    parser.add_argument('--dist_url', default='tcp://127.0.0.1:29500', type=str, help='url used to set up distributed training')
    parser.add_argument('--world_size', default=-1, type=int, metavar='N', help='number of nodes for distributed training')
    
    parser.add_argument('--working-dir', type=str, default='./', metavar='PATH', help='The ROOT working directory')
    parser.add_argument('--multiprocessing_distributed', action='store_true', help='Use multi-processing distributed training to launch '
                             'N processes per node, which has N GPUs. This is the '
                             'fastest way to use PyTorch for either single node or '
                             'multi node data parallel training')
    
    ##############     Model configs            ########################
    
    parser.add_argument('-a', '--arch', type=str, default='darknet', metavar='ARCH', help='The name of the model architecture')
    parser.add_argument('--model_def', type=str, default='config/cfg/complex_yolov4.cfg', metavar='PATH', help='The path for cfgfile (only for darknet)')
    parser.add_argument('--pretrained_path', type=str, default="checkpoints/complex_yolov4_mse_loss.pth", metavar='PATH', help='the path of the pretrained checkpoint')
    # parser.add_argument('--pretrained_path', type=str, default="checkpoints/Model_complexer_yolo_V4.pth", metavar='PATH', help='the path of the pretrained checkpoint')
    parser.add_argument('--save_path', type=str, default="checkpoints/Model_complexer_yolo_V4.pth", metavar='PATH', help='the path of the save checkpoint')
    parser.add_argument('--use_giou_loss', action='store_true', help='If true, use GIoU loss during training. If false, use MSE loss for training')
    parser.add_argument('--gradient_accumulations', type=int, default=2, help="number of gradient accums before step")
    parser.add_argument('--evaluation_interval', type=int, default=2, help="interval evaluations on validation set")

    ##############     Dataloader and Running configs            #######

    parser.add_argument('--img_size', type=int, default=608, help='the size of input image')
    parser.add_argument('--hflip_prob', type=float, default=0.5, help='The probability of horizontal flip')
    parser.add_argument('--cutout_prob', type=float, default=0., help='The probability of cutout augmentation')
    parser.add_argument('--cutout_nholes', type=int, default=1, help='The number of cutout area')
    parser.add_argument('--cutout_ratio', type=float, default=0.3, help='The max ratio of the cutout area')
    parser.add_argument('--cutout_fill_value', type=float, default=0., help='The fill value in the cut out area, default 0. (black)')
    parser.add_argument('--multiscale_training', action='store_true', help='If true, use scaling data for training')
    parser.add_argument('--mosaic', action='store_true', help='If true, compose training samples as mosaics')
    parser.add_argument('--random-padding', action='store_true', help='If true, random padding if using mosaic augmentation')
    parser.add_argument('--no-val', action='store_true', help='If true, dont evaluate the model on the val set')
    parser.add_argument('--num_samples', type=int, default=None, help='Take a subset of the dataset to run and debug')
    parser.add_argument('--num_workers', type=int, default=4, help='Number of threads for loading data')
    parser.add_argument('--batch_size', type=int, default=1,  help='mini-batch size (default: 4), this is the total'
                             'batch size of all GPUs on the current node when using'
                             'Data Parallel or Distributed Data Parallel')
    parser.add_argument('--print_freq', type=int, default=50, metavar='N', help='print frequency (default: 50)')
    parser.add_argument('--tensorboard_freq', type=int, default=20, metavar='N', help='frequency of saving tensorboard (default: 20)')
    parser.add_argument('--checkpoint_freq', type=int, default=2, metavar='N', help='frequency of saving checkpoints (default: 2)')

    ##############     Training strategy            ####################
    
    parser.add_argument('--start_epoch', type=int, default=1, metavar='N', help='the starting epoch')
    parser.add_argument('--num_epochs', type=int, default=4, metavar='N', help='number of total epochs to run')
    parser.add_argument('--lr_type', type=str, default='cosin', help='the type of learning rate scheduler (cosin or multi_step)')
    parser.add_argument('--lr', type=float, default=0.001, metavar='LR', help='initial learning rate')
    parser.add_argument('--minimum_lr', type=float, default=1e-7, metavar='MIN_LR', help='minimum learning rate during training')
    parser.add_argument('--momentum', type=float, default=0.949, metavar='M', help='momentum')
    parser.add_argument('-wd', '--weight_decay', type=float, default=5e-4, metavar='WD', help='weight decay (default: 5e-4)')
    parser.add_argument('--optimizer_type', type=str, default='adam', metavar='OPTIMIZER', help='the type of optimizer, it can be sgd or adam')
    parser.add_argument('--burn_in', type=int, default=50, metavar='N', help='number of burn in step')
    parser.add_argument('--steps', nargs='*', default=[1500, 4000], help='number of burn in step')

    ##############     Loss weight            ##########################

    ##############     Distributed Data Parallel            ############

    parser.add_argument('--rank', default=-1, type=int, metavar='N', help='node rank for distributed training')
    parser.add_argument('--dist-backend', default='nccl', type=str, help='distributed backend')
    
    parser.add_argument('--no_cuda', action='store_true', help='If true, cuda is not used.')
    
    ##############     Evaluation configurations     ###################

    # parser.add_argument('--evaluate', action='store_true', help='only evaluate the model, not training')
    parser.add_argument('--resume_path', type=str, default=None, metavar='PATH', help='the path of the resumed checkpoint')
    parser.add_argument('--conf_thres', type=float, default=0.5, help='for evaluation - the threshold for class conf')
    parser.add_argument('--nms_thres', type=float, default=0.5, help='for evaluation - the threshold for nms')
    parser.add_argument('--iou_thres', type=float, default=0.5, help='for evaluation - the threshold for IoU')
    parser.add_argument('--saved_fn', type=str, default='complexer_yolo', metavar='FN', help='The name using for saving logs, models,...')
    

    configs = edict(vars(parser.parse_args()))

    ############## Hardware configurations #############################

    configs.device = torch.device('cpu' if configs.no_cuda else 'cuda')
    configs.ngpus_per_node = torch.cuda.device_count()
    configs.pin_memory = True

    ############## Dataset, logs, Checkpoints dir ######################
    
    configs.dataset_dir = os.path.join(configs.working_dir, 'dataset', 'kitti')
    configs.checkpoints_dir = os.path.join(configs.working_dir, 'checkpoints')
    configs.logs_dir = os.path.join(configs.working_dir, 'logs')

    if not os.path.isdir(configs.checkpoints_dir):
        os.makedirs(configs.checkpoints_dir)
    if not os.path.isdir(configs.logs_dir):
        os.makedirs(configs.logs_dir)

    return configs
