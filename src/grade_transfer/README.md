# CSV Canvas Grade Transfer
> A Python tool to streamline uploading grades to Canvas from CSVs by simplifying formatting and automatically matching students.

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Workflow](#workflow)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
This program transfers students' grades of one or more assignments from a CSV file to a Canvas course. 



## Technologies Used
- Python - version 3.8
  - Install [Python 3.8.0](https://www.python.org/downloads/release/python-380/).


## Features
- Simplify the grade transfer process by requiring only three things:
    1. Canvas url, 
    2. User's Canvas token
    3. The path to the user's CSV file. 


- Match students automatically by their emails and SIDs first, then match the rest of students by their
unique full names or last names and prompt the user to verify name-based matches.

- Display a summary of unmatched students at the end. 



## Setup
#### Make sure three things are available before running the program:
1. Canvas url 
    - Example: https://canvas.ucdavis.edu/
    
2. The Canvas token
    - How to get Canvas API access tokens: https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89

3. The path to the CSV file on user's local computer

#### To run the program:

1. Install [CanvasAPI](https://github.com/ucfopen/canvasapi) by typing this command on the terminal and hitting <kbd>Enter</kbd>:

    `pip install canvasapi`

2. Clone this Git repository to a user chosen directory with git clone:   

    `git clone https://github.com/mfbutner/CanvasHelpers.git`

3. Inside the directory from step 2, go to the new sub-directory called "CanvasHelpers":   

    `cd CanvasHelpers`
   
4. Run the program using the `python3` command:

    `python3 start_grade_transfer.py`

5. Answer the first prompt which asks for the Canvas url:

    ![First_prompt_example](./first_prompt.png)
    
6. Follow the prompts and happy uploading :)


## Workflow

1. **Input collection**  
   The user provides:
   - Canvas URL  
   - Canvas API token  
   - Path to the CSV file  

2. **Course and assignment selection**  
   The program prompts the user to:
   - Select the course  
   - Choose the assignment group  
   - Select one or more assignments for grade upload  

3. **CSV column identification**  
   The first five rows of the CSV file are displayed.  
   The user is asked to identify the meaning of each column (e.g., name, email, SID, grade).

4. **Student matching**  
   The program attempts to match students from the CSV file with those in the Canvas course:
   - First by email and student ID (SID)  
   - Then by unique full name or last name (if still unmatched)  
   - The user is prompted to verify each name-based match  

5. **Grade upload**  
   The program updates grades on Canvas for all successfully matched students.  
   Progress is shown as each assignment’s grades are uploaded.

6. **Unmatched students report**  
   At the end, the program lists students from the CSV file whose grades were **not transferred**, showing:
   - Full names  
   - Emails  
   - Student IDs  
- Please visit [ExternalDocumentation](./ExternalDocumentation) for a more detailed workflow about this program. 



## Project Status
Functional and actively used, with room for future UI and logic improvements.


## Room for Improvement
To do:
- Upgrade the user interface from terminal command line to a local website.

- Find a more efficient algorithm to 
    1. Match students based on Email, SIDs, and names. 
    2. Link students together when filling in the grade book dictionary.

- Change the update announcements to after the grades are uploaded to Canvas.

- Use other data structures than dictionary when announcing the leftover CSV students at the end because at this point 
names are not guaranteed to be unique and SID/email may not exist.

- Test more corner cases.

- Add more comments to functions. 



## Acknowledgements
- This project uses the [CanvasAPI](https://github.com/ucfopen/canvasapi) package which served as a Python API wrapper for
instructor's Canvas learning management system (LMS).   

- Many thanks to Matthew Butner (mfbutner@ucdavis.edu), UC Davis CS instructor, to guide this project.



## Contact
Created by Qianhan "Janet" Zhang (jqhzhang@gmail.com) - feel free to contact me!

