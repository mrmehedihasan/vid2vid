### Copyright (C) 2017 NVIDIA Corporation. All rights reserved. 
### Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
### Next Day Line 10
import time
import os
import numpy as np
from collections import OrderedDict
from torch.autograd import Variable
from options.test_options import TestOptions
from data.data_loader import CreateDataLoader
from models.models import create_model
import util.util as util
from util.visualizer import Visualizer
from util import html

opt = TestOptions().parse(save=False)
opt.nThreads = 1   # test code only supports nThreads = 1
opt.batchSize = 1  # test code only supports batchSize = 1
opt.serial_batches = True  # no shuffle
opt.no_flip = True  # no flip
opt.dataset_mode = 'test'

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
model = create_model(opt)
visualizer = Visualizer(opt)
input_nc = 1 if opt.label_nc != 0 else opt.input_nc

# create website
web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))

print('Doing %d frames' % len(dataset))
for i, data in enumerate(dataset):
    if i >= opt.how_many:
        break    
    if data['change_seq']:
        model.fake_B_prev = None

    _, _, height, width = data['A'].size()
    A = Variable(data['A']).view(1, -1, input_nc, height, width)
    B = Variable(data['B']).view(1, -1, opt.output_nc, height, width) if opt.use_real_img else None
    inst = Variable(data['inst']).view(1, -1, 1, height, width) if opt.use_instance else None
    generated = model.inference(A, B, inst)
    
    if opt.label_nc != 0:
        real_A = util.tensor2label(generated[1][0], opt.label_nc)
    else:            
        real_A = util.tensor2im(generated[1][0,0:1], normalize=False)    
    
    visual_list = [('real_A', real_A), 
                   ('fake_B', util.tensor2im(generated[0].data[0]))]    
    visuals = OrderedDict(visual_list) 
    img_path = data['A_paths']
    print('process image... %s' % img_path)
    visualizer.save_images(webpage, visuals, img_path)    
