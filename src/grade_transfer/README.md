# CSV Canvas Grade Transfer
> An improvement/alternative (?) of the current Canvas method of uploading grades from CSV files.

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
This program transfers students' grades of one or more assignments from a CSV file to a Canvas course. 



## Technologies Used
- Python - version 3.8


## Features
- Simplify the grade transfer process by requiring only three things: 1. Canvas url, 2. user's Canvas token, and 3. the 
path to the user's CSV file. 

- Match students automatically by their emails and student IDs (SIDs) first, then match the rest of students by their
unique full names or last names and ask user to verify these name matches.

- Notify the user about which students' grades are not successfully transferred from the CSV file at the end of the program. 



## Setup
Make sure three things are available before running the program:
1. a Canvas url (example: https://canvas.ucdavis.edu/)

2. the Canvas token (How to get Canvas API access tokens: https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89)

3. the path to the CSV file on user's local computer

To run the program, 
1. (Skip if Python >= 3.8.0 is installed) Install [Python 3.8.0](https://www.python.org/downloads/release/python-380/). 

2. Install CanvasAPI by typing this command on the terminal and hitting <kbd>Enter</kbd>:

    `pip install canvasapi`

3. Clone this Git repository to the user chosen directory with git clone:
    
    `git clone https://github.com/mfbutner/CanvasHelpers.git`

4. Inside the chosen directory of step 3, go to the new sub-directory called "CanvasHelpers":
    
    `cd CanvasHelpers`
    
5. Go to the sub-directory called " src":

    `cd src`
    
6. Go to the sub-directory called "grade_transfer":

    `cd grade_transfer`
    
7. Run the program using the `python3` command:

    ``



## Usage
- After given a valid Canvas url, the user's Canvas token, and the path to the CSV file, the program asks the user to 
specify the course and assignments to which they want the grades to be uploaded. 

- Then the program shows the first five rows 
in the CSV file and ask user to identify what each column represents.

- The program first matches students from the CSV file and the Canvas course by their emails and student IDs (SID), then 
it matches the leftover students who can't be matched by emails or SIDs by their unique full names and last names. 



## Project Status
The program is functional but it's not in the ideal state. More updates will be upcoming.


## Room for Improvement
To do:
- Upgrade the user interface from terminal command line to local website.

- Find a more efficient algorithm to match students based on Email, SIDs, and names. 

- Add more comments to functions. 



## Acknowledgements
- This project uses the [CanvasAPI](https://github.com/ucfopen/canvasapi) package which served as a Python API wrapper for
instructor's Canvas learning management system (LMS).   

- Many thanks to Matthew Butner (mfbutner@ucdavis.edu), UC Davis CS instructor, to guide this project.



## Contact
Created by Qianhan "Janet" Zhang (jqhzhang@ucdavis.edu) - feel free to contact me!

