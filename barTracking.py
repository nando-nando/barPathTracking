import cv2
import os


"""
author: Nando
Program is used to track bar movements of a workout then output save a video
Video is saved as an mp4 and input file paths are asked for, output file path is static 
and user only gives the name of the output program.
The most ideal input video is one that is taken in a side view so the full face of the plate is present. (Make it easier to track)
"""


def getFilePath():

    """
    author: Nando
    Function gets the file path of the original video
    throws: FileNotFoundError -> if the file can't be found/does not exist
            Exception -> if the file given is not an mp4 file
    return: filepath
    """

    filepath = input("Enter filepath of video: ")

    #check of the file exists
    if os.path.exists(filepath) == False:
        raise FileNotFoundError("The file given does not exist")

    #check if the file is a mp4 file
    if filepath.endswith(".mp4") != True:
        raise Exception("File is not a video.")

    return filepath


def getNameOfNewVideo():

    """
    author: Nando
    Function creates file path for the output video
    return: file path
    """

    destination = input("Enter where the video should be saved: ")
    newFileName = input("Enter the name of the new video: ")
    newFileName = newFileName + ".mp4"
    finalFilePath = destination + newFileName

    return finalFilePath



def createCaptureTracker():

    """
    author: Nando
    Function creates video capture object (can be thought as the video) and tracker objects
    return: Video and Tracker objects
    """

    filepath = getFilePath()
    video = cv2.VideoCapture(filepath)
    tracker = cv2.TrackerKCF_create()

    return video, tracker


def createVideoWriter(video):

    """
    author: Nando
    Function creates video writer object
    params: video object
    return: video writer object
    """
    
    #get size of the original video in otder to make output video same size
    sizeOfOutput = (int(video.get(3)), int(video.get(4)))
    outputName = getNameOfNewVideo()
    output = cv2.VideoWriter(outputName, cv2.VideoWriter_fourcc(*"mp4v"), 30, sizeOfOutput)

    return output


def createBoundingBox(video, tracker):

    """
    author: Nando
    Function attempts to initialize the tracker while allowing user to apply a bounding box to an object in the video
    params: video object
    return: video writer object
    """

    #read in the first frame of the video
    #if returnValue is false, that tells us that no frames have been read (video is over).
    returnValue, frame = video.read()
    #show the frame
    cv2.imshow("Frame", frame)
    #This allows the user to select the "region of interest"
    boundingBox = cv2.selectROI("Frame", frame)

    #initialize the tracker with the frame and the object being tracked in the ROI
    try:
        tracker.init(frame, boundingBox)
    #if this fails throw exception
    except:
        print("A bounding box was not correctly created. Please try again.")
    
    return tracker




def main():

    """
    author: Nando
    Main driver of the program
    The program will end up drawing a circle in the middle of the object being tracked as well as showing the 
    previous path of that object.
    """
    
    video, tracker = createCaptureTracker()
    videoWriter = createVideoWriter(video)
    tracker = createBoundingBox(video, tracker)
    #list to hold all prev posiotions of object
    centerPoints = []
    
    while True:
        
        returnValue, frame = video.read()
        #if the return value is false we can break bc the video is done
        if not returnValue:
            break
        
        #find the next pos of object being tracked, (success is true if the object is located)
        (success, box) = tracker.update(frame)

        if success: #if true
            #gives coords for bounding box
            (x, y, w, h) = [int(i) for i in box]
            #draw it
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #gives the pos of the center of the object to later show its prev positions
            centerOfRectangle = (int(x + w/2), int(y + h/2))
            #this circle drawn in the center shows the center
            cv2.circle(img = frame, center = centerOfRectangle, radius = 3, color = (0, 0, 255), thickness = -1)
            #we append the the center of the object to later then be able to draw prev positions
            centerPoints.append(centerOfRectangle)
            #go thru the list of center points
            for i in range(len(centerPoints)):
                #we are drawing lines through the first point recorded to the most recent
                #this if statement makes sure that we dont connect the last point to the first creating a polygon
                if (i - 1) == -1:
                    continue
                #connect points with a line
                cv2.line(frame, pt1 = centerPoints[i - 1], pt2 = centerPoints[i], color = (0, 0, 255), thickness = 2)
            #write this frame to output video
            videoWriter.write(frame)
            #shwo the frame
            cv2.imshow("Frame", frame)

            #this code allows us to assign a key that would break the object tracking
            #in this use case it is not needed but it is nice to have
            #KEY IS "q"
            key = cv2.waitKey(5) & 0xFF
            if key == ord("q"):
                break

    #closes video, and writer when done
    videoWriter.release()
    video.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    main()
