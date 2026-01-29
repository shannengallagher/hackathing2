# hackathing2

## Syllabus Parser

## Project Description
I attempted to build a website that a user can upload a syllabus to and the website will parse the syllabus for assignments. Each assignment will be sorted into a category (homework, paper, exam, etc.) and depending on the category, an estimated length till completion. This number can also be edited by the user if they think it is an over/under estimate. Due dates can also be added to each assignment. 

## What was learned
1. Frontend/backend communication with error tracing
2. How to figure out when the product might be 'working' on the backend (not producing erros), yet not functioning as intended on the frontend.
3. LLM responses need extensive type checking
4. Simpler prompts worked substantially better. Asking for assignment titles rather than full details produced more reliable results.
5. JSON format constraint in Ollama caused some empty responses. Needed to consider this. 

## How does this relate to possible project ideas
In the actual project, we are hoping to be able to link google calendar/personal calendars with canvas, class syllabi, etc. Our project will need to be able to parse data of various formats and provide useful output that does not require extensive manual entry of information. This was an attempt to kickstart understanding how frontend/backend document uploading worked and what information could easy be parsed and what couldn't. 

## What didn't work
1. It was hard to get syllabi of different formats to be processed in the same way. This created issues with parsing assignment-specific information such as due date. 
2. Due to syllabi format, some were recognized as having 0 assignments listed. This required changing AI model, character limits, etc. to find the right balance as to not overload the system and make sure that substantial information could still be parsed.
3. The tool still requires a lot of manual user input, which makes it fairly ineffective for its purpose. 
4. Asking for due dates, descriptions, and time estimates produced unreliable or incorrectly formed JSON due to format variation 
5. Sometimes the first upload does not take and you have to reupload. I was having trouble ironing out this issue. 

## Technical References
Claude code
