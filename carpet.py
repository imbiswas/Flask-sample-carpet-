from PIL import Image, ImageOps
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import colormap as cm
import webcolors

class carpet(object):
    def __init__(self,image_import,no_of_cluster):
        self.image_import=image_import
        self.partitions={}
        self.hexs=[]
        self.names=[]
        self.hsv=[]
        self.outputList=[]
        self.image(self.image_import)
        self.no_of_cluster = no_of_cluster
        self.starter()


    def image(self,image_import):
        target_size = (229, 229)
        self.im = Image.open(image_import)
        if self.im!=target_size:
            self.im=self.im.resize(target_size)
        self.im_a = np.array(self.im)
        self.width, self.height = self.im.size
        if (self.im_a.shape[2] == 4):
            self.im_mode = "RGBA"
        else:
            self.im_mode = "RGB"


    def closest_colour(self,requested_colour):
        min_colours = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        # print("closest_colour")
        return min_colours[min(min_colours.keys())]

    def get_colour_name(self,requested_colour):
        try:
            closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
        except ValueError:
            closest_name = self.closest_colour(requested_colour)
            actual_name = None
        # print("get_colour_name")
        return actual_name, closest_name

    def rgb_2_hsv(self,rgb_list):
        r = rgb_list[0] / 255
        g = rgb_list[1] / 255
        b = rgb_list[2] / 255

        minRGB = min(r, g, b)
        maxRGB = max(r, g, b)
        RGBrange = maxRGB - minRGB
        # print("rgb_2_hsv")
        # Black/White/Any Shade of Grey
        if (minRGB == maxRGB):
            Value = minRGB
            return [0, 0, Value]
        else:
            Saturation = RGBrange / maxRGB
            Value = maxRGB

            if (maxRGB == r):
                Hue = ((g - b) / RGBrange) % 6
            elif (maxRGB == g):
                Hue = ((b - r) / RGBrange) + 2
            elif (maxRGB == b):
                Hue = ((r - g) / RGBrange) + 4

            return [Hue * 60, Saturation, Value]

    def modified_rgb2hex(self,RGB):
        self.hexs.append(cm.rgb2hex(int(RGB[0]), int(RGB[1]), int(RGB[2])))
        self.names.append(self.get_colour_name((int(RGB[0]), int(RGB[1]), int(RGB[2])))[1])
        self.hsv.append(self.rgb_2_hsv([int(RGB[0]), int(RGB[1]), int(RGB[2])]))
        # print("modified_rgb2hex")

    def add_border(self,image, color):
        # print("add_border")
        return ImageOps.expand(image, border=10, fill=color)

    def mp(self, entry):
        # print("mp")
        return self.newclusters.get(entry, entry)

    def starter(self):
        pixel_values = list(self.im.getdata())

        # K Means Clustering
        self.clusters = range(0, self.no_of_cluster)#total number of cluster to be formed for the gicen set
        test_K = KMeans(n_clusters=len(self.clusters), random_state=0).fit(pixel_values)
        labels = test_K.labels_

        # Extract the Cluster Centers Info and Initialize the Final DF
        Kmeans_df = test_K.cluster_centers_
        Kmeans_df = [[int(x) for x in colors] for colors in Kmeans_df]
        try:
            Kmeans_df = pd.DataFrame(Kmeans_df, columns=("R", "G", "B"))
        except:
            Kmeans_df = pd.DataFrame(Kmeans_df, columns=("R", "G", "B","tmp"))
        Kmeans_df['RGB'] = Kmeans_df.iloc[:, 0:3].values.tolist()
        Kmeans_df.drop(Kmeans_df.columns[0:3], axis=1, inplace=True)

        
        list(map(self.modified_rgb2hex, Kmeans_df['RGB']))

        make_percent = lambda x: x * 100
        for v in self.hsv:
            v[0] = int(v[0])
            v[1] = round((make_percent(v[1])), 1)
            v[2] = round((make_percent(v[2])), 1)

        Kmeans_df['Hex'] = self.hexs
        Kmeans_df['Color Name'] = self.names
        Kmeans_df['HSV'] = self.hsv

        # Get the color tags (all color names in each cluster)
        tags = list(map(lambda x: self.get_colour_name(((int(x[0]), int(x[1]), int(x[2])))), pixel_values))
        tags = [colors[1] for colors in tags]
        try:
            color_tags = pd.DataFrame(pixel_values, columns=("R", "G", "B"))
        except:

            color_tags = pd.DataFrame(pixel_values, columns=("R", "G", "B","tmp"))
        color_tags['Cluster Number'] = labels
        color_tags['Tags'] = tags
        Kmeans_df['Tags'] = color_tags.groupby(by=['Cluster Number']).apply(lambda x: x['Tags'].unique())
        Kmeans_df

        # Cluster Percentages
        Kmeans_df['Percent'] = np.unique(labels, return_counts=True)[1]
        Kmeans_df['Percent'] = round((Kmeans_df['Percent'] / Kmeans_df['Percent'].sum()) * 100, 2)
        Kmeans_df.sort_values('Percent', ascending=False, axis=0, inplace=True)
        Kmeans_df['Percent'] = [str(x) + "%" for x in Kmeans_df['Percent']]
        Kmeans_df = Kmeans_df[['Percent', 'Color Name', 'Hex', 'RGB', 'HSV', 'Tags']]
        Kmeans_df.reset_index(drop=True, inplace=True)

        # #### Cluster Colorbar (By Pixels)

        positions = list(Kmeans_df['Percent'].copy(deep=True))
        positions = [x[:-1] for x in positions]
        positions = pd.DataFrame(positions, columns=["Percent"]).apply(pd.to_numeric)
        positions['Percent'] = positions['Percent'] / 100
        positions['End'] = positions['Percent'].cumsum(axis=0)
        positions['Start'] = positions['End'] - positions['Percent']


        # Create the Image Cluster Partitions
        # Reorder clusters from largest to smallest
        cluster_df = pd.DataFrame(np.unique(labels, return_counts=True)[0], columns=["Initial"])
        cluster_df['Counts'] = np.unique(labels, return_counts=True)[1]
        cluster_df.sort_values('Counts', ascending=False, axis=0, inplace=True)
        cluster_df['New'] = list(self.clusters)
        self.newclusters = dict(zip(cluster_df.Initial, cluster_df.New))

        #for mp from method
        mp = np.vectorize(self.mp)

        labels = mp(labels)
        labels2 = labels.reshape(self.height, self.width)

        partitions = {}

        for i in self.clusters:
            img = Image.new(self.im_mode, (self.width, self.height), "white")
            img_a = np.array(img)

            C0 = np.where(labels2 == i)
            rows = list(C0[0])
            cols = list(C0[1])

            for x in range(len(rows)):
                img_a[rows[x]][cols[x]] = self.im_a[rows[x]][cols[x]]

            img_new = Image.fromarray(img_a, mode=self.im_mode)
            img_new = self.add_border(img_new, Kmeans_df['Hex'][i])
            title_string = "Partition " + str(i + 1)
            partitions[title_string] = img_new

        df_shape=Kmeans_df.shape[0]
        for i in range(df_shape):
            alist=[]
            alist.append(Kmeans_df['Percent'][i])
            alist.append(Kmeans_df['Color Name'][i])
            alist.append(Kmeans_df['Hex'][i])
            self.outputList.append(alist)
        return (self.outputList)