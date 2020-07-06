import carpet
class manager(object):
    def __init__(self,len,bre,img,no_of_cluster):
        self.len=len
        self.bre=bre
        self.img=img
        self.no_of_color=no_of_cluster
        self.valueTaker()



    def valueTaker(self):
        self.area=self.len*self.bre
        datas=carpet.carpet(self.img,self.no_of_color).outputList
        return(datas,self.area)
        