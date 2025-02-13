#%% Import Libraries

import cv2
import numpy as np
from tqdm import tqdm
from itertools import product
import time
import os
import shutil

#%% Class calculus for the upscaling

class upsc:
    
   def __init__ (self,name):
       
           #Import the picture using cv2 librairy
        
        self.picture_color = cv2.imread(name)
        self.picture_color = cv2.convertScaleAbs(self.picture_color) 
            
            #Creating the three matrices corresponding to each layer of the initial colored pictured 
        
        if (type(self.picture_color) != type(None)):    #check if the picture.color is a correct type (type(None) <=> wrong file name))

            self.picture_B = self.picture_color[:,:,0]
            self.picture_G = self.picture_color[:,:,1]
            self.picture_R = self.picture_color[:,:,2]

        else:                                           #Send the error message 

            warning = '\x1b[0;4;33m'                    #Red underline for the error message
            end  = '\x1b[0m'
            print(warning+"\nUnable to upscale the name of the file is incorrect or unuseable by openCV\n"+end)
            raise FileExistsError(name)                 #Raise the existing of the file error
            
            

   def black_edge (self,matrix_init,matrix_shape):
       
        #Adding a black line of two pixels around the initial matrix
       
        self.mag_matrix = np.zeros((matrix_shape[0] + 2,matrix_shape[1] + 2))
        
        for i in range (0, np.shape(matrix_init)[0]):
             for j in range (0, np.shape(matrix_init)[1]):
                 self.mag_matrix[i+1, j+1] = matrix_init[i, j]
                 
   def matrix_G (self,i,j,F): 
    
        self.G = np.array([[F[i,j], F[i,j+1], (F[i,j+1]-F[i,j-1])/2, (F[i,j+2]-F[i,j])/2],
                [F[i+1,j], F[i+1,j+1], (F[i+1,j+1]-F[i+1,j-1])/2, (F[i+1,j+2]-F[i+1,j])/2],
                [(F[i+1,j]-F[i-1,j])/2, (F[i+1,j+1]-F[i-1,j+1])/2, (F[i+1,j+1]-F[i+1,j]-F[i,j+1]+2*F[i,j]-F[i-1,j]-F[i,j-1]+F[i-1,j-1])/2, (F[i+1,j+2]-F[i+1,j+1]-F[i,j+2]+2*F[i,j+1]-F[i-1,j+1]-F[i,j]+F[i-1,j])/2],
                [(F[i+2,j]-F[i,j])/2, (F[i+2,j+1]-F[i,j+1])/2, (F[i+2,j+1]-F[i+2,j]-F[i+1,j+1]+2*F[i+1,j]-F[i,j]-F[i+1,j-1]+F[i,j-1])/2, (F[i+2,j+2]-F[i+2,j+1]-F[i+1,j+2]+2*F[i+1,j+1]-F[i,j+1]-F[i+1,j]+F[i,j])/2]])

   def Pf(self,x,y,C):
       
        X = np.array([1, x, x**2, x**3])
        Y = np.array([1, y, y**2, y**3])
        self.Z = X@C@np.transpose(Y)


   def Interpol(self,H):
       
        A=np.array([[1, 0, 0, 0],
                    [1, 1, 1, 1],
                    [0, 1, 0, 0],
                    [0, 1, 2, 3]])
    
        B = np.transpose(A)
        A = np.linalg.inv(A)
        B = np.linalg.inv(B)
        h_shape = H.shape
        self.N = np.zeros((2*h_shape[0]-2,2*h_shape[1]-2))
        
        #Creating the loading bar 
        with tqdm(total = 100) as pbar:
            
            for i in range (0,h_shape[0]-2):
                
                #Updating the loading bar
                pbar.update(100/(h_shape[0]-2))
                
                limit1 = range (0,h_shape[1]-2)
                limit2 = range(0,2,1)
                limit3 = range(0,2,1)
                
                for j,y,x in product (limit1,limit2,limit3):
                    
                    if x == 0 and y == 0:
                        self.N[2*i,2*j] = H[i,j]
                        
                    if x == 0 and y == 2:
                        self.N[2*i,2*j+1] = H[i,j+1]
                        
                    if x == 2 and y == 0:
                       self.N[2*i+1,2*j] = H[i+1,j]
                        
                    if x == 2 and y == 2:
                        self.N[2*i+1,2*j+1] = H[i+1,j+1]
                        
                    else:
                        self.matrix_G(i,j,H)
                        C = A@self.G@B
                        
                        self.Pf(x/2,y/2,C)
                        self.N[2*i+x,2*j+y] = self.Z


   def calc_image (self,file_name):
       
        if (type(file_name) != str):                    #Need a str as file name at least (do not check if there is an extension)
            warning = '\x1b[0;4;33m'                    #Red underline for the error message
            end  = '\x1b[0m'
            print(warning+"\nUnable to save the file the name of the file is incorrect!\n\nThe name of the file must be a str type\n"+end)
            raise TypeError(file_name)  
            
        #Recreating a matrix with three colored layer
       
        self.black_edge(self.picture_B, self.picture_B.shape)
        matrix_blue_edge = self.mag_matrix
        
        self.Interpol(matrix_blue_edge)
        matrix_blue = self.N
        
        self.black_edge(self.picture_G, self.picture_G.shape)
        matrix_green_edge = self.mag_matrix

        self.Interpol(matrix_green_edge)
        matrix_green = self.N
        
        self.black_edge(self.picture_R, self.picture_R.shape)
        matrix_red_edge = self.mag_matrix
        
        self.Interpol(matrix_red_edge)
        matrix_red = self.N
        
        C = np.zeros((matrix_blue.shape[0],matrix_blue.shape[1],3))
        
        C[:,:,0] = matrix_blue
        C[:,:,1 ]= matrix_green
        C[:,:,2] = matrix_red
        
        #Saving the file
    
        cv2.imwrite (file_name,C)

#%%
class save :                                        #Saving txt file class
                                                    #Class not mandatory as it add nothing to the efficieny of the prog or the picture quality output.
    
    def __init__ (self):
        self.directory = str(os.path.abspath(os.getcwd()))
        
        now = time.localtime(time.time())
        year, month, day, hour, minute, second, weekday, yearday, daylight = now
        self.hour = "%02dm%02dd%02dh%02dmin%02ds" % (month,day,hour, minute, second)
        self.file_name = "résultat ("+str(self.hour)+").txt"
        
    def write_file (self,string):
        
        fichier = open(self.file_name,"a")
        fichier.write(string)
        fichier.close()
        
    def clear_file (self):
        
        file = open(self.file_name,"w")
        file.close()
        
        
    def clear_folder(self,folder) :
        
        path = os.path.sep.join([self.directory,folder])
        
        if os.path.exists(path):
            shutil.rmtree(os.path.sep.join([self.directory,folder]))
            time.sleep(0.5)
        self.create_folder(folder)
        
    def create_folder (self,name):
        
        os.mkdir(name)

    def archiving_txt_file(self,name_archive_folder):
        
        path = os.path.sep.join([self.directory,name_archive_folder])
        
        if os.path.exists(path):
            src = os.path.sep.join([self.directory,self.file_name])
            dst = os.path.sep.join([path,self.file_name])
            shutil.copy(src,dst)
        
        else:
            self.create_folder(name_archive_folder)
            src = os.path.sep.join([self.directory,self.file_name])
            dst = os.path.sep.join([path,self.file_name])
            shutil.copy(src,dst)
        
        os.remove(src)
        
  
# class CSR:
    
    
#     def Matrix2CSR (self,init_matrix):            #From initial matrix to a CSR (compressed Row Storage) matrix
    
#         n,m = np.shape(init_matrix)
#         self.AX = []
#         self.AJ = []
#         self.AI = [0]
#         k = 0
        
#         for i in range (m):
#             for j in range (n):
                
#                 if init_matrix[i,j]!= 0:
                    
#                     k += 1
#                     self.AX = np.concatenate( (self.AX,[init_matrix[i,j]]),axis = 0)
#                     self.AJ = np.concatenate ( (self.AJ,[j]), axis = 0)
                    
#             self.AI = np.concatenate((self.AI,[k]), axis=0) 


#     def CSR2Matrix(self):  #From CSR matrix to the initial matrix
       
#         n = np.size(self.AI) - 1
#         self.reconstruct_matrix = np.zeros((n,n))
#         s = 0
        
#         for i in range(n):
#             nbr_term = self.AI[i+1]
            
#             while s < nbr_term:
#                 for j in range(s,nbr_term):
#                     ind_col = int(self.AJ[j])
#                     self.reconstruct_matrix[i,ind_col] = self.AX[s]
#                     s+=1
        
    
    
#     def ProdCSR(self,x):    #Multiplication using CSR matrix (using sparse matrix to improve performance)
       
#         prod_matrix = np.zeros(np.shape(x))   
#         n = np.size(self.AI) - 1
#         c = 0
        
#         for i in range(n):
#             nbr_term = self.AI[i+1] 
#             S = 0 
            
#             while c < nbr_term:
#                 for j in range(c,nbr_term):
#                     ind_col = int(self.AJ[j])
                   
#                     S += self.AX[c]*x[ind_col]
#                     c+=1
                    
#             prod_matrix[i] = S
#         return(prod_matrix)
        
#%% Main code
 
saving = save()
saving.clear_file()

start = time.time()

name_picture = "fraise4.jpg"
image = upsc(name_picture)
image.calc_image("upscaled_"+name_picture)

end = time.time()

sentence = "Time taken by the algorithm : "+str(end-start)
saving.write_file(sentence)

saving.archiving_txt_file("archive_folder")


