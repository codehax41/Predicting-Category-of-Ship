# -*- coding: utf-8 -*-
"""multi-classifiers.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16hHmi_h6sy4o4SK2WiQKdnGhEr7lwunP
"""



from fastai.vision import *

# %reload_ext autoreload
# %autoreload 2
# %matplotlib inline

"""**connect gdrive**"""

from google.colab import drive
drive.mount('/content/gdrive')

"""# **make directory data/image**"""

mkdir data

mkdir data/image

"""moving image dataset to data/image"""

mv 'gdrive/My Drive/ieee/images.rar' data/image

"""using unrar tool to extract rar file"""

cd data/image

!unrar e -r images.rar

"""upload train,test csv files"""

cd ..

mv train.csv data/image

mv test.csv data/image

df = pd.read_csv('data/image/train.csv')
df.head()

tfms = get_transforms(flip_vert=True, max_lighting=0.1, max_zoom=1.05, max_warp=0.)

np.random.seed(42)
src = (ImageList.from_csv('data/image', 'train.csv')
       .split_by_rand_pct(0.2)
       .label_from_df(label_delim=' '))

data = (src.transform(tfms, size=128)
        .databunch().normalize(imagenet_stats))

data.show_batch(rows=3, figsize=(12,9))

print(data.classes)
len(data.classes),data.c

data.label_list

arch = models.resnet50

f_score = partial(fbeta, thresh=0.5)
learn = cnn_learner(data, arch, metrics=[f_score])

learn.lr_find()

learn.recorder.plot()

lr=0.01

learn.fit_one_cycle(5, slice(lr))

learn.save('stage-1-rn50')

"""fine tuning the model"""

learn.unfreeze()

learn.lr_find()
learn.recorder.plot(suggestion=True)

learn.fit_one_cycle(5, slice(1e-5, lr/5))

learn.save('stage-2-rn50')

"""changing the image size to 256"""

data = (src.transform(tfms, size=256).databunch().normalize(imagenet_stats))

learn.data = data
data.train_ds[0][0].shape

learn.freeze()

learn.lr_find()
learn.recorder.plot(suggestion=True)

lr=1e-2/2

learn.fit_one_cycle(5, slice(lr))

learn.save('stage-1-256-rn50')

learn.unfreeze()

learn.fit_one_cycle(5, slice(1e-5, lr/5))

learn.recorder.plot_losses()

learn.save('stage-2-256-rn50')

learn.export()

"""# testing(submission.csv generation)"""

test = ImageList.from_csv('data/image', 'test.csv')
len(test)

learn = load_learner("data/image", test=test)
preds, _ = learn.get_preds(ds_type=DatasetType.Test)

thresh = 0.2
labelled_preds = [' '.join([learn.data.classes[i] for i,p in enumerate(pred) if p > thresh]) for pred in preds]

max(preds[9])

labelled_preds[15]

fnames = [f[11:] for f in learn.data.test_ds.items]

df = pd.DataFrame({'image':fnames, 'category':labelled_preds}, columns=['image', 'category'])

df.head()





df.to_csv('data/image/submission.csv', index=False)

mv data/image/submission.csv data

