# CanvasHelpers
A collection of useful applications for doing things Canvas can't do natively


## Installation
1. Each time the program is run, the follow needs to enter the following:
  APIKEY : personal API key
  CLASS_ID : the unique class number (you can see it in the url if you navigate to the class)
  QUIZ_ID: the quiz's identification (you can see it in the url if you navigate to the quiz)
  className: the name of the class you are evaluating
  studyGroupNumber: the number study group you are on, in int form
  
2. If ever moved from ECS 036A and ECS 154A, the quiz numbers in the parser will need to be updated and possibly the questions themselves

3. There is no UI, the code's main file must be changed. The needed MACROs are located on the top of the header.

## Usage
 
When given a Canvas Quiz containing the appropriate questions, the program will automatically download the class list and the student responses. It create groups of students based on their own stated preferences.  Students who do not fill the quiz are given lowest priority.  The program will actively go into Canvas and create groups with the name "Study Group " + str(studyGroupNumber), no additional work is necessary.  Students will also get a message in their canvas inbox, listing their groupmates available schedules and preferences.

## Contributing

This project was built by Rebekah Grace, Howard Wang, and Stephanie Chung for a Professor Butner at UC Davis.
This is a closed project, not available for contributions.  
