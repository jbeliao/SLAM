SLAM
====

SLAM : a method for the automatic Stylization and LAbelling of speech Melody
(optimized only for LINUX distributions)


please cite :  Obin, N., Beliao, J., Veaux, C., & Lacheret, A. (2014). 
               SLAM: Automatic Stylization and Labelling of Speech Melody. 
               Speech Prosody 7, 246-250.

/!\
First of all :
- download SLAM and swipe-installer and put them in the same repository.
- then, follow the instructions below:
/!\

1) install SWIPE module

Swipe, by Kyle Gorman (http://ling.upenn.edu/~kgorman/c/swipe/),  is a pitch estimation algorithm which is required for SLAM to work. 
Sources of swipe are provided in the swipe-installer directory. These are slightly modified versions different from the official github release. Modifications are only for the purpose of swipe compiling under C89 instead of C99 standards.
  
2) Use SLAM
   a) drop your wav files and textgrid files in the corresponding directories. wav and textgrid files must come in pair of the same name 
     example:
     "myfile1.wav" "myfile1.TextGrid" "myfile2.wav" "myfile2.TextGrid"

   b) open a terminal and go to the SLAM directory
   c) type "python SLAM.py"
   d) follow the instructions.

3) Configure SLAM

you can open SLAM.py and modify the parameters to suit your needs. 
