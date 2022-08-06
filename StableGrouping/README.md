# CanvasHelpers
A collection of useful applications for doing things Canvas can't do natively.  
This folder contains the study group matching program

## Installation
1. Clone this repository
2. Install Python libraries listed in `requirements.txt` with `pip install -r requirements.txt`
3. Copy the `template.env` file and name the copy `.env`
4. Place the `.env` file in the project root if it is not there already (Same folder as `requirements.txt`)
5. Update the lines in the `.env` file as needed:
   * `API_URL`: URL for the university's Canvas. Do not end with trailing `/`
   * `API_KEY`: Your Canvas API Key, generate one from your Canvas Profile page
   * `ENVIRONMENT`: Set to `PRODUCTION` to actually run the code and anything else for dry test runs
6. Update `config.json` as needed. You will need to update this every time you run the program for a new class/quiz
   * Also, `group_number` should be increased by `1` each time you run it again for the same course
   * `course.id`: Found in the URL on the Course page (Example: `1599` from `https://canvas.ucdavis.edu/courses/1599`)
   * `course.name`: Arbitrary, it's never used (at the moment) and is only for your reference
   * `quiz_id`: Found in the URL on the preferences survey/quiz on Canvas (Example: `178978` in `https://canvas.ucdavis.edu/courses/1599/quizzes/178978`)
   * `patterns`: Update if the questions on the quiz change. The default should be fine for now. If a quiz question contains the text, it is mapped to that property

## Usage
Run the `main.py` file once installation is complete to match students and create Canvas Groups.  
When given a Canvas Quiz containing the appropriate questions, the program will automatically fetch responses and create groups of students based on their stated preferences.  
Students who do not fill the quiz are given the lowest priority.  
The program will actively go into Canvas and create groups with the name "Study Group {studyGroupNumber}", no additional work is necessary.  Students will also get a message in their Canvas inbox, listing their group mates' available schedules and preferences.

## Contributing
The revised project was built by Marvin Lee, Megan Mok, Shyam Agarwal, and Shang Wu for Professor Butner at UC Davis.  
The original project was built by Rebekah Grace, Howard Wang, and Stephanie Chung for Professor Butner at UC Davis.  
This is a closed project, so public contributions may not be considered.