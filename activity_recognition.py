import numpy as np
import cv2

def readData(files, N):
    output = '/Users/jordancampbell/Desktop/all_asfamc/data/temp.amc'
    data = []
    DOF = 0
    for fidx, f in enumerate(files):
        file = open(f)
        out = open(output, 'w')
        lines = [line.split() for line in file]
        for i in range(3, len(lines)):
            if len(lines[i]) == 1:
                for k in range(1,28):
                    for j in range(1, len(lines[i+k])):
                        out.write(lines[i+k][j])
                        out.write(' ')
                out.write('\n')
        out.close()
        file = open(output)
        lines = [[float(x) for x in line.split()] for line in file]
        data.append(np.zeros((N, len(lines[0]))))
        index = np.linspace(0, len(lines)-1, num=N).astype(int)
        DOF = len(lines[0])
        for i in range(N):
            for k in range(len(lines[0])):
                data[fidx][i,k] = lines[index[i]][k]
    return data

def run():

    files = []
    files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(1)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(2)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(3)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(4)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(5)+ '.amc')

    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/107/08_0'+ str(1)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/107/08_0'+ str(2)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/107/08_0'+ str(3)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(4)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(5)+ '.amc')

    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(1)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(2)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(3)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(4)+ '.amc')
    # files.append('/Users/jordancampbell/Desktop/all_asfamc/subjects/08/08_0'+ str(5)+ '.amc')

    N = 100

    data = readData(files, N)

    print len(data)

def draw_flow(im, flow, step=8):

    h,w = im.shape[:2]

    y,x = np.mgrid[step/2:h:step,step/2:w:step].reshape(2,-1)
    fx,fy = flow[y,x].T

    lines = np.vstack([x,y,x+fx, y+fy]).T.reshape(-1,2,2)
    lines = lines.astype(int)

    for (x1,y1), (x2,y2) in lines:
        cv2.line(im, (x1,y1),(x2,y2),(0,255,0),1)
        cv2.circle(im,(x1,y1),1,(0,255,0), -1)
    return im


def show_tracks(flow_tensor, image, frame, save=False):

    step = 8
    h,w = image.shape[:2]

    pt = np.zeros(2)
    pt2 = np.zeros(2)

    x,y = np.linspace(0+step/2.,w-step/2.,w/step).astype(int), np.linspace(0+step/2.,h-step/2.,h/step).astype(int)

    tracks = np.zeros((x.shape[0]*y.shape[0],frame, 2))

    index = 0
    for i in range(x.shape[0]):
        for k in range(y.shape[0]):

            pt[:] = x[i],y[k]

            for j in range(frame):

                if pt[0] < 0:
                     pt[0] = 0
                if pt[1] < 0:
                     pt[1] = 0
                if pt[0] > w:
                     pt[0] = w-1
                if pt[1] > h:
                     pt[1] = h-1

                pt2 = pt + flow_tensor[j][pt[1].astype(int), pt[0].astype(int)]

                cv2.line(image, (pt[0].astype(int), pt[1].astype(int)), 
                    (pt2[0].astype(int), pt2[1].astype(int)) ,(0,0,255))

                tracks[index,j,:] = pt2[0].astype(int), pt2[1].astype(int)

                pt = np.copy(pt2)

            index += 1

    return image, tracks


def optical_flow_tracking():


    dir = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/data/CHG/0000/0000/frame-00'
    file = dir + str(0)+str(0) + '.jpg'
    frame = cv2.imread(file)

    flow_tensor = []

    for i in range(60):

        if i < 9:
            file_p = dir + str(0)+str(i) + '.jpg'
            file_n = dir + str(0)+str(i+1) + '.jpg'
        elif i == 9:
            file_p = dir + str(0)+str(i) + '.jpg'
            file_n = dir + str(i+1) + '.jpg'
        else:
            file_p = dir + str(i) + '.jpg'
            file_n = dir + str(i+1) + '.jpg'

        prev = cv2.imread(file_p, 0)
        next = cv2.imread(file_n, 0)
        frame = cv2.imread(file_p)

        flow = cv2.calcOpticalFlowFarneback(prev,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        flow_tensor.append(flow)

        # flow_img, tracks = show_tracks(flow_tensor, frame, i+1)

        flow_img = draw_flow(frame, flow)

        cv2.imshow("Prev", prev)
        cv2.imshow("Prev", next)
        cv2.imshow("Flow", flow_img)

        cv2.waitKey(1)

    flow_img, tracks = show_tracks(flow_tensor, frame, i+1)

    frame = cv2.imread(file_p)

    for i in range(tracks.shape[0]):
        for k in range(tracks.shape[1]-1):
                cv2.line(frame, (tracks[i,k,0].astype(int), tracks[i,k,1].astype(int)), 
                    (tracks[i,k+1,0].astype(int), tracks[i,k+1,1].astype(int)) ,(255,0,0))

    cv2.imshow("Flow", frame)
    cv2.waitKey(0)




